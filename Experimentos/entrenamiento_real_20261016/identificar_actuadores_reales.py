#!/usr/bin/env python3
"""Identifica retardo y ganancia de las articulaciones del robot real a partir
de las caminatas `b` registradas por el Arduino Uno (sensores via MUX 16CH).

Fuente: ~/CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite (tabla trama).
Escala ADC->grado: ~2.45 cuentas/grado (fémures y tibias medidos el 16-oct);
el signo se toma de la correlación. Solo lee datos guardados.
"""
import json, sqlite3, sys
from pathlib import Path
import numpy as np

DB = Path.home() / "CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite"
OUT = Path(__file__).with_name("actuadores_reales.json")
CUENTAS_POR_GRADO = 2.45
# (nombre, indice de orden en la trama, canal MUX, articulacion MuJoCo)
SENSADAS = [
    ("Femur 2", 5, 5, "front_left_femur_joint"),
    ("Femur 4", 7, 6, "rear_left_femur_joint"),
    ("Tibia 2", 9, 9, "front_left_tibia_joint"),
    ("Tibia 3", 10, 11, "rear_right_tibia_joint"),
    ("Tibia 4", 11, 10, "rear_left_tibia_joint"),
]

def medfilt(x, k=5):
    p = k // 2; xp = np.pad(x, p, mode="edge")
    return np.array([np.median(xp[i:i + k]) for i in range(len(x))])

def main(sesiones):
    c = sqlite3.connect(DB)
    res = {}
    for nombre, j, ch, junta in SENSADAS:
        filas = []
        for s in sesiones:
            filas += c.execute(
                f"select orden_ch{j}, adc_ch{ch} from trama where sesion_id=? "
                "and estado='CAMINATA_FASE' order by id", (s,)).fetchall()
        o = np.array([f[0] for f in filas], float); a = medfilt(np.array([f[1] for f in filas], float))
        if o.std() == 0:
            continue
        mejor = max(((np.corrcoef(o[:len(o) - l], a[l:])[0, 1], l) for l in range(5)),
                    key=lambda t: abs(np.nan_to_num(t[0])))
        r, lag = mejor
        oo, aa = o[:len(o) - lag], a[lag:]
        pend = np.polyfit(oo, aa, 1)[0]
        ganancia = abs(pend) / CUENTAS_POR_GRADO
        fiable = bool(abs(r) >= 0.6)
        res[junta] = dict(nombre=nombre, r=round(float(r), 3), retardo_s=round(lag * 0.1, 2),
                          ganancia=round(float(min(ganancia, 1.2)), 3), fiable=fiable,
                          muestras=len(o))
        print(f"{nombre:8s} r={r:+.2f} retardo={lag*100:3d} ms ganancia={ganancia:.2f} "
              f"{'fiable' if fiable else 'NO fiable (no se usa)'}")
    validos = [v for v in res.values() if v["fiable"]]
    resumen = dict(
        sesiones=sesiones,
        retardo_s=float(np.median([v["retardo_s"] for v in validos])) if validos else 0.1,
        ganancia=float(np.median([v["ganancia"] for v in validos])) if validos else 1.0,
        articulaciones=res,
        tibia1_sin_pwm=True,
        coxas_fijas_grados={"coxa1": 150, "coxa2": 45, "coxa3": 55, "coxa4": 150},
    )
    OUT.write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print("Modelo de actuador:", {k: resumen[k] for k in ("retardo_s", "ganancia")}, "->", OUT)

if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or [131, 135, 136])
