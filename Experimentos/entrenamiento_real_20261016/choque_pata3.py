#!/usr/bin/env python3
"""Error del fémur 3 (C9, compensado con C0) por fase de la caminata gateo.

Entre las fases 0,38 y 0,50 la pata 3 avanza mientras la pata 1 está atrás; si chocan,
el fémur 3 se queda corto (error positivo de varios grados) solo en ese tramo.
Uso: choque_pata3.py caminata.csv [otra.csv ...]
"""
import csv
import sys

import numpy as np

for ruta in sys.argv[1:]:
    r = list(csv.DictReader(open(ruta)))[34:]
    col = lambda c: np.array([float(x[c]) for x in r])
    fase, c0 = col("fase"), col("C0")
    m = ((col("C9") - (c0 - c0[0]))[3:] - col("C9")[3]) / -2.52
    o = col("orden_6")[:-3] - col("orden_6")[0]
    e = (m - m.mean()) - (o - o.mean())
    f = fase[:-3]
    choque = e[(f >= 0.38) & (f < 0.5)].mean()
    resto = e[(f < 0.3) | (f > 0.6)].mean()
    print(f"{ruta}: error del fémur 3 en la fase de choque {choque:+.1f}° (resto {resto:+.1f}°) -> "
          f"{'CHOQUE' if choque - resto > 4 else 'sin choque'}")
