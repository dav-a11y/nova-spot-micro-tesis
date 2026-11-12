#!/usr/bin/env python3
"""Reidentifica el actuador real a partir de los registros del modo `@`
(registros_robot/*.csv): retardo, ganancia y límites alcanzados por F2, F4, T2.
Escribe actuadores_reales_v2.json a partir de actuadores_reales.json."""
import csv, glob, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
CPG = 2.45
SENS = {"front_left_femur_joint": (5, "C5"), "rear_left_femur_joint": (7, "C6"),
        "front_left_tibia_joint": (9, "C9")}
rutas = sys.argv[1:] or sorted(glob.glob(str(HERE / "registros_robot/*.csv")))
datos = {j: ([], []) for j in SENS}
periodos = []
for ruta in rutas:
    rows = list(csv.DictReader(open(ruta)))
    t = np.array([float(r["t"]) for r in rows]); periodos.append(np.diff(t).mean())
    for j, (oi, ch) in SENS.items():
        o = np.array([float(r[f"orden_{oi}"]) for r in rows])
        a = np.array([float(r[ch]) for r in rows])
        datos[j][0].append(o); datos[j][1].append(o[0] - (a - a[0]) / CPG)
periodo = float(np.mean(periodos))
base = json.loads((HERE / "actuadores_reales.json").read_text())
base["periodo_control_s"] = round(periodo, 4)
base["fuente_v2"] = [Path(r).name for r in rutas]
retardos = []
for j in SENS:
    o = np.concatenate(datos[j][0]); m = np.concatenate(datos[j][1])
    r, lag = max(((np.corrcoef(o[:len(o)-l], m[l:])[0, 1], l) for l in range(8)), key=lambda x: x[0])
    oo, mm = o[:len(o)-lag], m[lag:]
    dentro = (mm > np.percentile(mm, 3)) & (mm < np.percentile(mm, 97))
    gan = float(np.polyfit(oo[dentro], mm[dentro], 1)[0])
    lim = (float(np.percentile(m, 1)), float(np.percentile(m, 99)))
    retardos.append(lag * periodo)
    base["articulaciones"][j].update(r=round(float(r), 3), retardo_s=round(lag * periodo, 3),
                                    ganancia=round(gan, 3), fiable=True,
                                    rango_servo_alcanzado=[round(lim[0], 1), round(lim[1], 1)])
    print(f"{base['articulaciones'][j]['nombre']:8s} r={r:+.3f} retardo={lag*periodo*1000:.0f} ms "
          f"ganancia={gan:.3f} rango alcanzado {lim[0]:.1f}-{lim[1]:.1f}°")
base["retardo_s"] = round(float(np.median(retardos)), 3)
fiables = [v["ganancia"] for v in base["articulaciones"].values() if v["fiable"]]
base["ganancia"] = round(float(np.median(fiables)), 3)
(HERE / "actuadores_reales_v2.json").write_text(json.dumps(base, indent=2, ensure_ascii=False))
print(f"periodo {periodo*1000:.1f} ms, retardo {base['retardo_s']*1000:.0f} ms, ganancia {base['ganancia']}")
