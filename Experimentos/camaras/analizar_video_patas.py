#!/usr/bin/env python3
"""Análisis de video de una caminata: movimiento de cada pata visto por cada cámara.

Para cada cámara de la carpeta (video.mkv, remota/, extra_*/):
1. Lee los fotogramas (gris, 160×90) con su hora real y las órdenes de los 4 fémures
   (caminata.csv).
2. Busca el retardo de la cámara (0-1,2 s) y hace, píxel a píxel, una regresión del
   brillo frente a las 4 órdenes: cada píxel con buen ajuste se asigna a la pata cuya
   orden lo explica más. Así se obtienen las máscaras de las patas sin marcadores.
3. Señal visible de cada pata = media de sus píxeles (con el signo de su coeficiente).
   Por ciclo: correlación con la orden, amplitud (desv. estándar) y desfase.
   Estabilidad: CV de la amplitud entre ciclos y tendencia a lo largo de la caminata.
4. Movimiento no explicado: varianza de los píxeles con mucho cambio que las órdenes
   no explican (balanceo del cuerpo, choques, coxas que caen, gente) por ciclo; los
   ciclos con valores muy altos se marcan como anomalías.
Salidas en la carpeta: video_analisis.json y video_analisis_<cámara>.png.

Uso: python3 analizar_video_patas.py grabaciones/<caminata>
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

COLORES = {1: (0, 0, 255), 2: (0, 200, 0), 3: (255, 0, 0), 4: (0, 200, 255)}
FEMUR = {1: "orden_4", 2: "orden_5", 3: "orden_6", 4: "orden_7"}
# 20-oct: en el trote las patas de cada par diagonal reciben la misma orden y los dos pares
# van en contrafase, así que solo se pueden separar los pares, con las órdenes de tibia
# (cada par levanta en su mitad del ciclo): grupo 1 = patas 2+3 (FL+RR), 2 = patas 1+4.
TROTE = {1: "orden_9", 2: "orden_8"}
NOMBRE_TROTE = {1: "P2+P3", 2: "P1+P4"}
TAM = (160, 90)


def leer(video, inicio):
    cap = cv2.VideoCapture(str(video))
    imgs, ts, muestra = [], [], None
    while True:
        ok, img = cap.read()
        if not ok:
            break
        ts.append(inicio + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), TAM).astype(np.float32))
        if len(imgs) == 300:
            muestra = img
    cap.release()
    return np.array(imgs), np.array(ts), muestra


def ajuste(X, O):
    """R² por píxel de X (n×p) frente a las órdenes O (n×4) y coeficientes estandarizados."""
    Xc = X - X.mean(0); Oc = O - O.mean(0)
    Oc /= Oc.std(0) + 1e-9
    B, *_ = np.linalg.lstsq(Oc, Xc, rcond=None)
    res = Xc - Oc @ B
    r2 = 1 - (res ** 2).sum(0) / ((Xc ** 2).sum(0) + 1e-9)
    return r2, B, res


def analizar_camara(nombre, sub, raiz, filas, ciclos, grupos=FEMUR):
    if not (sub / "video.mkv").exists() or not (sub / "video.inicio.txt").exists():
        return None
    imgs, ts, muestra = leer(sub / "video.mkv", float((sub / "video.inicio.txt").read_text()))
    if len(imgs) < 100:
        return dict(error=f"solo {len(imgs)} fotogramas")
    t0 = float((raiz / "caminata.inicio.txt").read_text())
    tc = t0 + np.array([float(f["t"]) for f in filas])
    ordenes = {p: np.array([float(f[c]) for f in filas]) for p, c in grupos.items()}
    claves = list(grupos)
    dentro = (ts >= tc[0] + 1.2) & (ts <= tc[-1])
    X = imgs[dentro].reshape(dentro.sum(), -1)
    t = ts[dentro]
    # Retardo de la cámara: el que maximiza el R² medio de los píxeles mejor explicados.
    mejor = (0.0, -1.0)
    for L in np.arange(0.0, 1.21, 0.1):
        O = np.column_stack([np.interp(t - L, tc, ordenes[p]) for p in claves])
        r2, _, _ = ajuste(X, O)
        q = float(np.percentile(r2, 99))
        if q > mejor[1]:
            mejor = (float(L), q)
    L = mejor[0]
    O = np.column_stack([np.interp(t - L, tc, ordenes[p]) for p in claves])
    r2, B, res = ajuste(X, O)
    # Un píxel es de una pata si esa orden lo explica al menos el doble que cualquier otra
    # y el ajuste es bueno; después se quitan los píxeles sueltos (zonas < 6 píxeles).
    absB = np.abs(B)
    orden_b = np.sort(absB, axis=0)
    pata = np.array(claves)[np.argmax(absB, axis=0)]
    buenos = (r2 > 0.5) & (orden_b[-1] >= 2 * orden_b[-2])
    limpio = np.zeros_like(buenos)
    for p in claves:
        m = (buenos & (pata == p)).reshape(TAM[1], TAM[0]).astype(np.uint8)
        n, etiquetas, est, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        for k in range(1, n):
            if est[k, cv2.CC_STAT_AREA] >= 6:
                limpio |= (etiquetas == k).ravel()
    buenos = limpio
    resultado = dict(retardo_s=L, r2_p99=round(mejor[1], 3), patas={})
    Xc = X - X.mean(0)
    for i, p in enumerate(claves):
        m = buenos & (pata == p)
        if m.sum() < 8:
            resultado["patas"][p] = dict(visible=False, pixeles=int(m.sum()))
            continue
        senal = (Xc[:, m] * np.sign(B[i, m])).mean(1)
        orden = O[:, i]
        por_ciclo = []
        for a, b in ciclos:
            sel = (t >= t0 + float(filas[a]["t"])) & (t < t0 + float(filas[min(b, len(filas) - 1)]["t"]))
            if sel.sum() < 8 or orden[sel].std() < 1e-6 or senal[sel].std() < 1e-6:
                continue
            por_ciclo.append(dict(r=float(np.corrcoef(senal[sel], orden[sel])[0, 1]),
                                  amplitud=float(senal[sel].std())))
        if not por_ciclo:
            resultado["patas"][p] = dict(visible=False, pixeles=int(m.sum()))
            continue
        amp = np.array([c["amplitud"] for c in por_ciclo])
        rr = np.array([c["r"] for c in por_ciclo])
        k = np.arange(len(amp))
        resultado["patas"][p] = dict(
            visible=True, pixeles=int(m.sum()), r_medio=float(rr.mean()), r_minimo=float(rr.min()),
            amplitud_media=float(amp.mean()), cv_amplitud_pct=float(100 * amp.std() / (amp.mean() + 1e-9)),
            tendencia_amplitud_pct_por_ciclo=float(100 * np.polyfit(k, amp, 1)[0] / (amp.mean() + 1e-9)) if len(amp) > 3 else 0.0,
            ciclos_r_bajo=[i + 1 for i, x in enumerate(rr) if x < 0.5], por_ciclo=por_ciclo)
    # Movimiento no explicado por las órdenes, por ciclo.
    activos = Xc.var(0) > np.percentile(Xc.var(0), 90)
    ruido = (res[:, activos] ** 2).mean(1)
    por_ciclo = []
    for a, b in ciclos:
        sel = (t >= t0 + float(filas[a]["t"])) & (t < t0 + float(filas[min(b, len(filas) - 1)]["t"]))
        if sel.sum() >= 8:
            por_ciclo.append(float(ruido[sel].mean()))
    v = np.array(por_ciclo)
    med = float(np.median(v)) if len(v) else 0.0
    resultado["no_explicado"] = dict(mediana=med, por_ciclo=por_ciclo,
                                     ciclos_anomalos=[i + 1 for i, x in enumerate(v) if x > 3 * med])
    # Figura: máscaras de cada pata sobre la imagen.
    if muestra is not None:
        h, w = muestra.shape[:2]
        capa = muestra.copy()
        for p in claves:
            m = (buenos & (pata == p)).reshape(TAM[1], TAM[0]).astype(np.uint8)
            m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST) > 0
            capa[m] = (0.45 * capa[m] + 0.55 * np.array(COLORES[p])).astype(np.uint8)
            if m.any():
                ys, xs = np.nonzero(m)
                cv2.putText(capa, NOMBRE_TROTE[p] if grupos is TROTE else f"P{p}", (int(xs.mean()), int(ys.mean())), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 4)
        cv2.putText(capa, f"{nombre}  retardo {L * 1000:.0f} ms", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.imwrite(str(raiz / f"video_analisis_{nombre}.png"), cv2.resize(capa, (960, int(960 * h / w))))
    return resultado


def main():
    raiz = Path(sys.argv[1])
    filas = list(csv.DictReader((raiz / "caminata.csv").open()))
    fase = np.array([float(f["fase"]) for f in filas])
    ini = [int(np.argmax(fase > 0))] + [i for i in range(1, len(fase)) if fase[i] < fase[i - 1]]
    ciclos = [(a, b) for a, b in zip(ini, ini[1:] + [len(fase)]) if b - a > 10]
    camaras = [("hp_pc1", raiz), ("hp_pc2", raiz / "remota")] + \
              [(d.name.replace("extra_", ""), d) for d in sorted(raiz.glob("extra_*"))]
    cfg = raiz / "caminata.config.json"
    marcha = json.loads(cfg.read_text()).get("marcha") if cfg.exists() else None
    grupos = TROTE if marcha == "trote" else FEMUR
    salida = {"marcha": marcha, "grupos": "pares diagonales" if grupos is TROTE else "patas"}
    from multiprocessing import Pool
    # 27-oct: como máximo 2 cámaras a la vez (~1,5 GB cada una); con 5 a la vez el PC se quedó sin
    # memoria y cortó la caminata siguiente (26-oct, rep_paso_v16d_paso_v16_r4).
    with Pool(min(2, len(camaras))) as pool:
        resultados = pool.starmap(analizar_camara, [(n, sub, raiz, filas, ciclos, grupos) for n, sub in camaras])
    for (nombre, sub), r in zip(camaras, resultados):
        if r is None:
            continue
        salida[nombre] = r
        if "error" in r:
            print(f"  {nombre:9s} {r['error']}")
            continue
        partes = []
        for p, d in r["patas"].items():
            et = NOMBRE_TROTE[p] if grupos is TROTE else f"P{p}"
            partes.append(f"{et} r {d['r_medio']:.2f} CV {d['cv_amplitud_pct']:.0f}%" if d["visible"] else f"{et} no visible")
        ne = r["no_explicado"]
        print(f"  {nombre:9s} retardo {r['retardo_s'] * 1000:4.0f} ms | " + " | ".join(partes) +
              (f" | anomalías en ciclos {ne['ciclos_anomalos']}" if ne["ciclos_anomalos"] else " | sin anomalías"))
    (raiz / "video_analisis.json").write_text(json.dumps(salida, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
