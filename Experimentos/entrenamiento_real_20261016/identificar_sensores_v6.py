#!/usr/bin/env python3
"""Identifica el sensor de cada fémur y tibia a partir de una caminata registrada con
ejecutar_politica_robot.py (modo @ con todos los sensores, 19-oct).

Para cada articulación ajusta  Δsensor(t) = k · Δorden(t − retardo)  en grados de servo
(sensor en cuentas o en grados de encoder) y elige el retardo con mayor correlación.
Guarda k en sensores_robot.json (lo usa el ejecutor) y escribe actuadores_reales_v5.json
con el retardo y la ganancia de cada articulación (ganancia = |k| / escala estática
del potenciómetro; en los encoders se toma 1,0 porque su escala solo se conoce así).
Los potenciómetros comparten un desplazamiento de la tierra con la corriente de los
servos (hasta 30 cuentas); se resta la variación de C0 (coxa 1, siempre quieta).

Uso: identificar_sensores_v6.py registros_robot/identificacion_v6_r2_20261019.csv
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# articulación del modelo: (columna de orden, campo del sensor)
ARTICULACIONES = {
    "front_right_femur_joint": ("orden_4", "C8"),
    "front_left_femur_joint": ("orden_5", "C5"),
    "rear_right_femur_joint": ("orden_6", "C9"),
    "rear_left_femur_joint": ("orden_7", "C6"),
    "front_right_tibia_joint": ("orden_8", "ENC_T1"),
    "front_left_tibia_joint": ("orden_9", "ENC_T2"),
    "rear_right_tibia_joint": ("orden_10", "C11"),
    "rear_left_tibia_joint": ("orden_11", "C10"),
}
REFERENCIA = "C0"           # potenciómetro de la coxa 1: solo ve el desplazamiento común
ESCALA_POT = 2.52
# 19-oct: encoders de respaldo (se usan si falla el sensor principal).
RESPALDOS = {"front_right_femur_joint": ("orden_4", "ENC_F1"), "rear_left_femur_joint": ("orden_7", "ENC_F4")}           # cuentas/° del barrido de rango del 16-oct
DT_ESPERADO = 0.03


def main():
    ruta = Path(sys.argv[1])
    filas = list(csv.DictReader(ruta.open()))
    t = np.array([float(f["t"]) for f in filas])
    dt = float(np.median(np.diff(t)))
    rampa = round(1.0 / DT_ESPERADO)
    cal = json.loads((HERE / "sensores_robot.json").read_text())
    act = json.loads((HERE / "actuadores_reales_v4.json").read_text())
    act["sesiones"] = [ruta.name]
    cal["compensar_con"] = REFERENCIA
    c0 = np.array([float(f[REFERENCIA]) for f in filas])[rampa:]
    resumen = {}
    for nombre, (col, campo) in ARTICULACIONES.items():
        o = np.array([float(f[col]) for f in filas])[rampa:]
        s = np.array([float(f[campo]) for f in filas])[rampa:]
        ok = s >= 0
        if ok.sum() < 50:
            print(f"{nombre:26s} {campo:7s} sin lecturas válidas: se conserva su calibración anterior")
            continue
        if not campo.startswith("ENC"):
            s = s - (c0 - c0[0])
        else:
            s = np.degrees(np.unwrap(np.radians(s * 360.0 / 4096.0)))
        o, s = o - o[0], s - s[ok][0]
        mejor = None
        for L in range(0, 9):
            oo, ss, kk = o[: len(o) - L], s[L:], ok[L:]
            oo, ss = oo[kk] - oo[kk].mean(), ss[kk] - ss[kk].mean()
            if oo.std() < 1e-6:
                continue
            r = float(np.corrcoef(oo, ss)[0, 1])
            k = float(oo @ ss / (oo @ oo))
            if mejor is None or abs(r) > abs(mejor[1]):
                mejor = (L, r, k, float(np.std(ss - k * oo)))
        L, r, k, res = mejor
        es_pot = not campo.startswith("ENC")
        ganancia = abs(k) / ESCALA_POT if es_pot else 1.0
        resumen[nombre] = dict(campo=campo, k=round(k, 4), r=round(r, 3), retardo_s=round(L * dt, 3),
                               residuo_grados=round(res / abs(k), 2), ganancia=round(ganancia, 3),
                               recorrido_orden=round(float(np.ptp(o)), 1))
        print(f"{nombre:26s} {campo:7s} k={k:+.3f} r={r:+.3f} retardo={L * dt * 1000:.0f} ms "
              f"ganancia={ganancia:.2f} residuo={res / abs(k):.2f}° recorrido={np.ptp(o):.0f}°")
        fiable = abs(r) >= 0.9
        if fiable:
            cal[nombre] = {"campo": campo, "k": round(k, 4)}
        datos = act["articulaciones"].get(nombre, {})
        datos.update(nombre=nombre, r=round(r, 3), retardo_s=round(L * dt, 3), fiable=fiable,
                     ganancia=round(min(1.1, ganancia), 3), sensor=campo, muestras=int(ok.sum()))
        act["articulaciones"][nombre] = datos
    for nombre, (col, campo) in RESPALDOS.items():
        if campo not in filas[0]:
            continue
        o = np.array([float(f[col]) for f in filas])[rampa:]
        s = np.array([float(f[campo]) for f in filas])[rampa:]
        ok = s >= 0
        if ok.sum() < 50:
            print(f"respaldo {campo} de {nombre}: sin lecturas suficientes ({int(ok.sum())})")
            continue
        s = np.degrees(np.unwrap(np.radians(np.where(ok, s, np.interp(np.arange(len(s)), np.flatnonzero(ok), s[ok])) * 360.0 / 4096.0)))
        L = 3
        oo, ss, kk = o[:len(o) - L] - o[0], s[L:] - s[L], ok[L:]
        oo, ss = oo[kk] - oo[kk].mean(), ss[kk] - ss[kk].mean()
        r, k = float(np.corrcoef(oo, ss)[0, 1]), float(oo @ ss / (oo @ oo))
        print(f"respaldo {nombre:26s} {campo:7s} k={k:+.3f} r={r:+.3f} perdidas={int((~ok).sum())}")
        if abs(r) >= 0.9 and nombre in cal:
            cal[nombre]["respaldo"] = {"campo": campo, "k": round(k, 4)}
    retardos = [v["retardo_s"] for v in resumen.values() if abs(v["r"]) >= 0.9]
    act["retardo_s"] = float(np.median(retardos)) if retardos else act["retardo_s"]
    act["periodo_control_s"] = dt
    act["tibia1_con_pwm"] = True
    (HERE / "sensores_robot.json").write_text(json.dumps(cal, indent=2, ensure_ascii=False))
    (HERE / "actuadores_reales_v6.json").write_text(json.dumps(act, indent=2, ensure_ascii=False))
    (HERE / "identificacion_sensores_v6.json").write_text(json.dumps(dict(registro=ruta.name, periodo_s=dt,
                                                                          articulaciones=resumen), indent=2, ensure_ascii=False))
    print(f"periodo {dt * 1000:.1f} ms | retardo mediano {act['retardo_s'] * 1000:.0f} ms")


if __name__ == "__main__":
    main()
