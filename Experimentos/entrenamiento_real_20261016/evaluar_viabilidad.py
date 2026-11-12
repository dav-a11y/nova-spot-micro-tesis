#!/usr/bin/env python3
"""Viabilidad de políticas PPO en MuJoCo (27-oct): % de episodios en que la política funciona.

Cada política se prueba en N episodios (semillas 1001… nunca usadas al entrenar ni al seleccionar) con
aleatorización de dominio y del actuador (retardo, ganancia, desfase de sensores, masas y fricción),
con el actuador medido en el robot. La marcha nominal se evalúa en las mismas semillas y cada episodio
se compara con su par. Un episodio es viable si:
  1. el robot no cae;
  2. avanza al menos el 90 % de lo que avanza la nominal en esa semilla;
  3. se desvía menos que la nominal o menos de 0,5 m;
  4. su inclinación máxima no pasa de 15°.
Viabilidad = episodios viables / N (en %).

Uso: evaluar_viabilidad.py --carpeta ppo_v18_carrera [--top 5] [--episodios 20]
     (toma las mejores copias de seleccion_<marcha>.csv; la selección debe haberse hecho antes)
     evaluar_viabilidad.py --politica ppo_v10_robot/<copia>/policy.zip
Escribe viabilidad_<carpeta>.csv y una línea por copia.
"""
import argparse
import csv
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

AVANCE_MIN, DERIVA_MAX, INCLINACION_MAX = 0.9, 0.5, 15.0


def marcha_de(ruta):
    """Parámetros de la marcha desde la metadata de la copia o de su campaña."""
    p = Path(ruta)
    for meta in (p.with_name("metadata.json"), p.parents[1] / "metadata.json" if p.parent.name == "intermedias" else None):
        if meta and meta.exists():
            return json.loads(meta.read_text())["marcha"]
    return json.loads(sorted((p.parents[2] if p.parent.name == "intermedias" else p.parents[1])
                             .glob("semilla_*/metadata.json"))[0].read_text())["marcha"]


def episodio(trabajo):
    import torch
    torch.set_num_threads(1)
    from stable_baselines3 import PPO
    import entrenar_ppo_real as E
    import seleccionar_copias as S
    ruta, m, ciclos, semilla, ruta_act = trabajo
    E.MARCHA = m["tipo"]
    E.PASO_CICLO_S, E.TROTE_CICLO_S = m.get("ciclo_paso_s", 2.0), m.get("ciclo_trote_s", 1.0)
    E.FEMUR_AMP_DEG, E.TIBIA_AMP_DEG, E.FASE_MOV_S = m["femur_deg"], m["tibia_deg"], m.get("fase_s", 0.5)
    E.APERTURA_DEG, E.COXA_AMP_DEG = m.get("apertura_deg", 0.0), m.get("coxa_deg", 0.0)
    E.NovaRealEnv.pesos = dict(avance=10.0, actitud=30.0, lateral=20.0, giro=10.0)
    E.SENSADAS, E.SIN_RESIDUAL = E.SENSADAS_COMPLETO, E.SIN_RESIDUAL_COMPLETO
    E.ALEATORIZAR = True
    actuador = json.loads(Path(ruta_act).read_text())
    env = E.NovaRealEnv(actuador, seed=semilla, control_dt=0.03, episode_cycles=ciclos)
    if actuador.get("retardo_pasos_rango"):
        env.rango_retardo = tuple(actuador["retardo_pasos_rango"])
    modelo = PPO.load(ruta, device="cpu") if ruta != "nominal" else None
    return ruta, semilla, S.episodio_completo(E, env, modelo, semilla)


def ciclos_para(m):
    ciclo = {"paso": m.get("ciclo_paso_s", 2.0), "gateo": 4 * (m.get("fase_s", 0.5) + 0.15)}.get(
        m["tipo"], m.get("ciclo_trote_s", 1.0))
    return max(8, round(20.0 / ciclo))           # unos 20 s de marcha por episodio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", type=Path)
    ap.add_argument("--politica", type=Path, action="append", default=[])
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--episodios", type=int, default=20)
    ap.add_argument("--procesos", type=int, default=10)
    # 5-nov: modelo del actuador de la evaluación (v32: ganancia ajustada por marcha); nominal y copias con el mismo.
    ap.add_argument("--actuador", type=Path, default=HERE / "actuadores_ciclo2.json")
    a = ap.parse_args()
    rutas = [str(p) for p in a.politica]
    if a.carpeta:
        m0 = marcha_de(next(a.carpeta.glob("semilla_*/policy.zip")))
        sel = HERE / f"seleccion_{m0['tipo']}.csv"
        filas = [f for f in csv.DictReader(sel.open()) if f["copia"].startswith(str(a.carpeta)) or
                 f"/{a.carpeta.name}/" in f["copia"]]
        rutas += [f["copia"] for f in filas[:a.top]]
    if not rutas:
        sys.exit("Sin políticas: indica --politica o --carpeta con su selección hecha")
    m = marcha_de(rutas[0])
    ciclos = ciclos_para(m)
    semillas = list(range(1001, 1001 + a.episodios))
    trabajos = [(r, m, ciclos, s, str(a.actuador)) for r in ["nominal"] + rutas for s in semillas]
    with Pool(a.procesos) as pool:
        res = pool.map(episodio, trabajos)
    por = {}
    for ruta, s, r in res:
        por.setdefault(ruta, {})[s] = r
    nom = por.pop("nominal")
    salida = []
    for ruta, eps in por.items():
        ok = []
        for s, r in eps.items():
            n = nom[s]
            viable = (not r["caida"] and r["avance_m"] >= AVANCE_MIN * n["avance_m"]
                      and (r["deriva_m"] <= DERIVA_MAX or r["deriva_m"] <= n["deriva_m"])
                      and r["inclinacion_max_deg"] <= INCLINACION_MAX)
            ok.append(viable)
        v = 100.0 * np.mean(ok)
        f = dict(copia=ruta, marcha=m["tipo"], viabilidad=round(v, 1), episodios=len(ok),
                 avance_m=round(np.mean([r["avance_m"] for r in eps.values()]), 3),
                 avance_nominal_m=round(np.mean([r["avance_m"] for r in nom.values()]), 3),
                 deriva_m=round(np.mean([r["deriva_m"] for r in eps.values()]), 3),
                 deriva_nominal_m=round(np.mean([r["deriva_m"] for r in nom.values()]), 3),
                 caidas=sum(r["caida"] for r in eps.values()), caidas_nominal=sum(r["caida"] for r in nom.values()),
                 inclinacion_max_deg=round(max(r["inclinacion_max_deg"] for r in eps.values()), 2))
        salida.append(f)
        print(f"{v:5.1f} % viable | {ruta} | avance {f['avance_m']:.2f} (nominal {f['avance_nominal_m']:.2f}) m, "
              f"deriva {f['deriva_m']:.2f} (nominal {f['deriva_nominal_m']:.2f}) m, caídas {f['caidas']}/{len(ok)} "
              f"(nominal {f['caidas_nominal']}), incl.máx {f['inclinacion_max_deg']}°", flush=True)
    nombre = a.carpeta.name if a.carpeta else "politicas"
    with (HERE / f"viabilidad_{nombre}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(salida[0])); w.writeheader(); w.writerows(salida)


if __name__ == "__main__":
    main()
