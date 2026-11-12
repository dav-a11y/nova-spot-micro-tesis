#!/usr/bin/env python3
"""Evaluación cruzada en el mismo robot simulado (actuador v5, tibia 1 con PWM):
caminata base, PPO v4 semilla 37 (observa F2, F4, T2) y PPO v6 (observa los 8
fémures y tibias). Semillas de evaluación nuevas (901–910), distintas de las de
desarrollo. Escribe evaluacion_<marcha>_v6.csv y muestra medias por política.
Con --marcha paso compara la base del paso con las PPO de ppo_v6_paso.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402

SEMILLAS = list(range(901, 911))
TIBIA1_ACTIVA = {j for j in E.JOINTS if "coxa" in j}


def episodio(env, modelo, semilla):
    obs, _ = env.reset(seed=semilla)
    x0 = y0 = None; inc = []
    while True:
        act = np.zeros(12) if modelo is None else modelo.predict(obs, deterministic=True)[0]
        obs, r, term, trunc, info = env.step(act)
        if x0 is None and not info["ramp_active"]:
            x0, y0 = info["x"], info["y"]
        if not info["ramp_active"]:
            inc.append((info["roll"], info["pitch"]))
        if term or trunc:
            break
    inc = np.degrees(np.array(inc))
    return dict(avance_m=info["x"] - x0, deriva_m=abs(info["y"] - y0),
                roll_rms_deg=float(np.sqrt(np.mean(inc[:, 0] ** 2))),
                pitch_rms_deg=float(np.sqrt(np.mean(inc[:, 1] ** 2))),
                inclinacion_max_deg=float(np.abs(inc).max()), caida=bool(term))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcha", choices=("gateo", "paso"), default="gateo")
    ap.add_argument("--carpeta", type=Path, help="carpeta de políticas (por defecto ppo_v6 o ppo_v6_paso)")
    ap.add_argument("--ciclos", type=int, default=6, help="ciclos por episodio (60 ≈ 3 min)")
    ap.add_argument("--semillas", type=int, default=10)
    args = ap.parse_args()
    marcha = args.marcha
    SEMILLAS[:] = SEMILLAS[:args.semillas]
    E.MARCHA, E.PASO_CICLO_S = marcha, 2.0
    actuador = json.loads((HERE / "actuadores_reales_v5.json").read_text())
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = 15.0, 10.0, 0.5
    E.NovaRealEnv.pesos = dict(avance=10.0, actitud=30.0, lateral=20.0, giro=10.0)
    carpeta = args.carpeta or HERE / ("ppo_v6" if marcha == "gateo" else "ppo_v6_paso")
    politicas = [("base", None, E.SENSADAS_COMPLETO, TIBIA1_ACTIVA)]
    if marcha == "gateo":
        politicas += [("ppo_v4_s37", HERE / "ppo_v4/semilla_37/policy.zip", E.SENSADAS,
                  {j for j in E.JOINTS if "coxa" in j} | {"front_right_tibia_joint"})]
    politicas += [(f"{carpeta.name}_s{p.parent.name.split('_')[1]}", p, E.SENSADAS_COMPLETO, TIBIA1_ACTIVA)
                  for p in sorted(carpeta.glob("semilla_*/policy.zip"))]
    filas = []
    for nombre, ruta, sensadas, sin_residual in politicas:
        E.SENSADAS = sensadas
        # La tibia 1 del robot simulado siempre tiene PWM; v4 simplemente no la corrige.
        E.SIN_RESIDUAL = sin_residual - {"front_right_tibia_joint"}
        modelo = PPO.load(ruta, device="cpu") if ruta else None
        for s in SEMILLAS:
            env = E.NovaRealEnv(actuador, seed=s, control_dt=0.03, episode_cycles=args.ciclos)
            if "front_right_tibia_joint" in sin_residual:
                env.mascara[E.JOINTS.index("front_right_tibia_joint")] = 0.0
            filas.append(dict(politica=nombre, semilla=s, **episodio(env, modelo, s)))
    with (HERE / f"evaluacion_{marcha}_{carpeta.name}_{args.ciclos}ciclos.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    claves = ("avance_m", "deriva_m", "roll_rms_deg", "pitch_rms_deg", "inclinacion_max_deg")
    print(f"{'política':22s} " + " ".join(f"{k:>18s}" for k in claves) + "  caídas")
    for nombre, *_ in politicas:
        sub = [f for f in filas if f["politica"] == nombre]
        print(f"{nombre:22s} " + " ".join(f"{np.mean([f[k] for f in sub]):8.3f} ±{np.std([f[k] for f in sub]):7.3f}"
                                          for k in claves) + f"  {sum(f['caida'] for f in sub)}")


if __name__ == "__main__":
    main()
