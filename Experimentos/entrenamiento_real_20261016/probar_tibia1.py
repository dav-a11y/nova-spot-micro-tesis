#!/usr/bin/env python3
"""Mueve solo la tibia 1 (índice 8, CH12) despacio en modo de transmisión '@' (5-nov): 40→80→20→40, dos veces;
las demás articulaciones quietas en su base. Para comprobar a la vista si el servo se mueve."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ejecutar_politica_robot import BASE, Lector, abrir  # noqa: E402

fd = abrir("/dev/ttyACM0")
lec = Lector(fd)
time.sleep(2.0)
os.read(fd, 4096)
os.write(fd, b"@")
while True:
    l = lec.linea(timeout=8.0)
    if l is None:
        sys.exit("sin STREAM_LISTO")
    if l.startswith("STREAM_LISTO"):
        break
orden = list(BASE)
recorrido = []
for a, b in [(100, 40), (40, 80), (80, 20), (20, 40)] * 1 + [(40, 80), (80, 20), (20, 40)]:
    paso = 1 if b > a else -1
    recorrido += list(range(a, b, paso))
recorrido.append(40)
for v in recorrido:
    orden[8] = v
    os.write(fd, ("S," + ",".join(map(str, orden)) + "\n").encode())
    lec.linea(timeout=0.5)
    time.sleep(0.04)
time.sleep(1.0)
os.write(fd, b"x\n")
print(f"tibia 1: {len(recorrido)} órdenes, de {min(recorrido)} a {max(recorrido)} grados de servo")
