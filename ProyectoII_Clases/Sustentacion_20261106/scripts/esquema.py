"""Agrega al deck del usuario (diapositiva 16, duplicada de «Arquitectura del sistema») el esquema de conexiones
del hardware usado en los ensayos: PC -> Arduino Uno -> PCA9685, TCA9548A (0x70, 0x71) y CD74HC4067.
Fuentes: Arduino/movimiento_suspendido_11_servos.ino y Documento_TESIS caps. 12 y 13."""
import sys
from pathlib import Path

src = Path(sys.argv[1]).read_text()
ini = src.index("# ---------- utilidades ----------")
fin = src.index("# ---------- 2 · Título ----------")
from pptx import Presentation  # noqa: E402

prs = Presentation(sys.argv[2])
S = Path(sys.argv[2]).parent
LAB = Path.home() / "Documents/LabRobotica"
GM = None
cabecera = src[:src.index("S = Path(sys.argv[1])")]
exec(cabecera, globals())
exec(src[src.index("NAVY = RGBColor"):src.index("prs = Presentation(")], globals())
exec(src[ini:fin], globals())

s = list(prs.slides)[15]
for sh in list(s.shapes):
    if sh.name != "CuadroTexto 9":
        sh._element.getparent().remove(sh._element)
t = forma(s, "CuadroTexto 9")
t.text_frame.paragraphs[0].runs[0].text = "Conexión del hardware"


def bloque(x, y, w, h, cab, lineas, fill=TINTE, borde=AZUL, color_cab=NAVY, color_txt=TINTA, sz_cab=14, sz=11):
    b = rect(s, x, y, w, h, fill=fill, line=borde)
    texto_en(b, [[(cab, {"b": True, "color": color_cab, "sz": sz_cab})]] + [[(l_, {"color": color_txt, "sz": sz})]
                                                                           for l_ in lineas],
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, margen=0.12)
    return b


def etiqueta(x, y, w, txt, color=GRIS, sz=10, align=PP_ALIGN.LEFT):
    caja(s, x, y, w, 0.3, [[(txt, {"i": True, "color": color})]], sz=sz, align=align, esp=0)


# PC y Arduino
bloque(1.13, 2.75, 1.4, 1.25, "PC Ubuntu", ["bucle de 30 ms", "marcha + PPO"], fill=NAVY, borde=None,
       color_cab=BLANCO, color_txt=BLANCO)
flecha(s, 2.53, 3.37, 3.55, 3.37, NAVY)
etiqueta(2.5, 3.0, 1.08, "USB serie", align=PP_ALIGN.CENTER)
etiqueta(2.5, 3.45, 1.08, "115 200 bd", align=PP_ALIGN.CENTER)
bloque(3.55, 1.85, 1.5, 3.05, "Arduino Uno", ["interfaz de E/S", "topes y límite", "de 3° por orden", "",
                                               "A4 = SDA", "A5 = SCL", "D4–D7 = S0–S3", "A0 = SIG (ADC)"],
       fill=NAVY, borde=None, color_cab=BLANCO, color_txt=BLANCO, sz=11)

# Bus I²C
BX = 5.6
ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(BX), Inches(2.05), Inches(BX), Inches(4.35))
ln.line.color.rgb = AZUL
ln.line.width = Pt(3)
flecha(s, 5.05, 3.2, BX, 3.2, AZUL)
etiqueta(5.08, 2.55, 0.6, "I²C", color=AZUL, sz=11)
etiqueta(5.08, 2.78, 0.6, "400 kHz", color=AZUL, sz=9)

DX, DW = 6.05, 3.7
filas = [(1.75, 0.95, "PCA9685 · 0x40", ["PWM 50 Hz → 12 servos MG996R", "coxas CH0–3 · fémures CH4–7 · tibias CH9, 10, 12, 14"]),
         (2.85, 0.8, "TCA9548A · 0x70", ["encoders AS5600: canal 1 fémur 1 · 3 tibia 2 · 4 fémur 2"]),
         (3.8, 0.8, "TCA9548A · 0x71", ["encoder AS5600: canal 5 fémur 4"])]
for y, h, cab, lin in filas:
    bloque(DX, y, DW, h, cab, lin)
    flecha(s, BX, y + h / 2, DX, y + h / 2, AZUL)

# Multiplexor analógico
bloque(DX, 4.95, DW, 1.05, "CD74HC4067 · MUX analógico", ["16 potenciómetros → ADC de 10 bits",
                                                          "coxas C0–3 · fémures C5, 6, 8, 9 · tibias C10, 12"],
       fill=TINTE_M, borde=MAGENTA, color_cab=MAGENTA)
c = s.shapes.add_connector(MSO_CONNECTOR.ELBOW, Inches(5.05), Inches(4.6), Inches(DX), Inches(5.47))
c.line.color.rgb = MAGENTA
c.line.width = Pt(2)
ln_ = c.line._get_or_add_ln()
ln_.append(ln_.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
etiqueta(4.05, 5.55, 1.95, "S0–S3 ← D4–D7 · SIG → A0", color=MAGENTA, sz=10, align=PP_ALIGN.RIGHT)

# Alimentación
p_ = rect(s, 1.13, 5.2, 2.8, 1.15, fill=TINTE_M)
texto_en(p_, [[("Alimentación", {"b": True, "color": MAGENTA, "sz": 12})],
              [("Fuente externa para los servos; masa común con la electrónica.", {"sz": 11})]],
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, margen=0.12)
caja(s, 1.13, 6.5, 8.4, 0.4, [[("Configuración de los ensayos de octubre y noviembre. Para pasar el control a la "
                                 "Raspberry Pi falta un ADC ADS1115 para los potenciómetros.", {"i": True,
                                                                                               "color": GRIS})]],
     sz=10)
s.notes_slide.notes_text_frame.text = (
    "En los ensayos el bucle de control corrió en un PC y un Arduino Uno hizo de interfaz por USB serie. Por el bus "
    "I2C, en los pines A4 y A5, el Arduino maneja el PCA9685, que genera el PWM de los doce servos, y dos "
    "multiplexores TCA9548A, porque todos los encoders AS5600 tienen la misma dirección. Los potenciómetros se leen "
    "con el multiplexor analógico CD74HC4067: el Arduino elige el canal con D4 a D7 y lee la señal en A0. Los "
    "servos tienen fuente propia con masa común.")
prs.save(sys.argv[3])
print("ok")
