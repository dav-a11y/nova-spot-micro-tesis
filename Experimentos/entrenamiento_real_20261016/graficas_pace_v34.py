#!/usr/bin/env python3
"""Gráficas de convergencia del pace v34 (6-nov-2026): recompensa, castigo y pérdidas de PPO, con la línea de convergencia.

Por semilla, una figura con 9 paneles:
  recompensa frente a pasos, episodios y épocas; castigo total frente a pasos;
  pérdidas de PPO frente a pasos (total, crítico, política, entropía, KL, varianza explicada).
Las semillas que continúan el trote cuentan los pasos y las épocas solo del pace (desde 0) y, si existe
ppo_v34_pace_desde_trote_parte2/semilla_<s>, se unen las dos partes del entrenamiento.

Criterio de convergencia (igual en todos los paneles): sobre la media móvil, el primer punto desde el que la curva ya
no sale de una banda alrededor del valor final (media del último 10 %). La banda es lo mayor entre ±BANDA del
recorrido total (del valor inicial al final) y la oscilación máxima de la tendencia en el último 20 % (lo que la
curva fluctúa una vez estable; sin esto, las pérdidas, ruidosas y con oscilaciones lentas, no entraban nunca). Además,
la recta ajustada al último 30 % no debe moverse más que la banda: una curva que sigue subiendo o bajando (p. ej. la
entropía) queda NO convergida. En
las gráficas con escala logarítmica el cálculo se hace en esa escala. Si ese punto cae en el último 20 % del entrenamiento, la curva se declara NO convergida y
no se dibuja la línea. Con BANDA = 2 % (el de v31/v33) las curvas ruidosas del pace salen y entran de la banda hasta
el final aunque a la vista ya están planas; por eso aquí BANDA = 5 % (--banda para cambiarlo).

Uso: graficas_pace_v34.py [--semilla ppo_v34_pace:9501] [--semilla ppo_v34_pace_desde_trote:9517] [--banda 0.05]
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
AZUL, NARANJA, AGUA, AMARILLO, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
GRIS, TINTA, TINTA2 = "#8f8e86", "#1f1f1d", "#5f5e58"
CASTIGOS = ["actitud", "altura", "base", "correccion", "lateral", "giro", "suavidad", "coxas", "giro_ciclo"]
PERDIDAS = [
    ("train/loss", "Pérdida total ℒ", "Lo que minimiza PPO", "Pérdida (escala log)", True),
    ("train/value_loss", "Error del crítico", "Error² al predecir V(s)", "Error² (escala log)", True),
    ("train/policy_gradient_loss", "Pérdida de la política", "Objetivo recortado", "Pérdida", False),
    ("train/entropy_loss", "Pérdida de entropía", "Más negativa = más exploración", "−Entropía", False),
    ("train/approx_kl", "Divergencia KL", "Freno en 0,03", "KL (nats)", False),
    ("train/explained_variance", "Varianza explicada", "1 = el crítico acierta", "Varianza explicada", False),
]
BANDA, FINAL, ULTIMO = 0.05, 0.10, 0.8


def media_movil(y, n):
    n = max(1, min(n, len(y) // 5))
    k = np.ones(n)
    return np.convolve(y, k, mode="same") / np.convolve(np.ones(len(y)), k, mode="same")


def convergencia(x, y, n, log=False):
    """(índice, convergió) según el criterio del encabezado (en escala log si la gráfica la usa)."""
    if log:                                   # misma transformación que el eje symlog (linthresh=1)
        y = np.sign(y) * np.log10(1.0 + np.abs(y))
    s = media_movil(y, n)
    m = len(y)
    final = y[-max(1, int(FINAL * m)):].mean()
    inicio = s[:max(1, m // 50)].mean()
    k = max(2, int((1 - ULTIMO) * m))
    banda = max(BANDA * abs(final - inicio), np.abs(s[-k:] - final).max(), 1e-12)
    fuera = np.nonzero(np.abs(s - final) > banda)[0]
    i = 0 if len(fuera) == 0 else min(fuera[-1] + 1, m - 1)
    # Tendencia: si en el último 30 % la recta ajustada a la curva se mueve más que la banda, aún no es estable.
    j = int(0.7 * m)
    deriva = abs(np.polyfit(x[j:], s[j:], 1)[0]) * (x[-1] - x[j])
    return i, bool(x[i] - x[0] <= ULTIMO * (x[-1] - x[0]) and deriva < banda)


def leer_partes(carpeta, semilla):
    partes = [HERE / carpeta / f"semilla_{semilla}"]
    p2 = HERE / f"{carpeta}_parte2" / f"semilla_{semilla}"
    if p2.exists():
        partes.append(p2)
    terminos, progreso = [], []
    for d in partes:
        with (d / "terminos.csv").open() as f:
            filas = list(csv.DictReader(f))
        # Al terminar, entrenar_ppo_real.evaluar() añade sus episodios de prueba (episodio vuelve a 0): se descartan.
        reinicios = [i for i, r in enumerate(filas) if i and r["episodio"] == "0"]
        terminos += filas[:reinicios[0]] if reinicios else filas
        with (d / "progress.csv").open() as f:
            progreso += [r for r in csv.DictReader(f) if r.get("time/total_timesteps")]
    meta = json.loads((partes[0] / "metadata.json").read_text())
    return partes, terminos, progreso, meta


def cargar(carpeta, semilla):
    partes, filas, prog, meta = leer_partes(carpeta, semilla)
    t = {k: np.array([float(r[k]) for r in filas]) for k in filas[0]}
    pasos = np.cumsum(t["pasos_ep"])
    xp = np.array([float(r["time/total_timesteps"]) for r in prog])
    ep = np.array([float(r.get("train/n_updates") or np.nan) for r in prog])
    # Continuación del trote: los contadores de SB3 traen los pasos y épocas del trote; se cuentan desde el pace.
    n = meta["ppo"]["n_steps"]
    x0 = xp[0] - n
    xp = xp - x0
    ok = ~np.isnan(ep)
    e0 = ep[ok][0] - (ep[ok][1] - ep[ok][0]) if ok.sum() > 1 else 0.0
    ep = ep - e0
    epocas = np.interp(pasos, xp[ok], ep[ok], left=0)
    origen = ("desde cero" if not meta.get("continuado_desde")
              else "continúa el trote v32 elegido" + (", dos partes unidas" if len(partes) > 1 else ""))
    perd = {}
    for col, *_ in PERDIDAS:
        par = [(x, float(r[col])) for x, r in zip(xp, prog) if r.get(col) not in ("", None)]
        perd[col] = np.array(par).T if par else None
    return dict(t=t, pasos=pasos, epocas=epocas, episodios=np.arange(1, len(pasos) + 1), total=t["total"],
                castigo=-sum(t[k] for k in CASTIGOS), xp=xp, ep=ep, perd=perd, origen=origen, partes=len(partes))


def estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#c9c8c0")
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(True, color="#ecebe6", linewidth=0.8)
    ax.set_axisbelow(True)


def panel(ax, x, y, color, titulo, nota, eje_x, eje_y, unidad, escala=1.0, ventana=100, log=False, limite=None):
    estilo(ax)
    i, ok = convergencia(x, y, ventana, log)
    xs = x / escala
    ax.plot(xs, y, color=color, linewidth=0.6, alpha=0.28)
    ax.plot(xs, media_movil(y, ventana), color=color, linewidth=2.2)
    if log:
        ax.set_yscale("symlog", linthresh=1)
    else:
        bajo, alto = np.percentile(y, [0.5, 99.5])
        m = 0.06 * (alto - bajo)
        ax.set_ylim(bajo - m, alto + m)
    if limite is not None:
        ax.axhline(limite, color=TINTA2, linewidth=1, linestyle=":")
    if ok:
        ax.axvline(xs[i], color=TINTA, linewidth=1.4, linestyle="--")
        valor = f"{xs[i]:.2f}" if escala != 1 else f"{xs[i]:,.0f}".replace(",", " ")
        texto = f"converge en {valor} {unidad}"
    else:
        texto = "aún no converge"
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA, pad=22)
    ax.text(0, 1.02, f"{nota} · {texto}" if nota else texto, transform=ax.transAxes, fontsize=8.8,
            color=TINTA if ok else NARANJA, va="bottom")
    ax.set_xlabel(eje_x, fontsize=9, color=TINTA2)
    ax.set_ylabel(eje_y, fontsize=9, color=TINTA2)
    return dict(indice=int(i), convergio=ok, en=float(x[i]))


def figura(carpeta, semilla, salida):
    d = cargar(carpeta, semilla)
    fig, axs = plt.subplots(3, 3, figsize=(17, 12.5))
    a = axs.flat
    res = {}
    pm = "Pasos de entrenamiento del pace (millones)"
    res["recompensa_pasos"] = panel(a[0], d["pasos"], d["total"], AZUL, "Recompensa frente a pasos", "",
                                    pm, "Recompensa del episodio (puntos)", "M de pasos", 1e6)
    res["recompensa_episodios"] = panel(a[1], d["episodios"].astype(float), d["total"], AZUL,
                                        "Recompensa frente a episodios", "", "Episodios de entrenamiento",
                                        "Recompensa del episodio (puntos)", "episodios")
    res["recompensa_epocas"] = panel(a[2], d["epocas"], d["total"], AZUL, "Recompensa frente a épocas", "",
                                     "Épocas acumuladas", "Recompensa del episodio (puntos)", "épocas")
    res["castigo_pasos"] = panel(a[3], d["pasos"], d["castigo"], NARANJA, "Castigo total frente a pasos", "",
                                 pm, "Suma de castigos del episodio (puntos)", "M de pasos", 1e6)
    for ax, (col, titulo, nota, eje_y, log), color in zip(a[4:], PERDIDAS[:5], [MAGENTA, NARANJA, AGUA, AMARILLO, GRIS]):
        x, y = d["perd"][col]
        res[col] = panel(ax, x, y, color, titulo, nota, pm, eje_y, "M de pasos", 1e6, ventana=25, log=log,
                         limite=0.03 if col == "train/approx_kl" else None)
    fig.suptitle(f"Pace v34 · semilla {semilla} ({d['origen']}): {len(d['total']):,} episodios, "
                 f"{d['pasos'][-1] / 1e6:.2f} M de pasos, {d['ep'][-1]:,.0f} épocas".replace(",", " "),
                 x=0.01, ha="left", fontsize=14, color=TINTA)
    fig.text(0.01, 0.006, f"Claro: cada episodio (o cada actualización de PPO en las pérdidas). Oscuro: media móvil de "
             f"100 episodios (25 actualizaciones).\nLínea discontinua: punto de convergencia, desde el que la tendencia ya "
             f"no sale de la banda alrededor del valor final (±{BANDA * 100:.0f} % del recorrido u oscilación de la tendencia en el "
             f"último 20 %, lo mayor; sin pendiente en el último 30 %).", fontsize=8.5, color=TINTA2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    nombre = f"convergencia_pace_v34_semilla_{semilla}.png"
    fig.savefig(salida / nombre, dpi=160, facecolor="#fcfcfb")
    plt.close(fig)
    # Varianza explicada aparte (sexta pérdida) en el resumen, sin panel.
    x, y = d["perd"]["train/explained_variance"]
    res["train/explained_variance"] = dict(zip(("indice", "convergio"), convergencia(x, y, 25)))
    res["train/explained_variance"]["en"] = float(x[res["train/explained_variance"]["indice"]])
    return nombre, d, res


def main():
    global BANDA
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", action="append",
                    default=[], help="carpeta:semilla (por defecto ppo_v34_pace:9501 y ppo_v34_pace_desde_trote:9517)")
    ap.add_argument("--banda", type=float, default=BANDA)
    ap.add_argument("--salida", type=Path, default=HERE / "graficas" / "convergencia_v34_pace")
    a = ap.parse_args()
    BANDA = a.banda
    a.salida.mkdir(parents=True, exist_ok=True)
    filas = []
    for cs in a.semilla or ["ppo_v34_pace:9501", "ppo_v34_pace_desde_trote:9517"]:
        carpeta, semilla = cs.split(":")
        nombre, d, res = figura(carpeta, semilla, a.salida)
        print(nombre)
        for k, r in res.items():
            unidad = "episodios" if k == "recompensa_episodios" else "épocas" if k == "recompensa_epocas" else "pasos"
            filas.append(dict(carpeta=carpeta, semilla=semilla, curva=k, convergio=r["convergio"],
                              converge_en=round(r["en"]), unidad=unidad))
            print(f"  {k:28s} {'converge en ' + format(round(r['en']), ',') + ' ' + unidad if r['convergio'] else 'aún no converge'}")
    with (a.salida / "convergencia_pace_v34.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


if __name__ == "__main__":
    main()
