#!/usr/bin/env python3
"""Mueve cada pata por separado para identificarla en las cámaras (21-oct).

Postura base (con calibracion_postura.json y la apertura indicada); cada fémur oscila
±8° (0,5 Hz, 2 ciclos = 4 s) mientras las demás patas quedan quietas, en el orden
1, 2, 3, 4, dos vueltas. Escribe un registro con el mismo formato que el ejecutor
(t, paso, fase, orden_0…11) para que grabar_caminata.py y analizar_colores_patas.py
lo usen igual que una caminata; «fase» indica la pata que se mueve (1-4, 0 = quietas).

Uso (normalmente desde grabar_caminata.py --ejecutor):
  identificar_patas_robot.py --salida caminata.csv [--apertura 8]
"""
import argparse
import csv
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
import ejecutar_politica_robot as R  # noqa: E402

AMP, FREC, CICLOS, VUELTAS = 8.0, 0.5, 2, 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--apertura", type=float, default=0.0)
    a, _ = ap.parse_known_args()
    E.APERTURA_DEG = a.apertura
    stand = np.tile(E.STAND, 4).astype(float)
    for pata, b in E.LEG_JOINT_BASE.items():
        stand[b + 1] = E.STAND[1] - E.apertura(pata)
    base = R.a_grados_servo(stand)
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
    while True:
        l = lec.linea(timeout=8.0)
        if l is None:
            sys.exit("El Uno no respondió STREAM_LISTO")
        if l.startswith("STREAM_LISTO"):
            break
    f = a.salida.open("w", newline=""); w = csv.writer(f)
    w.writerow(["t", "paso", "fase", *[f"orden_{i}" for i in range(12)]])
    t0 = time.time(); a.salida.with_suffix(".inicio.txt").write_text(f"{t0:.6f}\n")
    k = 0

    def enviar(g, fase):
        nonlocal k
        os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode()); lec.linea(timeout=0.3)
        w.writerow([round(time.time() - t0, 3), k, fase, *g]); k += 1
        time.sleep(0.03)

    try:
        actual = list(R.BASE)
        while actual != base:                                   # llegada suave a la postura base
            actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, base)]
            enviar(actual, 0)
        for _ in range(60):
            enviar(base, 0)
        for _ in range(VUELTAS):
            for pata in (1, 2, 3, 4):
                i = 3 + pata; ti = time.time()
                while time.time() - ti < CICLOS / FREC:
                    d = AMP * np.sin(2 * np.pi * FREC * (time.time() - ti))
                    g = list(base); g[i] = int(round(base[i] + R.SIGNO_FEMUR[pata] * d))
                    enviar(g, pata)
                for _ in range(30):
                    enviar(base, 0)
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd); f.close()
        print(f"Registro: {a.salida} | pasos: {k} | duración: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
