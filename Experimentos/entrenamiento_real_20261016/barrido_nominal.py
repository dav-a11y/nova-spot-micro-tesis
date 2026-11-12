#!/usr/bin/env python3
"""Barrido de la marcha nominal (sin PPO) con aleatorización (28-oct): avance, caídas e inclinación
para varias amplitudes de fémur/tibia. Sirve para elegir una marcha base que no se caiga antes de entrenar.
Uso: barrido_nominal.py --tipo galope --femur 10,13,16 --tibia 6,8,10,14 [--coxa 8] [--apertura 5] [--ciclo 0.8]"""
import argparse
import itertools
from multiprocessing import Pool

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import evaluar_viabilidad as V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", required=True)
    ap.add_argument("--femur", default="16")
    ap.add_argument("--tibia", default="14")
    ap.add_argument("--coxa", type=float, default=0.0)
    ap.add_argument("--apertura", type=float, default=5.0)
    ap.add_argument("--ciclo", type=float, default=0.8)
    ap.add_argument("--episodios", type=int, default=10)
    ap.add_argument("--procesos", type=int, default=10)
    a = ap.parse_args()
    combos = list(itertools.product([float(x) for x in a.femur.split(",")], [float(x) for x in a.tibia.split(",")]))
    trabajos = []
    for f, t in combos:
        m = dict(tipo=a.tipo, femur_deg=f, tibia_deg=t, fase_s=0.5, ciclo_paso_s=a.ciclo, ciclo_trote_s=a.ciclo,
                 apertura_deg=a.apertura, coxa_deg=a.coxa)
        trabajos += [("nominal", m, V.ciclos_para(m), 1001 + i) for i in range(a.episodios)]
    with Pool(a.procesos) as p:
        res = p.map(V.episodio, trabajos)
    for k, (f, t) in enumerate(combos):
        r = [x[2] for x in res[k * a.episodios:(k + 1) * a.episodios]]
        print(f"fémur {f:4.1f} tibia {t:4.1f} | avance {np.mean([x['avance_m'] for x in r]):6.2f} m | "
              f"deriva {np.mean([x['deriva_m'] for x in r]):.2f} m | caídas {sum(x['caida'] for x in r)}/{len(r)} | "
              f"incl.máx {np.mean([x['inclinacion_max_deg'] for x in r]):5.1f}°", flush=True)


if __name__ == "__main__":
    main()
