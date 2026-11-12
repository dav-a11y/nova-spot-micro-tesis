#!/usr/bin/env python3
"""Propone el canal MUX de cada servo a partir de una sesión `--orden c`."""

from __future__ import annotations

import argparse
import statistics
import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).with_name("datos_cuadrupedo.sqlite")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sesion", type=int)
    parser.add_argument("--estado", default="CAL",
                        help="Estado de movimiento a analizar (por defecto: CAL).")
    args = parser.parse_args()

    with sqlite3.connect(RUTA_BD) as db:
        articulaciones = db.execute(
            "SELECT nombre, posicion_estatica_deg FROM articulacion ORDER BY canal_pca"
        ).fetchall()
        filas = db.execute(
            """SELECT orden_ch0, orden_ch1, orden_ch2, orden_ch3,
                      orden_ch4, orden_ch5, orden_ch6, orden_ch7,
                      orden_ch8, orden_ch9, orden_ch10, orden_ch11,
                      adc_ch0, adc_ch1, adc_ch2, adc_ch3,
                      adc_ch4, adc_ch5, adc_ch6, adc_ch7,
                      adc_ch8, adc_ch9, adc_ch10, adc_ch11,
                      adc_ch12, adc_ch13, adc_ch14, adc_ch15
               FROM trama WHERE sesion_id=? AND estado=?""",
            (args.sesion, args.estado),
        ).fetchall()

    if not filas:
        raise SystemExit(f"No hay tramas {args.estado} en esa sesion.")

    print("Servo     | MUX candidato | ADC(-8) | ADC(+8) | delta | n-/n+ | corr max | calidad")
    for indice, (nombre, centro) in enumerate(articulaciones):
        ordenes = [fila[indice] for fila in filas]
        media_orden = statistics.mean(ordenes)
        suma_orden = sum((valor - media_orden) ** 2 for valor in ordenes)
        correlaciones = []
        for mux in range(16):
            lecturas = [fila[12 + mux] for fila in filas]
            media_adc = statistics.mean(lecturas)
            suma_adc = sum((valor - media_adc) ** 2 for valor in lecturas)
            covarianza = sum((orden - media_orden) * (adc - media_adc)
                             for orden, adc in zip(ordenes, lecturas))
            correlacion = (covarianza / (suma_orden * suma_adc) ** 0.5
                           if suma_orden and suma_adc else 0.0)
            correlaciones.append(correlacion)
        mejor_correlacion_mux = max(range(16), key=lambda mux: abs(correlaciones[mux]))
        correlacion_texto = f"CH{mejor_correlacion_mux:02d} {correlaciones[mejor_correlacion_mux]:+.2f}"

        negativos = [fila for fila in filas if fila[indice] <= centro - 7]
        positivos = [fila for fila in filas if fila[indice] >= centro + 7]
        if len(negativos) < 3 or len(positivos) < 3:
            print(f"{nombre:9s} | sin mesetas ±7° | {correlacion_texto:14s} | sin contraste de mesetas")
            continue
        deltas = []
        ruidos = []
        for mux in range(16):
            adc_neg = [fila[12 + mux] for fila in negativos]
            adc_pos = [fila[12 + mux] for fila in positivos]
            delta = statistics.median(adc_pos) - statistics.median(adc_neg)
            ruido = (statistics.pstdev(adc_neg) ** 2 +
                     statistics.pstdev(adc_pos) ** 2) ** 0.5
            deltas.append(delta)
            ruidos.append(ruido)
        # Resta el desplazamiento común que aparece simultáneamente en varios
        # canales por ruido eléctrico o por entradas todavía compartidas.
        desplazamiento_comun = statistics.median(deltas)
        candidatos = []
        for mux, delta in enumerate(deltas):
            residual = delta - desplazamiento_comun
            ruido = ruidos[mux]
            candidatos.append((abs(residual) / (ruido + 1), mux,
                               delta, residual, ruido))
        _, mux, delta, residual, ruido = max(candidatos)
        calidad = "respuesta clara" if abs(residual) >= 12 and abs(residual) >= 2 * ruido else "sin señal concluyente"
        print(f"{nombre:9s} | CH{mux:02d}          | delta {delta:+5.1f} | diferencial {residual:+5.1f} | ruido {ruido:4.1f} | n-/n+ {len(negativos):2d}/{len(positivos):2d} | {correlacion_texto:14s} | {calidad}")


if __name__ == "__main__":
    main()
