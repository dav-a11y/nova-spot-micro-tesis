#!/usr/bin/env python3
"""¿Se mueve el robot igual que la simulación? (27-oct)

Toma una caminata grabada en el robot suspendido (grabaciones/<caminata>/caminata.csv y su config), ejecuta
la MISMA marcha y política en MuJoCo con el robot colgado (sin peso en las patas, actuador medido, sin
aleatorización) y compara, articulación por articulación con sensor, el ciclo medio del ángulo:
  - forma: correlación r entre el ciclo del robot y el de la simulación (tras alinear el desfase);
  - amplitud: recorrido del robot / recorrido de la simulación;
  - desfase: retraso del robot respecto a la simulación (ms).
Parecido de una articulación = 100 × max(0, r) × min(amplitud, 1/amplitud). Parecido de la caminata =
media de las articulaciones con sensor válido.

Uso: comparar_sim_real.py ../camaras/grabaciones/<caminata> [--figura]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
BINS = 60


def ciclo_medio(fase, x):
    """Media de x en BINS intervalos de fase (0-1)."""
    idx = np.minimum((np.asarray(fase) * BINS + 0.01).astype(int), BINS - 1)   # la fase del robot va redondeada
    out = np.full(BINS, np.nan)
    for b in range(BINS):
        v = x[(idx == b) & ~np.isnan(x)]
        if len(v):
            out[b] = v.mean()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caminata", type=Path)
    ap.add_argument("--figura", action="store_true")
    ap.add_argument("--calibracion-actual", action="store_true",
                    help="28-oct: usar sensores_robot.json de hoy en vez de la calibración guardada con la caminata")
    # 5-nov: probar un modelo del actuador distinto (p. ej. con la ganancia ajustada por marcha) sin pisar el resultado.
    ap.add_argument("--actuador", type=Path, default=HERE / "actuadores_ciclo2.json")
    ap.add_argument("--salida", default="comparacion_sim_real.json", help="nombre del json de resultados en la caminata")
    a = ap.parse_args()
    import csv
    import entrenar_ppo_real as E
    import ejecutar_politica_robot as R
    cfg = json.loads((a.caminata / "caminata.config.json").read_text())
    filas = list(csv.DictReader((a.caminata / "caminata.csv").open()))
    # Marcha igual que la ejecutada en el robot.
    E.MARCHA = cfg["marcha"]
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = cfg["femur_deg"], cfg["tibia_deg"], cfg["fase_s"]
    if cfg.get("ciclo_paso_s"):
        E.PASO_CICLO_S = cfg["ciclo_paso_s"]
    arg = cfg.get("argumentos", [])
    def valor(nombre, defecto):
        return float(arg[arg.index(nombre) + 1]) if nombre in arg else defecto
    modelo = None
    if cfg.get("politica"):
        md = json.loads((Path(cfg["politica"]).parent / "metadata.json").read_text()) \
            if Path(cfg["politica"]).is_absolute() else \
            json.loads((HERE / Path(cfg["politica"]).parent / "metadata.json").read_text())
        m = md["marcha"]
        E.TROTE_CICLO_S = m.get("ciclo_trote_s", 1.0)
        E.APERTURA_DEG, E.COXA_AMP_DEG = m.get("apertura_deg", 0.0), m.get("coxa_deg", 0.0)
        E.PASO_CICLO_S = m.get("ciclo_paso_s", E.PASO_CICLO_S)
        from stable_baselines3 import PPO
        ruta = Path(cfg["politica"]) if Path(cfg["politica"]).is_absolute() else HERE / cfg["politica"]
        modelo = PPO.load(ruta, device="cpu")
    else:
        E.TROTE_CICLO_S = valor("--ciclo-trote", 1.0)
        E.APERTURA_DEG, E.COXA_AMP_DEG = valor("--apertura", 0.0), valor("--coxa", 0.0)
        E.PASO_CICLO_S = valor("--ciclo-paso", E.PASO_CICLO_S)
    E.SENSADAS, E.SIN_RESIDUAL = E.SENSADAS_COMPLETO, E.SIN_RESIDUAL_COMPLETO
    E.ALEATORIZAR = False
    actuador = json.loads(a.actuador.read_text())
    dt = cfg.get("dt", 0.03)
    n_ciclos = int(np.ceil(len(filas) * dt / (len(E.generar_marcha(dt)) * dt))) + 2
    env = E.NovaRealEnv(actuador, seed=901, control_dt=dt, episode_cycles=n_ciclos, domain_randomization=False)
    obs, _ = env.reset(seed=901)
    env.model.body_gravcomp[:] = 1.0                 # suspendido, como el robot en la barra
    env.data.qpos[2] += 0.15
    sim_q, sim_fase = [], []
    nominal_len = len(env.nominal)
    for k in range(len(filas)):
        act = np.zeros(12) if modelo is None else modelo.predict(obs, deterministic=True)[0]
        obs, _, term, trunc, info = env.step(act)
        if not info["ramp_active"]:
            i = (env.step_count - env.ramp_steps - 1) % nominal_len
            sim_q.append(np.degrees(env.data.qpos[env.qpos_ids].copy()))
            sim_fase.append(i / nominal_len)
        if term or trunc:
            break
    sim_q, sim_fase = np.array(sim_q), np.array(sim_fase)
    global BINS
    BINS = min(60, nominal_len)          # un intervalo por paso de control como máximo (trote: 33)
    # Robot: ángulo del modelo medido por el sensor de cada articulación (grados, respecto a la referencia).
    ref = cfg["referencias_sensores"]
    R_cal = (json.loads(R.CALIBRACION.read_text()) if a.calibracion_actual
             else cfg.get("calibracion_sensores", json.loads(R.CALIBRACION.read_text())))
    rampa = round(1.0 / dt)
    filas = filas[rampa:]
    fase_r = np.array([float(f["fase"]) for f in filas])
    resultados = {}
    for n in E.JOINTS:
        if "coxa" in n or n not in R_cal or R_cal[n].get("sin_sensor"):
            continue
        vals = []
        for f in filas:
            v = {k: int(f[k]) for k in R.SENSORES if k in f and f[k] not in ("", None)}
            d = R.delta_modelo(n, v, ref, R_cal)
            vals.append(np.nan if d is None else d)           # delta_modelo ya tiene el signo de q del modelo
        x = np.array(vals, float)
        if np.isnan(x).mean() > 0.5:
            continue
        cr = ciclo_medio(fase_r, x)
        cs = ciclo_medio(sim_fase, sim_q[:, E.JOINTS.index(n)])
        if np.isnan(cr).any() or np.isnan(cs).any():
            continue
        cr, cs = cr - cr.mean(), cs - cs.mean()
        mejor = max(range(-BINS // 2, BINS // 2), key=lambda s: np.corrcoef(np.roll(cs, s), cr)[0, 1])
        r = float(np.corrcoef(np.roll(cs, mejor), cr)[0, 1])
        amp = float(np.ptp(cr) / np.ptp(cs)) if np.ptp(cs) > 0 else np.nan
        ciclo_s = nominal_len * dt
        parecido = 100 * max(0.0, r) * (min(amp, 1 / amp) if amp > 0 else 0)
        resultados[n] = dict(r=round(r, 3), amplitud=round(amp, 2), desfase_ms=round(mejor / BINS * ciclo_s * 1000),
                             parecido=round(parecido, 1), robot=cr, sim=np.roll(cs, mejor))
    total = np.mean([v["parecido"] for v in resultados.values()]) if resultados else float("nan")
    print(f"{a.caminata.name}: marcha {E.MARCHA}, política {cfg.get('politica') or 'nominal'}")
    for n, v in resultados.items():
        print(f"  {n:24s} forma r={v['r']:+.2f}  amplitud robot/sim {v['amplitud']:.2f}  desfase {v['desfase_ms']:+d} ms"
              f"  parecido {v['parecido']:.0f} %")
    print(f"PARECIDO DE LA CAMINATA: {total:.0f} %")
    (a.caminata / a.salida).write_text(json.dumps(dict(
        parecido=round(float(total), 1), articulaciones={k: {kk: vv for kk, vv in v.items() if kk not in ("robot", "sim")}
                                                          for k, v in resultados.items()}), indent=2, ensure_ascii=False))
    if a.figura and resultados:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ejes = plt.subplots(2, 4, figsize=(12, 5), sharex=True)
        for eje, (n, v) in zip(ejes.flat, resultados.items()):
            x = np.linspace(0, 1, BINS)
            eje.plot(x, v["sim"], color="#2a78d6", lw=2, label="simulación")
            eje.plot(x, v["robot"], color="#eb6834", lw=2, label="robot")
            eje.set_title(f"{n.replace('_joint', '')}: {v['parecido']:.0f} %", fontsize=9)
        ejes.flat[0].legend(fontsize=8, frameon=False)
        fig.suptitle(f"{a.caminata.name}: parecido {total:.0f} %")
        fig.tight_layout()
        fig.savefig(a.caminata / "comparacion_sim_real.png", dpi=120)


if __name__ == "__main__":
    main()
