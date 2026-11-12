#!/usr/bin/env python3
"""Analiza identificacion_robot/*.csv: escala ADC, zona muerta, escalones, senoides y acoplamiento."""
import csv, glob, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
CANALES = ["C5", "C6", "C9", "C1", "C3", "C2", "C10", "C11"]
PROPIO = {"femur2": "C5", "femur4": "C6", "tibia2": "C9", "tibia3": "C11", "tibia4": "C10"}
resumen = {}
for nombre, ch in PROPIO.items():
    ruta = sorted(glob.glob(str(HERE / f"identificacion_robot/{nombre}_*.csv")))[-1]
    rows = list(csv.DictReader(open(ruta)))
    etq = np.array([r["etiqueta"] for r in rows]); o = np.array([float(r["orden"]) for r in rows])
    A = {c: np.array([float(r[c]) for r in rows]) for c in CANALES}
    a = A[ch]; base = o[0]
    # Escala con las mesetas de ±6 y ±12 (segunda mitad de cada escalón).
    xs, ys = [], []
    for e in ("escalon_+6", "escalon_-6", "escalon_+12", "escalon_-12", "reposo"):
        idx = np.where(etq == e)[0]
        if len(idx):
            idx = idx[len(idx)//2:]; xs.append(o[idx].mean() - base); ys.append(np.median(a[idx]))
    pend, off = np.polyfit(xs, ys, 1)
    r2 = np.corrcoef(xs, ys)[0, 1] ** 2
    ruido = float(np.std(a[np.where(etq == "reposo")[0]]))
    medido = (a - off) / pend if abs(pend) > 0.3 else np.full_like(a, np.nan)
    info = dict(canal=ch, cuentas_por_grado=round(float(pend), 2), r2_escala=round(float(r2), 3),
                ruido_cuentas=round(ruido, 1))
    if abs(pend) > 0.3:
        meseta = {}
        for e in ("escalon_+1", "escalon_-1", "escalon_+2", "escalon_-2", "escalon_+6", "escalon_-6", "escalon_+12", "escalon_-12"):
            idx = np.where(etq == e)[0]; idx = idx[len(idx)//2:]
            meseta[e] = round(float(np.median(medido[idx])), 1)
        info["mesetas_grados"] = meseta
        # Tiempo de subida 10-90 % del escalón +12.
        idx = np.where(etq == "escalon_+12")[0]
        t = np.array([float(rows[i]["t"]) for i in idx]); m = medido[idx]
        lo, hi = medido[idx[0]-1], np.median(m[len(m)//2:])
        try:
            t10 = t[np.argmax((m - lo) >= 0.1 * (hi - lo))]; t90 = t[np.argmax((m - lo) >= 0.9 * (hi - lo))]
            info["subida_10_90_ms_escalon12"] = round((t90 - t10) * 1000)
        except Exception:
            pass
        sen = {}
        for f in ("0.5", "1.0", "2.0"):
            idx = np.where(etq == f"seno_{f}Hz")[0]
            tt = np.array([float(rows[i]["t"]) for i in idx]); oo = o[idx] - base; mm = medido[idx]
            w = 2 * np.pi * float(f)
            M = np.c_[np.sin(w * tt), np.cos(w * tt), np.ones_like(tt)]
            co, *_ = np.linalg.lstsq(M, oo, rcond=None); cm, *_ = np.linalg.lstsq(M, mm, rcond=None)
            ao, ph_o = np.hypot(co[0], co[1]), np.arctan2(co[1], co[0])
            am, ph_m = np.hypot(cm[0], cm[1]), np.arctan2(cm[1], cm[0])
            retr = ((ph_o - ph_m) % (2 * np.pi)) / w
            sen[f + "Hz"] = dict(ganancia=round(float(am / ao), 2), retardo_ms=round(float(retr * 1000)))
        info["senoides"] = sen
    acop = {}
    for c in CANALES:
        if c == ch: continue
        rr = np.corrcoef(o, A[c])[0, 1] if A[c].std() > 0 else 0
        if abs(rr) > 0.5: acop[c] = round(float(rr), 2)
    info["acoplamiento_otros_canales"] = acop
    resumen[nombre] = info
    print(f"\n{nombre} ({ch}): {info}")
(HERE / "identificacion_sistema.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
