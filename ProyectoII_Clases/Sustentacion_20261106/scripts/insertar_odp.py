"""Inserta en el ODP del usuario (zu/, sin convertir) la diapositiva «Conexión del hardware» tomada de zv/ (página 16).
Clona la diapositiva «Arquitectura del sistema» del usuario (para conservar su fondo, maestro y título), le quita el
contenido y le pone las formas del esquema con sus estilos automáticos renombrados (prefijo hw_). No toca nada más."""
import copy
import re
import sys

from lxml import etree

NS = {
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
D = "{%s}" % NS["draw"]
ST = "{%s}" % NS["style"]


def q(p, n):
    return "{%s}%s" % (NS[p], n)


u = etree.parse("zu/content.xml")
v = etree.parse("zv/content.xml")
us = etree.parse("zu/styles.xml")
vs = etree.parse("zv/styles.xml")

pu = u.findall(".//draw:page", NS)
pv = v.findall(".//draw:page", NS)
arq = pu[14]
fuente = pv[15]
assert "Arquitectura" in "".join(arq.itertext()), "la página 15 del usuario no es Arquitectura"
assert "Conexión del hardware" in "".join(fuente.itertext())


def es_titulo(el, texto):
    return etree.QName(el).localname in ("frame", "custom-shape") and "".join(el.itertext()).strip() == texto


# 1. clonar la diapositiva del usuario y vaciarla (salvo el título)
nueva = copy.deepcopy(arq)
nueva.set(D + "name", "page_hardware")
for k in list(nueva.attrib):
    if k.endswith("}id") or k == q("xml", "id"):
        del nueva.attrib[k]
for hijo in list(nueva):
    if es_titulo(hijo, "Arquitectura del sistema"):
        titulo = hijo
        continue
    nueva.remove(hijo)
# texto del título
spans = [e for e in titulo.iter() if e.text and "Arquitectura del sistema" in e.text]
assert spans
spans[0].text = spans[0].text.replace("Arquitectura del sistema", "Conexión del hardware")

# 2. formas del esquema y notas de zv
formas = [copy.deepcopy(h) for h in fuente if not es_titulo(h, "Conexión del hardware")]

# 3. estilos automáticos referenciados -> copiar con prefijo
auto_v = v.find("office:automatic-styles", NS)
auto_u = u.find("office:automatic-styles", NS)
por_nombre = {e.get(ST + "name"): e for e in auto_v if e.get(ST + "name")}
existentes_u = {e.get(ST + "name") for e in auto_u if e.get(ST + "name")}


def atributos_estilo(el):
    for k, val in el.attrib.items():
        loc = etree.QName(k).localname
        if loc.endswith("style-name") and loc != "parent-style-name" and loc != "master-page-name":
            yield k, val


usados = set()
pendientes = []
for f in formas:
    for e in f.iter():
        for k, val in atributos_estilo(e):
            if val in por_nombre:
                pendientes.append(val)
while pendientes:
    n = pendientes.pop()
    if n in usados:
        continue
    usados.add(n)
    for e in por_nombre[n].iter():
        for k, val in list(atributos_estilo(e)) + ([(ST + "parent-style-name", e.get(ST + "parent-style-name"))]
                                                  if e.get(ST + "parent-style-name") else []):
            if val in por_nombre:
                pendientes.append(val)
ren = {n: "hw_" + n for n in usados}
assert not (set(ren.values()) & existentes_u)


def renombrar(el):
    for e in el.iter():
        for k, val in list(e.attrib.items()):
            loc = etree.QName(k).localname
            if loc.endswith("style-name") and val in ren:
                e.set(k, ren[val])
        # ids de formas (conectores, glue) -> únicos
        for k in list(e.attrib):
            loc = etree.QName(k).localname
            if loc == "id" or loc in ("start-shape", "end-shape"):
                e.set(k, "hw_" + e.get(k))


for n in sorted(usados):
    st = copy.deepcopy(por_nombre[n])
    st.set(ST + "name", ren[n])
    renombrar(st)
    auto_u.append(st)
for f in formas:
    renombrar(f)
    nueva.append(f)

# 4. recursos con nombre (flechas, guiones, degradados...) que falten en styles.xml del usuario
REC = {"marker-start": "marker", "marker-end": "marker", "stroke-dash": "stroke-dash",
       "fill-gradient-name": "gradient", "fill-hatch-name": "hatch", "fill-image-name": "fill-image",
       "opacity-name": "opacity"}
ofic_u = us.find("office:styles", NS)
ofic_v = vs.find("office:styles", NS)
tiene = {(etree.QName(e).localname, e.get(D + "name")) for e in ofic_u if e.get(D + "name")}
falta = set()
for n in usados:
    for e in por_nombre[n].iter():
        for k, val in e.attrib.items():
            loc = etree.QName(k).localname
            if loc in REC and (REC[loc], val) not in tiene:
                falta.add((REC[loc], val))
for tipo, nombre in falta:
    el = ofic_v.find("draw:%s[@draw:name='%s']" % (tipo, nombre), NS)
    assert el is not None, (tipo, nombre)
    ofic_u.insert(0, copy.deepcopy(el))
print("estilos copiados:", len(usados), "recursos añadidos:", sorted(falta))

# 5. imágenes
imgs = {e.get("{http://www.w3.org/1999/xlink}href") for f in formas for e in f.iter()
        if e.get("{http://www.w3.org/1999/xlink}href")}
print("imágenes:", imgs)

arq.addnext(nueva)
u.write("zu/content.xml", xml_declaration=True, encoding="UTF-8")
us.write("zu/styles.xml", xml_declaration=True, encoding="UTF-8")
print("páginas:", len(u.findall(".//draw:page", NS)))
