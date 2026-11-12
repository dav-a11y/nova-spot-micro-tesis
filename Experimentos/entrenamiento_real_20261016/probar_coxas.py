#!/usr/bin/env python3
"""Comprueba el sentido de cada coxa (27-oct): con el modo `+` del firmware (coxas con órdenes), gira cada
coxa +8° de servo sobre su base, la mantiene 2 s y la devuelve; coxas 1, 2, 3, 4.

En la cámara de abajo (PC con Windows) o la de frente se ve si la pata se abre hacia afuera o se cierra
hacia el cuerpo: con eso se fija SIGNO_COXA en ejecutar_politica_robot.py. Escribe t, coxa (0 = reposo) y
orden_0…11 para grabar_caminata.py --ejecutor.
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
import ejecutar_politica_robot as R  # noqa: E402

GIRO_DEG = 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, required=True)
    a, _ = ap.parse_known_args()
    base = list(R.BASE)
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"+")
    while not (lec.linea(timeout=8.0) or "").startswith("STREAM_LISTO"):
        pass
    f = a.salida.open("w", newline=""); w = csv.writer(f)
    w.writerow(["t", "paso", "fase", *[f"orden_{i}" for i in range(12)]])
    t0 = time.time(); a.salida.with_suffix(".inicio.txt").write_text(f"{t0:.6f}\n")
    k = 0

    def enviar(g, coxa, n):
        nonlocal k
        for _ in range(n):
            os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode()); lec.linea(timeout=0.3)
            w.writerow([round(time.time() - t0, 3), k, coxa, *g]); k += 1
            time.sleep(0.03)

    try:
        enviar(base, 0, 50)
        for pata in (1, 2, 3, 4):
            i = pata - 1
            g = list(base)
            g[i] = int(np.clip(base[i] + GIRO_DEG, R.TOPE_MIN[i], R.TOPE_MAX[i]))
            print(f"coxa {pata}: base {base[i]} -> {g[i]}", flush=True)
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
