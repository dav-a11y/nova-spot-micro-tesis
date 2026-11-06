#!/usr/bin/env python3
"""Convergencia de cada marcha (3-nov): recompensa, castigos, épocas y pasos, de las campañas ppo_v31_<marcha>.

Por marcha, convergencia_<marcha>.png con 6 paneles: recompensa y castigo frente a pasos y frente a épocas, épocas
frente a pasos y castigos por término. Además convergencia.csv y terminos_inicio_final.csv.

Criterio de convergencia de una curva (media móvil de 100 episodios): el primer punto a partir del cual la curva ya
no sale de una banda de ±2 % del recorrido total alrededor de su valor final (media del último 10 % de episodios).
Si ese punto cae en el último 20 % del entrenamiento, la curva se declara NO convergida.

Época: una pasada sobre los 2048 pasos de una recolección (train/n_updates de Stable-Baselines3, acumulado; el freno
KL puede cortar épocas, así que no siempre son 10 por recolección).

Uso: graficas_convergencia.py [--salida graficas/convergencia]
"""
import argparse
import json
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
MARCHAS = ["paso", "trote", "carrera", "gateo", "galope"]
PREMIOS = ["vivo", "avance"]
CASTIGOS = ["actitud", "altura", "base", "correccion", "lateral", "giro", "suavidad", "coxas", "giro_ciclo"]
NOMBRES = dict(vivo="Seguir de pie", avance="Avance", actitud="Inclinación", altura="Altura", base="Lejos de la base",
               correccion="Corrección grande", lateral="Desvío lateral", giro="Giro", suavidad="Brusquedad",
               coxas="Coxas", giro_ciclo="Giro por ciclo")
# Paleta categórica validada con la skill dataviz (modo claro).
AZUL, NARANJA, AGUA, AMARILLO, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
GRIS, TINTA, TINTA2 = "#8f8e86", "#1f1f1d", "#5f5e58"
CAMPANA, SEMILLA = "v31", {}
BANDA, FINAL, VENTANA = 0.02, 0.10, 100


def media_movil(y, n=VENTANA):
    n = min(n, max(1, len(y) // 5))
    # 5-nov: en los bordes se promedian solo los episodios que existen (antes se repetía el último episodio n/2 veces,
    # y un episodio raro al final torcía la curva y el punto de convergencia).
    k = np.ones(n)
    return np.convolve(y, k, mode="same") / np.convolve(np.ones(len(y)), k, mode="same")


def convergencia(x, y):
    """(índice, convergió, valor final) según el criterio del encabezado."""
    s = media_movil(y)
    n = len(y)
    final = y[-max(1, int(FINAL * n)):].mean()
    inicio = y[:max(1, n // 100)].mean()
    banda = BANDA * abs(final - inicio)
    fuera = np.nonzero(np.abs(s - final) > banda)[0]
    i = 0 if len(fuera) == 0 else min(fuera[-1] + 1, n - 1)
    return i, bool(x[i] <= 0.8 * x[-1]), final


def cargar(marcha):
    d = next((HERE / f"ppo_{CAMPANA}_{marcha}").glob(f"semilla_{SEMILLA.get(marcha, '*')}"))
    meta = json.loads((d / "metadata.json").read_text()) if (d / "metadata.json").exists() else {}
    origen = "desde cero" if not meta.get("continuado_desde") else "continúa la política elegida"
    if meta.get("actuador", {}).get("ganancia_marcha"):
        origen += ", modelo de servos ajustado"
    with (d / "terminos.csv").open() as f:
        filas = list(csv.DictReader(f))
    # Al terminar, evaluar() de entrenar_ppo_real.py añadió sus episodios de prueba (episodio vuelve a 0): no son
    # entrenamiento y se descartan.
    reinicios = [i for i, r in enumerate(filas) if i and r["episodio"] == "0"]
    if reinicios:
        filas = filas[:reinicios[0]]
    t = {k: np.array([float(r[k]) for r in filas]) for k in filas[0]}
    pasos = np.cumsum(t["pasos_ep"])
    with (d / "progress.csv").open() as f:
        prog = [r for r in csv.DictReader(f) if r.get("train/n_updates")]
    xp = np.array([float(r["time/total_timesteps"]) for r in prog])
    ep = np.array([float(r["train/n_updates"]) for r in prog])
    epocas = np.interp(pasos, xp, ep, left=0)
    premio = sum(t[k] for k in PREMIOS)
    castigo = -sum(t[k] for k in CASTIGOS)
    return dict(semilla=d.name.split("_")[1], origen=origen, t=t, pasos=pasos, epocas=epocas, premio=premio, castigo=castigo,
                total=t["total"], xp=xp, ep=ep, caidas=int(t["caida"].sum()))


def estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#c9c8c0")
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(True, color="#ecebe6", linewidth=0.8)
    ax.set_axisbelow(True)


def curva(ax, x, y, color, conv, etiqueta_x, unidad, titulo, eje_y, escala=1.0):
    estilo(ax)
    x = x / escala
    ax.plot(x, y, color=color, linewidth=0.6, alpha=0.28)
    ax.plot(x, media_movil(y), color=color, linewidth=2.2)
    i, ok, _ = conv
    # Eje recortado para que unos pocos episodios extremos no aplasten la curva.
    bajo, alto = np.percentile(y, [0.5, 99.5])
    m = 0.06 * (alto - bajo)
    ax.set_ylim(bajo - m, alto + m)
    if ok:
        ax.axvline(x[i], color=TINTA, linewidth=1.2, linestyle="--")
    texto = f"converge en {x[i]:,.2f} {unidad}" if ok else "no convergió"
    if escala == 1:
        texto = f"converge en {x[i]:,.0f} {unidad}" if ok else "no convergió"
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA, pad=20)
    ax.text(0, 1.02, texto.replace(",", " "), transform=ax.transAxes, fontsize=9, color=TINTA2, va="bottom")
    ax.set_xlabel(etiqueta_x, fontsize=9, color=TINTA2)
    ax.set_ylabel(eje_y, fontsize=9, color=TINTA2)


def figura(marcha, d, salida, vertical=False):
    """vertical: los mismos 6 paneles en 3 filas, para una página del informe."""
    p, e = d["pasos"], d["epocas"]
    if vertical:
        fig, axs = plt.subplots(3, 2, figsize=(8.5, 10))
        (a, f), (b, g), (c, h) = axs
    else:
        fig, axs = plt.subplots(2, 3, figsize=(17, 8.2))
        (a, b, c), (f, g, h) = axs
    cr_p, cc_p = convergencia(p, d["total"]), convergencia(p, d["castigo"])
    curva(a, p, d["total"], AZUL, cr_p, "Pasos de entrenamiento (millones)", "M de pasos", "Recompensa frente a pasos",
          "Recompensa del episodio (puntos)", 1e6)
    curva(b, p, d["castigo"], NARANJA, cc_p, "Pasos de entrenamiento (millones)", "M de pasos",
          "Castigo total frente a pasos", "Suma de castigos del episodio (puntos)", 1e6)
    estilo(c)
    c.plot(d["xp"] / 1e6, d["ep"], color=AGUA, linewidth=2.2)
    c.set_title("Épocas frente a pasos", loc="left", fontsize=11, color=TINTA, pad=20)
    c.text(0, 1.02, f"{d['ep'][-1]:,.0f} épocas en {d['xp'][-1] / 1e6:.1f} M de pasos".replace(",", " "),
           transform=c.transAxes, fontsize=9, color=TINTA2, va="bottom")
    c.set_xlabel("Pasos de entrenamiento (millones)", fontsize=9, color=TINTA2)
    c.set_ylabel("Épocas acumuladas", fontsize=9, color=TINTA2)
    curva(f, e, d["total"], AZUL, (cr_p[0], cr_p[1], cr_p[2]), "Épocas acumuladas", "épocas",
          "Recompensa frente a épocas", "Recompensa del episodio (puntos)")
    curva(g, e, d["castigo"], NARANJA, (cc_p[0], cc_p[1], cc_p[2]), "Épocas acumuladas", "épocas",
          "Castigo total frente a épocas", "Suma de castigos del episodio (puntos)")
    estilo(h)
    orden = sorted(CASTIGOS, key=lambda k: d["t"][k].mean())
    principales, resto = orden[:4], orden[4:]
    for k, color in zip(principales, [NARANJA, AZUL, MAGENTA, AGUA]):
        h.plot(p / 1e6, media_movil(-d["t"][k]), color=color, linewidth=2, label=NOMBRES[k])
    h.plot(p / 1e6, media_movil(-sum(d["t"][k] for k in resto)), color=GRIS, linewidth=2, label="Los otros 5")
    h.set_title("Castigos por término", loc="left", fontsize=11, color=TINTA, pad=20)
    h.text(0, 1.02, "Tendencia de cada castigo", transform=h.transAxes, fontsize=9, color=TINTA2, va="bottom")
    h.set_xlabel("Pasos de entrenamiento (millones)", fontsize=9, color=TINTA2)
    h.set_ylabel("Castigo del episodio (puntos)", fontsize=9, color=TINTA2)
    h.legend(frameon=False, fontsize=8.5)
    fig.suptitle(f"{marcha.capitalize()}: convergencia del entrenamiento (semilla {d['semilla']}, {d['origen']})", x=0.01,
                 ha="left", fontsize=14, color=TINTA)
    if vertical:
        fig.tight_layout(rect=(0, 0, 1, 0.96))
        fig.savefig(salida / f"convergencia_{marcha}_informe.png", dpi=200, facecolor="#fcfcfb")
        plt.close(fig)
        return cr_p, cc_p
    fig.text(0.01, 0.005, "Claro: cada episodio. Oscuro: media móvil de 100 episodios. Línea discontinua: punto de "
             "convergencia (entra y ya no sale de ±2 % del recorrido alrededor del valor final). "
             "Ejes verticales recortados al percentil 0,5–99,5.", fontsize=8.5, color=TINTA2)
    fig.tight_layout(rect=(0, 0.025, 1, 0.95))
    fig.savefig(salida / f"convergencia_{marcha}.png", dpi=160, facecolor="#fcfcfb")
    plt.close(fig)
    return cr_p, cc_p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=HERE / "graficas" / "convergencia")
    # 5-nov: otra campaña (v33: desde cero con el modelo ajustado) y, si tiene varias semillas, cuál por marcha.
    ap.add_argument("--campana", default="v31")
    ap.add_argument("--semilla", action="append", default=[], help="marcha=semilla")
    a = ap.parse_args()
    global CAMPANA
    CAMPANA = a.campana
    SEMILLA.update(dict(x.split("=") for x in a.semilla))
    a.salida.mkdir(parents=True, exist_ok=True)
    resumen, terminos = [], []
    for m in MARCHAS:
        d = cargar(m)
        cr, cc = figura(m, d, a.salida)
        figura(m, d, a.salida, vertical=True)
        pc = convergencia(d["pasos"], d["premio"])
        n = len(d["total"])
        k0, k1 = max(1, n // 100), max(1, n // 10)
        fila = dict(marcha=m, semilla=d["semilla"], episodios=n, caidas=d["caidas"], pasos_total=int(d["pasos"][-1]),
                    epocas_total=int(d["ep"][-1]),
                    recompensa_inicio=round(d["total"][:k0].mean(), 1), recompensa_final=round(cr[2], 1),
                    recompensa_convergio=cr[1], recompensa_conv_pasos=int(d["pasos"][cr[0]]),
                    recompensa_conv_epocas=int(d["epocas"][cr[0]]),
                    castigo_inicio=round(d["castigo"][:k0].mean(), 1), castigo_final=round(cc[2], 1),
                    castigo_convergio=cc[1], castigo_conv_pasos=int(d["pasos"][cc[0]]),
                    castigo_conv_epocas=int(d["epocas"][cc[0]]),
                    premio_inicio=round(d["premio"][:k0].mean(), 1), premio_final=round(pc[2], 1),
                    ruido_inicio=round(d["total"][:max(k1, 2)].std(), 1), ruido_final=round(d["total"][-k1:].std(), 1))
        resumen.append(fila)
        for k in PREMIOS + CASTIGOS:
            terminos.append(dict(marcha=m, termino=k, nombre=NOMBRES[k], inicio=round(d["t"][k][:k0].mean(), 2),
                                 final=round(d["t"][k][-k1:].mean(), 2)))
    for nombre, filas in (("convergencia.csv", resumen), ("terminos_inicio_final.csv", terminos)):
        with (a.salida / nombre).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
    print("Gráficas y tablas en", a.salida)


if __name__ == "__main__":
    main()
