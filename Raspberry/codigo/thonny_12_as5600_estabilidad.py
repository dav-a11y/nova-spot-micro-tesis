#!/usr/bin/env python3
"""Mide la estabilidad de los 12 AS5600 desde Thonny en Raspberry Pi.

Hace 100 barridos del mapa confirmado de sensores, resume cada articulación y
guarda las lecturas y estadísticas en Raspberry/datos. Solo lee AS5600 y cambia
la selección de los TCA9548A; no genera PWM ni mueve servos.
"""

import csv
import statistics
import time
from datetime import datetime
from pathlib import Path

from leer_as5600_tca import AS5600Reader, SENSORS


NUM_MUESTRAS = 100
PAUSA_BARRIDO_S = 0.5
UMBRAL_MUY_ESTABLE = 0.30
UMBRAL_ESTABLE = 0.70
UMBRAL_MODERADO = 1.50


def estado_estabilidad(variacion):
    if variacion <= UMBRAL_MUY_ESTABLE:
        return "SE MANTIENE MUY ESTABLE"
    if variacion <= UMBRAL_ESTABLE:
        return "SE MANTIENE ESTABLE"
    if variacion <= UMBRAL_MODERADO:
        return "EL VALOR VARIA MODERADAMENTE"
    return "EL VALOR ESTA VARIANDO MUCHO"


def guardar_csv(ruta, postura, valores, errores):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        campos = [
            "fecha_hora", "postura", "sensor", "articulacion", "tca",
            "canal_tca", "muestras_ok", "errores", "min_deg", "max_deg",
            "promedio_deg", "variacion_deg", "estado", "lecturas_deg",
        ]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        fecha = datetime.now().astimezone().isoformat(timespec="seconds")
        for sensor in SENSORS:
            etiqueta = sensor.label.upper()
            lecturas = valores[etiqueta]
            if lecturas:
                minimo = min(lecturas)
                maximo = max(lecturas)
                promedio = statistics.mean(lecturas)
                variacion = maximo - minimo
                estado = estado_estabilidad(variacion)
            else:
                minimo = maximo = promedio = variacion = ""
                estado = "SIN LECTURAS VALIDAS"
            escritor.writerow({
                "fecha_hora": fecha,
                "postura": postura,
                "sensor": etiqueta,
                "articulacion": sensor.joint,
                "tca": f"0x{sensor.tca:02X}",
                "canal_tca": sensor.channel,
                "muestras_ok": len(lecturas),
                "errores": errores[etiqueta],
                "min_deg": f"{minimo:.3f}" if lecturas else "",
                "max_deg": f"{maximo:.3f}" if lecturas else "",
                "promedio_deg": f"{promedio:.3f}" if lecturas else "",
                "variacion_deg": f"{variacion:.3f}" if lecturas else "",
                "estado": estado,
                "lecturas_deg": ";".join(f"{valor:.3f}" for valor in lecturas),
            })


def main():
    print("PRUEBA DE ESTABILIDAD: 12 AS5600 / 2 TCA9548A")
    print("100 muestras por articulacion; no se enviara PWM a los servos.")
    postura = input("Describe la postura que vas a mantener fija: ").strip()
    if not postura:
        postura = "sin especificar"
    input("Deja la plataforma quieta y pulsa Enter para iniciar la captura...")

    valores = {sensor.label.upper(): [] for sensor in SENSORS}
    errores = {sensor.label.upper(): 0 for sensor in SENSORS}
    lector = AS5600Reader(bus_number=1)
    inicio = time.monotonic()
    try:
        for numero_muestra in range(1, NUM_MUESTRAS + 1):
            inicio_barrido = time.monotonic()
            for sensor in SENSORS:
                resultado = None
                for intento in range(3):
                    resultado = lector.read_sensor(sensor)
                    if resultado["status"] == "ok":
                        break
                nombre = sensor.label.upper()
                if resultado["status"] == "ok":
                    valores[nombre].append(resultado["angle_deg"])
                else:
                    errores[nombre] += 1
                    print(
                        f"Error {nombre} TCA 0x{sensor.tca:02X}/ch{sensor.channel}: "
                        f"{resultado.get('error', 'lectura fallida')}"
                    )
            print(f"Barrido {numero_muestra}/{NUM_MUESTRAS} completado")
            restante = PAUSA_BARRIDO_S - (time.monotonic() - inicio_barrido)
            if restante > 0 and numero_muestra < NUM_MUESTRAS:
                time.sleep(restante)
    except KeyboardInterrupt:
        print("Captura interrumpida; se guardaran las muestras obtenidas.")
    finally:
        lector.close()

    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = Path(__file__).resolve().parents[1] / "datos" / (
        f"estabilidad_as5600_{marca_tiempo}.csv")
    guardar_csv(destino, postura, valores, errores)

    print("\nRESULTADOS (angulos absolutos del iman AS5600):")
    for sensor in SENSORS:
        nombre = sensor.label.upper()
        lecturas = valores[nombre]
        print(f"\n{nombre} | TCA 0x{sensor.tca:02X}, canal {sensor.channel}")
        print(f"Muestras: {len(lecturas)}/{NUM_MUESTRAS}; errores: {errores[nombre]}")
        if not lecturas:
            print("ESTADO: SIN LECTURAS VALIDAS")
            continue
        minimo = min(lecturas)
        maximo = max(lecturas)
        promedio = statistics.mean(lecturas)
        variacion = maximo - minimo
        print(f"Minimo: {minimo:.3f} grados")
        print(f"Maximo: {maximo:.3f} grados")
        print(f"Promedio: {promedio:.3f} grados")
        print(f"Variacion total: {variacion:.3f} grados")
        print(f"ESTADO: {estado_estabilidad(variacion)}")

    print(f"\nCSV guardado en: {destino}")
    print(f"Duracion: {time.monotonic() - inicio:.1f} s")
    print("Nota: el rango maximo-minimo no corrige el cruce angular 0/360.")
    print("Estas lecturas no son limites PWM ni autorizan movimiento.")


if __name__ == "__main__":
    main()
