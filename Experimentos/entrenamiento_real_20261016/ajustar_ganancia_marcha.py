#!/usr/bin/env python3
"""Ganancia del actuador por marcha a partir de caminatas del robot suspendido (5-nov).

En el robot colgado la forma del movimiento coincide con la simulación (r≈0,9-1,0) pero la amplitud no: las marchas
rápidas (carrera, galope; ciclo 0,8 s) se mueven hasta 1,8× lo simulado. Para cada marcha se toma la amplitud relativa
A_j = recorrido robot / recorrido simulación de comparacion_sim_real.json (articulaciones con r ≥ 0,8) y se escribe un
modelo del actuador con la ganancia multiplicada por A:
  --modo articulacion: una ganancia por articulación medida; las no medidas, la mediana de la marcha.
  --modo marcha: la mediana de la marcha para todas las articulaciones.
Uso: ajustar_ganancia_marcha.py --modo marcha --nombre paso caminata1 [caminata2 ...] → actuadores_<nombre>_<modo>.json
"""
import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PIERNAS = ["front_left_femur_joint", "front_right_femur_joint", "rear_left_femur_joint", "rear_right_femur_joint",
           "front_left_tibia_joint", "front_right_tibia_joint", "rear_left_tibia_joint", "rear_right_tibia_joint"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caminatas", nargs="+", type=Path)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--modo", choices=("articulacion", "marcha"), default="marcha")
    ap.add_argument("--base", type=Path, default=HERE / "actuadores_ciclo2.json")
    ap.add_argument("--r-min", type=float, default=0.8)
    a = ap.parse_args()
    medidas = {}
    for c in a.caminatas:
        for n, v in json.loads((c / "comparacion_sim_real.json").read_text())["articulaciones"].items():
            if v["r"] >= a.r_min and v["amplitud"] > 0:
                medidas.setdefault(n, []).append(v["amplitud"])
    A = {n: float(np.exp(np.mean(np.log(x)))) for n, x in medidas.items()}       # media geométrica entre tomas
    mediana = float(np.median(list(A.values())))
    act = json.loads(a.base.read_text())
    g0 = act.get("ganancia", 1.0)
    for n in PIERNAS:
        art = act["articulaciones"].setdefault(n, {"nombre": n})
        factor = A.get(n, mediana) if a.modo == "articulacion" else mediana
        art["ganancia"] = round(float(np.clip(art.get("ganancia", g0) * factor, 0.5, 2.0)), 3)
    act["ganancia_marcha"] = dict(fecha="2026-11-05", modo=a.modo, caminatas=[c.name for c in a.caminatas],
                                  amplitud_medida={n: round(v, 3) for n, v in A.items()}, mediana=round(mediana, 3))
    salida = HERE / f"actuadores_{a.nombre}_{a.modo}.json"
    salida.write_text(json.dumps(act, indent=2, ensure_ascii=False))
    print(f"{salida.name}: mediana {mediana:.2f}; " + ", ".join(f"{n.replace('_joint', '')} {act['articulaciones'][n]['ganancia']}"
                                                         for n in PIERNAS))


if __name__ == "__main__":
    main()
