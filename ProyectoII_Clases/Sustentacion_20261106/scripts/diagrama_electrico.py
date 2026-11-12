"""Diagrama eléctrico de la diapositiva 12 (8-nov-2026): potenciómetros -> CD74HC4067, encoders AS5600 -> TCA9548A,
PCA9685 con la fuente de los servos, todo hacia un Arduino Uno.
Conexiones del firmware vigente (Arduino/movimiento_suspendido_11_servos.ino, desde el 19-oct):
MUX S0-S3 = D4-D7, SIG = A0, EN = GND; I2C en A4/A5; servos en el PCA9685 (tibias CH12, 9, 10, 14).
Canales de los potenciómetros y encoders: sensores_robot.json y diapositiva «Conexión del hardware».
Uso: python3 diagrama_electrico.py salida.png"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon  # noqa: E402

W, H = 23.6, 14.2                     # cm, tamaño con el que va en la diapositiva
NAVY, AZUL, MAG, TINTA, GRIS = "#002060", "#2E3192", "#A31A9A", "#262626", "#595959"
TINTE, TINTE_M = "#ECEEF8", "#F6EAF5"
ROJO, NEGRO, SDA_C, SCL_C, POT = "#C62828", "#262626", "#1565C0", "#00897B", "#E65100"

fig = plt.figure(figsize=(W / 2.54, H / 2.54), dpi=300)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
plt.rcParams["font.family"] = "DejaVu Sans"


def caja(x0, y0, x1, y1, fill=TINTE, borde=AZUL, lw=1.4):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=fill, ec=borde, lw=lw, zorder=2))


def txt(x, y, s, sz=9, c=TINTA, ha="center", va="center", b=False, i=False, z=5):
    ax.text(x, y, s, fontsize=sz, color=c, ha=ha, va=va, fontweight="bold" if b else "normal",
            fontstyle="italic" if i else "normal", zorder=z)


def linea(pts, c, lw=1.3, z=3):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=z)


def punto(x, y, c):
    ax.plot([x], [y], "o", ms=3.2, color=c, zorder=6)


def tierra(x, y, c=NEGRO):
    """Símbolo de tierra colgando de (x, y)."""
    linea([(x, y), (x, y - 0.22)], c, 1.1)
    for k, w in enumerate((0.22, 0.14, 0.06)):
        linea([(x - w, y - 0.22 - 0.07 * k), (x + w, y - 0.22 - 0.07 * k)], c, 1.1)


def cinco_v(x, y, lado="izq"):
    """Etiqueta de red 5 V al final de un cable en (x, y)."""
    dx = -0.55 if lado == "izq" else 0.55
    linea([(x, y), (x + dx * 0.35, y)], ROJO, 1.1)
    txt(x + dx * 0.75, y, "5 V", 8, ROJO, b=True)


def pin(x, y, nombre, lado, sz=8):
    """Nombre de pin dentro de la caja; lado = borde en el que está el pin."""
    if lado == "izq":
        txt(x + 0.1, y, nombre, sz, GRIS, ha="left")
    else:
        txt(x - 0.1, y, nombre, sz, GRIS, ha="right")


# ---------------- Potenciómetros y MUX analógico ----------------
MX0, MX1, MY0, MY1 = 4.6, 6.5, 1.35, 12.95
caja(MX0, MY0, MX1, MY1, TINTE_M, MAG)
txt((MX0 + MX1) / 2, MY1 + 0.55, "CD74HC4067", 10.5, MAG, b=True)
txt((MX0 + MX1) / 2, MY1 + 0.2, "MUX analógico 16 canales", 8, MAG)

def ypin(k):
    return 12.55 - 0.71 * k


POTS = {0: "Coxa 1", 1: "Coxa 2", 2: "Coxa 4", 3: "Coxa 3", 5: "Fémur 2", 6: "Fémur 4", 8: "Fémur 1",
        9: "Fémur 3", 10: "Tibia 4", 12: "Tibia 3"}
R5, RG = 0.35, 0.75                      # rieles de 5 V y GND de los potenciómetros
y_top, y_bot = ypin(0) + 0.5, ypin(12) - 0.45
linea([(R5, y_top), (R5, y_bot)], ROJO, 1.4)
linea([(RG, y_top - 0.3), (RG, y_bot - 0.3)], NEGRO, 1.4)
txt(R5, y_top + 0.25, "5 V", 8, ROJO, b=True)
tierra(RG, y_bot - 0.3)
for k in range(16):
    y = ypin(k)
    pin(MX0, y, f"C{k}", "izq")
    if k not in POTS:
        txt(MX0 - 0.12, y, "×", 8, GRIS, ha="right")
        continue
    # potenciómetro vertical en x=1.6: extremo superior a 5 V, inferior a GND, cursor a Ck
    px, h = 1.55, 0.5
    ax.add_patch(Rectangle((px - 0.1, y - h / 2), 0.2, h, fc="white", ec=POT, lw=1.2, zorder=4))
    linea([(px, y + h / 2), (px, y + h / 2 + 0.06), (R5, y + h / 2 + 0.06)], ROJO, 1.0)
    punto(R5, y + h / 2 + 0.06, ROJO)
    linea([(px, y - h / 2), (px, y - h / 2 - 0.06), (RG, y - h / 2 - 0.06)], NEGRO, 1.0)
    punto(RG, y - h / 2 - 0.06, NEGRO)
    ax.add_patch(Polygon([(px + 0.11, y), (px + 0.3, y + 0.08), (px + 0.3, y - 0.08)], fc=POT, ec=POT, zorder=5))
    linea([(px + 0.3, y), (MX0, y)], POT, 1.2)
    txt(2.0, y + 0.17, POTS[k], 7.5, TINTA, ha="left", va="bottom")
txt(0.05, 0.45, "Potenciómetros de eje", 8.5, POT, ha="left", b=True)

# ---------------- Arduino Uno ----------------
AX0, AX1, AY0, AY1 = 8.7, 10.9, 3.6, 12.2
caja(AX0, AY0, AX1, AY1, NAVY, NAVY)
txt((AX0 + AX1) / 2, AY1 - 0.45, "Arduino", 11, "white", b=True)
txt((AX0 + AX1) / 2, AY1 - 0.85, "Uno", 11, "white", b=True)
# USB al PC
linea([((AX0 + AX1) / 2, AY1), ((AX0 + AX1) / 2, 13.25)], NAVY, 2.2)
txt((AX0 + AX1) / 2, 13.6, "USB → PC (marcha + PPO)", 8.5, NAVY, b=True)


def pin_ard(y, nombre, lado):
    x = AX0 if lado == "izq" else AX1
    txt(x + (0.12 if lado == "izq" else -0.12), y, nombre, 8.5, "white", ha="left" if lado == "izq" else "right")


# MUX -> Arduino: SIG, S0-S3, VCC, GND, EN
MUXR = [("SIG", "A0", 10.6, MAG), ("S0", "D4", 9.7, AZUL), ("S1", "D5", 9.1, AZUL), ("S2", "D6", 8.5, AZUL),
        ("S3", "D7", 7.9, AZUL), ("VCC", "5V", 6.2, ROJO), ("GND", "GND", 5.4, NEGRO)]
for m, a, y, c in MUXR:
    pin(MX1, y, m, "der")
    pin_ard(y, a, "izq")
    linea([(MX1, y), (AX0, y)], c, 1.6 if m == "SIG" else 1.3)
pin(MX1, 4.6, "EN", "der")
linea([(MX1, 4.6), (7.2, 4.6), (7.2, 5.4)], NEGRO, 1.1)
punto(7.2, 5.4, NEGRO)
txt(7.6, 10.83, "señal analógica", 7.5, MAG, i=True)
txt(7.6, 8.8, "selección\nde canal", 7.5, AZUL, i=True, va="center")
txt(7.6, 4.35, "EN a GND", 7.5, GRIS, i=True)

# ---------------- Bus I2C ----------------
BS, BC = 11.65, 12.05                         # x de SDA y SCL
YSDA, YSCL = 11.0, 10.4
pin_ard(YSDA, "A4 SDA", "der")
pin_ard(YSCL, "A5 SCL", "der")
linea([(AX1, YSDA), (BS, YSDA)], SDA_C, 1.6)
linea([(AX1, YSCL), (BC, YSCL)], SCL_C, 1.6)
TX0, TX1 = 13.0, 15.2
mods = [("TCA9548A · 0x70", 9.35, 12.75, "A0–A2 → GND"),
        ("TCA9548A · 0x71", 6.2, 8.75, "A0 → 5 V"),
        ("PCA9685 · 0x40", 1.3, 5.0, None)]
ys_sda, ys_scl = [], []
for nombre, y0, y1, addr in mods:
    caja(TX0, y0, TX1, y1)
    txt((TX0 + TX1) / 2, y1 + 0.25, nombre, 10, AZUL, b=True)
    yd, yc = y1 - 0.45, y1 - 0.95
    pin(TX0, yd, "SDA", "izq")
    pin(TX0, yc, "SCL", "izq")
    pin(TX0, y1 - 1.45, "VCC", "izq")
    pin(TX0, y1 - 1.95, "GND", "izq")
    linea([(BS, yd), (TX0, yd)], SDA_C, 1.4)
    linea([(BC, yc), (TX0, yc)], SCL_C, 1.4)
    punto(BS, yd, SDA_C)
    punto(BC, yc, SCL_C)
    cinco_v(TX0, y1 - 1.45)
    linea([(TX0, y1 - 1.95), (TX0 - 0.3, y1 - 1.95)], NEGRO, 1.1)
    tierra(TX0 - 0.3, y1 - 1.95)
    if addr:
        txt((TX0 + TX1) / 2, y0 + 0.25, addr, 7.5, GRIS, i=True)
    ys_sda.append(yd)
    ys_scl.append(yc)
linea([(BS, max(ys_sda)), (BS, min(ys_sda))], SDA_C, 1.6)
punto(BS, YSDA, SDA_C)
linea([(BC, max(ys_scl)), (BC, min(ys_scl))], SCL_C, 1.6)
punto(BC, YSCL, SCL_C)
txt(BS + 0.2, 13.15, "I²C", 9, AZUL, b=True)

# ---------------- Encoders AS5600 ----------------
EX0, EX1 = 17.4, 20.3


def encoder(ycanal, canal, nombre):
    yd, yc = ycanal + 0.12, ycanal - 0.12
    pin(TX1, ycanal, f"SD{canal}/SC{canal}", "der", 7.5)
    linea([(TX1, yd), (EX0, yd)], SDA_C, 1.2)
    linea([(TX1, yc), (EX0, yc)], SCL_C, 1.2)
    caja(EX0, ycanal - 0.35, EX1, ycanal + 0.35, "white", AZUL, 1.2)
    txt((EX0 + EX1) / 2, ycanal, f"AS5600 · {nombre}", 8.5, TINTA)


encoder(11.75, 1, "Fémur 1")
encoder(10.95, 3, "Tibia 2")
encoder(10.15, 4, "Fémur 2")
encoder(7.2, 5, "Fémur 4")
txt((EX0 + EX1) / 2, 12.5, "encoders magnéticos (0x36)", 7.5, GRIS, i=True)
txt((EX0 + EX1) / 2, 6.45, "VCC 5 V y GND comunes", 7.5, GRIS, i=True)

# ---------------- PCA9685, fuente y servos ----------------
# salidas PWM
pin(TX1, 2.15, "PWM", "der")
SX0, SX1, SY0, SY1 = 17.4, 21.6, 1.3, 3.0
for k, dy in enumerate((0.18, 0.0, -0.18)):
    linea([(TX1, 2.15 + dy), (SX0, 2.15 + dy)], [AZUL, ROJO, NEGRO][k], 1.1)
caja(SX0, SY0, SX1, SY1, TINTE, AZUL)
txt((SX0 + SX1) / 2, 2.6, "12 servos MG996R", 9.5, AZUL, b=True)
txt((SX0 + SX1) / 2, 2.1, "coxas CH0–3 · fémures CH4–7", 7.5, TINTA)
txt((SX0 + SX1) / 2, 1.7, "tibias CH12, 9, 10, 14", 7.5, TINTA)
txt((TX1 + SX0) / 2, 2.55, "señal · V+ · GND", 7, GRIS, i=True)
# fuente de potencia en el borne V+ / GND del PCA
FX0, FX1, FY0, FY1 = 17.4, 19.9, 3.7, 4.9
caja(FX0, FY0, FX1, FY1, "#FFF3E0", POT)
txt((FX0 + FX1) / 2, 4.5, "Fuente 6 V", 9.5, POT, b=True)
txt((FX0 + FX1) / 2, 4.05, "potencia servos", 7.5, TINTA)
pin(TX1, 4.55, "V+", "der")
pin(TX1, 3.95, "GND", "der")
linea([(FX0, 4.55), (TX1, 4.55)], ROJO, 2.6)
linea([(FX0, 3.95), (TX1, 3.95)], NEGRO, 2.6)
punto(16.3, 3.95, NEGRO)
tierra(16.3, 3.95)
txt(16.3, 3.2, "masa común", 7.5, GRIS, i=True)

# ---------------- Leyenda ----------------
ley = [(SDA_C, "SDA"), (SCL_C, "SCL"), (ROJO, "5 V / V+"), (NEGRO, "GND"), (AZUL, "selección / PWM"),
       (MAG, "analógica")]
x = 4.6
for c, s in ley:
    linea([(x, 0.45), (x + 0.5, 0.45)], c, 2.0)
    txt(x + 0.6, 0.45, s, 7.5, TINTA, ha="left")
    x += 0.6 + 0.16 * len(s) + 0.55

fig.savefig(sys.argv[1], dpi=300, transparent=True)
print("ok", sys.argv[1])
