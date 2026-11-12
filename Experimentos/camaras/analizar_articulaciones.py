#!/usr/bin/env python3
"""Mide los fémures y tibias con las cámaras laterales (marcadores ArUco 4X4_50 de 25 mm).

Marcadores (marcadores_articulaciones_25mm.pdf), pegados en la mitad de cada segmento:
  lado izquierdo (cámara 1): 10 cuerpo, 11 fémur 2, 12 tibia 2, 13 fémur 4, 14 tibia 4
  lado derecho  (cámara 2): 15 cuerpo, 16 fémur 1, 17 tibia 1, 18 fémur 3, 19 tibia 3
Con la cámara de lado, la rotación del marcador en la imagen es la rotación del
segmento en el plano sagital. Fémur = segmento − cuerpo; rodilla = tibia − fémur.
Se compara con la orden de caminata.csv (interpolada a la hora de cada fotograma):
cambio respecto a la postura inicial, ganancia, retardo, correlación y error.

Salidas en la carpeta: articulaciones.csv (por fotograma) y articulaciones.json.
Uso: python3 analizar_articulaciones.py grabaciones/base_01 [grabaciones/base_01/remota]
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

CUERPO = (10, 15)
# id: (nombre, id del segmento padre, columna de orden en caminata.csv)
SEGMENTOS = {
    11: ("femur2", 10, "orden_5"), 12: ("tibia2", 11, "orden_9"),
    13: ("femur4", 10, "orden_7"), 14: ("tibia4", 13, "orden_11"),
    16: ("femur1", 15, "orden_4"), 17: ("tibia1", 16, "orden_8"),
    18: ("femur3", 15, "orden_6"), 19: ("tibia3", 18, "orden_10"),
}
MAX_RETARDO_S = 0.3


def angulo_imagen(esq):
    """Ángulo (°) del borde superior del marcador (esquina 0 → 1) en la imagen."""
    d = esq[1] - esq[0]
    return float(np.degrees(np.arctan2(d[1], d[0])))


def envolver(a):
    return (a + 180.0) % 360.0 - 180.0


def medir_video(carpeta):
    cap = cv2.VideoCapture(str(carpeta / "video.mkv"))
    t_video = float((carpeta / "video.inicio.txt").read_text())
    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters_create()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    filas, n = [], 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        n += 1
        t = t_video + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        esq, ids, _ = cv2.aruco.detectMarkers(img, dic, parameters=params)
        if ids is None:
            continue
        ang = {int(i): angulo_imagen(e.reshape(4, 2)) for i, e in zip(ids.ravel(), esq)}
        fila = {"t": t}
        for i, (nombre, padre, _) in SEGMENTOS.items():
            if i in ang and padre in ang:
                fila[nombre] = envolver(ang[i] - ang[padre])
        if len(fila) > 1:
            filas.append(fila)
    cap.release()
    return filas, n


def comparar(t, medido, t_orden, orden):
    """Ganancia, retardo, r y error RMS de Δmedido frente a Δorden (desde la postura inicial)."""
    medido = envolver(medido - np.median(medido[:10]))
    mejor = None
    for L in np.arange(0.0, MAX_RETARDO_S + 1e-9, 0.01):
        o = np.interp(t - L, t_orden, orden) - orden[0]
        if np.std(o) < 1e-6:
            continue
        oc, mc = o - o.mean(), medido - medido.mean()
        r = float(np.corrcoef(oc, mc)[0, 1])
        if mejor is None or abs(r) > abs(mejor["r"]):
            k = float(oc @ mc / (oc @ oc))
            mejor = dict(r=round(r, 3), ganancia=round(k, 3), retardo_s=round(float(L), 2),
                         error_rms_grados=round(float(np.sqrt(np.mean((mc - k * oc) ** 2))), 2),
                         recorrido_medido_grados=round(float(np.ptp(medido)), 1),
                         recorrido_orden_grados=round(float(np.ptp(o)), 1))
    return mejor


def analizar(carpeta):
    filas, n = medir_video(carpeta)
    nombres = [v[0] for v in SEGMENTOS.values()]
    with (carpeta / "articulaciones.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["t", *nombres]); w.writeheader(); w.writerows(filas)
    resumen = dict(fotogramas=n, fotogramas_con_marcadores=len(filas), articulaciones={})
    cam = carpeta / "caminata.csv"
    pasos = list(csv.DictReader(cam.open())) if cam.exists() else []
    t0 = float((carpeta / "caminata.inicio.txt").read_text()) if pasos else 0.0
    for i, (nombre, _, col) in SEGMENTOS.items():
        sel = [(r["t"], r[nombre]) for r in filas if nombre in r]
        if len(sel) < 20:
            continue
        t, m = map(np.array, zip(*sel))
        res = dict(fotogramas=len(sel))
        if pasos:
            t_orden = np.array([t0 + float(p["t"]) for p in pasos])
            orden = np.array([float(p[col]) for p in pasos])
            dentro = (t >= t_orden[0]) & (t <= t_orden[-1])
            if dentro.sum() >= 20:
                res.update(comparar(t[dentro], m[dentro], t_orden, orden))
        resumen["articulaciones"][nombre] = res
    (carpeta / "articulaciones.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print(carpeta, f"{len(filas)}/{n} fotogramas con marcadores")
    for nombre, r in resumen["articulaciones"].items():
        print(f"  {nombre:7s}", ", ".join(f"{k}={v}" for k, v in r.items()))
    return resumen


def main():
    carpetas = [Path(c) for c in sys.argv[1:]]
    if len(carpetas) == 1 and (carpetas[0] / "remota" / "video.mkv").exists():
        carpetas.append(carpetas[0] / "remota")
    for c in carpetas:
        analizar(c)


if __name__ == "__main__":
    main()
