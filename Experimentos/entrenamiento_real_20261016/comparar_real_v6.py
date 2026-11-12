#!/usr/bin/env python3
"""Compara en el robot real una caminata base y una con PPO (registros del ejecutor v6).

Por articulación (8 fémures y tibias, sensores de sensores_robot.json, potenciómetros
compensados con C0):
- seguimiento: r y error RMS entre la orden y lo medido (con 87 ms de retardo);
- corrección: RMS de la orden PPO − nominal, y qué parte se realiza
  (medido_PPO − medido_base frente a la corrección pedida, paso a paso);
y la desviación de las coxas 2–4 respecto a su equilibrio (C1, C3, C2 compensados).

Uso: comparar_real_v6.py base/caminata.csv ppo/caminata.csv [--json salida.json]
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARTICULACIONES = {
    "femur1": ("front_right_femur_joint", 4), "femur2": ("front_left_femur_joint", 5),
    "femur3": ("rear_right_femur_joint", 6), "femur4": ("rear_left_femur_joint", 7),
    "tibia1": ("front_right_tibia_joint", 8), "tibia2": ("front_left_tibia_joint", 9),
    "tibia3": ("rear_right_tibia_joint", 10), "tibia4": ("rear_left_tibia_joint", 11),
}
COXAS = {"coxa2": "C1", "coxa3": "C3", "coxa4": "C2"}
RAMPA, RETARDO = 34, 3


def cargar(ruta, cal):
    filas = list(csv.DictReader(open(ruta)))[RAMPA:]
    col = lambda c: np.array([float(f[c]) for f in filas])
    c0 = col("C0"); c0 = c0 - c0[0]
    med = {}
    for corto, (nombre, i) in ARTICULACIONES.items():
        c = cal[nombre]
        s = col(c["campo"])
        if (s < 0).any():          # lecturas perdidas: se interpolan desde las válidas
            ok = s >= 0
            s = np.interp(np.arange(len(s)), np.flatnonzero(ok), s[ok])
            print(f"aviso: {nombre} ({c['campo']}) con {int((~ok).sum())} lecturas perdidas")
        if c["campo"].startswith("ENC"):
            s = np.degrees(np.unwrap(np.radians(s * 360.0 / 4096.0)))
        else:
            s = s - c0
        med[corto] = dict(orden=col(f"orden_{i}"), nominal=col(f"nominal_{i}"), medido=s / c["k"])
    coxas = {n: (col(c) - c0) / 2.45 for n, c in COXAS.items()}
    return med, coxas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("base"); p.add_argument("ppo"); p.add_argument("--json", type=Path)
    a = p.parse_args()
    cal = json.loads((HERE / "sensores_robot.json").read_text())
    mb, cb = cargar(a.base, cal)
    mp, cp = cargar(a.ppo, cal)
    res = {"articulaciones": {}, "coxas": {}}
    print(f"{'art.':7s} {'r base':>7s} {'err base':>8s} {'r ppo':>7s} {'err ppo':>8s} {'corr. pedida':>12s} {'realizada':>9s}")
    for n in ARTICULACIONES:
        fila = {}
        for etiqueta, m in (("base", mb[n]), ("ppo", mp[n])):
            o = m["orden"][:-RETARDO] - m["orden"][0]
            s = m["medido"][RETARDO:] - m["medido"][0]
            fila[f"r_{etiqueta}"] = float(np.corrcoef(o, s)[0, 1])
            fila[f"error_rms_{etiqueta}"] = float(np.sqrt(np.mean(((s - s.mean()) - (o - o.mean())) ** 2)))
        k = min(len(mb[n]["medido"]), len(mp[n]["medido"]))
        pedida = (mp[n]["orden"] - mp[n]["nominal"])[:k - RETARDO]
        real = ((mp[n]["medido"] - mp[n]["medido"][0]) - (mb[n]["medido"] - mb[n]["medido"][0]))[RETARDO:k]
        fila["correccion_rms_grados"] = float(np.sqrt(np.mean(pedida ** 2)))
        # Sin la componente constante: la referencia de cada registro ya incluye el residual inicial.
        pc, rc = pedida - pedida.mean(), real - real.mean()
        fila["realizada"] = float(pc @ rc / (pc @ pc)) if pc.any() else 0.0
        fila["r_correccion"] = float(np.corrcoef(pc, rc)[0, 1]) if pc.any() else 0.0
        res["articulaciones"][n] = fila
        print(f"{n:7s} {fila['r_base']:7.3f} {fila['error_rms_base']:7.2f}° {fila['r_ppo']:7.3f} {fila['error_rms_ppo']:7.2f}° "
              f"{fila['correccion_rms_grados']:11.2f}° {100 * fila['realizada']:8.0f}% (r={fila['r_correccion']:.2f})")
    for n in COXAS:
        d = {}
        for etiqueta, c in (("base", cb[n]), ("ppo", cp[n])):
            dev = np.abs(c - np.median(c[:20]))
            d[f"media_{etiqueta}"], d[f"p95_{etiqueta}"] = float(dev.mean()), float(np.percentile(dev, 95))
        res["coxas"][n] = d
        print(f"{n}: desviación media base {d['media_base']:.2f}° / PPO {d['media_ppo']:.2f}° "
              f"(p95 {d['p95_base']:.2f}° / {d['p95_ppo']:.2f}°)")
    if a.json:
        a.json.write_text(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
