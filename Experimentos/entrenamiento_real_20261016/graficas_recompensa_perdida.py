#!/usr/bin/env python3
"""Gráficas de recompensa y de pérdidas del entrenamiento PPO (29-oct).

1. recompensa_5_marchas.png: recompensa media por episodio durante el entrenamiento, un panel por marcha,
   una línea por semilla de la campaña que dio la política elegida (resaltada la semilla elegida).
2. perdidas_<carpeta>.png: pérdidas de PPO por actualización (progress.csv de entrenar_ppo_real.py
   --registrar-perdidas): recompensa, pérdida total, del crítico, de la política, entropía, KL,
   fracción recortada y varianza explicada.

Uso: graficas_recompensa_perdida.py [--perdidas ppo_v29_trote_perdidas] [--salida graficas]
"""
import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
# Paleta categórica validada (skill dataviz, modo claro): azul, naranja, aguamarina, amarillo, magenta.
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
GRIS = "#b9b8b0"
TINTA, TINTA2 = "#1f1f1d", "#5f5e58"

# marcha: (campaña, semilla elegida, pasos de la copia elegida, viabilidad)
ELEGIDAS = {
    "Paso": ("ppo_v24_paso", 4109, 200_000, "100 %"),
    "Trote": ("ppo_v24_trote", 4209, 200_000, "100 %"),
    "Carrera": ("ppo_v24_carrera", 4309, 200_000, "100 %"),
    "Gateo": ("ppo_v27_gateo", 7013, 4_100_064, "100 %"),
    "Galope": ("ppo_v28_galope", 8417, 175_000, "90 %"),
}


def estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#c9c8c0")
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(True, color="#ecebe6", linewidth=0.8)
    ax.set_axisbelow(True)


def suavizar(y, n=15):
    if len(y) < n:
        return np.asarray(y)
    k = np.ones(n) / n
    return np.convolve(np.pad(y, (n // 2, n - 1 - n // 2), mode="edge"), k, mode="valid")


def traza(carpeta):
    pts = {}
    for nombre in ("training_trace_parte1.csv", "training_trace.csv"):
        f = carpeta / nombre
        if f.exists():
            for linea in f.read_text().splitlines():
                try:
                    d = json.loads(linea)
                    pts[int(d["timesteps"])] = float(d["mean_reward"])
                except (ValueError, KeyError):
                    pass
    x = np.array(sorted(pts))
    return x, np.array([pts[k] for k in x])


def crudo_y_suave(ax, x, y, color, n):
    """Curva cruda (clara, con ruido) y encima su media móvil (oscura, la tendencia)."""
    ax.plot(x, y, color=color, linewidth=0.8, alpha=0.30)
    ys = suavizar(y, n)
    ax.plot(x, ys, color=color, linewidth=2.2)
    return ys


def recompensa_5_marchas(salida):
    fig, axs = plt.subplots(1, 5, figsize=(17, 4.1))
    for ax, (marcha, (camp, elegida, pasos, viab)) in zip(axs, ELEGIDAS.items()):
        estilo(ax)
        x, y = traza(HERE / camp / f"semilla_{elegida}")
        ys = crudo_y_suave(ax, x / 1e6, y, COLORES[0], 25)
        i = int(np.argmin(np.abs(x - pasos)))
        ax.plot(x[i] / 1e6, ys[i], "o", markersize=8, color=COLORES[1], markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(f"copia elegida\n{pasos / 1e6:.2f} M · {viab}", (x[i] / 1e6, ys[i]), xytext=(10, -28),
                    textcoords="offset points", fontsize=8.5, color=TINTA)
        ax.set_title(f"{marcha} ({camp.split('_')[1]}, s{elegida})", loc="left", fontsize=11, color=TINTA)
        ax.set_xlabel("Pasos de entrenamiento (millones)", fontsize=9, color=TINTA2)
        ax.set_ylabel("Recompensa media por episodio", fontsize=9, color=TINTA2)
    fig.legend(handles=[plt.Line2D([], [], color=COLORES[0], linewidth=0.8, alpha=0.35, label="Valor crudo (con ruido)"),
                        plt.Line2D([], [], color=COLORES[0], linewidth=2.2, label="Tendencia (media móvil)"),
                        plt.Line2D([], [], marker="o", color=COLORES[1], linestyle="", label="Copia elegida")],
               loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.01, 0.99, "Cada panel tiene su propia escala: los pesos de la recompensa cambian entre marchas. "
             "Gateo y galope continúan entrenamientos anteriores, por eso no empiezan en 0.",
             fontsize=8.5, color=TINTA2, va="top")
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    fig.savefig(salida / "recompensa_5_marchas.png", dpi=160, facecolor="#fcfcfb")
    plt.close(fig)


PANELES = [
    ("rollout/ep_rew_mean", "Recompensa por episodio", "Sube: la red camina mejor", "Recompensa (puntos)"),
    ("train/loss", "Pérdida total ℒ", "Lo que minimiza PPO", "Pérdida (escala log)"),
    ("train/value_loss", "Pérdida del crítico", "Error al predecir V(s)", "Error² (escala log)"),
    ("train/policy_gradient_loss", "Pérdida de la política", "Término del objetivo recortado", "Pérdida"),
    ("train/entropy_loss", "Pérdida de entropía", "Más negativa = más exploración", "−Entropía"),
    ("train/approx_kl", "Divergencia KL aproximada", "Freno en 0,03", "KL (nats)"),
    ("train/clip_fraction", "Fracción recortada", "Muestras frenadas por ε = 0,2", "Fracción (0 a 1)"),
    ("train/explained_variance", "Varianza explicada", "1 = el crítico acierta", "Varianza explicada"),
]


def episodios(monitor):
    """Recompensa cruda de cada episodio y pasos acumulados al terminarlo (monitor.csv de SB3)."""
    with monitor.open() as f:
        next(f)
        rows = list(csv.DictReader(f))
    r = np.array([float(x["r"]) for x in rows])
    pasos = np.cumsum([int(x["l"]) for x in rows])
    return pasos, r


def semilla_y_marcha(carpeta):
    d = sorted(carpeta.glob("semilla_*"))[0]
    meta = d / "metadata.json"
    marcha = json.loads(meta.read_text())["marcha"]["tipo"] if meta.exists() else carpeta.name.split("_")[2]
    return d.name.split("_")[1], ("de la " if marcha == "carrera" else "del ") + marcha


def recompensa_cruda(carpeta, salida, semilla=None):
    s0, marcha = semilla_y_marcha(carpeta)
    semilla = semilla or s0
    pasos, r = episodios(carpeta / f"semilla_{semilla}" / "monitor.monitor.csv")
    fig, ax = plt.subplots(figsize=(11, 5.2))
    estilo(ax)
    ys = crudo_y_suave(ax, pasos / 1e6, r, COLORES[0], 50)
    # Unos pocos episodios muy malos al inicio aplastan la escala: se recorta el eje al percentil 0,5.
    piso = min(np.percentile(r, 0.5), ys.min())
    fuera = int((r < piso).sum())
    if fuera:
        rango = r.max() - piso
        ax.set_ylim(piso - 0.05 * rango, r.max() + 0.05 * rango)
        ax.text(0.01, 0.02, f"Eje recortado: {fuera} episodios iniciales quedan por debajo (mínimo {r.min():.0f})",
                transform=ax.transAxes, fontsize=8.5, color=TINTA2)
    ax.set_title(f"Recompensa por episodio durante el entrenamiento {marcha} (semilla {semilla}, desde cero)",
                 loc="left", fontsize=12, color=TINTA)
    ax.set_xlabel("Pasos de entrenamiento (millones)", fontsize=10, color=TINTA2)
    ax.set_ylabel("Recompensa del episodio (puntos)", fontsize=10, color=TINTA2)
    ax.legend(handles=[plt.Line2D([], [], color=COLORES[0], linewidth=0.8, alpha=0.35, label=f"Cada episodio ({len(r)} episodios)"),
                       plt.Line2D([], [], color=COLORES[0], linewidth=2.2, label="Tendencia (media móvil de 50 episodios)")],
              frameon=False, fontsize=9.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(salida / f"recompensa_{carpeta.name}.png", dpi=160, facecolor="#fcfcfb")
    plt.close(fig)


def perdidas(carpeta, salida, semilla=None):
    s0, marcha = semilla_y_marcha(carpeta)
    semilla = semilla or s0
    filas = {}
    for p in sorted(carpeta.glob("semilla_*/progress.csv")):
        with p.open() as f:
            filas[p.parent.name.split("_")[1]] = list(csv.DictReader(f))
    fig, axs = plt.subplots(2, 4, figsize=(17, 7.2))
    for ax, (col, titulo, nota, eje_y) in zip(axs.flat, PANELES):
        estilo(ax)
        mon = carpeta / f"semilla_{semilla}" / "monitor.monitor.csv"
        if col == "rollout/ep_rew_mean" and mon.exists():
            x, y = episodios(mon)
            crudo_y_suave(ax, x / 1e6, y, COLORES[0], 50)
        else:
            rows = filas[semilla]
            pares = [(float(r["time/total_timesteps"]), float(r[col])) for r in rows if r.get(col) not in ("", None)]
            if pares:
                x, y = np.array(pares).T
                crudo_y_suave(ax, x / 1e6, y, COLORES[0], 15)
        if col == "train/approx_kl":
            ax.axhline(0.03, color=TINTA2, linewidth=1, linestyle="--")
            ax.annotate("objetivo KL 0,03", (0.02, 0.03), xycoords=("axes fraction", "data"), xytext=(0, -12),
                        textcoords="offset points", fontsize=8, color=TINTA2)
        if col in ("train/loss", "train/value_loss"):
            ax.set_yscale("symlog", linthresh=1)
        ax.set_title(titulo, loc="left", fontsize=11, color=TINTA, pad=20)
        ax.text(0, 1.02, nota, transform=ax.transAxes, fontsize=8.5, color=TINTA2, va="bottom")
        ax.set_xlabel("Pasos de entrenamiento (millones)", fontsize=9, color=TINTA2)
        ax.set_ylabel(eje_y, fontsize=9, color=TINTA2)
    fig.legend(handles=[plt.Line2D([], [], color=COLORES[0], linewidth=0.8, alpha=0.35, label="Valor crudo (cada episodio o actualización, con ruido)"),
                        plt.Line2D([], [], color=COLORES[0], linewidth=2.2, label="Tendencia (media móvil)")],
               loc="lower center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle(f"Pérdidas de PPO durante el entrenamiento {marcha} (semilla {semilla}, desde cero, 1 M de pasos)",
                 x=0.01, ha="left", fontsize=13, color=TINTA)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(salida / f"perdidas_{carpeta.name}.png", dpi=160, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perdidas", type=Path, nargs="*", default=[])
    ap.add_argument("--salida", type=Path, default=HERE / "graficas")
    a = ap.parse_args()
    a.salida.mkdir(exist_ok=True)
    recompensa_5_marchas(a.salida)
    for c in a.perdidas:
        perdidas(HERE / c, a.salida)
        if list((HERE / c).glob("semilla_*/monitor.monitor.csv")):
            recompensa_cruda(HERE / c, a.salida)
    print("Gráficas en", a.salida)


if __name__ == "__main__":
    main()
