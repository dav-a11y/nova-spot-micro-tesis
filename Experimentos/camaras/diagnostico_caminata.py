#!/usr/bin/env python3
"""Diagnóstico completo de una caminata grabada con grabar_caminata.py.

Sensores (caminata.csv), ciclo por ciclo:
- periodo de control real (mediana, p99, pasos > 40 ms);
- por articulación: correlación orden-medido, error RMS, desfase medio (deriva del
  sensor o del servo a lo largo de la caminata) y lecturas perdidas;
- coxas 2-4: desviación respecto al equilibrio (compensada con C0);
- desplazamiento común de los potenciómetros (C0) a lo largo del tiempo.
Cámaras (video.mkv y remota/video.mkv):
- fotogramas, fps real, huecos de tiempo (> 50 ms = fotogramas perdidos);
- brillo y nitidez (varianza del laplaciano) en la zona con movimiento;
- desfase real cámara-sensores: correlación entre el movimiento visible (diferencia
  entre fotogramas) y la velocidad de las órdenes. Si no es ~0, revisar la sincronía;
- detección de marcadores ArUco por ID (si están pegados).
Salidas en la carpeta: diagnostico.json y diagnostico.png.

Uso: python3 diagnostico_caminata.py grabaciones/<nombre>
"""
import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
CAL = json.loads((AQUI.parent / "entrenamiento_real_20261016/sensores_robot.json").read_text())
ARTICULACIONES = {
    "femur1": ("front_right_femur_joint", 4), "femur2": ("front_left_femur_joint", 5),
    "femur3": ("rear_right_femur_joint", 6), "femur4": ("rear_left_femur_joint", 7),
    "tibia1": ("front_right_tibia_joint", 8), "tibia2": ("front_left_tibia_joint", 9),
    "tibia3": ("rear_right_tibia_joint", 10), "tibia4": ("rear_left_tibia_joint", 11),
}
COXAS = {"coxa2": "C1", "coxa3": "C3", "coxa4": "C2"}
RETARDO_PASOS = 3


def sensores(carpeta):
    filas = list(csv.DictReader((carpeta / "caminata.csv").open()))
    col = lambda c: np.array([float(f[c]) for f in filas])
    t, fase = col("t"), col("fase")
    rampa = int(np.argmax(fase > 0)) if (fase > 0).any() else 0
    inicio_ciclos = [rampa] + [i for i in range(rampa + 1, len(fase)) if fase[i] < fase[i - 1]]
    ciclos = [(a, b) for a, b in zip(inicio_ciclos, inicio_ciclos[1:] + [len(fase)]) if b - a > 10]
    dt = np.diff(t) * 1000
    c0 = col("C0"); comun = c0 - c0[rampa]
    res = dict(pasos=len(filas), duracion_s=float(t[-1]), ciclos=len(ciclos),
               periodo_ms=dict(mediana=float(np.median(dt)), p99=float(np.percentile(dt, 99)),
                               maximo=float(dt.max()), pasos_mas_de_40ms=int((dt > 40).sum())),
               desplazamiento_comun_C0=dict(maximo_cuentas=float(np.abs(comun).max()),
                                            por_ciclo=[float(comun[a:b].mean()) for a, b in ciclos]),
               articulaciones={}, coxas={})
    series = dict(t=t, comun=comun, ciclos=ciclos)
    for corto, (nombre, i) in ARTICULACIONES.items():
        c = CAL[nombre]
        s = col(c["campo"])
        perdidas = s < 0
        if perdidas.mean() > 0.5 or c.get("sin_sensor"):   # caído en esta caminata o marcado sin sensor (21-oct)
            res["articulaciones"][corto] = dict(sensor=c["campo"], caido=True, lecturas_perdidas=int(len(s)))
            continue
        if perdidas.any():
            ok = ~perdidas
            s = np.interp(np.arange(len(s)), np.flatnonzero(ok), s[ok])
        if c["campo"].startswith("ENC"):
            s = np.degrees(np.unwrap(np.radians(s * 360.0 / 4096.0)))
        else:
            s = s - comun
        med = (s - s[rampa]) / c["k"]
        orden = col(f"orden_{i}") - col(f"orden_{i}")[rampa]
        o, m = orden[:-RETARDO_PASOS], med[RETARDO_PASOS:]
        por_ciclo = []
        for a, b in ciclos:
            b = min(b, len(o))
            if b - a < 10:
                continue
            oo, mm = o[a:b], m[a:b]
            por_ciclo.append(dict(r=float(np.corrcoef(oo, mm)[0, 1]) if oo.std() > 0 else 0.0,
                                  error_rms=float(np.sqrt(np.mean(((mm - mm.mean()) - (oo - oo.mean())) ** 2))),
                                  desfase=float((mm - oo).mean()),
                                  perdidas=int(perdidas[a:b].sum())))
        desf = [p["desfase"] for p in por_ciclo]
        res["articulaciones"][corto] = dict(
            sensor=c["campo"], r_medio=float(np.mean([p["r"] for p in por_ciclo])),
            r_minimo=float(np.min([p["r"] for p in por_ciclo])),
            error_rms_medio=float(np.mean([p["error_rms"] for p in por_ciclo])),
            deriva_desfase_grados=float(desf[-1] - desf[0]) if desf else 0.0,
            lecturas_perdidas=int(perdidas.sum()), por_ciclo=por_ciclo)
        series[corto] = (o, m)
    for n, c in COXAS.items():
        v = (col(c) - comun) / 2.45
        v = v - np.median(v[rampa:rampa + 20])
        res["coxas"][n] = dict(desviacion_media=float(np.abs(v[rampa:]).mean()),
                               p95=float(np.percentile(np.abs(v[rampa:]), 95)),
                               por_ciclo=[float(np.abs(v[a:b]).mean()) for a, b in ciclos])
        series[n] = v
    t0 = float((carpeta / "caminata.inicio.txt").read_text())
    velocidad = np.zeros(len(t))
    for _, i in ARTICULACIONES.values():
        velocidad[1:] += np.abs(np.diff(col(f"orden_{i}")))
    series["t_abs"], series["velocidad_orden"] = t0 + t, velocidad
    return res, series


def camara(video, inicio, t_orden, vel_orden):
    cap = cv2.VideoCapture(str(video))
    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters_create()
    ts, energia, brillo, nitidez, marcadores, previo = [], [], [], [], {}, None
    n = 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        n += 1
        ts.append(inicio + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        peq = cv2.resize(gris, (320, 180)).astype(np.float32)
        # Movimiento por bloques de 10×10 px (rejilla 18×32) para aislar las patas.
        dif = np.abs(peq - previo) if previo is not None else np.zeros_like(peq)
        energia.append(dif.reshape(18, 10, 32, 10).mean(axis=(1, 3)).ravel())
        previo = peq
        if n % 15 == 0:
            brillo.append(float(gris.mean()))
            nitidez.append(float(cv2.Laplacian(gris, cv2.CV_64F).var()))
            _, ids, _ = cv2.aruco.detectMarkers(gris, dic, parameters=params)
            for i in ([] if ids is None else ids.ravel().tolist()):
                marcadores[i] = marcadores.get(i, 0) + 1
    cap.release()
    ts, energia = np.array(ts), np.array(energia)
    huecos = np.diff(ts) * 1000
    # Desfase cámara-sensores: correlación cruzada entre el movimiento visible de los
    # bloques que siguen a las órdenes (las patas; no la gente del fondo) y la orden.
    dentro = (ts >= t_orden[0]) & (ts <= t_orden[-1])
    mejor = (0.0, 0.0)
    if dentro.sum() > 60:
        e = energia[dentro] - energia[dentro].mean(axis=0)
        e = e / (e.std(axis=0) + 1e-9)
        lags = np.arange(-0.5, 0.501, 0.01)
        corr = []
        for lag in lags:
            v = np.interp(ts[dentro] - lag, t_orden, vel_orden)
            v = (v - v.mean()) / (v.std() + 1e-9)
            corr.append(e.T @ v / len(v))
        corr = np.array(corr)                                  # lags × bloques
        patas = np.argsort(corr.max(axis=0))[-20:]            # 20 bloques más ligados a la orden
        perfil = corr[:, patas].mean(axis=1)
        k = int(np.argmax(perfil))
        mejor = (float(lags[k]), float(perfil[k]))
        energia = energia[:, patas].mean(axis=1)
    elif energia.ndim == 2 and len(energia):
        energia = energia.mean(axis=1)
    else:                                   # 21-oct: sin fotogramas útiles en la caminata
        energia = np.zeros(len(ts))
    muestras_marc = max(1, n // 15)
    return dict(
        fotogramas=n, fps_real=float(1000 / np.median(huecos)) if len(huecos) else 0.0,
        huecos_mas_de_50ms=int((huecos > 50).sum()), hueco_maximo_ms=float(huecos.max()) if len(huecos) else 0.0,
        brillo_medio=float(np.mean(brillo)) if brillo else 0.0,
        nitidez_media=float(np.mean(nitidez)) if nitidez else 0.0,
        retardo_movimiento_s=mejor[0], correlacion_movimiento=mejor[1],
        deteccion_marcadores={str(k): round(v / muestras_marc, 2) for k, v in sorted(marcadores.items())},
    ), (ts, energia)


def figura(carpeta, res, series, camaras):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(4, 1, figsize=(13, 13))
    nombres = list(ARTICULACIONES)
    nombres = [n for n in nombres if not res["articulaciones"][n].get("caido")]
    for n in nombres:
        pc = res["articulaciones"][n]["por_ciclo"]
        ax[0].plot([p["error_rms"] for p in pc], label=n)
    ax[0].set_title("Error RMS de seguimiento por ciclo (°)"); ax[0].legend(ncol=8, fontsize=8)
    for n in nombres:
        ax[1].plot([p["desfase"] for p in res["articulaciones"][n]["por_ciclo"]], label=n)
    ax[1].set_title("Desfase medio medido − orden por ciclo (°): deriva del sensor o del servo")
    for n in COXAS:
        ax[2].plot(series["t"], series[n], label=n, lw=0.8)
    ax[2].plot(series["t"], series["comun"] / 2.45, "k--", lw=0.8, label="desplazamiento común C0 (°)")
    ax[2].set_title("Coxas (compensadas) y desplazamiento común"); ax[2].legend(fontsize=8)
    t0 = series["t_abs"][0]
    v = series["velocidad_orden"]
    ax[3].plot(series["t_abs"] - t0, v / (v.max() or 1), "k", lw=0.8, label="velocidad de las órdenes")
    for nombre, (ts, e) in camaras.items():
        ax[3].plot(ts - t0, e / (e.max() or 1), lw=0.8, label=f"movimiento visible {nombre}")
    ax[3].set_xlim(0, min(30, series["t"][-1])); ax[3].legend(fontsize=8)
    ax[3].set_title("Sincronía cámara-sensores (primeros 30 s)"); ax[3].set_xlabel("s")
    fig.tight_layout(); fig.savefig(carpeta / "diagnostico.png", dpi=90)


def main():
    carpeta = Path(sys.argv[1])
    res, series = sensores(carpeta)
    camaras = {}
    camaras_dir = [("camara1", carpeta), ("camara2", carpeta / "remota")]
    camaras_dir += [(d.name.replace("extra_", "camara_"), d) for d in sorted(carpeta.glob("extra_*"))]
    for nombre, sub in camaras_dir:
        if (sub / "video.mkv").exists():
            inicio = float((sub / "video.inicio.txt").read_text())
            # 21-oct: si una cámara falla, se anota y el diagnóstico de sensores sigue.
        try:
            res[nombre], camaras[nombre] = camara(sub / "video.mkv", inicio, series["t_abs"], series["velocidad_orden"])
        except Exception as e:
            res[nombre] = dict(error=f"{type(e).__name__}: {e}")
    (carpeta / "diagnostico.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    try:
        figura(carpeta, res, series, camaras)
    except Exception as e:                  # 21-oct: la figura no debe impedir el diagnóstico
        print(f"AVISO: figura no generada ({type(e).__name__}: {e})")
    p = res["periodo_ms"]
    print(f"{carpeta.name}: {res['duracion_s']:.0f} s, {res['ciclos']} ciclos | periodo {p['mediana']:.1f} ms "
          f"(p99 {p['p99']:.0f}, máx {p['maximo']:.0f}, >40 ms: {p['pasos_mas_de_40ms']}) | "
          f"desplazamiento común máx {res['desplazamiento_comun_C0']['maximo_cuentas']:.0f} cuentas")
    for n, a in res["articulaciones"].items():
        if a.get("caido"):
            print(f"  {n:7s} {a['sensor']:7s} SENSOR CAÍDO: ninguna lectura válida")
            continue
        print(f"  {n:7s} {a['sensor']:7s} r {a['r_medio']:.3f} (mín {a['r_minimo']:.3f})  error {a['error_rms_medio']:.2f}°  "
              f"deriva {a['deriva_desfase_grados']:+.2f}°  perdidas {a['lecturas_perdidas']}")
    for n, c in res["coxas"].items():
        pc = c["por_ciclo"]
        print(f"  {n}: media {c['desviacion_media']:.2f}° p95 {c['p95']:.2f}° (primer ciclo {pc[0]:.2f}°, último {pc[-1]:.2f}°)")
    for nombre, _ in camaras_dir:
        if nombre in res:
            c = res[nombre]
            print(f"  {nombre}: {c['fotogramas']} fotogramas, {c['fps_real']:.1f} fps, huecos >50 ms {c['huecos_mas_de_50ms']} "
                  f"(máx {c['hueco_maximo_ms']:.0f} ms), brillo {c['brillo_medio']:.0f}, nitidez {c['nitidez_media']:.0f}, "
                  f"retardo movimiento {c['retardo_movimiento_s'] * 1000:+.0f} ms (r {c['correlacion_movimiento']:.2f}), "
                  f"marcadores {c['deteccion_marcadores'] or 'ninguno'}")


if __name__ == "__main__":
    main()
