"""Inserta en el ODP del usuario (sin convertir) las 7 diapositivas de diapositivas_modelo_ppo.py (8-nov-2026):
usa las diapositivas que el usuario dejó preparadas en -final.odp (solo título: 2 «Modelo y simulación (OE2)» y
2 «Control PPO residual (OE3)»), agrega copias de la última cuando hacen falta (4 y 3 en total) y pone en cada una la
imagen (con el marco de imagen de «Modelo y simulación») y sus notas. No cambia títulos ni otras diapositivas.
Uso: python3 insertar_modelo_ppo_odp.py DIR_DESCOMPRIMIDO DIR_IMAGENES"""
import copy
import shutil
import sys
from pathlib import Path

from lxml import etree

Z, IMGS = Path(sys.argv[1]), Path(sys.argv[2])
NS = {"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
      "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
      "xlink": "http://www.w3.org/1999/xlink",
      "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
      "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
      "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"}
D, SVG, XL, TX = ("{%s}" % NS[k] for k in ("draw", "svg", "xlink", "text"))

MODELO = [
    ("1_cinematica", "Cinemática de la pata",
     "Cinemática de cada pata. La directa da la posición del pie a partir de los tres ángulos; la inversa, los "
     "ángulos para poner el pie donde lo pide la marcha. La inversa elige la rodilla flexionada y rechaza los "
     "puntos fuera de alcance. El jacobiano relaciona velocidades del pie y de los motores, y fuerzas del pie con "
     "pares; en la postura de pie el número de condición es 6,65, lejos de una singularidad."),
    ("2_dinamica", "Dinámica del robot",
     "Dinámica de base flotante por Lagrange: el cuerpo no está fijo y el piso empuja a través de los pies. La "
     "matriz de masa sale de la energía cinética y la gravedad de la potencial. MuJoCo resuelve esta ecuación cada "
     "2 ms. Las masas, inercias y fricción son las nominales del modelo, no medidas en nuestro robot."),
    ("3_servo_caracterizacion", "Caracterización del servo",
     "Los servos MG996R no obedecen perfecto, así que los medimos en el robot en cuatro etapas: caminatas, "
     "escalones y senoides, barrido de rango y un ciclo de mejora. De ahí salen el retardo de unos 99 ms, la zona "
     "muerta de 0,42°, una ganancia por articulación y el límite de 3° por orden del firmware."),
    ("4_servo_simulador", "Servo en el simulador",
     "Así se lleva el servo real a MuJoCo. La función de transferencia es la ganancia medida, el retardo y el "
     "servo de posición de MuJoCo, que es de segundo orden. Antes pasan las no linealidades medidas: límite de 3° "
     "por orden y zona muerta. En cada episodio se sortean el retardo, la ganancia y el sesgo de los sensores para "
     "que la política funcione con cualquier servo parecido al real."),
]
PPO = [
    ("5_markov", "Proceso de decisión de Markov",
     "El problema se plantea como un proceso de decisión de Markov. El estado son 22 valores que el robot puede "
     "medir: ocho ángulos, la fase de la marcha y la corrección anterior. La acción son las correcciones de las "
     "articulaciones, acotadas a 4,6°. La transición la da MuJoCo con el modelo del servo, y el descuento de 0,99 "
     "mira unos 3 s hacia adelante."),
    ("6_politica_ppo", "Política PPO",
     "Usamos PPO, un método actor-crítico. El actor es una red 22-64-64-12 que da la media de una gaussiana; el "
     "crítico estima el valor del estado. El recorte con épsilon 0,2 impide que la política cambie demasiado en "
     "cada actualización, y la ventaja se estima con GAE. En el robot solo corre el actor, con la media."),
    ("7_recompensa", "Función de recompensa",
     "La recompensa premia sobrevivir y avanzar, y castiga inclinarse, cambiar de altura, alejarse de la marcha "
     "base, desviarse, girar, las correcciones bruscas y mover las coxas. Los pesos cambian por marcha: más peso "
     "al avance en gateo y galope, y menos castigo a las coxas en el pace, porque ahí se mueven a propósito."),
]

u = etree.parse(str(Z / "content.xml"))
paginas = u.findall(".//draw:page", NS)


def forma_titulo(p):
    return next((h for h in p if (h.get(D + "name") or "").startswith("CuadroTexto")), None)


def titulo(p):
    f = forma_titulo(p)
    return "".join(f.itertext()).strip() if f is not None else ""


def vacia(p):
    return [etree.QName(h).localname for h in p] == ["custom-shape", "notes"]


con_imagen = next(p for p in paginas if titulo(p) == "Modelo y simulación (OE2)" and not vacia(p))
marco = next(h for h in con_imagen if h.get(D + "name") == "Picture 11")
manifest = etree.parse(str(Z / "META-INF/manifest.xml"))


def sin_ids(el):
    for e in el.iter():
        for a in list(e.attrib):
            if etree.QName(a).localname == "id":
                del e.attrib[a]


def llenar(p, img, tit, notas):
    f = copy.deepcopy(marco)
    sin_ids(f)
    f.set(D + "name", tit)
    for a, v in (("x", "2.87cm"), ("y", "4.2cm"), ("width", "23.7cm"), ("height", "13.4cm")):
        f.set(SVG + a, v)
    for c in list(f):
        if etree.QName(c).localname in ("title", "desc"):
            f.remove(c)
    ruta = "Pictures/modelo_ppo_20261108_%s.png" % img
    f.find("draw:image", NS).set(XL + "href", ruta)
    shutil.copy(IMGS / f"{img}.png", Z / ruta)
    ent = etree.SubElement(manifest.getroot(), "{%s}file-entry" % NS["manifest"])
    ent.set("{%s}full-path" % NS["manifest"], ruta)
    ent.set("{%s}media-type" % NS["manifest"], "image/png")
    forma_titulo(p).addnext(f)
    for fr in p.iter(D + "frame"):
        if fr.get("{%s}class" % NS["presentation"]) == "notes":
            ps = fr.findall(".//text:p", NS)
            for p_ in ps[1:]:
                p_.getparent().remove(p_)
            for c in list(ps[0]):
                ps[0].remove(c)
            ps[0].text = notas


for nombre, lista in (("Modelo y simulación (OE2)", MODELO), ("Control PPO residual (OE3)", PPO)):
    huecos = [p for p in paginas if titulo(p) == nombre and vacia(p)]
    assert len(huecos) == 2, (nombre, len(huecos))
    ultima = huecos[-1]
    plantilla = copy.deepcopy(ultima)
    for k, (img, tit, notas) in enumerate(lista):
        if k < len(huecos):
            p = huecos[k]
        else:
            p = copy.deepcopy(plantilla)
            sin_ids(p)
            p.set(D + "name", "page_nueva_%s" % img)
            ultima.addnext(p)
        llenar(p, img, tit, notas)
        ultima = p

u.write(str(Z / "content.xml"), xml_declaration=True, encoding="UTF-8")
manifest.write(str(Z / "META-INF/manifest.xml"), xml_declaration=True, encoding="UTF-8")
for i, p in enumerate(u.findall(".//draw:page", NS), 1):
    print(i, titulo(p))
