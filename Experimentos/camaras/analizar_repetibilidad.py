#!/usr/bin/env python3
"""Patrones de estabilidad por marcha y repetibilidad entre repeticiones.

Lee grabaciones/catalogo.csv y ciclos.csv (catalogo_caminatas.py) y, para las caminatas
rep_<sesión>_<condición>_r<n>, calcula por condición (marcha + política):
- estabilidad dentro de cada caminata: media y tendencia por ciclo (°/min) del error de
  seguimiento y de la desviación de las coxas, y variación ciclo a ciclo (desv. estándar);
- repetibilidad entre repeticiones: media ± desviación estándar entre repeticiones y
  coeficiente de variación (CV %) de cada métrica.
Escribe repetibilidad_<sesión>.csv, repetibilidad_<sesión>.json y repetibilidad_<sesión>.png.

Uso: python3 analizar_repetibilidad.py --sesion 20261019
"""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
GRAB = AQUI / "grabaciones"
PATAS = ["femur1", "femur2", "femur3", "femur4", "tibia1", "tibia2", "tibia3", "tibia4"]
COXAS = ["coxa2", "coxa3", "coxa4"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sesion", required=True)
    a = ap.parse_args()
    patron = re.compile(rf"rep_{a.sesion}_(.+)_r(\d+)$")
    filas = [f for f in csv.DictReader((GRAB / "ciclos.csv").open()) if patron.match(f["caminata"])]
    if not filas:
        raise SystemExit("No hay caminatas del protocolo en ciclos.csv: ejecutar catalogo_caminatas.py")
    cat = {f["caminata"]: float(f["duracion_s"]) / max(1, int(f["ciclos"])) for f in csv.DictReader((GRAB / "catalogo.csv").open())}
    seg_ciclo = defaultdict(list)
    datos = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))   # cond -> rep -> art -> [valores por ciclo]
    for f in filas:
        cond, rep = patron.match(f["caminata"]).groups()
        datos[cond][int(rep)][f["articulacion"]].append(float(f["error_rms"]))
        if f["caminata"] in cat:
            seg_ciclo[cond].append(cat[f["caminata"]])
    resultado, tabla = {}, []
    for cond in sorted(datos):
        por_rep = {}
        for rep, arts in sorted(datos[cond].items()):
            m = {}
            for art, v in arts.items():
                v = np.array(v)
                k = np.arange(len(v))
                pend = float(np.polyfit(k, v, 1)[0]) if len(v) > 3 else 0.0
                m[art] = dict(media=float(v.mean()), variacion_ciclo=float(v.std()), tendencia_por_ciclo=pend,
                              ciclos=len(v))
            patas = [m[x]["media"] for x in PATAS if x in m]
            coxas = [m[x]["media"] for x in COXAS if x in m]
            m["resumen"] = dict(error_patas=float(np.mean(patas)) if patas else None,
                                coxas=float(np.mean(coxas)) if coxas else None,
                                variacion_ciclo_patas=float(np.mean([m[x]["variacion_ciclo"] for x in PATAS if x in m])),
                                tendencia_coxas=float(np.mean([m[x]["tendencia_por_ciclo"] for x in COXAS if x in m])))
            por_rep[rep] = m
        reps = sorted(por_rep)
        spc = float(np.mean(seg_ciclo[cond])) if seg_ciclo[cond] else 2.9
        res = {"segundos_por_ciclo": spc, "repeticiones": reps, "por_repeticion": {str(r): por_rep[r]["resumen"] for r in reps}, "metricas": {}}
        for art in PATAS + COXAS:
            vals = [por_rep[r][art]["media"] for r in reps if art in por_rep[r]]
            if len(vals) < 2:
                continue
            media, sd = float(np.mean(vals)), float(np.std(vals, ddof=1))
            tend = float(np.mean([por_rep[r][art]["tendencia_por_ciclo"] for r in reps if art in por_rep[r]]))
            res["metricas"][art] = dict(media=media, sd_entre_repeticiones=sd, cv_pct=100 * sd / media if media else None,
                                        tendencia_media_por_ciclo=tend, n=len(vals))
            tabla.append(dict(condicion=cond, articulacion=art, n=len(vals), media_grados=round(media, 3),
                              sd_entre_reps=round(sd, 3), cv_pct=round(100 * sd / media, 1) if media else "",
                              tendencia_grados_por_min=round(tend * 60 / spc, 4),
                              valores=" ".join(f"{x:.3f}" for x in vals)))
        resultado[cond] = res
    salida = AQUI / f"repetibilidad_{a.sesion}"
    with salida.with_suffix(".csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tabla[0])); w.writeheader(); w.writerows(tabla)
    salida.with_suffix(".json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    conds = sorted(resultado)
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    for i, cond in enumerate(conds):
        for j, art in enumerate(PATAS + COXAS):
            m = resultado[cond]["metricas"].get(art)
            if m:
                x = j + (i - len(conds) / 2) * 0.18
                ax[0 if art in PATAS else 1].errorbar(x if art in PATAS else j - 8 + (i - len(conds) / 2) * 0.18,
                                                       m["media"], yerr=m["sd_entre_repeticiones"], fmt="o",
                                                       color=f"C{i}", label=cond if j in (0, 8) else None, capsize=3)
    ax[0].set_xticks(range(8)); ax[0].set_xticklabels(PATAS, rotation=30)
    ax[0].set_ylabel("error RMS de seguimiento (°)"); ax[0].set_title("Patas: media ± sd entre repeticiones")
    ax[1].set_xticks(range(3)); ax[1].set_xticklabels(COXAS)
    ax[1].set_ylabel("desviación media de la coxa (°)"); ax[1].set_title("Coxas: media ± sd entre repeticiones")
    for x in ax:
        x.legend(fontsize=8); x.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(salida.with_suffix(".png"), dpi=90)
    for cond in conds:
        r = resultado[cond]
        print(f"\n{cond} (repeticiones {r['repeticiones']})")
        for rep, s in r["por_repeticion"].items():
            print(f"  r{rep}: error patas {s['error_patas']:.2f}°, coxas {s['coxas']:.2f}°, "
                  f"variación ciclo a ciclo {s['variacion_ciclo_patas']:.2f}°, tendencia coxas {s['tendencia_coxas'] * 60 / r['segundos_por_ciclo']:+.3f}°/min")
        cvs = [m["cv_pct"] for m in r["metricas"].values() if m["cv_pct"] is not None]
        if cvs:
            print(f"  repetibilidad: CV medio entre repeticiones {np.mean(cvs):.1f}% (máx {np.max(cvs):.1f}%)")
    print("\n->", salida.with_suffix(".csv"), salida.with_suffix(".png"))


if __name__ == "__main__":
    main()
