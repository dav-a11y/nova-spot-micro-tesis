#!/usr/bin/env python3
"""Barrido de parámetros de la caminata `b` en la simulación ajustada (actuador v3),
buscando la combinación más estable. Solo simulación."""
import csv, itertools, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E

act = json.loads((HERE / "actuadores_reales_v3.json").read_text())
SEMILLAS = [801, 802, 803, 804, 805]
filas = []
for fem, tib, fase in itertools.product((10, 15, 20), (10, 14, 18), (0.5, 0.8)):
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = fem, tib, fase
    res = []
    for s in SEMILLAS:
        env = E.NovaRealEnv(act, seed=s, control_dt=0.03)
        env.reset(seed=s)
        incl, x0, y0, caida, t = [], None, None, False, 0
        while True:
            _, _, term, trunc, info = env.step(np.zeros(12)); t += 1
            if not info["ramp_active"]:
                if x0 is None: x0, y0 = info["x"], info["y"]
                incl.append(np.hypot(info["roll"], info["pitch"]))
            if term: caida = True
            if term or trunc: break
        dur = t * 0.03
        res.append(dict(avance=info["x"] - x0, deriva=abs(info["y"] - y0), incl_max=max(incl),
                        incl_rms=float(np.sqrt(np.mean(np.square(incl)))), caida=caida,
                        velocidad=(info["x"] - x0) / dur))
    m = {k: float(np.mean([r[k] for r in res])) for k in ("avance", "deriva", "incl_max", "incl_rms", "velocidad")}
    filas.append(dict(femur_deg=fem, tibia_deg=tib, fase_s=fase, caidas=sum(r["caida"] for r in res),
                      **{k: round(v, 4) for k, v in m.items()}))
    print(filas[-1], flush=True)
with open(HERE / "barrido_estabilidad_nominal.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
ok = [f for f in filas if f["caidas"] == 0 and f["avance"] > 0.08]
ok.sort(key=lambda f: (f["incl_rms"], f["deriva"]))
print("\nMás estables con avance > 0,08 m:")
for f in ok[:5]: print(" ", f)
