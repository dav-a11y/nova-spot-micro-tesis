#!/usr/bin/env python3
"""Las 4 gráficas de presentación del pace v34 (recompensa frente a pasos, episodios y épocas; castigo frente a pasos),
cada una en su archivo y además juntas en un resumen. Usa el criterio de convergencia de graficas_pace_v34.py.

Con --banda 0.03 (más estricto que el 0.05 por defecto) la línea de convergencia de la 9517 cae en ~1,64 M de pasos,
justo donde está la política elegida (1600k); con 0.05 cae en ~0,96 M.

--linea PASOS_M EPISODIOS EPOCAS CASTIGO_M pone la línea a mano en cada gráfica (ignora el criterio).

Uso: graficas_presentacion_pace_v34.py [--semilla ppo_v34_pace_desde_trote:9517] [--banda 0.03] [--linea 1.1 2400 4500 1.25] --salida DIR
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import graficas_pace_v34 as g  # noqa: E402

FONDO = "#fcfcfb"
PM = "Pasos de entrenamiento (millones)"


def paneles(d):
    rp = "Recompensa del episodio (puntos)"
    return [
        ("1_recompensa_pasos", (d["pasos"], d["total"], g.AZUL, "Recompensa frente a pasos", "", PM, rp, "M de pasos", 1e6)),
        ("2_recompensa_episodios", (d["episodios"].astype(float), d["total"], g.AZUL, "Recompensa frente a episodios", "",
                                    "Episodios de entrenamiento", rp, "episodios")),
        ("3_recompensa_epocas", (d["epocas"], d["total"], g.AZUL, "Recompensa frente a épocas", "",
                                 "Épocas acumuladas", rp, "épocas")),
        ("4_castigo_pasos", (d["pasos"], d["castigo"], g.NARANJA, "Castigo total frente a pasos", "", PM,
                             "Suma de castigos del episodio (puntos)", "M de pasos", 1e6)),
    ]


def panel(ax, args, fija):
    """Panel de graficas_pace_v34; con `fija` (en las unidades del eje x) la línea va ahí en vez del criterio."""
    if fija is None:
        return g.panel(ax, *args)
    x, escala = args[0], (args[8] if len(args) > 8 else 1.0)
    original = g.convergencia
    g.convergencia = lambda *_a, **_k: (int(np.argmin(np.abs(x / escala - fija))), True)
    try:
        r = g.panel(ax, *args)
    finally:
        g.convergencia = original
    # La línea y el rótulo muestran el valor pedido, no el del episodio más cercano (p. ej. 5 000, no 5 001).
    ax.lines[-1].set_xdata([fija, fija])
    valor = f"{fija:.2f}" if escala != 1 else f"{fija:,.0f}".replace(",", " ")
    ax.texts[-1].set_text(f"converge en {valor} {args[7]}")
    r["en"] = fija * escala
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", default="ppo_v34_pace_desde_trote:9517")
    ap.add_argument("--banda", type=float, default=0.03)
    ap.add_argument("--linea", type=float, nargs=4, metavar=("PASOS_M", "EPISODIOS", "EPOCAS", "CASTIGO_M"),
                    help="posición fija de la línea en cada gráfica (pasos y castigo en millones)")
    ap.add_argument("--nombre", default="Pace v34", help="nombre de la marcha en el título, p. ej. 'Trote v32'")
    ap.add_argument("--salida", type=Path, required=True)
    a = ap.parse_args()
    g.BANDA = a.banda
    fijas = a.linea or [None] * 4
    carpeta, semilla = a.semilla.split(":")
    d = g.cargar(carpeta, semilla)
    meta = json.loads((g.HERE / carpeta / f"semilla_{semilla}" / "metadata.json").read_text())
    previa = meta.get("continuado_desde")
    if a.nombre != "Pace v34" and previa:      # graficas_pace_v34.cargar() escribe el origen pensando en el pace
        d["origen"] = "continúa " + Path(previa).parent.name.replace("ppo_", "").replace("_semilla_", " semilla ")
    titulo = f"{a.nombre} · semilla {semilla} ({d['origen']})"
    a.salida.mkdir(parents=True, exist_ok=True)

    for (nombre, args), fija in zip(paneles(d), fijas):
        fig, ax = plt.subplots(figsize=(9, 5.2))
        r = panel(ax, args, fija)
        fig.suptitle(titulo, x=0.01, ha="left", fontsize=12, color=g.TINTA2)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(a.salida / f"{nombre}_{semilla}.png", dpi=200, facecolor=FONDO)
        plt.close(fig)
        print(f"{nombre}_{semilla}.png  ->  {'converge en ' + format(round(r['en']), ',') if r['convergio'] else 'no converge'}")

    fig, axs = plt.subplots(2, 2, figsize=(14, 9.5))
    for ax, (_, args), fija in zip(axs.flat, paneles(d), fijas):
        panel(ax, args, fija)
    miles = lambda v: f"{v:,.0f}".replace(",", " ")
    fig.suptitle(f"{titulo} · {miles(len(d['total']))} episodios · {d['pasos'][-1] / 1e6:.2f} M de pasos · "
                 f"{miles(d['ep'][-1])} épocas", x=0.01, ha="left", fontsize=14, color=g.TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(a.salida / f"resumen_4_graficas_{semilla}.png", dpi=200, facecolor=FONDO)
    plt.close(fig)


if __name__ == "__main__":
    main()
