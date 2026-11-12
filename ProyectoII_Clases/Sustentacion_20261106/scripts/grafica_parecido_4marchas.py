"""Gráfica «Parecido robot–simulación (%)» con paso, gateo, trote y galope (sin carrera), 8-nov-2026.
Datos: tesis, cap. 14, tabla tab:parecido (una toma de 60 s por política en el robot suspendido).
Mismo tamaño que el gráfico de la diapositiva «Pruebas en el robot (OE4)»: 12,445 x 11,175 cm.
Uso: python3 grafica_parecido_4marchas.py salida.png"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DATOS = [("Paso", "v24", 83), ("Gateo", "v27", 76), ("Trote", "v24", 70), ("Galope", "v28", 66)]
AZUL, TINTA, GRIS = "#2E3192", "#262626", "#7F7F7F"
plt.rcParams["font.family"] = "Liberation Sans"

fig = plt.figure(figsize=(12.445 / 2.54, 11.175 / 2.54), dpi=300)
fig.patch.set_facecolor("white")
fig.add_artist(plt.Rectangle((0.003, 0.003), 0.994, 0.994, transform=fig.transFigure, fill=False,
                             ec="#D9D9D9", lw=0.8))
ax = fig.add_axes([0.2, 0.06, 0.68, 0.8])
y = list(range(len(DATOS)))[::-1]
ax.barh(y, [d[2] for d in DATOS], height=0.62, color=AZUL)
for yi, (m, v, p) in zip(y, DATOS):
    ax.text(p + 1, yi, f"{p} %", va="center", ha="left", fontsize=11, fontweight="bold", color=TINTA)
    ax.text(-3, yi, m, va="center", ha="right", fontsize=11, color=TINTA)
ax.set_xlim(0, 100)
ax.set_ylim(-0.6, len(DATOS) - 0.4)
ax.axis("off")
fig.text(0.5, 0.93, "Parecido robot–simulación (%)", ha="center", va="center", fontsize=12, fontweight="bold",
         color="#002060")
fig.savefig(sys.argv[1], dpi=300)
print("ok", sys.argv[1])
