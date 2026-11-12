#!/usr/bin/env python3
"""Cuantifica con los sensores cuánto corrigió la política respecto a la base.
Uso: cuantificar_correccion.py base.csv ppo.csv"""
import csv, sys
import numpy as np
CPG = 2.45
ART = (("Fémur 2", 5, "C5"), ("Fémur 4", 7, "C6"), ("Tibia 2", 9, "C9"))
COX = (("Coxa 2", "C1"), ("Coxa 3", "C3"), ("Coxa 4", "C2"))
def carga(r):
    rows = list(csv.DictReader(open(r)))
    return {k: np.array([float(x[k]) for x in rows]) for k in rows[0] if k != "fase"}
b, p = carga(sys.argv[1]), carga(sys.argv[2])
n = min(len(b["paso"]), len(p["paso"])); rampa = 34
print(f"Pasos comparados: {n - rampa} (sin la rampa inicial)\n")
print(f"{'Articulación':10s} {'corr. ordenada':>16s} {'corr. realizada':>16s} {'realizado':>10s} {'r':>6s} {'retardo':>8s}")
for nom, oi, ch in ART:
    ordenada = (p[f"orden_{oi}"] - p[f"nominal_{oi}"])[rampa:n]
    if nom == "Tibia 2" and "ENC_T2" in b and "ENC_T2" in p:
        # 19-oct: la tibia 2 se mide con su AS5600 (−0,66 °encoder/°servo).
        def enc_a_servo(d):
            e = (d["ENC_T2"] - d["ENC_T2"][0]) * 360.0 / 4096.0
            e = (e + 180.0) % 360.0 - 180.0
            return d[f"orden_{oi}"][0] + e / -0.66
        med_b, med_p = enc_a_servo(b), enc_a_servo(p)
    else:
        med_b = b[f"orden_{oi}"][0] - (b[ch] - b[ch][0]) / CPG
        med_p = p[f"orden_{oi}"][0] - (p[ch] - p[ch][0]) / CPG
    # Ajuste por la misma posición inicial: ambas parten de la base.
    realizada = (med_p - med_b)[rampa:n]
    lag = max(range(6), key=lambda l: np.corrcoef(ordenada[:len(ordenada)-l], realizada[l:])[0, 1] if ordenada.std() > 0 else 0)
    o, r = ordenada[:len(ordenada)-lag], realizada[lag:]
    cc = np.corrcoef(o, r)[0, 1]
    pct = 100 * np.polyfit(o, r, 1)[0] if o.std() > 0 else float("nan")
    print(f"{nom:10s} {np.abs(o).mean():7.2f}° (máx {np.abs(o).max():4.1f}) {np.abs(r).mean():7.2f}° (máx {np.abs(r).max():4.1f}) {pct:9.0f}% {cc:6.2f} {lag*33:6d} ms")
print("\nCoxas (desviación respecto a su equilibrio, medida por sensor):")
for nom, ch in COX:
    def desv(d):
        x = d[ch][rampa:n]; ref = np.median(d[ch][:rampa]) if rampa else x[0]
        return np.abs(x - ref) / 2.4
    db, dp = desv(b), desv(p)
    print(f"  {nom}: base media {db.mean():.2f}° (p95 {np.percentile(db,95):.1f}°) | PPO media {dp.mean():.2f}° (p95 {np.percentile(dp,95):.1f}°)")
