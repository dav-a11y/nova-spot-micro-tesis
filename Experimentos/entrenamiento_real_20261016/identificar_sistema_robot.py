#!/usr/bin/env python3
"""Identificación articulación por articulación del robot real (modo `@`).

Para cada articulación con sensor aplica, con las demás quietas en su base:
escalones de ±1°, ±2°, ±6° y ±12°, y senoides de 8° a 0,5, 1 y 2 Hz.
Registra los 8 canales que devuelve el Uno (C5, C6, C9, C1, C3, C2, C10, C11).
Los límites del firmware siguen activos (fémur ±20°, tibia ±18°, 3°/paso).
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ejecutar_politica_robot import BASE, Lector, abrir

HERE = Path(__file__).resolve().parent
CANALES = ["C5", "C6", "C9", "C1", "C3", "C2", "C10", "C11"]
ARTICULACIONES = {  # nombre: (índice del firmware, canal propio)
    "femur2": (5, "C5"), "femur4": (7, "C6"), "tibia2": (9, "C9"),
    "tibia3": (10, "C11"), "tibia4": (11, "C10"),
}


def secuencia(dt):
    """Lista de (desplazamiento en grados, etiqueta) por paso de control."""
    pasos = []
    def mantener(v, seg, etq):
        pasos.extend([(v, etq)] * round(seg / dt))
    mantener(0, 1.0, "reposo")
    for a in (1, 2, 6, 12):
        for s in (1, -1):
            mantener(s * a, 1.5 if a >= 6 else 1.0, f"escalon_{s*a:+d}")
            mantener(0, 1.0, "retorno")
    for f, seg in ((0.5, 4.0), (1.0, 3.0), (2.0, 2.0)):
        n = round(seg / dt)
        pasos.extend([(8 * math.sin(2 * math.pi * f * k * dt), f"seno_{f}Hz") for k in range(n)])
        mantener(0, 1.0, "retorno")
    return pasos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--puerto", default="/dev/ttyACM0")
    p.add_argument("--dt", type=float, default=0.03)
    p.add_argument("--articulaciones", nargs="+", default=list(ARTICULACIONES))
    a = p.parse_args()
    salida = HERE / "identificacion_robot"
    salida.mkdir(exist_ok=True)
    fd = abrir(a.puerto)
    lec = Lector(fd)
    time.sleep(2.0)
    os.read(fd, 4096)
    os.write(fd, b"@")
    while (l := lec.linea(timeout=8.0)) is not None and not l.startswith("STREAM_LISTO"):
        pass
    if l is None:
        raise SystemExit("El Uno no respondió STREAM_LISTO")
    seq = secuencia(a.dt)
    try:
        for nombre in a.articulaciones:
            idx, _ = ARTICULACIONES[nombre]
            ruta = salida / f"{nombre}_{time.strftime('%H%M%S')}.csv"
            with ruta.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["t", "etiqueta", "orden", *CANALES])
                t0 = time.time()
                for k, (d, etq) in enumerate(seq):
                    grados = list(BASE)
                    grados[idx] = round(BASE[idx] + d)
                    os.write(fd, ("S," + ",".join(map(str, grados)) + "\n").encode())
                    resp = lec.linea(timeout=0.3)
                    if not resp or not resp.startswith("R,"):
                        raise SystemExit(f"Respuesta perdida en {nombre}, paso {k}: {resp}")
                    v = resp.split(",")[2:10]
                    w.writerow([round(time.time() - t0, 3), etq, grados[idx], *v])
                    espera = t0 + (k + 1) * a.dt - time.time()
                    if espera > 0:
                        time.sleep(espera)
            print(f"{nombre}: {len(seq)} pasos -> {ruta.name}", flush=True)
    finally:
        os.write(fd, b"X\n")
        time.sleep(0.2)
        os.close(fd)


if __name__ == "__main__":
    main()
