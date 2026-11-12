#!/usr/bin/env python3
"""Figuras de la fase física para la tesis (22-oct-2026).

1. Figures/Resultados/ppo_curvas_semillas.png: recompensa media de entrenamiento frente a los
   pasos, una línea por semilla, en tres campañas (gateo v14, trote v15, primer trote). Las
   campañas del ciclo no se dibujan: sus cuatro semillas dieron ejecuciones idénticas (22-oct).
2. Figures/Resultados/ppo_ciclo_robot.png: puntuación en el robot (grados, menor es mejor) de la
   marcha nominal y las políticas PPO en cada vuelta del ciclo de mejora, gateo y trote.

Datos: Experimentos/entrenamiento_real_20261016/<campaña>/semilla_*/training_trace.csv y
Experimentos/camaras/repetibilidad_ciclo*.csv + grabaciones/ciclos.csv (vuelta 3, una repetición).
Colores: paleta categórica validada (azul, naranja, verde agua, amarillo, magenta, verde, violeta).
Uso: python3 generar_figuras_ppo_fisico.py
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parent / "Experimentos"
ENT = EXP / "entrenamiento_real_20261016"
CAM = EXP / "camaras"
SALIDA = AQUI / "Figures" / "Resultados"
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({"font.size": 9, "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA, "xtick.color": TINTA2,
                     "ytick.color": TINTA2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "font.family": "DejaVu Sans"})


def traza(carpeta):
    datos = {}
    for f in sorted((ENT / carpeta).glob("semilla_*/training_trace.csv")):
        xs, ys = [], []
        for linea in f.read_text().splitlines():
            linea = linea.strip()
            if linea.startswith("{"):
                d = json.loads(linea)
                xs.append(d["timesteps"] / 1e6); ys.append(d["mean_reward"])
        if xs:
            datos[int(f.parent.name.split("_")[1])] = (np.array(xs), np.array(ys))
    return datos


def suavizar(y, n=15):
    if len(y) < n:
        return y
    k = np.ones(n) / n
    return np.convolve(np.pad(y, (n // 2, n - 1 - n // 2), mode="edge"), k, mode="valid")


def figura_curvas():
    campanas = [("ppo_v14_gateo", "Gateo v14 (5 semillas)"), ("ppo_v15_trote", "Trote v15 (7 semillas)"),
                ("ppo_trote", "Trote inicial (8 semillas)")]
    fig, ejes = plt.subplots(1, 3, figsize=(10.5, 3.3))
    for eje, (carpeta, titulo) in zip(ejes, campanas):
        for i, (semilla, (x, y)) in enumerate(sorted(traza(carpeta).items())):
            eje.plot(x, suavizar(y), color=COLORES[i % len(COLORES)], lw=1.6, label=f"{semilla}")
        eje.set_title(titulo, color=TINTA, fontsize=9.5, loc="left")
        eje.set_xlabel("Pasos de entrenamiento (millones)")
        eje.grid(True, color=REJILLA, lw=0.6); eje.set_axisbelow(True)
        eje.legend(title="Semilla", fontsize=7, title_fontsize=7, frameon=False, loc="lower right")
    ejes[0].set_ylabel("Recompensa media por episodio")
    fig.tight_layout()
    fig.savefig(SALIDA / "ppo_curvas_semillas.png", dpi=200)
    plt.close(fig)


def puntuaciones_ciclo():
    """{vuelta: {condición: puntuación}} con la misma agregación que analizar_repetibilidad.py."""
    sys.path.insert(0, str(CAM))
    import analizar_repetibilidad as A
    pat = re.compile(r"rep_ciclo(\d)_(.+)_r(\d+)$")
    d = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list))))
    for f in csv.DictReader((CAM / "grabaciones" / "ciclos.csv").open()):
        m = pat.match(f["caminata"])
        if m and f["articulacion"] in A.PATAS + A.COXAS:
            d[int(m.group(1))][m.group(2)][int(m.group(3))][f["articulacion"]].append(float(f["error_rms"]))
    res = {}
    for vuelta, conds in d.items():
        res[vuelta] = {}
        for cond, reps in conds.items():
            arts = collections.defaultdict(list)
            for arts_rep in reps.values():
                for art, v in arts_rep.items():
                    arts[art].append(np.mean(v))
            res[vuelta][cond] = (float(np.mean([np.mean(v) for v in arts.values()])), len(reps))
    return res


def figura_ciclo():
    p = puntuaciones_ciclo()
    paneles = [("Gateo", [("gateo_base", "Nominal"), ("gateo_ppo1", "PPO v14"), ("gateo_ppo2", "PPO nueva")]),
               ("Trote", [("trote_base", "Nominal"), ("trote_ppo1", "PPO v15")])]
    fig, ejes = plt.subplots(1, 2, figsize=(10.5, 3.4), gridspec_kw={"width_ratios": [3, 2]})
    for eje, (titulo, conds) in zip(ejes, paneles):
        vueltas = [v for v in sorted(p) if any(c in p[v] for c, _ in conds)]
        ancho = 0.8 / len(conds)
        for j, (cond, etiqueta) in enumerate(conds):
            xs, ys, ns = [], [], []
            for i, v in enumerate(vueltas):
                if cond in p[v]:
                    xs.append(i + (j - (len(conds) - 1) / 2) * ancho); ys.append(p[v][cond][0]); ns.append(p[v][cond][1])
            barras = eje.bar(xs, ys, width=ancho - 0.04, color=COLORES[j], label=etiqueta, edgecolor="white", linewidth=1)
            for b, y, n in zip(barras, ys, ns):
                eje.text(b.get_x() + b.get_width() / 2, y + 0.03, f"{y:.2f}" + ("*" if n == 1 else ""),
                         ha="center", va="bottom", fontsize=7.5, color=TINTA)
        eje.set_xticks(range(len(vueltas)), [f"Vuelta {v}" for v in vueltas])
        eje.set_title(titulo, color=TINTA, fontsize=9.5, loc="left")
        eje.grid(True, axis="y", color=REJILLA, lw=0.6); eje.set_axisbelow(True)
        eje.legend(frameon=False, fontsize=7.5, loc="upper right", ncol=len(conds))
        eje.set_ylim(0, 2.9)
    ejes[0].set_ylabel("Puntuación en el robot (°, menor es mejor)")
    fig.text(0.01, 0.005, "* una sola repetición válida", fontsize=7, color=TINTA2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(SALIDA / "ppo_ciclo_robot.png", dpi=200)
    plt.close(fig)
    return p


if __name__ == "__main__":
    figura_curvas()
    p = figura_ciclo()
    for v in sorted(p):
        print(v, {c: round(x, 2) for c, (x, n) in p[v].items()})
