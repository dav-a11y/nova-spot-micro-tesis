#!/usr/bin/env python3
"""Visor de MuJoCo que configura la marcha con la metadata de la política, igual que
evaluar_viabilidad.py. ver_marcha_sim.py usa valores fijos, así que, por ejemplo, la carrera
se ve igual que el trote y el galope sale con otros ángulos.

Uso: ver_marcha_con_metadata.py --marcha galope [--segundos 30] [--nominal] [--suspendido]
     ver_marcha_con_metadata.py --politica ppo_v10_robot/<copia>/policy.zip
  --marcha: toma la copia para el robot de esa marcha (lista COPIAS_ROBOT).
  --nominal: solo la marcha base, sin la corrección PPO.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
from evaluar_viabilidad import marcha_de  # noqa: E402

# Copias para el robot según CONTINUIDAD.md (27-28 oct 2026).
COPIAS_ROBOT = {
    "paso": "ppo_v10_robot/ppo_v24_paso_semilla_4109_200k/policy.zip",
    "gateo": "ppo_v10_robot/ppo_v27_gateo_semilla_7013_4100k/policy.zip",
    "trote": "ppo_v10_robot/ppo_v24_trote_semilla_4209_200k/policy.zip",
    "carrera": "ppo_v10_robot/ppo_v24_carrera_semilla_4309_200k/policy.zip",
    "galope": "ppo_v10_robot/ppo_v28_galope_semilla_8417_175k/policy.zip",
}


def configurar(m):
    """Los mismos ajustes que evaluar_viabilidad.episodio(), sin aleatorización."""
    E.MARCHA = m["tipo"]
    E.PASO_CICLO_S, E.TROTE_CICLO_S = m.get("ciclo_paso_s", 2.0), m.get("ciclo_trote_s", 1.0)
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = m["femur_deg"], m["tibia_deg"], m.get("fase_s", 0.5)
    E.APERTURA_DEG, E.COXA_AMP_DEG = m.get("apertura_deg", 0.0), m.get("coxa_deg", 0.0)
    E.NovaRealEnv.pesos = dict(avance=10.0, actitud=30.0, lateral=20.0, giro=10.0)
    E.SENSADAS, E.SIN_RESIDUAL = E.SENSADAS_COMPLETO, E.SIN_RESIDUAL_COMPLETO
    E.ALEATORIZAR = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcha", choices=tuple(COPIAS_ROBOT))
    ap.add_argument("--politica", type=Path)
    ap.add_argument("--nominal", action="store_true")
    ap.add_argument("--suspendido", action="store_true")
    ap.add_argument("--segundos", type=float, help="cierra la ventana después de este tiempo")
    a = ap.parse_args()
    if not (a.marcha or a.politica):
        ap.error("indica --marcha o --politica")

    ruta = a.politica or HERE / COPIAS_ROBOT[a.marcha]
    m = marcha_de(ruta)
    configurar(m)
    modelo = None
    if not a.nominal:
        from stable_baselines3 import PPO
        modelo = PPO.load(ruta, device="cpu")

    ajustes = (f"fémur {m['femur_deg']}°, tibia {m['tibia_deg']}°, coxa {m.get('coxa_deg', 0.0)}°, "
               f"ciclo {m.get('ciclo_paso_s') if m['tipo'] == 'paso' else m.get('ciclo_trote_s')} s")
    titulo = f"{m['tipo'].upper()} {'(marcha base, sin PPO)' if a.nominal else '(con PPO)'}"
    print(titulo, "|", Path(ruta).parent.name, "|", ajustes, flush=True)

    actuador = json.loads((HERE / "actuadores_ciclo2.json").read_text())
    env = E.NovaRealEnv(actuador, seed=901, control_dt=0.03, episode_cycles=1000)
    obs, _ = env.reset(seed=901)
    if a.suspendido:
        env.model.body_gravcomp[:] = 1.0
        env.data.qpos[2] += 0.15

    fin = time.time() + a.segundos if a.segundos else None
    with mujoco.viewer.launch_passive(env.model, env.data) as visor:
        visor.cam.distance, visor.cam.elevation, visor.cam.azimuth = 0.9, -15, 90
        visor.set_texts((None, None, titulo, ajustes))
        while visor.is_running() and (fin is None or time.time() < fin):
            t0 = time.time()
            act = np.zeros(12) if modelo is None else modelo.predict(obs, deterministic=True)[0]
            obs, _, term, trunc, _ = env.step(act)
            visor.cam.lookat[:] = env.data.xpos[env.base_body]
            visor.sync()
            if term or trunc:
                obs, _ = env.reset(seed=901)
            espera = env.control_dt - (time.time() - t0)
            if espera > 0:
                time.sleep(espera)
        visor.close()
        # Esperar a que el hilo del visor cierre la ventana: si Python termina antes,
        # glfw.terminate() choca con ese hilo y el proceso cae con "Segmentation fault".
        limite = time.time() + 5.0
        while visor.is_running() and time.time() < limite:
            time.sleep(0.05)
    time.sleep(0.5)


if __name__ == "__main__":
    main()
