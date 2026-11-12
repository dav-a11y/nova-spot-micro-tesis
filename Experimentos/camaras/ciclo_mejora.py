#!/usr/bin/env python3
"""Ciclo de mejora en la plataforma física (21-oct).

Cada vuelta:
1. Prueba en el robot (protocolo_repetibilidad.py, 2 repeticiones, 5 cámaras): base y candidatas
   PPO de gateo y de trote. Análisis de video y colores en segundo plano.
2. Puntuación con los sensores (analizar_repetibilidad.py): media del error de seguimiento de
   fémures y tibias (potenciómetro o, si falta, su encoder de respaldo) y de la desviación de las
   coxas, en grados. Menor es mejor. Gana, por marcha, la condición con menor puntuación.
3. Reentrenamiento: 4 semillas continúan la mejor PPO de cada marcha (+1 M de pasos, actuador real,
   geometría real, postura abierta) y se elige la mejor copia en simulación (seleccionar_copias.py).
4. La ganadora en el robot y la nueva copia son las candidatas de la vuelta siguiente.
Registro en ciclo_mejora.log y estado en ciclo_mejora.json; commit local al final de cada vuelta.

Uso: python3 ciclo_mejora.py [--vueltas 3]
"""
import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENT = AQUI.parent / "entrenamiento_real_20261016"
RAIZ = AQUI.parent.parent
PY = RAIZ / ".venv-mujoco/bin/python"
LOG = AQUI / "ciclo_mejora.log"
ESTADO = AQUI / "ciclo_mejora.json"
MARCHAS = {
    "gateo": dict(extra="--apertura 8",
                  entrenar="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 10 --w-suavidad 0.3"),
    "trote": dict(extra="--apertura 5",
                  entrenar="--marcha trote --ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 "
                           "--w-avance 20 --w-suavidad 0.2"),
}
COMUN = ("--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador {actuador} "
         "--dt 0.03 --w-actitud 30 --w-lateral 20 --w-giro 10 --w-giro-ciclo 5 --w-coxas 1.0")
SEMILLAS = [401, 409, 419, 421]


def log(texto):
    linea = f"{time.strftime('%H:%M')} {texto}"
    print(linea, flush=True)
    with LOG.open("a") as f:
        f.write(linea + "\n")


def puntuar(sesion):
    """{condición: puntuación} = media de 'media_grados' de todas sus articulaciones."""
    subprocess.run([sys.executable, "-I", str(AQUI / "analizar_repetibilidad.py"), "--sesion", sesion],
                   capture_output=True, cwd=AQUI)
    p = AQUI / f"repetibilidad_{sesion}.csv"
    acum = {}
    for f in csv.DictReader(p.open()):
        acum.setdefault(f["condicion"], []).append(float(f["media_grados"]))
    return {c: sum(v) / len(v) for c, v in acum.items()}


def actualizar_modelo(sesion, vuelta):
    """21-oct: el robot enseña a la simulación. Mide retardo, holgura y residuo de cada articulación en
    las caminatas de la vuelta y genera actuadores_ciclo<N>.json para entrenar la siguiente."""
    caminatas = sorted(str(d) for d in (AQUI / "grabaciones").glob(f"rep_{sesion}_*") if "fallo" not in d.name)
    r = subprocess.run([str(PY), "-I", "actualizar_modelo_real.py", "--nombre", f"ciclo{vuelta}", *caminatas],
                       capture_output=True, text=True, cwd=ENT)
    for l in r.stdout.splitlines():
        if l.startswith("modelo") or l.startswith("brecha"):
            log(l)
    f = ENT / f"actuadores_ciclo{vuelta}.json"
    return f.name if f.exists() else "actuadores_reales_v5.json"


def entrenar(marcha, desde, vuelta, actuador):
    salida = f"ppo_ciclo{vuelta}_{marcha}"
    procs = []
    for s in SEMILLAS:
        cmd = (f"{PY} -I entrenar_ppo_real.py {COMUN.format(actuador=actuador)} {MARCHAS[marcha]['entrenar']} --timesteps 1000000 "
               f"--seed {s} --continuar {desde} --output {salida}")
        procs.append(subprocess.Popen(["nice", "-n", "5", "taskset", "-c", "2-11", "bash", "-c", cmd + f" > log_{salida}_{s}.txt 2>&1"],
                                      cwd=ENT, env={**__import__('os').environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}))
    return salida, procs


def elegir(marcha, carpeta):
    r = subprocess.run([str(PY), "-I", "seleccionar_copias.py", "--marcha", marcha, "--carpeta", carpeta,
                        "--procesos", "8", "--semillas", "2"], capture_output=True, text=True, cwd=ENT,
                       env={**__import__('os').environ, "OMP_NUM_THREADS": "1"})
    (ENT / f"seleccion_{carpeta}.txt").write_text(r.stdout + r.stderr)
    for l in r.stdout.splitlines():
        if l.startswith("Elegida:"):
            return str(Path(l.split(":", 1)[1].strip()).relative_to(ENT))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vueltas", type=int, default=3)
    a = ap.parse_args()
    estado = json.loads(ESTADO.read_text()) if ESTADO.exists() else {}
    cand = estado.get("candidatas", {
        "gateo": ["ppo_v10_robot/ppo_v14_gateo_semilla_43_1700k"],
        "trote": ["ppo_v10_robot/ppo_v15_trote_semilla_307_100k", "ppo_v10_robot/ppo_v15_trote_semilla_211_3000k"]})
    inicio = estado.get("vuelta", 0) + 1
    for vuelta in range(inicio, inicio + a.vueltas):
        sesion = f"ciclo{vuelta}"
        log(f"== vuelta {vuelta}: candidatas {cand}")
        conds = []
        for marcha, info in MARCHAS.items():
            conds += ["--condicion", f"{marcha}_base:{marcha}::{info['extra']}"]
            for i, c in enumerate(cand[marcha]):
                conds += ["--condicion", f"{marcha}_ppo{i + 1}:{marcha}:{c}/policy.zip"]
        r = subprocess.run([sys.executable, "protocolo_repetibilidad.py", "--sesion", sesion, "--repeticiones", "2",
                            "--duracion-s", "180", "--pausa-s", "120", *conds],
                           cwd=AQUI, stdout=open(AQUI / f"protocolo_{sesion}.log", "a"), stderr=subprocess.STDOUT)
        log(f"protocolo terminado (código {r.returncode})")
        if r.returncode != 0:
            log("el protocolo se detuvo (sensores o servos): el ciclo se para para revisar el robot")
            break
        punt = puntuar(sesion)
        log("puntuación en el robot (° medios, menor = mejor): " +
            ", ".join(f"{c} {v:.2f}" for c, v in sorted(punt.items())))
        actuador = actualizar_modelo(sesion, vuelta)
        log(f"entrenamiento con el modelo del actuador medido en el robot: {actuador}")
        ganadoras, procs = {}, []
        for marcha in MARCHAS:
            ppos = {c: v for c, v in punt.items() if c.startswith(f"{marcha}_ppo")}
            if not ppos:
                continue
            mejor = min(ppos, key=ppos.get)
            ganadoras[marcha] = cand[marcha][int(mejor.split("ppo")[1]) - 1]
            base = punt.get(f"{marcha}_base")
            log(f"{marcha}: mejor PPO en el robot {ganadoras[marcha]} ({ppos[mejor]:.2f}°; base {base:.2f}°)")
            salida, p = entrenar(marcha, f"{ganadoras[marcha]}/policy.zip", vuelta, actuador)
            procs.append((marcha, salida, p))
        for marcha, salida, p in procs:
            for x in p:
                x.wait()
        nuevas = {}
        for marcha, salida, _ in procs:
            nuevas[marcha] = elegir(marcha, salida)
            log(f"{marcha}: nueva copia elegida en simulación {nuevas[marcha]}")
        cand = {m: [ganadoras[m]] + ([nuevas[m]] if nuevas.get(m) and nuevas[m] != ganadoras[m] else [])
                for m in ganadoras}
        ESTADO.write_text(json.dumps(dict(vuelta=vuelta, candidatas=cand, puntuacion=punt), indent=2))
        subprocess.run(["git", "add", "-A", "Experimentos/camaras/ciclo_mejora.json",
                        f"Experimentos/camaras/repetibilidad_{sesion}.csv"], cwd=RAIZ)
        subprocess.run(["git", "commit", "-q", "-m", f"Ciclo de mejora en el robot: vuelta {vuelta}\n\n"
                        "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=RAIZ)
    log("FIN del ciclo")


if __name__ == "__main__":
    main()
