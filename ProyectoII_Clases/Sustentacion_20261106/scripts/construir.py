"""Rellena la plantilla USTA (ya reestructurada en struct.pptx) con la sustentación de resultados de Proyecto de Grado II."""
import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

S = Path(sys.argv[1])
SAL = Path(sys.argv[2])
HOME = Path.home()
LAB = HOME / "Documents/LabRobotica"
GM = HOME / "Escritorio/Graficas_presentacion_marchas"

NAVY = RGBColor(0x00, 0x20, 0x60)
AZUL = RGBColor(0x2E, 0x31, 0x92)
MAGENTA = RGBColor(0xA3, 0x1A, 0x9A)
TINTA = RGBColor(0x26, 0x26, 0x26)
GRIS = RGBColor(0x59, 0x59, 0x59)
TINTE = RGBColor(0xEC, 0xEE, 0xF8)
TINTE_M = RGBColor(0xF6, 0xEA, 0xF5)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
FUENTE = "Arial"

prs = Presentation(S / "struct.pptx")
sl = list(prs.slides)


# ---------- utilidades ----------
def forma(slide, nombre):
    for s in slide.shapes:
        if s.name == nombre:
            return s
    raise KeyError(nombre)


def cambiar_texto(shape, texto, sz=None):
    """Cambia el texto del primer run conservando su formato y borra el resto de runs/párrafos."""
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    runs = p0.runs
    runs[0].text = texto
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    if sz:
        runs[0].font.size = Pt(sz)
    return runs[0]


def fijar_titulo(shape):
    """El cuadro del título venía con ajuste automático sin ajuste de línea: al crecer se centraba y tapaba la barra
    morada. Se deja anclado a la izquierda con ancho fijo."""
    bp = shape.text_frame._txBody.bodyPr
    bp.set("wrap", "square")
    for hijo in list(bp):
        if hijo.tag in (qn("a:spAutoFit"), qn("a:normAutofit")):
            bp.remove(hijo)
    shape.left = Emu(1032926 + 120000)
    shape.width = Inches(8.4)


def titulo(slide, texto, sz=32):
    sh = forma(slide, "CuadroTexto 9")
    cambiar_texto(sh, texto, sz)
    fijar_titulo(sh)


def notas(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto


def caja(slide, x, y, w, h, parrafos, sz=14, color=TINTA, anchor=MSO_ANCHOR.TOP, nombre=None, align=PP_ALIGN.LEFT,
         esp=6):
    """parrafos: lista de str o de listas de (texto, {b, color, sz, i}); un str que empieza por '• ' va con viñeta."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if nombre:
        tb.name = nombre
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(esp)
        vineta = False
        if isinstance(par, str):
            if par.startswith("• "):
                vineta, par = True, par[2:]
            par = [(par, {})]
        elif par and par[0][0].startswith("• "):
            vineta = True
            par = [(par[0][0][2:], par[0][1])] + list(par[1:])
        for texto, o in par:
            r = p.add_run()
            r.text = texto
            f = r.font
            f.name = FUENTE
            f.size = Pt(o.get("sz", sz))
            f.bold = o.get("b", False)
            f.italic = o.get("i", False)
            f.color.rgb = o.get("color", color)
        if vineta:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Emu(Inches(0.22))))
            pPr.set("indent", str(-Emu(Inches(0.22))))
            bu = pPr.makeelement(qn("a:buClr"), {})
            clr = bu.makeelement(qn("a:srgbClr"), {"val": "A31A9A"})
            bu.append(clr)
            pPr.append(bu)
            ch = pPr.makeelement(qn("a:buChar"), {"char": "•"})
            pPr.append(ch)
    return tb


def rect(slide, x, y, w, h, fill=TINTE, forma_=MSO_SHAPE.ROUNDED_RECTANGLE, line=None, nombre=None, radio=0.08):
    s = slide.shapes.add_shape(forma_, Inches(x), Inches(y), Inches(w), Inches(h))
    if nombre:
        s.name = nombre
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if forma_ == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radio
    s.text_frame.text = ""
    return s


def texto_en(s, parrafos, sz=13, color=TINTA, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, margen=0.08):
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right"):
        setattr(tf, m, Inches(margen))
    for m in ("margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.04))
    for i, par in enumerate(parrafos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if isinstance(par, str):
            par = [(par, {})]
        elif isinstance(par, tuple):
            par = [par]
        for t, o in par:
            r = p.add_run()
            r.text = t
            r.font.name = FUENTE
            r.font.size = Pt(o.get("sz", sz))
            r.font.bold = o.get("b", False)
            r.font.color.rgb = o.get("color", color)


def circulo(slide, x, y, d, txt, fill=NAVY, sz=16):
    s = rect(slide, x, y, d, d, fill=fill, forma_=MSO_SHAPE.OVAL)
    texto_en(s, [(txt, {"b": True, "color": BLANCO, "sz": sz})], margen=0)
    return s


def flecha(slide, x1, y1, x2, y2, color=AZUL):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return c


def imagen(slide, ruta, x, y, w=None, h=None, alt=""):
    p = slide.shapes.add_picture(str(ruta), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    p._element.nvPicPr.cNvPr.set("descr", alt)
    return p


def stat(slide, x, y, w, h, numero, etiqueta, fill=TINTE, color=NAVY, sz_num=30, sz_et=12):
    s = rect(slide, x, y, w, h, fill=fill)
    texto_en(s, [(numero, {"b": True, "color": color, "sz": sz_num}), (etiqueta, {"color": TINTA, "sz": sz_et})])
    return s


X0 = 1.13          # margen izquierdo del contenido (alineado con el título de la plantilla)
Y0 = 1.75          # debajo del título
DER = 9.75         # borde derecho seguro en toda la altura (triángulo decorativo abajo a la derecha)
DER_ALTO = 11.3    # borde derecho seguro por encima de y = 4,8 in

# ---------- 2 · Título ----------
s = sl[1]
r = cambiar_texto(forma(s, "CuadroTexto 1"),
                  "DISEÑO DE UN SISTEMA DE CONTROL PARA LA LOCOMOCIÓN Y ESTABILIZACIÓN DE UN ROBOT CUADRÚPEDO "
                  "BASADO EN APRENDIZAJE POR REFUERZO", 22)
caja(s, 0.93, 0.62, 7.0, 0.35, [[("PROYECTO DE GRADO II · SUSTENTACIÓN DE RESULTADOS", {"b": True, "color": BLANCO})]],
     sz=13)
dirs = forma(s, "CuadroTexto 4").text_frame.paragraphs
for p, nombre in zip(dirs, ["MSc. Armando Mateus Rojas", "PhD. Billy Vladimir Toro Tovar",
                            "MSc. Carlos Javier Mojica Casallas"]):
    base = p.runs[-1]
    nuevo = copy.deepcopy(base._r)
    p._p.append(nuevo)
    run = p.runs[-1]
    run.text = " " + nombre
    run.font.size = Pt(16)
    run.font.name = FUENTE
    run.font.bold = False
est = forma(s, "CuadroTexto 3").text_frame.paragraphs
est[0].runs[0].text = "David Esteban Díaz Castro"
for r_ in est[0].runs[1:]:
    r_.text = ""
est[1].runs[0].text = "David Felipe Díaz Suesca"
for r_ in est[1].runs[1:]:
    r_.text = ""
g = forma(s, "CuadroTexto 8").text_frame.paragraphs[0]
g.runs[-1].text = g.runs[-1].text.rstrip() + " GED – Grupo de Estudio y Desarrollo en Robótica"

# ---------- 3 · Contenido ----------
s = sl[2]
agenda = ["Introducción", "Objetivos", "Marco teórico", "Metodología", "Desarrollo", "Resultados", "Conclusiones",
          "Trabajo futuro", "Bibliografía"]
for nombre, t in zip(["CuadroTexto 10", "CuadroTexto 11", "CuadroTexto 13", "CuadroTexto 22", "CuadroTexto 24",
                      "CuadroTexto 26", "CuadroTexto 28", "CuadroTexto 30", "CuadroTexto 1"], agenda):
    tf = forma(s, nombre).text_frame
    runs = tf.paragraphs[0].runs
    runs[0].text = t
    for r_ in runs[1:]:
        r_.text = ""

# ---------- 5 · Problema y justificación (según el anteproyecto: caps. 2 y 4; pregunta problema literal) ----------
s = sl[4]
titulo(s, "Problema y justificación")
caja(s, X0, 1.55, 5.85, 4.1, [
    [("Problema", {"b": True, "color": NAVY, "sz": 16})],
    "• La plataforma Nova Spot Micro, adquirida por el laboratorio en 2021, permanecía inactiva desde su compra.",
    "• No tenía un sistema electrónico funcional de accionamiento ni sensorización y potencia adecuadas.",
    "• No existía un modelo cinemático y dinámico ni una estrategia de control que generara patrones de marcha.",
    "• Faltaba documentación técnica de sus características mecánicas y geométricas.",
    [("Justificación", {"b": True, "color": NAVY, "sz": 16})],
    [("• Científica: ", {"b": True, "color": NAVY}), ("recurso experimental para estudiar la locomoción cuadrúpeda.", {})],
    [("• Tecnológica: ", {"b": True, "color": NAVY}), ("plataforma operativa y caracterizada para nuevos proyectos.",
                                                      {})],
    [("• Académica: ", {"b": True, "color": NAVY}), ("control, instrumentación, robótica y sistemas embebidos; "
                                                    "ODS 4, 8 y 9.", {})],
], sz=13, esp=3)
imagen(s, LAB / "Raspberry/documentacion/cuadrupedo_real_vista_1_2026-09-03.jpeg", 7.35, 1.6, h=3.95,
       alt="Plataforma Nova Spot Micro del laboratorio")
q = rect(s, X0, 5.85, 8.45, 1.1, fill=TINTE_M)
texto_en(q, [[("Pregunta problema · ", {"b": True, "color": MAGENTA, "sz": 13}),
              ("¿En qué medida una estrategia de aprendizaje por refuerzo, utilizada como capa correctiva de una marcha "
               "nominal, mejora la estabilidad y la repetibilidad de la locomoción tipo paso y gateo del robot "
               "cuadrúpedo Nova Spot Micro en una superficie plana y bajo condiciones controladas de laboratorio?",
               {"sz": 13})]], align=PP_ALIGN.LEFT, margen=0.18)
notas(s, "En 2021 el laboratorio adquirió la plataforma Nova Spot Micro, pero no se podía usar: no tenía electrónica "
         "funcional para moverla, ni sensores ni potencia adecuados, ni un modelo matemático o una estrategia de "
         "control para generar marchas, y faltaba documentación técnica. El proyecto se justifica en lo científico, "
         "porque deja un recurso experimental para estudiar la locomoción; en lo tecnológico, porque la plataforma "
         "queda operativa y caracterizada; y en lo académico, porque apoya asignaturas de control, instrumentación, "
         "robótica y sistemas embebidos, alineado con los ODS 4, 8 y 9. De ahí la pregunta: en qué medida una capa "
         "correctiva de aprendizaje por refuerzo mejora la estabilidad y la repetibilidad del paso y el gateo.")

# ---------- 7 · Objetivos ----------
s = sl[6]
titulo(s, "Objetivos")
og = rect(s, X0, 1.6, 10.1, 1.05, fill=NAVY)
texto_en(og, [[("Objetivo general · ", {"b": True, "color": BLANCO, "sz": 14}),
               ("Desarrollar un sistema de control para la plataforma cuadrúpeda Spot Micro que integre aprendizaje "
                "por refuerzo para su ejecución y estabilización en los diferentes modos de locomoción tipo paso y "
                "gateo en condiciones de entorno controladas.", {"color": BLANCO, "sz": 14})]],
         align=PP_ALIGN.LEFT, margen=0.2)
oes = [("OE1 · Hardware y software", "Implementar el hardware y software para la ejecución de movimiento de las "
        "extremidades del Spot Micro del laboratorio, según la documentación del fabricante."),
       ("OE2 · Modelado", "Modelar el comportamiento cinemático y dinámico de la plataforma para simulación y diseño, "
        "a partir de la literatura sobre robots cuadrúpedos."),
       ("OE3 · Control aprendido", "Diseñar una estrategia de control basada en aprendizaje automático que garantice "
        "estabilidad y continuidad en los modos de locomoción paso y gateo."),
       ("OE4 · Evaluación", "Evaluar la caminata con tres pruebas: margen de estabilidad estática, seguimiento de "
        "posición articular y repetibilidad del patrón de marcha.")]
for i, (cab, txt) in enumerate(oes):
    x = X0 + (i % 2) * 4.38
    y = 2.9 + (i // 2) * 2.05
    c = rect(s, x, y, 4.2, 1.85)
    texto_en(c, [[(cab, {"b": True, "color": NAVY, "sz": 15})], [(txt, {"sz": 13})]], align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, margen=0.15)
notas(s, "Estos son los objetivos aprobados en el anteproyecto. Los resultados se presentan siguiendo estos cuatro "
         "objetivos y al final se resume el grado de cumplimiento de cada uno.")

# ---------- 12 · Aprendizaje por refuerzo y PPO ----------
s = sl[11]
titulo(s, "Aprendizaje por refuerzo (PPO)")
ag = rect(s, X0, 2.0, 3.6, 1.0, fill=NAVY)
texto_en(ag, [[("Agente", {"b": True, "color": BLANCO, "sz": 16})], [("política PPO (red neuronal)", {"color": BLANCO,
                                                                                                    "sz": 12})]])
en = rect(s, X0, 4.6, 3.6, 1.0, fill=AZUL)
texto_en(en, [[("Entorno", {"b": True, "color": BLANCO, "sz": 16})], [("robot simulado en MuJoCo", {"color": BLANCO,
                                                                                                "sz": 12})]])
flecha(s, X0 + 3.0, 3.0, X0 + 3.0, 4.6, MAGENTA)
caja(s, X0 + 3.1, 3.55, 1.6, 0.5, [[("acción aₜ", {"b": True, "color": MAGENTA})]], sz=13)
flecha(s, X0 + 0.6, 4.6, X0 + 0.6, 3.0, NAVY)
caja(s, X0 - 0.95, 3.45, 1.5, 0.7, [[("estado sₜ", {"b": True, "color": NAVY})], [("recompensa rₜ", {"b": True,
                                                                                                   "color": NAVY})]],
     sz=12, align=PP_ALIGN.RIGHT, esp=0)
caja(s, 5.75, Y0, 4.0, 5.0, [
    "• El agente aprende por ensayo y error a maximizar la recompensa acumulada [1].",
    "• PPO (Proximal Policy Optimization) es un método actor-crítico que limita cuánto cambia la política en cada "
    "actualización, lo que lo hace estable [2].",
    "• Control residual: la red no genera la marcha completa, solo corrige una marcha nominal ya diseñada [3].",
    "• Aleatorización del entorno durante el entrenamiento para transferir la política de la simulación al robot "
    "real [4].",
], sz=14, esp=10)
notas(s, "En aprendizaje por refuerzo un agente observa el estado, actúa y recibe una recompensa. Usamos PPO porque "
         "es estable y es el estándar en locomoción. La política no reemplaza la marcha: suma una corrección pequeña "
         "a la marcha nominal, lo que se llama control residual.")

# ---------- 14 · Metodología ----------
s = sl[13]
titulo(s, "Metodología")
pasos = [("Modelado cinemático y dinámico", "Cinemática directa e inversa y dinámica nominal de base flotante "
          "(Lagrange); el mismo robot en Gazebo y MuJoCo.", "OE2"),
         ("Identificación del actuador", "Retardo, zona muerta y ganancia de los servos medidos en el robot real.",
          "OE2"),
         ("Marchas nominales", "Gateo, paso, trote, carrera, galope y pace como trayectorias articulares.", "OE1"),
         ("Entrenamiento PPO residual", "Varias semillas por marcha; elección por viabilidad en simulación.", "OE3"),
         ("Validación", "Robot suspendido con sensores y 5 cámaras: seguimiento, repetibilidad y parecido con la "
          "simulación.", "OE4")]
for i, (cab, txt, oe) in enumerate(pasos):
    y = 1.7 + i * 1.02
    circulo(s, X0, y + 0.08, 0.62, str(i + 1), fill=NAVY if i % 2 == 0 else MAGENTA)
    caja(s, X0 + 0.85, y, 6.6, 0.9, [[(cab, {"b": True, "color": NAVY, "sz": 15})], [(txt, {"sz": 13})]], esp=2)
    b = rect(s, 8.85, y + 0.18, 0.85, 0.42, fill=TINTE)
    texto_en(b, [[(oe, {"b": True, "color": NAVY, "sz": 12})]], margen=0)
notas(s, "La metodología siguió cinco etapas, cada una ligada a un objetivo. Primero el modelo, luego la medición "
         "del actuador real para que la simulación se pareciera al robot, después las marchas nominales, el "
         "entrenamiento PPO y finalmente la validación en el robot suspendido.")

# ---------- 15 · Arquitectura del sistema ----------
s = sl[14]
titulo(s, "Arquitectura del sistema")
fila1 = [("Raspberry Pi 4", "ROS 2 Humble · bucle de 30 ms · política PPO"), ("PCA9685", "I²C · PWM a 50 Hz"),
         ("12 servos MG996R", "coxa, fémur y tibia por pata"), ("Robot Spot Micro", "suspendido en los ensayos")]
fila2 = [("5 cámaras", "sincronizadas, patrón de marcha"), ("TCA9548A + MUX", "multiplexores I²C y analógico"),
         ("Encoders AS5600", "y potenciómetros articulares")]
w, gap = 2.0, 0.42
for i, (cab, txt) in enumerate(fila1):
    x = X0 + i * (w + gap)
    b = rect(s, x, 1.85, w, 1.15, fill=NAVY)
    texto_en(b, [[(cab, {"b": True, "color": BLANCO, "sz": 14})], [(txt, {"color": BLANCO, "sz": 11})]])
    if i:
        flecha(s, x - gap + 0.04, 2.42, x - 0.04, 2.42)
for i, (cab, txt) in enumerate(fila2):
    x = X0 + i * (w + gap)
    b = rect(s, x, 3.75, w, 1.15, fill=TINTE, line=AZUL)
    texto_en(b, [[(cab, {"b": True, "color": NAVY, "sz": 14})], [(txt, {"sz": 11})]])
# medición: robot -> encoders -> multiplexores -> Raspberry; cámaras -> Raspberry
flecha(s, X0 + 3 * (w + gap) + w / 2, 3.0, X0 + 2 * (w + gap) + w - 0.3, 3.75, AZUL)
flecha(s, X0 + 2 * (w + gap) - 0.04, 4.32, X0 + (w + gap) + w + 0.04, 4.32, AZUL)
flecha(s, X0 + (w + gap) + 0.3, 3.75, X0 + w - 0.3, 3.0, AZUL)
flecha(s, X0 + 0.5, 3.75, X0 + 0.5, 3.0, AZUL)
caja(s, X0 + 3 * (w + gap) + 0.85, 3.2, 1.0, 0.4, [[("medición", {"i": True, "color": GRIS})]], sz=11)
sw = rect(s, X0, 5.35, 8.5, 1.2, fill=TINTE_M)
texto_en(sw, [[("Software · ", {"b": True, "color": MAGENTA, "sz": 14}),
               ("ROS 2 Humble · MuJoCo 3 · Gazebo · Stable-Baselines3 (PPO) · Python. Supervisor de seguridad con "
                "topes por articulación y límite de cambio por paso.", {"sz": 13})]], align=PP_ALIGN.LEFT, margen=0.2)
notas(s, "La Raspberry Pi ejecuta la marcha nominal y la política, y manda las órdenes al PCA9685, que genera el "
         "PWM de los doce servos. La realimentación viene de encoders magnéticos y potenciómetros a través de "
         "multiplexores, y cinco cámaras registran el patrón de marcha.")

# ---------- 16 · divisor DESARROLLO ----------
cambiar_texto(forma(sl[15], "CuadroTexto 3"), "DESARROLLO")

# ---------- 17 · Modelo y simulación ----------
s = sl[16]
titulo(s, "Modelo y simulación (OE2)")
caja(s, X0, Y0, 4.45, 5.1, [
    "• Cinemática directa e inversa y Jacobianos, con las medidas reales de las patas.",
    "• Dinámica nominal de base flotante por Lagrange (M, C, g) y dinámica inversa por pata.",
    "• El mismo robot en URDF (Gazebo) y MJCF (MuJoCo), que simulan la dinámica con contactos.",
    "• Actuador identificado en el robot: retardo ≈ 99 ms, zona muerta e histéresis < 1,5° y ganancia por "
    "articulación.",
    [("Limitación: ", {"b": True, "color": MAGENTA}), ("masas, inercias y fricción nominales, no medidas en el robot; "
                                                       "no es un gemelo digital.", {})],
], sz=14, esp=9)
imagen(s, S / "mujoco_crop.png", 5.85, 1.6, w=5.3, alt="Robot simulado en MuJoCo caminando en pace")
caja(s, 5.85, 4.98, 4.6, 0.4, [[("Robot en MuJoCo ejecutando la marcha pace (política v34).", {"i": True,
                                                                                            "color": GRIS})]], sz=11)
notas(s, "El modelo incluye cinemática y dinámica: la dinámica nominal se obtuvo por Lagrange y MuJoCo y Gazebo "
         "simulan la dinámica completa con contactos. El modelo se construyó con las medidas reales. Lo más importante fue identificar el actuador: el servo "
         "responde con unos 99 ms de retardo, y meter eso en MuJoCo fue lo que permitió que las políticas funcionaran "
         "en el robot. No identificamos masas ni fricción, así que no lo llamamos gemelo digital.")

# ---------- 18 · Plataforma física ----------
s = sl[17]
titulo(s, "Plataforma física (OE1)")
caja(s, X0, Y0, 5.0, 5.1, [
    "• Las 12 articulaciones se mueven desde ROS 2 a través del PCA9685.",
    "• Realimentación en 9 a 10 articulaciones con encoders AS5600 y potenciómetros.",
    "• Topes por articulación, límite de cambio por paso y supervisor: detectó los 9 fallos provocados.",
    "• 5 cámaras sincronizadas para medir el patrón de marcha.",
    "• Ensayos con el robot suspendido de una barra, sin riesgo de caída.",
    [("Pendiente: ", {"b": True, "color": MAGENTA}), ("alimentación separada de servos y electrónica.", {})],
], sz=14, esp=10)
imagen(s, S / "robot_suspendido.jpg", 6.45, 1.6, h=4.5, alt="Robot suspendido de una barra durante los ensayos")
caja(s, 6.45, 6.2, 3.3, 0.4, [[("Robot suspendido durante los ensayos.", {"i": True, "color": GRIS})]], sz=11)
notas(s, "El robot físico quedó operativo: las doce articulaciones responden, hay realimentación en casi todas y el "
         "supervisor detuvo la marcha en los nueve fallos provocados. Todas las pruebas se hicieron con el robot "
         "colgado para no arriesgar caídas.")

# ---------- 19 · Control PPO residual ----------
s = sl[18]
titulo(s, "Control PPO residual (OE3)")
b1 = rect(s, X0, 1.75, 2.4, 1.0, fill=NAVY)
texto_en(b1, [[("Marcha nominal", {"b": True, "color": BLANCO, "sz": 14})], [("q_nom(t)", {"color": BLANCO,
                                                                                       "sz": 12})]])
b2 = rect(s, X0, 3.3, 2.4, 1.0, fill=MAGENTA)
texto_en(b2, [[("Política PPO", {"b": True, "color": BLANCO, "sz": 14})], [("Δq acotada ±0,08 rad", {"color": BLANCO,
                                                                                                 "sz": 12})]])
suma = circulo(s, 4.35, 2.6, 0.6, "+", fill=AZUL, sz=22)
flecha(s, X0 + 2.4, 2.25, 4.42, 2.75)
flecha(s, X0 + 2.4, 3.8, 4.42, 3.05)
b3 = rect(s, 5.55, 2.4, 2.3, 1.0, fill=TINTE, line=AZUL)
texto_en(b3, [[("Límites y topes", {"b": True, "color": NAVY, "sz": 14})], [("seguridad", {"sz": 12})]])
flecha(s, 4.95, 2.9, 5.55, 2.9)
b4 = rect(s, 8.45, 2.4, 2.3, 1.0, fill=TINTE, line=AZUL)
texto_en(b4, [[("Servos", {"b": True, "color": NAVY, "sz": 14})], [("robot o MuJoCo", {"sz": 12})]])
flecha(s, 7.85, 2.9, 8.45, 2.9)
c = s.shapes.add_connector(MSO_CONNECTOR.ELBOW, Inches(9.6), Inches(3.4), Inches(X0 + 2.4), Inches(3.95))
c.line.color.rgb = GRIS
c.line.width = Pt(1.5)
c.line.dash_style = 4
ln = c.line._get_or_add_ln()
ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))
caja(s, 5.6, 3.95, 3.6, 0.4, [[("observaciones (27): ángulos, actitud, fase", {"i": True, "color": GRIS})]], sz=11)
for i, (n, et) in enumerate([("27", "observaciones"), ("12", "correcciones articulares"), ("6", "marchas entrenadas"),
                             ("30 ms", "periodo de control")]):
    stat(s, X0 + i * 2.17, 4.75, 2.0, 1.15, n, et, sz_num=26, sz_et=11)
caja(s, X0, 6.1, 8.5, 0.6, [[("Recompensa: ", {"b": True, "color": NAVY}),
                             ("avance hacia adelante menos castigos por actitud, desvío lateral, giro, brusquedad y "
                              "movimiento de las coxas.", {})]], sz=13)
notas(s, "La política recibe 27 observaciones y entrega 12 correcciones pequeñas que se suman a la marcha nominal. "
         "Antes de llegar a los servos pasan por límites de seguridad. La recompensa premia avanzar y castiga "
         "inclinarse, desviarse, girar o moverse bruscamente.")

# ---------- 20 · divisor RESULTADOS ----------
cambiar_texto(forma(sl[19], "CuadroTexto 3"), "RESULTADOS")

# ---------- 21 · Convergencia ----------
s = sl[20]
titulo(s, "Convergencia de PPO")
figs = [GM / "gateo_v33_desde_cero/1_recompensa_pasos_9900.png", GM / "trote_v33_desde_cero/1_recompensa_pasos_9900.png",
        GM / "galope_v33_desde_cero/1_recompensa_pasos_9900.png", GM / "pace_v34_9517/1_recompensa_pasos_9517.png"]
nombres = ["gateo", "trote", "galope", "pace"]
for i, (f, n) in enumerate(zip(figs, nombres)):
    imagen(s, f, X0 + (i % 2) * 4.35, 1.55 + (i // 2) * 2.55, w=4.2,
           alt=f"Recompensa frente a pasos de entrenamiento de {n}, con la línea de convergencia")
notas(s, "Estas son las curvas de recompensa de cuatro marchas entrenadas. En todas se ve la rampa de aprendizaje y "
         "luego la meseta; la línea punteada marca la convergencia: gateo 1,5 M de pasos, trote 1,25 M, galope "
         "2,4 M y pace 1,1 M. Gateo, trote y galope se entrenaron desde cero; el pace partió del trote.")

# ---------- 22 · Pace ----------
s = sl[21]
titulo(s, "Marcha nueva: pace (v34)")
imagen(s, GM / "pace_v34_9517/resumen_4_graficas_9517.png", X0, 1.6, w=5.75,
       alt="Recompensa por pasos, episodios y épocas, y castigo, del pace v34")
for i, (n, et) in enumerate([("100 %", "viabilidad en 60 episodios"), ("3,66 m", "de avance en 20 s"),
                             ("1,1 M", "pasos hasta converger")]):
    stat(s, 7.2, 1.6 + i * 1.5, 2.5, 1.3, n, et, fill=TINTE if i != 0 else TINTE_M,
         color=NAVY if i else MAGENTA, sz_num=28)
caja(s, X0, 5.65, 5.75, 1.1, [
    "• Ambladura: se mueven juntas las dos patas de un mismo lado.",
    "• Entrenada partiendo del trote; la política elegida (1 600 k pasos) está lista para el robot.",
], sz=13, esp=4)
notas(s, "El pace es una marcha nueva en la que se mueven juntas las patas del mismo lado. Se entrenó partiendo del "
         "trote, convergió hacia 1,1 millones de pasos y la política elegida fue viable en el 100 % de 60 episodios, "
         "avanzando 3,66 m en 20 s.")

# ---------- 23 · Viabilidad ----------
s = sl[22]
titulo(s, "Viabilidad en simulación")
vals = [("Gateo", "100 %"), ("Paso", "100 %"), ("Trote", "100 %"), ("Carrera", "100 %"), ("Galope", "90 %"),
        ("Pace", "100 %")]
for i, (m, v) in enumerate(vals):
    x = X0 + (i % 3) * 2.9
    y = 1.65 + (i // 3) * 1.85
    stat(s, x, y, 2.7, 1.65, v, m, fill=TINTE_M if m == "Galope" else TINTE, color=MAGENTA if m == "Galope" else NAVY,
         sz_num=36, sz_et=15)
caja(s, X0, 5.55, 8.4, 1.3, [
    [("Viabilidad: ", {"b": True, "color": NAVY}), ("porcentaje de episodios sin caída, con aleatorización del "
                                                    "entorno (20 episodios; 60 en pace).", {})],
    [("Lectura honesta: ", {"b": True, "color": MAGENTA}), ("ventaja modesta frente a la marcha nominal, y copias "
                                                            "elegidas sobre esos mismos episodios.", {})],
], sz=13, esp=6)
notas(s, "Las políticas elegidas no se cayeron en ningún episodio en cinco marchas, y el galope en el 90 %. Hay que "
         "decir que la ventaja frente a la marcha nominal es modesta y que las copias se eligieron con esos mismos "
         "episodios.")

# ---------- 24 · Robot suspendido ----------
s = sl[23]
titulo(s, "Pruebas en el robot (OE4)")
cd = CategoryChartData()
cd.categories = ["Paso", "Gateo", "Trote", "Carrera", "Galope"]
cd.add_series("Parecido robot–simulación (%)", (83, 76, 70, 69, 66))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(X0), Inches(1.65), Inches(4.9), Inches(4.4), cd)
ch = gf.chart
ch.has_legend = False
ch.has_title = True
ch.chart_title.text_frame.text = "Parecido robot–simulación (%)"
tp = ch.chart_title.text_frame.paragraphs[0]
tp.runs[0].font.size = Pt(14)
tp.runs[0].font.bold = True
tp.runs[0].font.color.rgb = NAVY
tp.runs[0].font.name = FUENTE
pl = ch.plots[0]
pl.gap_width = 60
pl.has_data_labels = True
dl = pl.data_labels
dl.font.size = Pt(12)
dl.font.bold = True
dl.font.color.rgb = TINTA
dl.number_format = '0" %"'
dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]
ser.format.fill.solid()
ser.format.fill.fore_color.rgb = AZUL
va = ch.value_axis
va.maximum_scale = 100
va.minimum_scale = 0
va.has_major_gridlines = False
va.visible = False
ca = ch.category_axis
ca.tick_labels.font.size = Pt(12)
ca.tick_labels.font.color.rgb = TINTA
ca.reverse_order = True
ca.format.line.fill.background()
caja(s, X0, 6.1, 4.9, 0.6, [[("Una toma por política: la forma del movimiento coincide; la diferencia está en la "
                              "amplitud.", {"i": True, "color": GRIS})]], sz=11)
for i, (n, et) in enumerate([("−15 a −19 %", "error de seguimiento con PPO frente a la marcha nominal (gateo y "
                                            "trote)"),
                             ("2 a 11 %", "coeficiente de variación entre repeticiones de 3 min (repetibilidad)"),
                             ("9 / 9", "fallos provocados detectados por el supervisor")]):
    stat(s, 6.4, 1.65 + i * 1.6, 3.3, 1.42, n, et, sz_num=24, sz_et=11)
notas(s, "En el robot suspendido medimos tres cosas. Primero, el parecido entre lo que hace el robot y lo que hace "
         "la simulación: entre 66 y 83 %, con la misma forma y diferencias de amplitud. Segundo, la política redujo "
         "entre 15 y 19 % el error de seguimiento frente a la marcha nominal. Tercero, la repetibilidad: variación "
         "entre 2 y 11 % entre repeticiones.")

# ---------- 25 · divisor CONCLUSIONES ----------
cambiar_texto(forma(sl[24], "CuadroTexto 3"), "CONCLUSIONES")

# ---------- 26 · Cumplimiento ----------
s = sl[25]
titulo(s, "Cumplimiento de objetivos")
filas = [("Objetivo", "Resultado principal", "Estado"),
         ("OE1 · Hardware y software", "12 articulaciones controladas desde ROS 2, con topes, supervisor y "
          "realimentación; robot suspendido.", "Cumplido · falta separar la alimentación"),
         ("OE2 · Modelado", "Modelo cinemático y MuJoCo con actuador identificado; usado para entrenar.",
          "Cumplido · sin dinámica identificada"),
         ("OE3 · Control aprendido", "PPO residual en 6 marchas; 90–100 % de viabilidad; −15 a −19 % de error en el "
          "robot.", "Cumplido en simulación · parcial en robot"),
         ("OE4 · Evaluación", "Seguimiento articular y repetibilidad medidos en el robot; margen estático en "
          "simulación.", "2 de 3 pruebas físicas")]
tb = s.shapes.add_table(len(filas), 3, Inches(X0), Inches(1.65), Inches(8.55), Inches(4.6)).table
for j, wcol in enumerate([2.15, 4.2, 2.2]):
    tb.columns[j].width = Inches(wcol)
for i, fila in enumerate(filas):
    for j, t in enumerate(fila):
        cel = tb.cell(i, j)
        cel.fill.solid()
        cel.fill.fore_color.rgb = NAVY if i == 0 else (TINTE if i % 2 else BLANCO)
        cel.margin_left = cel.margin_right = Inches(0.1)
        cel.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cel.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ""
        r_ = p.add_run()
        r_.text = t
        r_.font.name = FUENTE
        r_.font.size = Pt(13 if i == 0 else 12)
        r_.font.bold = i == 0 or j == 0
        r_.font.color.rgb = BLANCO if i == 0 else (NAVY if j == 0 else (MAGENTA if j == 2 else TINTA))
notas(s, "Resumen honesto por objetivo: OE1 y OE2 cumplidos con sus limitaciones; OE3 cumplido en simulación y con "
         "mejora medida en el robot suspendido; OE4 con dos de las tres pruebas físicas, porque el margen de "
         "estabilidad estática necesita el robot apoyado.")

# ---------- 27 · Conclusiones ----------
s = sl[26]
titulo(s, "Conclusiones")
concl = [("Plataforma operativa", "Las 12 articulaciones se controlan desde ROS 2 con supervisión y realimentación; "
          "el robot ejecuta seis marchas suspendido."),
         ("El actuador era la clave", "Incluir el retardo y la ganancia medidos de los servos en MuJoCo permitió que "
          "las políticas funcionaran en el robot real (66–83 % de parecido)."),
         ("PPO residual converge y mejora", "Convergió en todas las marchas, con 90–100 % de viabilidad en "
          "simulación y 15–19 % menos error de seguimiento en el robot."),
         ("Evaluación parcial en el robot", "Seguimiento y repetibilidad medidos; la locomoción apoyada y el margen "
          "estático físico quedan como siguiente paso.")]
for i, (cab, txt) in enumerate(concl):
    y = 1.7 + i * 1.22
    circulo(s, X0, y + 0.1, 0.6, str(i + 1), fill=NAVY if i % 2 == 0 else MAGENTA)
    caja(s, X0 + 0.85, y, 7.6, 1.1, [[(cab, {"b": True, "color": NAVY, "sz": 15})], [(txt, {"sz": 13})]], esp=2)
notas(s, "Las cuatro ideas que nos llevamos: la plataforma funciona; modelar bien el actuador fue lo que hizo "
         "transferible el aprendizaje; PPO residual convergió y mejoró el seguimiento; y la evaluación con el robot "
         "apoyado en el piso es el siguiente paso.")

# ---------- 28 · Trabajo futuro ----------
s = sl[27]
titulo(s, "Limitaciones y trabajo futuro")
for k, (cab, items, fill, col) in enumerate([
        ("Limitaciones", ["Ensayos con el robot suspendido, sin apoyo en el piso.",
                          "Masas, inercias y fricción sin identificar.",
                          "Sin realimentación en tres tibias y una coxa.",
                          "Servos y electrónica con la misma alimentación."], TINTE_M, MAGENTA),
        ("Trabajo futuro", ["Locomoción apoyada y margen de estabilidad estática con IMU.",
                            "Identificación dinámica completa del robot.",
                            "Transición automática entre marchas.",
                            "Alimentación separada y protección eléctrica."], TINTE, NAVY)]):
    x = X0 + k * 4.35
    c = rect(s, x, 1.7, 4.15, 3.7, fill=fill)
    texto_en(c, [[(cab, {"b": True, "color": col, "sz": 18})]] + [[("• " + t, {"sz": 14})] for t in items],
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margen=0.25)
    for p in c.text_frame.paragraphs:
        p.space_after = Pt(10)
notas(s, "La principal limitación es que todo se probó con el robot colgado. El siguiente paso es caminar apoyado, "
         "medir el margen de estabilidad con una IMU, identificar la dinámica y separar la alimentación.")

# ---------- 30 · Referencias ----------
s = sl[29]
titulo(s, "Referencias")
refs = ["[1] R. S. Sutton y A. G. Barto, Reinforcement Learning: An Introduction, 2.ª ed. MIT Press, 2018.",
        "[2] J. Schulman, F. Wolski, P. Dhariwal, A. Radford y O. Klimov, “Proximal Policy Optimization "
        "Algorithms”, arXiv:1707.06347, 2017.",
        "[3] T. Johannink et al., “Residual Reinforcement Learning for Robot Control”, en Proc. IEEE ICRA, 2019, "
        "pp. 6023–6029.",
        "[4] J. Tobin et al., “Domain Randomization for Transferring Deep Neural Networks from Simulation to the "
        "Real World”, en Proc. IEEE/RSJ IROS, 2017, pp. 23–30.",
        "[5] J. Tan et al., “Sim-to-Real: Learning Agile Locomotion for Quadruped Robots”, en Proc. RSS, 2018.",
        "[6] J. Hwangbo et al., “Learning agile and dynamic motor skills for legged robots”, Science Robotics, "
        "vol. 4, n.º 26, 2019.",
        "[7] E. Todorov, T. Erez y Y. Tassa, “MuJoCo: A Physics Engine for Model-Based Control”, en Proc. IEEE/RSJ "
        "IROS, 2012, pp. 5026–5033.",
        "[8] A. Raffin et al., “Stable-Baselines3: Reliable Reinforcement Learning Implementations”, JMLR, vol. 22, "
        "n.º 268, 2021."]
caja(s, X0, 1.65, 8.5, 5.2, refs, sz=13, esp=7)
notas(s, "Referencias principales del trabajo; la lista completa está en el documento de tesis.")

for k in (8, 9, 10):   # títulos de las diapositivas del marco teórico del anteproyecto
    sh = forma(sl[k], "CuadroTexto 9")
    fijar_titulo(sh)
    if sl[k].has_notes_slide:   # quitar la nota guía de la plantilla
        sl[k].notes_slide.notes_text_frame.text = ""
    for par in sh.text_frame.paragraphs:
        for r_ in par.runs:
            r_.font.size = Pt(32)
prs.save(SAL)
print("guardado", SAL)
