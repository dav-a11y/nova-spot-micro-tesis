#!/usr/bin/env python3
"""Mantiene el robot en la postura base (modo @) con la corrección de calibracion_postura.json.

Relee el archivo cada segundo: al cambiar la corrección de un fémur, el robot se mueve
suavemente (1° por paso) a la nueva postura. Sirve para ajustar a ojo, comparando con la
simulación, que las patas de cada lado queden como en el modelo. Ctrl+C o --duracion-s
para terminar (deja las coxas sostenidas y apaga el resto, como el ejecutor).

Uso: python3 postura_calibracion.py [--duracion-s 900] [--apertura 8]
"""
import argparse
import json
import os
import sys
import termios
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
import ejecutar_politica_robot as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracion-s", type=float, default=900)
    ap.add_argument("--apertura", type=float, default=0.0, help="apertura de la marcha que se mostrará (°)")
    a = ap.parse_args()
    fd = R.abrir("/dev/ttyACM0")
    lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
    while True:
        l = lec.linea(timeout=8.0)
        if l is None:
            sys.exit("El Uno no respondió STREAM_LISTO")
        if l.startswith("STREAM_LISTO"):
            break
    stand = np.tile(E.STAND, 4).astype(float)
    E.APERTURA_DEG = a.apertura
    for pata, b in E.LEG_JOINT_BASE.items():
        stand[b + 1] = E.STAND[1] - E.apertura(pata)
    actual = list(R.BASE)
    ultimo_cal, t0 = None, time.time()
    try:
        while time.time() - t0 < a.duracion_s:
            cal = json.loads((HERE / "calibracion_postura.json").read_text()).get("femur_offset_deg", {})
            if cal != ultimo_cal:
                R.CAL_POSTURA.clear(); R.CAL_POSTURA.update(cal)
                print(time.strftime("%H:%M:%S"), "corrección fémures (°, + adelante):", cal,
                      "-> servos", R.a_grados_servo(stand)[4:8], flush=True)
                ultimo_cal = cal
            objetivo = R.a_grados_servo(stand)
            actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, objetivo)]
            os.write(fd, ("S," + ",".join(map(str, actual)) + "\n").encode())
            lec.linea(timeout=0.3)
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd)
        print("fin: coxas sostenidas, resto apagado")


if __name__ == "__main__":
    main()
