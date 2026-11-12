#!/usr/bin/env python3
"""Ajusta la postura base del robot a la de la simulación con las cintas de colores (21-oct).

Cada vuelta: prueba de identificación (cada pata se mueve por separado, postura base con
calibracion_postura.json y apertura 8°) grabada con las cámaras; en las laterales
(Logitech: lado derecho, patas 1 y 3; General: lado izquierdo, patas 2 y 4) se mide el eje de la
cinta roja (fémur) y de la verde (tibia) en el fotograma de postura base y se compara con la
simulación (respecto a la vertical, + = parte baja hacia delante del robot):
  fémur_off += k·(fémur_sim − fémur_real)
  tibia_off += k·((tibia_sim − tibia_real) − (fémur_sim − fémur_real))   (la tibia gira con el fémur)
con k = 0,7 y un máximo de 15° por vuelta. Termina cuando todo está a menos de 5°.

Uso: python3 calibrar_postura_colores.py [--vueltas 4]
"""
import argparse
import csv
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
ENT = AQUI.parent / "entrenamiento_real_20261016"
CAL = ENT / "calibracion_postura.json"
# Simulación (geometría real, apertura 8°): delanteras / traseras.
SIM = {1: (-16.1, 32.1), 2: (-16.1, 32.1), 3: (-32.1, 16.1), 4: (-32.1, 16.1)}
CAMARA = {"logitech": (-1, (1, 3)), "general": (+1, (2, 4))}     # signo de «delante» en la imagen
K, PASO_MAX, TOL = 0.7, 15.0, 5.0
LIM = {"femur_offset_deg": (-30.0, 30.0), "tibia_offset_deg": (-15.0, 60.0)}


def ejes(raiz):
    """{pata: {'femur': °, 'tibia': °}} medidos en el fotograma de postura base."""
    ident = json.loads((raiz / "colores_patas.json").read_text())
    t0 = float((raiz / "caminata.inicio.txt").read_text())
    filas = list(csv.DictReader((raiz / "caminata.csv").open()))
    k = next(i for i, f in enumerate(filas) if f["fase"] != "0") - 5
    tb = t0 + float(filas[k]["t"])
    out = {}
    for cam, (delante, _) in CAMARA.items():
        sub = raiz / f"extra_{cam}"
        if cam not in ident or not (sub / "video.mkv").exists():
            continue
        ini = float((sub / "video.inicio.txt").read_text())
        png = raiz / f"base_{cam}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tb - ini:.2f}", "-i", str(sub / "video.mkv"),
                        "-frames:v", "1", str(png)], check=True)
        img = cv2.imread(str(png)); img = cv2.resize(img, (480, int(480 * img.shape[0] / img.shape[1])))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = {"femur": cv2.inRange(hsv, (0, 110, 70), (8, 255, 255)) | cv2.inRange(hsv, (170, 110, 70), (179, 255, 255)),
                "tibia": cv2.inRange(hsv, (40, 80, 40), (90, 255, 255))}
        dib = img.copy()
        for v in ident[cam].values():
            if not isinstance(v, dict) or not v["pata"] or v["pieza"] not in mask:
                continue
            n, et, est, cen = cv2.connectedComponentsWithStats(mask[v["pieza"]])
            cand = [(math.hypot(cen[i][0] - v["x_medio"], cen[i][1] - v["y_medio"]), i)
                    for i in range(1, n) if est[i, cv2.CC_STAT_AREA] > 300]
            if not cand:
                continue
            dist, lab = min(cand)
            if dist > 60:
                continue
            ys, xs = np.nonzero(et == lab)
            pts = np.column_stack([xs, ys]).astype(float); c = pts.mean(0)
            _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
            e = vt[0] if vt[0][1] > 0 else -vt[0]
            ang = math.degrees(math.atan2(e[0], e[1])) * delante
            prev = out.setdefault(v["pata"], {}).get(v["pieza"])
            if prev is None or len(xs) > prev[1]:
                out[v["pata"]][v["pieza"]] = (ang, len(xs))
            a, b = (c - e * 60).astype(int), (c + e * 60).astype(int)
            cv2.line(dib, tuple(a), tuple(b), (255, 0, 255), 2)
            cv2.putText(dib, f"P{v['pata']} {v['pieza'][0]} {ang:+.0f}", tuple(c.astype(int)), 0, 0.5, (255, 255, 255), 2)
        cv2.imwrite(str(raiz / f"ejes_{cam}.jpg"), dib)
    return {p: {pz: a for pz, (a, _) in d.items()} for p, d in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vueltas", type=int, default=4)
    a = ap.parse_args()
    historial = []
    for vuelta in range(1, a.vueltas + 1):
        nombre = time.strftime(f"calib_colores_%Y%m%d_%H%M%S_v{vuelta}")
        subprocess.run([sys.executable, str(AQUI / "grabar_caminata.py"), "--nombre", nombre, "--remota", "",
                        "--ejecutor", str(ENT / "identificar_patas_robot.py"), "--", "--apertura", "8"],
                       check=True, capture_output=True)
        raiz = AQUI / "grabaciones" / nombre
        subprocess.run([sys.executable, "-I", str(AQUI / "analizar_colores_patas.py"), str(raiz), "logitech,general"],
                       check=True, capture_output=True)
        med = ejes(raiz)
        cal = json.loads(CAL.read_text())
        fo, to = cal["femur_offset_deg"], cal.setdefault("tibia_offset_deg", {})
        listo, filas = True, []
        for p in (1, 2, 3, 4):
            sf, st = SIM[p]
            m = med.get(p, {})
            ef = sf - m["femur"] if "femur" in m else None
            et = st - m["tibia"] if "tibia" in m else None
            if ef is not None and abs(ef) >= TOL or et is not None and abs(et) >= TOL:
                listo = False
            df = 0.0 if ef is None else float(np.clip(K * ef, -PASO_MAX, PASO_MAX))
            dt = 0.0 if et is None else float(np.clip(K * (et - (ef or 0.0)), -PASO_MAX, PASO_MAX))
            fo[str(p)] = round(float(np.clip(fo.get(str(p), 0.0) + df, *LIM["femur_offset_deg"])), 1)
            to[str(p)] = round(float(np.clip(to.get(str(p), 0.0) + dt, *LIM["tibia_offset_deg"])), 1)
            filas.append(dict(pata=p, femur_real=m.get("femur"), tibia_real=m.get("tibia"), error_femur=ef, error_tibia=et,
                              femur_offset=fo[str(p)], tibia_offset=to[str(p)]))
            fmt = lambda x: "  —  " if x is None else f"{x:+5.1f}"
            print(f"vuelta {vuelta} P{p}: fémur {fmt(m.get('femur'))} (sim {sf:+.0f}, err {fmt(ef)}) | tibia {fmt(m.get('tibia'))} "
                  f"(sim {st:+.0f}, err {fmt(et)}) -> corrección fémur {fo[str(p)]:+.1f}°, tibia {to[str(p)]:+.1f}°", flush=True)
        historial.append(dict(vuelta=vuelta, grabacion=nombre, patas=filas))
        if listo:
            print(f"Postura igual a la simulación (todo < {TOL}°): no se cambia la calibración.", flush=True)
            break
        cal["nota"] = ("21-oct: corrección de la postura base respecto a la simulación (fémur: + = pie adelante; tibia: + = "
                       "rodilla más doblada), medida con las cintas de colores por calibrar_postura_colores.py.")
        CAL.write_text(json.dumps(cal, indent=2, ensure_ascii=False))
    (AQUI / "grabaciones" / time.strftime("calib_colores_%Y%m%d_%H%M%S_historial.json")).write_text(
        json.dumps(historial, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
