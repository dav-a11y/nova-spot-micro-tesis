#!/usr/bin/env python3
"""Base SQLite para calibrar los 12 servos y almacenar telemetria real.

Uso:
  python3 base_datos_aprendizaje.py inicializar
  python3 base_datos_aprendizaje.py resumen

La adquisicion serie se activara cuando el firmware transmita lineas DATA.
No interpreta los limites declarados como limites seguros de movimiento.
"""

from __future__ import annotations

import argparse
import os
import select
import sqlite3
import termios
import time
from datetime import datetime, timezone
from pathlib import Path

RUTA_BD = Path(__file__).with_name("datos_cuadrupedo.sqlite")

# Los dos extremos se conservan tal como los declaro el operador.  Los campos
# seguro_min/seguro_max quedan nulos hasta obtener medidas y validar roces.
ARTICULACIONES = (
    ("coxa1", 0, 150, "arriba", 95, "abajo", 180, ""),
    ("coxa2", 1, 40, "arriba", 95, "abajo", 0, ""),
    ("coxa3", 2, 55, "arriba", 100, "abajo", 15, ""),
    ("coxa4", 3, 147, "arriba", 115, "abajo", 180, ""),
    ("femur1", 4, 110, "delante", 20, "atras", 180,
     "El extremo atras puede chocar con el palo."),
    ("femur2", 5, 100, "delante", 180, "atras", 15,
     "El extremo atras puede chocar con el palo."),
    ("femur3", 6, 100, "delante", 30, "atras", 170, ""),
    ("femur4", 7, 100, "delante", 180, "atras", 15, ""),
    ("tibia1", 8, 100, "delante", 15, "atras", 170, ""),
    ("tibia2", 9, 80, "delante", 15, "atras", 100,
     "Limites corregidos por el operador; validar gradualmente."),
    ("tibia3", 10, 100, "delante", 1, "atras", 170, ""),
    ("tibia4", 11, 70, "delante", 160, "atras", 5, ""),
)

ESQUEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS articulacion (
  id INTEGER PRIMARY KEY,
  nombre TEXT NOT NULL UNIQUE,
  canal_pca INTEGER NOT NULL UNIQUE CHECK(canal_pca BETWEEN 0 AND 11),
  canal_mux INTEGER UNIQUE,
  posicion_estatica_deg INTEGER NOT NULL CHECK(posicion_estatica_deg BETWEEN 0 AND 180),
  etiqueta_extremo_a TEXT NOT NULL,
  extremo_a_deg INTEGER NOT NULL CHECK(extremo_a_deg BETWEEN 0 AND 180),
  etiqueta_extremo_b TEXT NOT NULL,
  extremo_b_deg INTEGER NOT NULL CHECK(extremo_b_deg BETWEEN 0 AND 180),
  seguro_min_deg INTEGER,
  seguro_max_deg INTEGER,
  habilitada INTEGER NOT NULL DEFAULT 0 CHECK(habilitada IN (0, 1)),
  observacion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS conexion_confirmada (
  servo_numero INTEGER PRIMARY KEY CHECK(servo_numero BETWEEN 1 AND 12),
  pata INTEGER NOT NULL CHECK(pata BETWEEN 1 AND 4),
  ubicacion TEXT NOT NULL,
  segmento TEXT NOT NULL CHECK(segmento IN ('coxa', 'femur', 'tibia')),
  canal_pca INTEGER NOT NULL UNIQUE CHECK(canal_pca BETWEEN 0 AND 11),
  fuente TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sesion (
  id INTEGER PRIMARY KEY,
  inicio_utc TEXT NOT NULL,
  proposito TEXT NOT NULL,
  firmware TEXT NOT NULL,
  sensor_mapeado INTEGER NOT NULL DEFAULT 0 CHECK(sensor_mapeado IN (0, 1)),
  valida_para_aprendizaje INTEGER NOT NULL DEFAULT 0 CHECK(valida_para_aprendizaje IN (0, 1)),
  notas TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS trama (
  id INTEGER PRIMARY KEY,
  sesion_id INTEGER NOT NULL REFERENCES sesion(id),
  tiempo_arduino_ms INTEGER NOT NULL,
  estado TEXT NOT NULL,
  orden_ch0 INTEGER NOT NULL, orden_ch1 INTEGER NOT NULL,
  orden_ch2 INTEGER NOT NULL, orden_ch3 INTEGER NOT NULL,
  orden_ch4 INTEGER NOT NULL, orden_ch5 INTEGER NOT NULL,
  orden_ch6 INTEGER NOT NULL, orden_ch7 INTEGER NOT NULL,
  orden_ch8 INTEGER NOT NULL, orden_ch9 INTEGER NOT NULL,
  orden_ch10 INTEGER NOT NULL, orden_ch11 INTEGER NOT NULL,
  adc_ch0 INTEGER NOT NULL, adc_ch1 INTEGER NOT NULL,
  adc_ch2 INTEGER NOT NULL, adc_ch3 INTEGER NOT NULL,
  adc_ch4 INTEGER NOT NULL, adc_ch5 INTEGER NOT NULL,
  adc_ch6 INTEGER NOT NULL, adc_ch7 INTEGER NOT NULL,
  adc_ch8 INTEGER NOT NULL, adc_ch9 INTEGER NOT NULL,
  adc_ch10 INTEGER NOT NULL, adc_ch11 INTEGER NOT NULL,
  adc_ch12 INTEGER NOT NULL, adc_ch13 INTEGER NOT NULL,
  adc_ch14 INTEGER NOT NULL, adc_ch15 INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_trama_sesion_tiempo ON trama(sesion_id, tiempo_arduino_ms);
"""


def abrir() -> sqlite3.Connection:
    conexion = sqlite3.connect(RUTA_BD)
    conexion.executescript(ESQUEMA)
    return conexion


def inicializar() -> None:
    with abrir() as conexion:
        for fila in ARTICULACIONES:
            conexion.execute(
                """INSERT INTO articulacion
                   (nombre, canal_pca, posicion_estatica_deg, etiqueta_extremo_a,
                    extremo_a_deg, etiqueta_extremo_b, extremo_b_deg, observacion)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(nombre) DO UPDATE SET
                     canal_pca=excluded.canal_pca,
                     posicion_estatica_deg=excluded.posicion_estatica_deg,
                     etiqueta_extremo_a=excluded.etiqueta_extremo_a,
                     extremo_a_deg=excluded.extremo_a_deg,
                     etiqueta_extremo_b=excluded.etiqueta_extremo_b,
                     extremo_b_deg=excluded.extremo_b_deg,
                     observacion=excluded.observacion""",
                fila,
            )
        mapa = (
            (1, 1, "delantera derecha", "coxa", 0),
            (5, 1, "delantera derecha", "femur", 4),
            (9, 1, "delantera derecha", "tibia", 8),
            (2, 2, "delantera izquierda", "coxa", 1),
            (6, 2, "delantera izquierda", "femur", 5),
            (10, 2, "delantera izquierda", "tibia", 9),
            (3, 3, "trasera derecha", "coxa", 2),
            (7, 3, "trasera derecha", "femur", 6),
            (11, 3, "trasera derecha", "tibia", 10),
            (4, 4, "trasera izquierda", "coxa", 3),
            (8, 4, "trasera izquierda", "femur", 7),
            (12, 4, "trasera izquierda", "tibia", 11),
        )
        for servo_numero, pata, ubicacion, segmento, canal in mapa:
            conexion.execute(
                """INSERT INTO conexion_confirmada
                   (servo_numero, pata, ubicacion, segmento, canal_pca, fuente)
                   VALUES (?, ?, ?, ?, ?, 'esquema del operador y movimiento observado')
                   ON CONFLICT(servo_numero) DO UPDATE SET
                     pata=excluded.pata, ubicacion=excluded.ubicacion,
                     segmento=excluded.segmento, canal_pca=excluded.canal_pca,
                     fuente=excluded.fuente""",
                (servo_numero, pata, ubicacion, segmento, canal),
            )
    print(f"Base inicializada: {RUTA_BD}")


def resumen() -> None:
    with abrir() as conexion:
        print("Canal | Articulacion | estatica | extremos declarados | estado")
        for fila in conexion.execute(
            """SELECT canal_pca, nombre, posicion_estatica_deg,
                      etiqueta_extremo_a, extremo_a_deg, etiqueta_extremo_b,
                      extremo_b_deg, observacion
               FROM articulacion ORDER BY canal_pca"""
        ):
            canal, nombre, centro, ea, va, eb, vb, nota = fila
            estado = "PENDIENTE" if nota else "sin validar"
            print(f"CH{canal:02d} | {nombre:7s} | {centro:3d} | {ea}={va}, {eb}={vb} | {estado}")
        cantidad = conexion.execute("SELECT COUNT(*) FROM trama").fetchone()[0]
        print(f"Tramas reales almacenadas: {cantidad}")
        print("Mapa de actuadores PCA9685 confirmado:")
        for fila in conexion.execute(
            "SELECT servo_numero, pata, ubicacion, segmento, canal_pca FROM conexion_confirmada ORDER BY servo_numero"
        ):
            servo_numero, pata, ubicacion, segmento, canal = fila
            print(f"  Servo {servo_numero:02d}: pata {pata} ({ubicacion}), {segmento}, PCA CH{canal}")


def configurar_puerto(fd: int) -> None:
    atributos = termios.tcgetattr(fd)
    atributos[0] = 0
    atributos[1] = 0
    atributos[2] = termios.CLOCAL | termios.CREAD | termios.CS8
    atributos[3] = 0
    atributos[4] = termios.B115200
    atributos[5] = termios.B115200
    atributos[6][termios.VMIN] = 0
    atributos[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, atributos)


def convertir_trama(linea: str) -> tuple[int, str, list[int]] | None:
    campos = linea.strip().split(",")
    # DATA,ms,estado,12 ordenes,16 ADC = 31 campos.
    if len(campos) != 31 or campos[0] != "DATA":
        return None
    try:
        return int(campos[1]), campos[2], [int(valor) for valor in campos[3:]]
    except ValueError:
        return None


def capturar(puerto: str, segundos: float, proposito: str, orden: str | None) -> None:
    with abrir() as conexion:
        sesion_id = conexion.execute(
            """INSERT INTO sesion(inicio_utc, proposito, firmware, notas)
               VALUES (?, ?, ?, ?)""",
            (datetime.now(timezone.utc).isoformat(), proposito,
             "movimiento_suspendido_11_servos con telemetria",
             "Datos crudos: no validos para aprendizaje hasta mapear MUX y calibrar ADC."),
        ).lastrowid

        fd = os.open(puerto, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            configurar_puerto(fd)
            # Abrir USB reinicia el Uno; esperar al firmware evita perder la orden.
            time.sleep(2.0)
            if orden:
                os.write(fd, orden.encode("ascii"))
            inicio = time.monotonic()
            pendiente = b""
            almacenadas = 0
            while time.monotonic() - inicio < segundos:
                listo, _, _ = select.select([fd], [], [], 0.25)
                if not listo:
                    continue
                pendiente += os.read(fd, 4096)
                while b"\n" in pendiente:
                    cruda, pendiente = pendiente.split(b"\n", 1)
                    trama = convertir_trama(cruda.decode("ascii", errors="ignore"))
                    if trama is None:
                        diagnostico = cruda.decode("ascii", errors="ignore").strip()
                        if diagnostico.startswith("COXA4") or diagnostico.startswith("FEMUR"):
                            print(diagnostico, flush=True)
                        continue
                    tiempo_ms, estado, valores = trama
                    fila = (sesion_id, tiempo_ms, estado, *valores)
                    if len(fila) != 31:
                        raise ValueError(f"Trama incompleta: {len(fila)} valores")
                    conexion.execute(
                        """INSERT INTO trama(
                           sesion_id, tiempo_arduino_ms, estado,
                           orden_ch0, orden_ch1, orden_ch2, orden_ch3,
                           orden_ch4, orden_ch5, orden_ch6, orden_ch7,
                           orden_ch8, orden_ch9, orden_ch10, orden_ch11,
                           adc_ch0, adc_ch1, adc_ch2, adc_ch3,
                           adc_ch4, adc_ch5, adc_ch6, adc_ch7,
                           adc_ch8, adc_ch9, adc_ch10, adc_ch11,
                           adc_ch12, adc_ch13, adc_ch14, adc_ch15)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                   ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        fila,
                    )
                    almacenadas += 1
                    # Persiste muestras incluso si una captura larga se corta.
                    if almacenadas % 20 == 0:
                        conexion.commit()
            conexion.commit()
        finally:
            os.close(fd)
    print(f"Sesion {sesion_id}: {almacenadas} tramas crudas guardadas en {RUTA_BD}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("accion", choices=("inicializar", "resumen", "capturar"))
    parser.add_argument("--puerto", default="/dev/ttyACM0")
    parser.add_argument("--segundos", type=float, default=30.0)
    parser.add_argument("--proposito", default="calibracion_estatica")
    parser.add_argument("--orden", choices=("c", "m", "s", "p", "t", "a", "f", "k", "l", "q", "r", "u", "v", "w", "e", "g", "h", "j", "n", "o", "x", "z", "y", "b", "i", "&", "%", "#", "d", "6", "7", "8", "9", "0", "1", "2", "3", "4", "5"),
                        help="Orden enviada al Uno tras su arranque.")
    args = parser.parse_args()
    if args.accion == "inicializar":
        inicializar()
    elif args.accion == "resumen":
        resumen()
    else:
        capturar(args.puerto, args.segundos, args.proposito, args.orden)


if __name__ == "__main__":
    main()
