#!/usr/bin/env python3
"""Recorre el rango útil de cada articulación con sensor (base ±40°, dentro de los
topes del firmware) en pasos de 3° con pausa, subiendo y bajando, y registra los
8 canales. Robot suspendido. Usa el modo `@` del firmware."""
import csv, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ejecutar_politica_robot import BASE, Lector, abrir
HERE = Path(__file__).resolve().parent
CANALES = ["C5", "C6", "C9", "C1", "C3", "C2", "C10", "C11"]
TOPES = {5: (45, 170), 7: (25, 170), 9: (25, 160), 11: (15, 150)}   # por índice: F2, F4, T3, T4
TOPES[9] = (25, 90)  # T2 está en CH12 -> tope 25-90
ART = {"femur2": 5, "femur4": 7, "tibia2": 9, "tibia4": 11}
DT, PASO, PAUSA = 0.03, 3, 0.4

def trayectoria(idx):
    b = BASE[idx]; lo, hi = TOPES[idx]
    arriba = min(b + 40, hi - 2); abajo = max(b - 40, lo + 2)
    pts = list(range(b, arriba + 1, PASO)) + list(range(arriba, abajo - 1, -PASO)) + list(range(abajo, b + 1, PASO))
    return pts, (abajo, arriba)

fd = abrir("/dev/ttyACM0"); lec = Lector(fd)
time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
while (l := lec.linea(timeout=8.0)) is not None and not l.startswith("STREAM_LISTO"):
    pass
salida = HERE / "barrido_rango"; salida.mkdir(exist_ok=True)
try:
    for nombre, idx in ART.items():
        pts, rango = trayectoria(idx)
        ruta = salida / f"{nombre}.csv"
        with ruta.open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["t", "orden", "sentido", *CANALES])
            t0 = time.time(); k = 0; prev = BASE[idx]
            for objetivo in pts:
                sentido = "sube" if objetivo > prev else ("baja" if objetivo < prev else "igual")
                prev = objetivo
                for _ in range(round(PAUSA / DT)):
                    g = list(BASE); g[idx] = objetivo
                    os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode())
                    r = lec.linea(timeout=0.3)
                    if not r or not r.startswith("R,"):
                        raise SystemExit(f"respuesta perdida en {nombre}")
                    w.writerow([round(time.time() - t0, 3), objetivo, sentido, *r.split(",")[2:10]])
                    k += 1
                    espera = t0 + k * DT - time.time()
                    if espera > 0: time.sleep(espera)
        print(f"{nombre}: rango {rango[0]}-{rango[1]}°, {k} pasos", flush=True)
finally:
    os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd)
