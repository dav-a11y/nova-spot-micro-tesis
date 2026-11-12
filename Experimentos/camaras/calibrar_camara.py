#!/usr/bin/env python3
"""Calibración de la webcam con el tablero de ajedrez impreso (9×6 esquinas, 25 mm).

Abre la cámara, y cada vez que detecta el tablero en una posición distinta a las
anteriores guarda la foto (hasta --fotos). Mueve el tablero por todo el encuadre,
con distintas inclinaciones y distancias. Al final calcula la matriz de la cámara y
la distorsión y las guarda en calibracion_<camara>.json.

Uso: python3 calibrar_camara.py --dispositivo /dev/video1 --nombre portatil1
"""
import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
ESQUINAS = (9, 6)
CUADRO_MM = 25.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dispositivo", default="/dev/video1")
    p.add_argument("--nombre", default="portatil1")
    p.add_argument("--fotos", type=int, default=15)
    p.add_argument("--maximo-s", type=float, default=180)
    a = p.parse_args()
    cam = cv2.VideoCapture(a.dispositivo, cv2.CAP_V4L2)
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    objp = np.zeros((ESQUINAS[0] * ESQUINAS[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:ESQUINAS[0], 0:ESQUINAS[1]].T.reshape(-1, 2) * CUADRO_MM
    puntos_obj, puntos_img, centros = [], [], []
    carpeta = AQUI / f"calibracion_{a.nombre}"
    carpeta.mkdir(exist_ok=True)
    fin = time.time() + a.maximo_s
    tam = None
    while len(puntos_img) < a.fotos and time.time() < fin:
        ok, img = cam.read()
        if not ok:
            continue
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tam = gris.shape[::-1]
        hay, esq = cv2.findChessboardCorners(gris, ESQUINAS, cv2.CALIB_CB_FAST_CHECK)
        if not hay:
            continue
        c = esq.reshape(-1, 2).mean(axis=0)
        # Solo posiciones nuevas: el centro del tablero debe moverse > 60 px.
        if any(np.linalg.norm(c - x) < 60 for x in centros):
            continue
        esq = cv2.cornerSubPix(gris, esq, (11, 11), (-1, -1),
                               (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        puntos_obj.append(objp); puntos_img.append(esq); centros.append(c)
        cv2.imwrite(str(carpeta / f"foto_{len(puntos_img):02d}.jpg"), img)
        print(f"Foto {len(puntos_img)}/{a.fotos} guardada (centro {c.astype(int)})", flush=True)
    cam.release()
    if len(puntos_img) < 6:
        raise SystemExit(f"Solo {len(puntos_img)} fotos válidas; hacen falta al menos 6.")
    err, K, dist, _, _ = cv2.calibrateCamera(puntos_obj, puntos_img, tam, None, None)
    salida = AQUI / f"calibracion_{a.nombre}.json"
    salida.write_text(json.dumps(dict(dispositivo=a.dispositivo, tam=tam, fotos=len(puntos_img),
                                      error_reproyeccion_px=err, K=K.tolist(),
                                      dist=dist.ravel().tolist()), indent=2))
    print(f"Calibración guardada en {salida} | error de reproyección {err:.2f} px "
          f"({'bueno' if err < 1.0 else 'revisar: repetir con el tablero más plano'})")


if __name__ == "__main__":
    main()
