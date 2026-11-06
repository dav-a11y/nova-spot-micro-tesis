#!/usr/bin/env python3
"""Ver en MuJoCo cómo mueve el robot una política PPO (5-nov-2026).

Reproduce en la simulación la marcha nominal + la corrección de la política, con la misma marcha, los mismos pesos
y el mismo modelo de servos con que se entrenó (todo sale de metadata.json, junto a policy.zip). Sin aleatorización.

Dos situaciones:
  --suspendido  el robot colgado, como en la barra del laboratorio (gravedad compensada, sin tocar el suelo);
  (por defecto) el robot apoyado en el piso, caminando.
Dos salidas:
  --video x.mp4 guarda un video (necesita ffmpeg);
  (por defecto) abre una ventana con la simulación en vivo (ffplay);
  --visor       el visor interactivo de MuJoCo (cámara con el ratón), si el controlador gráfico lo permite.

Ejemplos (desde esta carpeta, con el entorno de politicas_elegidas_20261105/requirements.txt):
  python ver_politica_mujoco.py ppo_v10_robot/ppo_v32_trote_semilla_9209_650k
  python ver_politica_mujoco.py ppo_v10_robot/ppo_v27_gateo_semilla_7013_4100k --video gateo_piso.mp4 --segundos 20
  python ver_politica_mujoco.py ppo_v10_robot/ppo_v32_galope_semilla_9407_475k --suspendido --video galope_colgado.mp4
  python ver_politica_mujoco.py ppo_v10_robot/ppo_v24_paso_semilla_4109_200k --nominal      (solo la marcha base)
Sin pantalla (servidor): MUJOCO_GL=egl o MUJOCO_GL=osmesa, solo con --video.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def preparar(carpeta, suspendido, segundos):
    import entrenar_ppo_real as E
    md = json.loads((carpeta / "metadata.json").read_text())
    m = md["marcha"]
    E.MARCHA = m["tipo"]
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = m["femur_deg"], m["tibia_deg"], m.get("fase_s", 0.5)
    E.PASO_CICLO_S, E.TROTE_CICLO_S = m.get("ciclo_paso_s", 2.0), m.get("ciclo_trote_s", 1.0)
    E.APERTURA_DEG, E.COXA_AMP_DEG = m.get("apertura_deg", 0.0), m.get("coxa_deg", 0.0)
    E.SENSADAS, E.SIN_RESIDUAL = E.SENSADAS_COMPLETO, E.SIN_RESIDUAL_COMPLETO
    E.ALEATORIZAR = False
    E.NovaRealEnv.pesos = md.get("pesos", {})
    dt = md.get("control_dt", 0.03)
    ciclo = len(E.generar_marcha(dt)) * dt
    env = E.NovaRealEnv(md["actuador"], seed=901, control_dt=dt, episode_cycles=int(np.ceil(segundos / ciclo)) + 1,
                        domain_randomization=False)
    obs, _ = env.reset(seed=901)
    if suspendido:
        env.model.body_gravcomp[:] = 1.0          # colgado de la barra: las patas no cargan peso
        env.data.qpos[2] += 0.15
    return env, obs, md, dt


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("politica", type=Path, help="carpeta con policy.zip y metadata.json (o el propio policy.zip)")
    ap.add_argument("--suspendido", action="store_true", help="robot colgado, como en la barra")
    ap.add_argument("--nominal", action="store_true", help="sin la política: solo la marcha base")
    ap.add_argument("--video", type=Path, help="guardar en este .mp4 en vez de abrir la ventana")
    ap.add_argument("--visor", action="store_true", help="usar el visor interactivo de MuJoCo (si funciona en ese PC)")
    ap.add_argument("--segundos", type=float, default=20.0)
    ap.add_argument("--ancho", type=int, default=1280)
    ap.add_argument("--alto", type=int, default=720)
    a = ap.parse_args()
    carpeta = a.politica.parent if a.politica.suffix == ".zip" else a.politica
    env, obs, md, dt = preparar(carpeta, a.suspendido, a.segundos)
    import mujoco
    modelo = None
    if not a.nominal:
        from stable_baselines3 import PPO
        modelo = PPO.load(carpeta / "policy.zip", device="cpu")
    pasos = int(a.segundos / dt)
    titulo = (f"{md['marcha']['tipo']} · {carpeta.name} · "
              f"{'colgado' if a.suspendido else 'en el piso'}{' · solo marcha base' if a.nominal else ''}")
    base = mujoco.mj_name2id(env.model, mujoco.mjtObj.mjOBJ_BODY, "base_link")
    x0 = float(env.data.xpos[base][0])

    def paso():
        nonlocal obs
        act = np.zeros(12) if modelo is None else modelo.predict(obs, deterministic=True)[0]
        obs, _, term, trunc, _ = env.step(act)
        return term or trunc

    # 5-nov: la imagen se dibuja fuera de pantalla y se manda a ffmpeg (video) o a ffplay (ventana en vivo). La ventana
    # interactiva de MuJoCo (mujoco.viewer) se colgaba con algunos controladores gráficos; esta vía funciona en cualquier PC
    # con ffmpeg. Con --visor se usa igualmente el visor de MuJoCo (permite girar la cámara con el ratón).
    if a.visor:
        import mujoco.viewer
        with mujoco.viewer.launch_passive(env.model, env.data) as v:
            v.cam.distance, v.cam.azimuth, v.cam.elevation = 0.9, 135.0, -18.0
            for _ in range(pasos):
                t = time.time()
                fin = paso()
                v.cam.lookat[:] = env.data.xpos[base]
                v.sync()
                if fin or not v.is_running():
                    break
                time.sleep(max(0.0, dt - (time.time() - t)))
    else:
        env.model.vis.global_.offwidth = max(env.model.vis.global_.offwidth, a.ancho)
        env.model.vis.global_.offheight = max(env.model.vis.global_.offheight, a.alto)
        r = mujoco.Renderer(env.model, a.alto, a.ancho)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 0.9, 135.0, -18.0
        rotulo = ("drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                  f"text='{titulo.replace(':', ' ')}':x=(w-tw)/2:y=14:fontsize=24:fontcolor=white")
        entrada = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{a.ancho}x{a.alto}", "-r", f"{1 / dt:.4f}", "-i", "-"]
        if a.video:
            cmd = ["ffmpeg", "-y", "-loglevel", "error", *entrada, "-vf", f"pad=iw:ih+50:0:50:black,{rotulo}",
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-movflags", "+faststart", str(a.video)]
        else:
            cmd = ["ffplay", "-loglevel", "error", "-window_title", titulo, "-f", "rawvideo", "-pixel_format", "rgb24",
                   "-video_size", f"{a.ancho}x{a.alto}", "-framerate", f"{1 / dt:.4f}", "-i", "-"]
        import os
        entorno = dict(os.environ)
        entorno.pop("SDL_AUDIODRIVER", None)     # pygame (vía gymnasium) lo pone en «dsp» y ffplay no arranca
        entorno["SDL_AUDIODRIVER"] = "dummy"
        sal = subprocess.Popen(cmd, stdin=subprocess.PIPE, env=entorno)
        for _ in range(pasos):
            t = time.time()
            fin = paso()
            cam.lookat[:] = env.data.xpos[base]
            r.update_scene(env.data, camera=cam)
            try:
                sal.stdin.write(r.render().tobytes())
            except BrokenPipeError:              # se cerró la ventana
                break
            if not a.video:
                time.sleep(max(0.0, dt - (time.time() - t)))
            if fin:
                break
        try:
            sal.stdin.close()
        except BrokenPipeError:
            pass
        sal.wait()
        if a.video:
            print(f"{a.video}: {titulo}")
    if not a.suspendido:
        print(f"avance en el piso: {float(env.data.xpos[base][0]) - x0:+.2f} m en {a.segundos:.0f} s")


if __name__ == "__main__":
    main()
