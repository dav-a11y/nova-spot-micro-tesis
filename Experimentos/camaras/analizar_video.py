#!/usr/bin/env python3
"""Mide el cuerpo del cuadrúpedo en una grabación (marcadores ArUco 4X4_50 de 50 mm).

Para cada fotograma estima la pose del marcador del cuerpo (por defecto el primero
que aparezca de los ID 0–3). Si se ve un marcador de suelo (ID 4 o 5), las medidas
se expresan en el sistema del suelo; si no, respecto a la cámara (vale para comparar
caminatas con la cámara fija). Sincroniza con caminata.csv para separar ciclos.

Salidas en la carpeta de la grabación: pose.csv (por fotograma) y resumen.json
(roll/pitch RMS y máximos, avance, desvío lateral y giro, por ciclo y totales).

Uso: python3 analizar_video.py grabaciones/base_01 [--calibracion calibracion_portatil1.json]
"""
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
LADO_M = 0.050
CUERPO = (0, 1, 2, 3)
SUELO = (4, 5)
MUESTRAS_POR_CICLO = 88          # caminata base: 4 fases × (17 + 5) pasos


def euler_zyx(R):
    """roll (x), pitch (y), yaw (z) en grados a partir de una matriz de rotación."""
    pitch = np.degrees(np.arcsin(-np.clip(R[2, 0], -1, 1)))
    roll = np.degrees(np.arctan2(R[2, 1], R[2, 2]))
    yaw = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
    return roll, pitch, yaw


def calib_por_defecto(ancho, alto):
    f = 0.9 * ancho          # aproximación para webcams gran angular sin calibrar
    return np.array([[f, 0, ancho / 2], [0, f, alto / 2], [0, 0, 1]]), np.zeros(5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("carpeta", type=Path)
    p.add_argument("--calibracion", type=Path)
    p.add_argument("--id-cuerpo", type=int)
    a = p.parse_args()
    video = a.carpeta / "video.mkv"
    cap = cv2.VideoCapture(str(video))
    ancho, alto = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if a.calibracion and a.calibracion.exists():
        c = json.loads(a.calibracion.read_text()); K, dist = np.array(c["K"]), np.array(c["dist"])
        calibrada = True
    else:
        K, dist = calib_por_defecto(ancho, alto); calibrada = False
    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters_create()
    t_video = float((a.carpeta / "video.inicio.txt").read_text())
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    filas, id_cuerpo, n, R_suelo, t_suelo = [], a.id_cuerpo, 0, None, None
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = t_video + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        n += 1
        esq, ids, _ = cv2.aruco.detectMarkers(img, dic, parameters=params)
        if ids is None:
            continue
        ids = ids.ravel().tolist()
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(esq, LADO_M, K, dist)
        poses = {i: (cv2.Rodrigues(rvecs[k])[0], tvecs[k].ravel()) for k, i in enumerate(ids)}
        for s in SUELO:
            if s in poses and R_suelo is None:
                R_suelo, t_suelo = poses[s]          # referencia fija (primer avistamiento)
        if id_cuerpo is None:
            presentes = [i for i in CUERPO if i in poses]
            if not presentes:
                continue
            id_cuerpo = presentes[0]
        if id_cuerpo not in poses:
            continue
        R, tv = poses[id_cuerpo]
        if R_suelo is not None:
            R_rel = R_suelo.T @ R; p_rel = R_suelo.T @ (tv - t_suelo)
        else:
            R_rel, p_rel = R, tv
        roll, pitch, yaw = euler_zyx(R_rel)
        filas.append(dict(t=t, x=p_rel[0], y=p_rel[1], z=p_rel[2], roll=roll, pitch=pitch, yaw=yaw))
    cap.release()
    if not filas:
        raise SystemExit(f"No se detectó el marcador del cuerpo en {n} fotogramas.")
    with (a.carpeta / "pose.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    T = np.array([r["t"] for r in filas]); P = np.array([[r["x"], r["y"], r["z"]] for r in filas])
    ang = np.array([[r["roll"], r["pitch"], r["yaw"]] for r in filas])
    ref = np.median(ang[: max(5, len(ang) // 20)], axis=0)           # postura inicial
    ang = (ang - ref + 180.0) % 360.0 - 180.0                          # relativo y sin saltos de ±360°
    # Ciclos según el registro de la caminata.
    ciclos = []
    cam = a.carpeta / "caminata.csv"
    if cam.exists():
        t0 = float((a.carpeta / "caminata.inicio.txt").read_text())
        pasos = list(csv.DictReader(cam.open()))
        tiempos = np.array([t0 + float(r["t"]) for r in pasos])
        rampa = next((k for k, r in enumerate(pasos) if float(r["fase"]) > 0), 0)
        for c0 in range(rampa, len(pasos) - MUESTRAS_POR_CICLO + 1, MUESTRAS_POR_CICLO):
            ini, fin = tiempos[c0], tiempos[min(c0 + MUESTRAS_POR_CICLO, len(tiempos) - 1)]
            sel = (T >= ini) & (T < fin)
            if sel.sum() < 5:
                continue
            ciclos.append(dict(ciclo=len(ciclos) + 1, fotogramas=int(sel.sum()),
                               roll_rms=float(np.sqrt(np.mean(ang[sel, 0] ** 2))), roll_max=float(np.abs(ang[sel, 0]).max()),
                               pitch_rms=float(np.sqrt(np.mean(ang[sel, 1] ** 2))), pitch_max=float(np.abs(ang[sel, 1]).max()),
                               desplazamiento_m=float(np.linalg.norm(P[sel][-1, :2] - P[sel][0, :2]))))
    resumen = dict(
        video=str(video), fotogramas=n, fotogramas_con_cuerpo=len(filas), id_cuerpo=id_cuerpo,
        referencia="suelo (ID 4/5)" if R_suelo is not None else "cámara (fija)",
        calibrada=calibrada,
        roll_rms_deg=float(np.sqrt(np.mean(ang[:, 0] ** 2))), roll_max_deg=float(np.abs(ang[:, 0]).max()),
        pitch_rms_deg=float(np.sqrt(np.mean(ang[:, 1] ** 2))), pitch_max_deg=float(np.abs(ang[:, 1]).max()),
        giro_total_deg=float(ang[-1, 2]),
        avance_m=float(P[-1, 0] - P[0, 0]), desvio_lateral_m=float(P[-1, 1] - P[0, 1]),
        ciclos=ciclos)
    (a.carpeta / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in resumen.items() if k != "ciclos"}, indent=1, ensure_ascii=False))
    if ciclos:
        print(f"{len(ciclos)} ciclos analizados; roll RMS medio {np.mean([c['roll_rms'] for c in ciclos]):.2f}°, "
              f"pitch RMS medio {np.mean([c['pitch_rms'] for c in ciclos]):.2f}°")


if __name__ == "__main__":
    main()
