#!/usr/bin/env python3
"""Compara orden frente a medición (F2, F4, T2) de un registro de ejecutar_politica_robot.py."""
import csv, sys
import numpy as np
for ruta in sys.argv[1:]:
    rows = list(csv.DictReader(open(ruta)))
    t = np.array([float(r["t"]) for r in rows])
    print(f"{ruta.split('/')[-1]}: {len(rows)} pasos, periodo medio {np.diff(t).mean()*1000:.1f} ms")
    for n, oi, ch in (("Femur 2", 5, "C5"), ("Femur 4", 7, "C6"), ("Tibia 2", 9, "C9")):
        o = np.array([float(r[f"orden_{oi}"]) for r in rows])
        a = np.array([float(r[ch]) for r in rows])
        med = o[0] - (a - a[0]) / 2.45          # grados de servo medidos
        best = max(((np.corrcoef(o[:len(o)-l], med[l:])[0, 1], l) for l in range(8)), key=lambda x: x[0])
        l = best[1]
        err = med[l:] - o[:len(o)-l]
        print(f"  {n}: r={best[0]:+.2f} retardo≈{l} pasos | orden {o.min():.0f}-{o.max():.0f}° | "
              f"medido {np.percentile(med,5):.0f}-{np.percentile(med,95):.0f}° | error RMS {np.sqrt((err-err.mean())**2).mean():.1f}°")
