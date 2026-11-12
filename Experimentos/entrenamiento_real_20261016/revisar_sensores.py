#!/usr/bin/env python3
"""Revisión de potenciómetros y encoders articulación por articulación (26-oct).

Lleva el robot a la postura base y mueve cada una de las 12 articulaciones por separado
(seno de 0,5 Hz, 2 ciclos; ±8° fémures y tibias, ±5° coxas, dentro de los topes), con las
demás quietas. Para cada articulación busca, entre todos los campos de la respuesta R, el
potenciómetro (C*) y el encoder (ENC_*) que mejor siguen la orden (correlación con retardo de
0 a 6 pasos) y da su ganancia (unidades/° de servo). También mide el ruido en reposo y las
lecturas perdidas (-1) de cada campo.

Uso: revisar_sensores.py [--salida revision_sensores_<fecha>.csv] [--amplitud 8]
  Con cámaras: grabar_caminata.py --nombre <n> --remota '' --ejecutor revisar_sensores.py -- --amplitud 15
Imprime la tabla y la guarda como .md junto al registro.
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
import ejecutar_politica_robot as R  # noqa: E402

FREC, CICLOS, DT = 0.5, 2, 0.03
NOMBRE = {0: "coxa", 1: "fémur", 2: "tibia"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=HERE / f"revision_sensores_{time.strftime('%Y%m%d_%H%M%S')}.csv")
    ap.add_argument("--amplitud", type=float, default=8.0, help="amplitud de fémures y tibias (°); coxas 5/8 de ella")
    ap.add_argument("--completo", action="store_true",
                    help="26-oct: lee los 16 canales del MUX (M0-M15) y los 16 encoders posibles (E70_0-E71_7)")
    a, _ = ap.parse_known_args()
    E.APERTURA_DEG = 8.0
    stand = np.tile(E.STAND, 4).astype(float)
    for pata, b in E.LEG_JOINT_BASE.items():
        stand[b + 1] = E.STAND[1] - E.apertura(pata)
    base = [int(np.clip(g, lo, hi)) for g, lo, hi in zip(R.a_grados_servo(stand), R.TOPE_MIN, R.TOPE_MAX)]
    cal = json.loads(R.CALIBRACION.read_text())
    esperado = {}                                    # canal -> campos de sensores_robot.json
    for n, c in cal.items():
        if isinstance(c, dict) and "campo" in c:
            pata = R.NUM_PATA[n.rsplit("_", 2)[0]]
            canal = (3 if "femur" in n else 7) + pata
            esperado[canal] = [c["campo"]] + ([c["respaldo"]["campo"]] if "respaldo" in c else []) + \
                (["(sin_sensor)"] if c.get("sin_sensor") else [])

    campos = R.SENSORES + ([f"M{c}" for c in range(16)] +
                           [f"E{0x70 if c < 8 else 0x71:x}_{c % 8}" for c in range(16)] if a.completo else [])
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"$" if a.completo else b"@")
    while True:
        l = lec.linea(timeout=8.0)
        if l is None:
            sys.exit("La interfaz de E/S no respondió STREAM_LISTO")
        if l.startswith("STREAM_LISTO"):
            break
    filas = []

    def enviar(g, canal):
        os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode())
        r = lec.linea(timeout=0.3)
        v = [int(x) for x in r.split(",")[2:]] if r and r.startswith("R,") else []
        v = (v + [-2] * len(campos))[:len(campos)]
        filas.append([time.time(), canal, *g, *v])
        time.sleep(DT)

    try:
        actual = list(R.BASE)
        while actual != base:
            actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, base)]
            enviar(actual, -2)
        for _ in range(70):                          # reposo: ruido de cada sensor
            enviar(base, -1)
        for canal in range(12):
            amp = a.amplitud * (5 / 8 if canal < 4 else 1.0)
            ti = time.time()
            while time.time() - ti < CICLOS / FREC:
                g = list(base)
                g[canal] = int(np.clip(round(base[canal] + amp * np.sin(2 * np.pi * FREC * (time.time() - ti))),
                                       R.TOPE_MIN[canal], R.TOPE_MAX[canal]))
                enviar(g, canal)
            for _ in range(25):
                enviar(base, -1)
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd)

    with a.salida.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "canal_movido", *[f"orden_{i}" for i in range(12)], *campos])
        w.writerows(filas)
    d = np.array(filas, float)
    sens = d[:, 14:]
    reposo = d[:, 1] == -1
    lineas = ["| Articulación | Canal | Esperado | Potenciómetro (r, k) | Encoder (r, k) | Estado |",
              "|---|---|---|---|---|---|"]
    for canal in range(12):
        m = d[:, 1] == canal
        orden = d[m, 2 + canal]
        mejor = {}
        for j, campo in enumerate(campos):
            if a.completo and j < len(R.SENSORES):
                continue                              # en modo completo se miran solo M* y E*
            x = sens[m, j]
            if (x < 0).mean() > 0.2 or np.ptp(x) == 0:
                continue
            for lag in range(7):
                o, s = orden[:len(orden) - lag], x[lag:]
                if np.std(o) == 0 or np.std(s) == 0:
                    continue
                r = np.corrcoef(o, s)[0, 1]
                tipo = "enc" if campo.startswith("E") else "pot"
                if abs(r) > abs(mejor.get(tipo, (0, 0, ""))[0]):
                    mejor[tipo] = (r, np.polyfit(o, s, 1)[0], campo)
        celdas = []
        for tipo in ("pot", "enc"):
            r, k, campo = mejor.get(tipo, (0, 0, ""))
            celdas.append(f"{campo} (r={r:.2f}, k={k:.2f})" if abs(r) >= 0.8 else
                          (f"débil: {campo} r={r:.2f}" if campo else "—"))
        ok = [mejor[t][2] for t in mejor if abs(mejor[t][0]) >= 0.8]
        esp = esperado.get(canal, [])
        if not ok:
            estado = "SIN LECTURA"
        elif esp and not set(esp) & set(ok):
            estado = "distinto del esperado"
        else:
            estado = "OK"
        pata = canal % 4 + 1
        lineas.append(f"| {NOMBRE[canal // 4]} {pata} | {canal} | {', '.join(esp) or '—'} | {celdas[0]} | {celdas[1]} | {estado} |")
    perdidas = {c: (sens[:, j] < 0).mean() for j, c in enumerate(campos)}
    ruido = {c: np.std(sens[reposo, j][sens[reposo, j] >= 0]) if (sens[reposo, j] >= 0).any() else np.nan
             for j, c in enumerate(campos)}
    lineas += ["", "| Campo | Lecturas perdidas | Ruido en reposo (desv. típica) |", "|---|---|---|"]
    lineas += [f"| {c} | {perdidas[c] * 100:.0f} % | {ruido[c]:.1f} |" for c in campos]
    texto = "\n".join(lineas)
    a.salida.with_suffix(".md").write_text(texto + "\n")
    print(texto)
    print(f"\nRegistro: {a.salida}")


if __name__ == "__main__":
    main()
