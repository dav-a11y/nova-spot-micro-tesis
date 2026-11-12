#!/usr/bin/env python3
"""Identifica cada pata por sus colores en todas las cámaras de una caminata (21-oct).

Colores de las piezas: coxa blanca, fémur rojo, tibia verde, pie amarillo.
1. En cada fotograma (480 px de ancho) se segmentan rojo, verde y amarillo en HSV
   (el blanco de la coxa se confunde con paredes y luces: no se usa).
2. Las manchas de cada color se siguen fotograma a fotograma (vecino más cercano).
3. Cada trayectoria larga se asigna a la pata cuya orden de fémur explica mejor su
   movimiento (correlación con retardo 0-1 s, en x o en y): así cada cámara se identifica
   sola, esté donde esté. Si ninguna pata da |r| ≥ 0,5, la mancha queda «sin pata».
4. En la cámara de abajo (windows) se mide además, con los pies amarillos, la distancia
   entre los pies de cada lado (1-3 y 2-4) a lo largo de la caminata, en píxeles.
Salidas: colores_patas.json y colores_<cámara>.jpg (manchas etiquetadas sobre un fotograma).

Uso: python3 analizar_colores_patas.py grabaciones/<caminata>
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ANCHO = 480
FEMUR = {1: "orden_4", 2: "orden_5", 3: "orden_6", 4: "orden_7"}
# HSV de OpenCV (H 0-179). Rojo en dos tramos.
COLORES = {
    "femur": [((0, 110, 70), (8, 255, 255)), ((170, 110, 70), (179, 255, 255))],
    "tibia": [((40, 80, 40), (90, 255, 255))],
    "pie": [((18, 110, 110), (34, 255, 255))],
}
DIBUJO = {"femur": (0, 0, 255), "tibia": (0, 200, 0), "pie": (0, 220, 255)}
# 21-oct: desde abajo (cámara «windows») los pies llevan una marca roja en la suela: allí el rojo
# es el pie (el fémur casi no se ve) y el amarillo no se usa (se confunde con el cartón y la carcasa).
PIEZAS_CAMARA = {"windows": {"pie": COLORES["femur"], "tibia": COLORES["tibia"]}}


def mascaras(img, colores=COLORES):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    out = {}
    for pieza, tramos in colores.items():
        m = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in tramos:
            m |= cv2.inRange(hsv, np.array(lo), np.array(hi))
        out[pieza] = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return out


def manchas(m, area_min):
    n, _, est, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    return [(cen[k][0], cen[k][1], est[k, cv2.CC_STAT_AREA]) for k in range(1, n) if est[k, cv2.CC_STAT_AREA] >= area_min]


def seguir(por_fotograma, ts, salto=35, perdida=15):
    """Trayectorias por vecino más cercano. por_fotograma: lista de listas (x, y, área)."""
    vivas, cerradas = [], []
    for i, lista in enumerate(por_fotograma):
        libres = list(lista)
        for tr in vivas:
            if not libres:
                break
            x0, y0 = tr["x"][-1], tr["y"][-1]
            d = [np.hypot(x - x0, y - y0) for x, y, _ in libres]
            k = int(np.argmin(d))
            if d[k] < salto:
                x, y, a = libres.pop(k)
                tr["x"].append(x); tr["y"].append(y); tr["t"].append(ts[i]); tr["a"].append(a); tr["ultimo"] = i
        for x, y, a in libres:
            vivas.append(dict(x=[x], y=[y], t=[ts[i]], a=[a], ultimo=i))
        siguen = []
        for tr in vivas:
            (siguen if i - tr["ultimo"] <= perdida else cerradas).append(tr)
        vivas = siguen
    return cerradas + vivas


def correlaciones(tr, tc, ordenes, L):
    """{pata: (r, eje)} con el retardo L: mejor de x o y para cada pata."""
    t = np.array(tr["t"]); out = {}
    for p, o in ordenes.items():
        v = np.interp(t - L, tc, o)
        best = (0.0, "")
        for eje in ("x", "y"):
            s = np.array(tr[eje])
            if s.std() >= 0.5 and v.std() > 1e-6:
                r = float(np.corrcoef(s, v)[0, 1])
                if abs(r) > abs(best[0]):
                    best = (r, eje)
        out[p] = best
    return out


def asignar(tr, tc, ordenes, L):
    """Pata con mayor |r| si supera 0,5 y gana a la segunda por ≥ 0,15 (si no, None)."""
    c = correlaciones(tr, tc, ordenes, L)
    orden = sorted(c.items(), key=lambda kv: -abs(kv[1][0]))
    (p, (r, eje)), (_, (r2, _)) = orden[0], orden[1]
    claro = abs(r) >= 0.5 and abs(r) - abs(r2) >= 0.15
    return r, (p if claro else None), eje, r2


def camaras_de(raiz):
    lista = [("hp_pc1", raiz)]
    if (raiz / "remota" / "video.mkv").exists():
        lista.append(("hp_pc2", raiz / "remota"))
    lista += [(d.name.replace("extra_", ""), d) for d in sorted(raiz.glob("extra_*")) if (d / "video.mkv").exists()]
    return lista


def main():
    raiz = Path(sys.argv[1])
    solo = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None    # 21-oct: p. ej. «logitech,general»
    filas = list(csv.DictReader((raiz / "caminata.csv").open()))
    t0 = float((raiz / "caminata.inicio.txt").read_text())
    tc = t0 + np.array([float(f["t"]) for f in filas])
    ordenes = {p: np.array([float(f[c]) for f in filas]) for p, c in FEMUR.items()}
    salida = {}
    for nombre, sub in camaras_de(raiz):
        if solo and nombre not in solo:
            continue
        if not (sub / "video.inicio.txt").exists():
            continue
        ini = float((sub / "video.inicio.txt").read_text())
        cap = cv2.VideoCapture(str(sub / "video.mkv"))
        colores = PIEZAS_CAMARA.get(nombre, COLORES)
        ts, por_pieza, muestra = [], {p: [] for p in colores}, None
        while True:
            ok, img = cap.read()
            if not ok:
                break
            t = ini + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            if t < tc[0] + 1.2 or t > tc[-1]:
                continue
            img = cv2.resize(img, (ANCHO, int(ANCHO * img.shape[0] / img.shape[1])))
            if muestra is None and t > tc[0] + 10:
                muestra = img.copy()
            area_min = img.shape[0] * img.shape[1] // 2500
            for pieza, m in mascaras(img, colores).items():
                por_pieza[pieza].append(manchas(m, area_min))
            ts.append(t)
        cap.release()
        if len(ts) < 50:
            continue
        res = {}
        dib = muestra.copy() if muestra is not None else None
        area_max = (muestra.shape[0] * muestra.shape[1] // 40) if muestra is not None else 10 ** 9
        trs = [(pieza, tr) for pieza, pf in por_pieza.items() for tr in seguir(pf, ts)
               if len(tr["t"]) >= 0.3 * len(ts) and np.median(tr["a"]) < area_max]   # sin ruido ni carcasa
        # Un solo retardo por cámara: el que mejor explica todas sus manchas a la vez (0-0,6 s).
        L = max(np.arange(0.0, 0.61, 0.05),
                key=lambda L: sum(max(abs(r) for r, _ in correlaciones(tr, tc, ordenes, L).values()) for _, tr in trs) if trs else 0)
        for pieza, tr in trs:
                r, p, eje, r2 = asignar(tr, tc, ordenes, L)
                etiqueta = f"P{p} {pieza}" if p else f"? {pieza}"
                clave = etiqueta if etiqueta not in res else f"{etiqueta} ({len(res)})"
                res[clave] = dict(pata=p, pieza=pieza, r=round(r, 3), r_segunda=round(r2, 3), retardo_s=round(float(L), 2), eje=eje,
                                  fotogramas=len(tr["t"]), x_medio=round(float(np.mean(tr["x"])), 1),
                                  y_medio=round(float(np.mean(tr["y"])), 1),
                                  recorrido_px=round(float(np.ptp(tr[eje]) if eje else 0), 1))
                if dib is not None:
                    c = (int(np.mean(tr["x"])), int(np.mean(tr["y"])))
                    cv2.circle(dib, c, 6, DIBUJO[pieza], -1)
                    cv2.putText(dib, etiqueta, (c[0] + 6, c[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)
                    cv2.putText(dib, etiqueta, (c[0] + 6, c[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.45, DIBUJO[pieza], 1)
        # Cámara de abajo: distancia entre pies del mismo lado (1-3 y 2-4).
        if nombre == "windows":
            pies = {v["pata"]: k for k, v in res.items() if v["pieza"] == "pie" and v["pata"]}
            for a, b in ((1, 3), (2, 4)):
                if a in pies and b in pies:
                    ra, rb = res[pies[a]], res[pies[b]]
                    res[f"distancia_pies_{a}_{b}_px"] = round(float(np.hypot(ra["x_medio"] - rb["x_medio"],
                                                                             ra["y_medio"] - rb["y_medio"])), 1)
        salida[nombre] = res
        if dib is not None:
            cv2.imwrite(str(raiz / f"colores_{nombre}.jpg"), dib)
        print(f"{nombre:9s}: retardo {L:.2f} s, {len(trs)} manchas seguidas", flush=True)
        ident = sorted({(v["pata"], v["pieza"]) for v in res.values() if isinstance(v, dict) and v["pata"]})
        print(f"{nombre:9s}: " + (", ".join(f"P{p} {pz}" for p, pz in ident) or "ninguna pata identificada") +
              "".join(f" | {k} = {v}" for k, v in res.items() if k.startswith("distancia")), flush=True)
    (raiz / "colores_patas.json").write_text(json.dumps(salida, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
