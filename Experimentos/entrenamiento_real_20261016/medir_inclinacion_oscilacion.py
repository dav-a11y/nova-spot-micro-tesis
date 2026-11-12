#!/usr/bin/env python3
"""Inclinación de cada pata a partir de la oscilación de su fémur (lo llama calibrar_postura_auto.py).

Para cada pata, en la cámara de su lado: correlación píxel a píxel (320×180) entre el
brillo y la orden de oscilación (con el retardo de la cámara que mejor ajusta); la zona
con |r| > 0,55 (componente principal) es la pata. Su eje principal, en el fotograma de
postura base previo a la oscilación, da la inclinación (+ = pie hacia delante del robot).
Escribe inclinaciones.json y una imagen por lado con el eje dibujado.
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

TAM = (320, 180)
VIDEO = {1: ("hp_pc2.mkv", -1), 3: ("hp_pc2.mkv", -1), 2: ("logitech.mkv", +1), 4: ("logitech.mkv", +1)}


def primer(video):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "packet=pts_time", "-read_intervals", "%+#1", "-of", "csv=p=0", str(video)])
    return float(s.decode().split()[0])


def leer(video, t0v, desde, hasta):
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, (desde - t0v) * 1000))
    imgs, ts, color = [], [], None
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = t0v + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if t > hasta:
            break
        if color is None:
            color = img
        imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), TAM).astype(np.float32)); ts.append(t)
    cap.release()
    return np.array(imgs), np.array(ts), color


def main():
    sub = Path(sys.argv[1])
    o = np.load(sub / "ordenes.npz")
    resultado, dibujos = {}, {}
    for pata, (nombre, delante) in VIDEO.items():
        video = sub / nombre
        corr = float(o["desfase"]) if nombre == "hp_pc2.mkv" else 0.0
        ts, ds = o[f"t{pata}"], o[f"d{pata}"]
        t0v = primer(video)
        X, tv, _ = leer(video, t0v, ts[0] + corr, ts[-1] + corr + 1.0)
        _, _, reposo = leer(video, t0v, ts[0] + corr - 0.6, ts[0] + corr - 0.3)
        if len(X) < 30 or reposo is None:
            continue
        tv = tv - corr
        Xc = X.reshape(len(X), -1); Xc = Xc - Xc.mean(0)
        mejor = None
        for L in np.arange(0.0, 1.01, 0.06):
            v = np.interp(tv - L, ts, ds); v = v - v.mean()
            r = (v @ Xc) / (np.linalg.norm(v) * np.linalg.norm(Xc, axis=0) + 1e-9)
            q = np.percentile(np.abs(r), 99.5)
            if mejor is None or q > mejor[0]:
                mejor = (q, r)
        m = (np.abs(mejor[1]) > 0.55).reshape(TAM[1], TAM[0]).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        n, et, est, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if n <= 1:
            continue
        k = 1 + int(np.argmax(est[1:, cv2.CC_STAT_AREA]))
        ys, xs = np.nonzero(et == k)
        h, w = reposo.shape[:2]
        pts = np.column_stack([xs * w / TAM[0], ys * h / TAM[1]])
        c = pts.mean(0)
        _, sv, vt = np.linalg.svd(pts - c, full_matrices=False)
        eje = vt[0] if vt[0][1] > 0 else -vt[0]
        ang = float(np.degrees(np.arctan2(eje[0], eje[1]))) * delante
        resultado[str(pata)] = round(ang, 2)
        dib = dibujos.setdefault(nombre, reposo.copy())
        a_, b_ = (c - eje * 220).astype(int), (c + eje * 220).astype(int)
        cv2.line(dib, tuple(a_), tuple(b_), (0, 0, 255), 3)
        cv2.putText(dib, f"P{pata} {ang:+.1f} ({len(xs)} px)", tuple(c.astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        print(f"pata {pata}: {ang:+.1f}° (+ = pie adelante), {len(xs)} píxeles, |r| p99,5 {mejor[0]:.2f}")
    for nombre, d in dibujos.items():
        cv2.imwrite(str(sub / f"eje_{nombre.replace('.mkv', '')}.jpg"), cv2.resize(d, (960, int(960 * d.shape[0] / d.shape[1]))))
    (sub / "inclinaciones.json").write_text(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()
