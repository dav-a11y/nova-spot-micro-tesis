"""Inserta entre las diapositivas 11 y 12 del ODP del usuario la diapositiva «Diagrama eléctrico» (8-nov-2026), sin
convertir el archivo. Clona la 11 («Planificación de gaits») para conservar fondo, maestro y estilo del título, le quita
el texto y cambia su imagen por el diagrama de diagrama_electrico.py. No toca nada más.
Uso: python3 insertar_diagrama_odp.py DIR_DESCOMPRIMIDO diagrama.png"""
import copy
import shutil
import sys
from pathlib import Path

from lxml import etree

Z, PNG = Path(sys.argv[1]), Path(sys.argv[2])
NS = {"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
      "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
      "xlink": "http://www.w3.org/1999/xlink",
      "manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"}
D, SVG, XL = ("{%s}" % NS[k] for k in ("draw", "svg", "xlink"))
TITULO = "Diagrama eléctrico"
IMG = "Pictures/diagrama_electrico_20261108.png"

u = etree.parse(str(Z / "content.xml"))
paginas = u.findall(".//draw:page", NS)
base = paginas[10]
assert "Planificación de gaits" in "".join(base.itertext())
assert "Aprendizaje por refuerzo" in "".join(paginas[11].itertext())

nueva = copy.deepcopy(base)
nueva.set(D + "name", "page_diagrama_electrico")
for e in nueva.iter():
    for k in list(e.attrib):
        if etree.QName(k).localname == "id":     # xml:id y draw:id deben ser únicos
            del e.attrib[k]

for h in list(nueva):
    nombre = h.get(D + "name")
    if nombre == "CuadroTexto 9":                # título
        spans = [e for e in h.iter() if e.text and "Planificación de gaits" in e.text]
        assert len(spans) == 1
        spans[0].text = spans[0].text.replace("Planificación de gaits", TITULO)
    elif nombre == "CuadroTexto 1":              # texto de los gaits
        nueva.remove(h)
    elif nombre == "Imagen 2":                   # imagen -> diagrama, 23,6 x 14,2 cm
        h.set(D + "name", TITULO)
        h.set(SVG + "x", "2.6cm")
        h.set(SVG + "y", "3.95cm")
        h.set(SVG + "width", "23.6cm")
        h.set(SVG + "height", "14.2cm")
        img = h.find("draw:image", NS)
        img.set(XL + "href", IMG)
        for c in list(h):
            if etree.QName(c).localname in ("title", "desc"):
                h.remove(c)

base.addnext(nueva)
u.write(str(Z / "content.xml"), xml_declaration=True, encoding="UTF-8")

shutil.copy(PNG, Z / IMG)
m = etree.parse(str(Z / "META-INF/manifest.xml"))
ent = etree.SubElement(m.getroot(), "{%s}file-entry" % NS["manifest"])
ent.set("{%s}full-path" % NS["manifest"], IMG)
ent.set("{%s}media-type" % NS["manifest"], "image/png")
m.write(str(Z / "META-INF/manifest.xml"), xml_declaration=True, encoding="UTF-8")
print("páginas:", len(u.findall(".//draw:page", NS)))
