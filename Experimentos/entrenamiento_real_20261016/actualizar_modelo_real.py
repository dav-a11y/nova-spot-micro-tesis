#!/usr/bin/env python3
"""Actualiza el modelo del actuador de la simulación con las caminatas reales de una vuelta (21-oct).

Para cada caminata y cada articulación con sensor válido (sensores_robot.json; si el principal
falla, su respaldo; las marcadas «sin_sensor» o caídas se omiten):
  ángulo_real = (sensor − referencia) / k                     (grados de servo)
  retardo     = desplazamiento (0-8 pasos) que mejor ajusta ángulo_real a la orden
  histéresis  = diferencia media entre subida y bajada a la misma orden (holgura)
  residuo     = error RMS que queda tras el mejor retardo (lo que el modelo no explica)
La ganancia se deja en 1: los potenciómetros se calibran contra la orden y no pueden medirla
(la cámara la confirmó ≈ 1,08 en el fémur 4).

Salida: actuadores_<nombre>.json (copia de la base con retardo, zona muerta y rango de retardo
para la aleatorización actualizados) y un resumen por articulación (brecha robot-modelo).

Uso: actualizar_modelo_real.py --nombre ciclo2 --base actuadores_reales_v5.json caminata1 caminata2 ...
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
COL = {"front_right_femur_joint": "orden_4", "front_left_femur_joint": "orden_5",
       "rear_right_femur_joint": "orden_6", "rear_left_femur_joint": "orden_7",
       "front_right_tibia_joint": "orden_8", "front_left_tibia_joint": "orden_9",
       "rear_right_tibia_joint": "orden_10", "rear_left_tibia_joint": "orden_11"}
DT = 0.033


def medir(filas, cal, nombre):
    c = cal[nombre]
    if c.get("sin_sensor"):
        return None
    for fuente in (c, c.get("respaldo")):
        if not fuente:
            continue
        s = np.array([float(f.get(fuente["campo"], -1)) for f in filas])
        ok = s >= 0
        if ok.mean() < 0.9:
            continue
        o = np.array([float(f[COL[nombre]]) for f in filas])
        s = np.interp(np.arange(len(s)), np.flatnonzero(ok), s[ok])
        if fuente["campo"].startswith("ENC"):
            s = np.degrees(np.unwrap(np.radians(s * 360.0 / 4096.0)))
        ang = (s - s[0]) / fuente["k"]
        o = o - o[0]
        if o.std() < 1.0:
            return None
        mejor = None
        for L in range(0, 9):
            a, b = o[: len(o) - L], ang[L:]
            b = b - b.mean() + a.mean()
            r = float(np.sqrt(np.mean((b - a) ** 2)))
            if mejor is None or r < mejor[1]:
                mejor = (L, r, a, b)
        L, res, a, b = mejor
        vel = np.gradient(a)
        sube, baja = vel > 0.05, vel < -0.05
        hist = 0.0
        if sube.sum() > 20 and baja.sum() > 20:
            bins = np.linspace(a.min(), a.max(), 12)
            d = []
            for lo, hi in zip(bins, bins[1:]):
                mu, md = sube & (a >= lo) & (a < hi), baja & (a >= lo) & (a < hi)
                if mu.sum() > 3 and md.sum() > 3:
                    d.append(np.mean((b - a)[md]) - np.mean((b - a)[mu]))
            hist = float(np.median(np.abs(d))) if d else 0.0
        return dict(sensor=fuente["campo"], retardo_pasos=L, residuo_grados=res, histeresis_grados=hist)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--base", default="actuadores_reales_v5.json")
    ap.add_argument("caminatas", nargs="+")
    a = ap.parse_args()
    cal = json.loads((HERE / "sensores_robot.json").read_text())
    medidas = {n: [] for n in COL}
    for c in a.caminatas:
        p = Path(c) / "caminata.csv"
        if not p.exists():
            continue
        filas = list(csv.DictReader(p.open()))[60:]
        for n in COL:
            m = medir(filas, cal, n)
            if m:
                medidas[n].append(m)
    base = json.loads((HERE / a.base).read_text())
    resumen, retardos, holguras = {}, [], []
    for n, ms in medidas.items():
        if not ms:
            resumen[n] = "sin sensor válido"
            continue
        L = float(np.median([m["retardo_pasos"] for m in ms]))
        h = float(np.median([m["histeresis_grados"] for m in ms]))
        r = float(np.median([m["residuo_grados"] for m in ms]))
        resumen[n] = dict(sensor=ms[0]["sensor"], caminatas=len(ms), retardo_ms=round(L * DT * 1000), histeresis_grados=round(h, 2),
                          residuo_grados=round(r, 2), retardo_min_ms=round(min(m["retardo_pasos"] for m in ms) * DT * 1000),
                          retardo_max_ms=round(max(m["retardo_pasos"] for m in ms) * DT * 1000))
        retardos += [m["retardo_pasos"] for m in ms]
        holguras.append(h)
        if n in base.get("articulaciones", {}):
            base["articulaciones"][n]["retardo_s"] = round(L * DT, 3)
            base["articulaciones"][n]["histeresis_grados"] = round(h, 2)
            base["articulaciones"][n]["ganancia"] = 1.0
    if retardos:
        base["retardo_s"] = round(float(np.median(retardos)) * DT, 3)
        # rango de retardo para la aleatorización: lo observado en el robot, con un paso de margen
        base["retardo_pasos_rango"] = [max(1, int(min(retardos)) - 1), int(max(retardos)) + 1]
    if holguras:
        base["zona_muerta_grados"] = round(float(np.median(holguras)) / 2, 2)
    base["ganancia"] = 1.0
    base["fuente_ciclo"] = dict(nombre=a.nombre, caminatas=[str(c) for c in a.caminatas], resumen=resumen)
    salida = HERE / f"actuadores_{a.nombre}.json"
    salida.write_text(json.dumps(base, indent=2, ensure_ascii=False))
    print(f"modelo -> {salida.name}: retardo {base.get('retardo_s')} s, rango {base.get('retardo_pasos_rango')} pasos, "
          f"zona muerta {base.get('zona_muerta_grados')}°")
    for n, v in resumen.items():
        print(f"  {n:24s} {v}")
    brecha = [v["residuo_grados"] for v in resumen.values() if isinstance(v, dict)]
    if brecha:
        print(f"brecha robot-modelo (residuo medio): {np.mean(brecha):.2f}°")


if __name__ == "__main__":
    main()
