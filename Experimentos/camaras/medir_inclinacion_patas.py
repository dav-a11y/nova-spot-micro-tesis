#!/usr/bin/env python3
"""Inclinación de cada pata en la postura base, medida con las cámaras laterales.

1. Con los fotogramas de la caminata (gris, 240×135) y las órdenes de los 4 fémures se
   obtienen las máscaras de cada pata (regresión píxel a píxel, como analizar_video_patas.py).
2. En el fotograma de reposo (justo antes de empezar a caminar, servos en su posición base)
   se ajusta un eje a los píxeles de cada pata (componente principal): su ángulo respecto a la
   vertical de la imagen es la inclinación cadera→pie.
3. En cada lado se compara la pata delantera con la trasera: en la simulación las dos tienen
   la misma inclinación, así que la diferencia es el error de calibración de ese lado
   (positivo = las patas convergen hacia el centro, negativo = divergen).
Cámaras: portátil 2 (remota/, lado derecho: patas 1 y 3, delante = izquierda de la imagen) y
Logitech (extra_logitech/, lado izquierdo: patas 2 y 4, delante = derecha de la imagen).

Uso: python3 medir_inclinacion_patas.py grabaciones/<caminata de gateo base>
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

TAM = (240, 135)
FEMUR = {1: "orden_4", 2: "orden_5", 3: "orden_6", 4: "orden_7"}
CAMARAS = {"derecho": ("remota", (1, 3), -1), "izquierdo": ("extra_logitech", (2, 4), +1)}


def main():
    raiz = Path(sys.argv[1])
    filas = list(csv.DictReader((raiz / "caminata.csv").open()))
    t0 = float((raiz / "caminata.inicio.txt").read_text())
    tc = t0 + np.array([float(f["t"]) for f in filas])
    ordenes = {p: np.array([float(f[c]) for f in filas]) for p, c in FEMUR.items()}
    resultado = {}
    for lado, (sub, patas, delante) in CAMARAS.items():
        video = raiz / sub / "video.mkv"
        if not video.exists():
            print(f"{lado}: sin video"); continue
        ini = float((raiz / sub / "video.inicio.txt").read_text())
        cap = cv2.VideoCapture(str(video))
        imgs, ts, reposo = [], [], None
        n = 0
        while True:
            ok, img = cap.read()
            if not ok:
                break
            t = ini + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            g = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), TAM).astype(np.float32)
            if t < tc[0] - 0.3:
                reposo = (img, g)                                  # último fotograma en reposo
            elif tc[0] + 1.2 <= t <= tc[-1] and n % 2 == 0:
                imgs.append(g); ts.append(t)
            n += 1
        cap.release()
        X = np.array(imgs).reshape(len(imgs), -1); X -= X.mean(0)
        t = np.array(ts)
        mejor = None
        for L in np.arange(0.0, 1.21, 0.1):
            O = np.column_stack([np.interp(t - L, tc, ordenes[p]) for p in (1, 2, 3, 4)]); O -= O.mean(0); O /= O.std(0) + 1e-9
            B, *_ = np.linalg.lstsq(O, X, rcond=None)
            r2 = 1 - ((X - O @ B) ** 2).sum(0) / ((X ** 2).sum(0) + 1e-9)
            if mejor is None or np.percentile(r2, 99) > mejor[0]:
                mejor = (np.percentile(r2, 99), B, r2)
        _, B, r2 = mejor
        absB = np.abs(B); orden_b = np.sort(absB, 0)
        pata = np.argmax(absB, 0) + 1
        buenos = (r2 > 0.4) & (orden_b[-1] >= 2 * orden_b[-2])
        img, _ = reposo
        h, w = img.shape[:2]
        dibujo = img.copy()
        inclin = {}
        for p in patas:
            m = (buenos & (pata == p)).reshape(TAM[1], TAM[0]).astype(np.uint8)
            n_, et, est, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
            if n_ <= 1:
                continue
            k = 1 + int(np.argmax(est[1:, cv2.CC_STAT_AREA]))          # zona principal de la pata
            ys, xs = np.nonzero(et == k)
            pts = np.column_stack([xs * w / TAM[0], ys * h / TAM[1]])
            c = pts.mean(0)
            _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
            eje = vt[0] if vt[0][1] > 0 else -vt[0]                       # hacia abajo
            ang = float(np.degrees(np.arctan2(eje[0], eje[1])))          # + = pie hacia la derecha de la imagen
            inclin[p] = ang * delante                                     # + = pie hacia delante del robot
            a, b = (c - eje * 150).astype(int), (c + eje * 150).astype(int)
            cv2.line(dibujo, tuple(a), tuple(b), (0, 0, 255), 3)
            cv2.putText(dibujo, f"P{p} {inclin[p]:+.1f}", tuple(c.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.imwrite(str(raiz / f"inclinacion_{lado}.jpg"), cv2.resize(dibujo, (960, int(960 * h / w))))
        delantera, trasera = patas
        if delantera in inclin and trasera in inclin:
            conv = inclin[trasera] - inclin[delantera]                   # + = convergen
            resultado[lado] = dict(inclinacion_delantera=round(inclin[delantera], 1),
                                   inclinacion_trasera=round(inclin[trasera], 1),
                                   convergencia_grados=round(conv, 1))
            print(f"lado {lado}: pata {delantera} {inclin[delantera]:+.1f}°, pata {trasera} {inclin[trasera]:+.1f}° "
                  f"(+ = pie hacia delante) -> {'CONVERGEN' if conv > 0 else 'DIVERGEN'} {abs(conv):.1f}°")
        else:
            print(f"lado {lado}: no se identificaron las dos patas ({sorted(inclin)})")
    (raiz / "inclinacion_patas.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
