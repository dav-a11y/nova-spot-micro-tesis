#!/usr/bin/env python3
"""Comprueba el sentido de cada tibia (27-oct): con la postura base, ordena a cada tibia «levantar» 15°
(con SIGNO_TIBIA y la calibración actuales), la mantiene 2 s y la devuelve; tibias 1, 2, 3, 4.

Si en las cámaras el pie sube y se acerca al cuerpo, el signo está bien; si baja o se estira, está
invertido. Escribe t, tibia (0 = reposo) y orden_0…11 para grabar_caminata.py --ejecutor.
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

LEVANTAR_DEG = 15.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, required=True)
    a, _ = ap.parse_known_args()
    E.APERTURA_DEG = 8.0
    stand = np.tile(E.STAND, 4).astype(float)
    for pata, b in E.LEG_JOINT_BASE.items():
        stand[b + 1] = E.STAND[1] - E.apertura(pata)
    base = R.a_grados_servo(stand)
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
    while not (lec.linea(timeout=8.0) or "").startswith("STREAM_LISTO"):
        pass
    f = a.salida.open("w", newline=""); w = csv.writer(f)
    w.writerow(["t", "paso", "fase", *[f"orden_{i}" for i in range(12)]])
    t0 = time.time(); a.salida.with_suffix(".inicio.txt").write_text(f"{t0:.6f}\n")
    k = 0

    def enviar(g, tibia, n):
        nonlocal k
        for _ in range(n):
            os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode()); lec.linea(timeout=0.3)
            w.writerow([round(time.time() - t0, 3), k, tibia, *g]); k += 1
            time.sleep(0.03)

    try:
        actual = list(R.BASE)
        while actual != base:
            actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, base)]
            enviar(actual, 0, 1)
        enviar(base, 0, 40)
        for pata in (1, 2, 3, 4):
            q = stand.copy()
            q[E.LEG_JOINT_BASE[{1: "FR", 2: "FL", 3: "RR", 4: "RL"}[pata]] + 2] -= np.deg2rad(LEVANTAR_DEG)
            g = R.a_grados_servo(q)
            print(f"tibia {pata}: base {base[7 + pata]} -> levantar {g[7 + pata]}", flush=True)
            actual = list(base)
            while actual != g:
                actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, g)]
                enviar(actual, pata, 1)
            enviar(g, pata, 60)
            while actual != base:
                actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, base)]
                enviar(actual, 0, 1)
            enviar(base, 0, 30)
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd); f.close()


if __name__ == "__main__":
    main()
