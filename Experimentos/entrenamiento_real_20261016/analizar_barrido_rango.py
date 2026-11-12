#!/usr/bin/env python3
"""Analiza barrido_rango/*.csv: linealidad ADC-ángulo en todo el rango, histéresis
subida/bajada y tramos anómalos. Escribe barrido_rango/modelo_rango.json."""
import csv, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
PROPIO = {"femur2": "C5", "femur4": "C6", "tibia2": "C9", "tibia4": "C10"}
modelo = {}
for nombre, ch in PROPIO.items():
    rows = list(csv.DictReader(open(HERE / f"barrido_rango/{nombre}.csv")))
    mesetas = []  # (orden, sentido, adc mediano en la segunda mitad de la meseta)
    i = 0
    while i < len(rows):
        j = i
        while j < len(rows) and rows[j]["orden"] == rows[i]["orden"] and rows[j]["sentido"] == rows[i]["sentido"]:
            j += 1
        seg = [float(r[ch]) for r in rows[i:j]][(j - i) // 2:]
        mesetas.append((float(rows[i]["orden"]), rows[i]["sentido"], float(np.median(seg)), float(np.std(seg))))
        i = j
    ang = np.array([m[0] for m in mesetas]); adc = np.array([m[2] for m in mesetas])
    pend, off = np.polyfit(ang, adc, 1)
    res = (adc - (pend * ang + off)) / abs(pend)          # residuo en grados
    # Histéresis: misma orden alcanzada subiendo y bajando.
    sube = {m[0]: m[2] for m in mesetas if m[1] == "sube"}
    baja = {m[0]: m[2] for m in mesetas if m[1] == "baja"}
    # Las rejillas de subida y bajada están desfasadas: se interpola la bajada.
    bx = np.array(sorted(baja)); by = np.array([baja[a] for a in bx])
    hist = [(sube[a] - np.interp(a, bx, by)) / abs(pend) for a in sorted(sube) if bx.min() <= a <= bx.max()]
    # Pendiente local por tramos de ~15°.
    orden_u = np.unique(ang)
    tramos = []
    for a0 in np.arange(orden_u.min(), orden_u.max(), 15):
        sel = (ang >= a0) & (ang < a0 + 15)
        if sel.sum() >= 4:
            tramos.append((int(a0), int(a0 + 15), round(float(np.polyfit(ang[sel], adc[sel], 1)[0]), 2)))
    peor = int(np.argmax(np.abs(res)))
    info = dict(canal=ch, rango_orden=[float(ang.min()), float(ang.max())],
                cuentas_por_grado=round(float(pend), 3), offset=round(float(off), 1),
                error_lineal_rms_grados=round(float(np.sqrt(np.mean(res ** 2))), 2),
                error_lineal_max_grados=round(float(np.abs(res).max()), 2), en_orden=float(ang[peor]),
                histeresis_media_grados=round(float(np.mean(np.abs(hist))), 2),
                histeresis_max_grados=round(float(np.max(np.abs(hist))), 2),
                pendiente_por_tramo=tramos,
                ruido_meseta_cuentas=round(float(np.median([m[3] for m in mesetas])), 2))
    modelo[nombre] = info
    print(f"\n{nombre} ({ch}) orden {ang.min():.0f}-{ang.max():.0f}°: {pend:+.3f} cuentas/° | "
          f"no linealidad RMS {info['error_lineal_rms_grados']}° (máx {info['error_lineal_max_grados']}° en {ang[peor]:.0f}°) | "
          f"histéresis media {info['histeresis_media_grados']}° (máx {info['histeresis_max_grados']}°)")
    print("   pendiente por tramos:", tramos)
(HERE / "barrido_rango/modelo_rango.json").write_text(json.dumps(modelo, indent=2, ensure_ascii=False))
