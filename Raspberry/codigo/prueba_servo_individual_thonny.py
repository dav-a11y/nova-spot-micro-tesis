#!/usr/bin/env python3
"""Prueba un servo continuo, limita el arco por AS5600 y observa el sensor.

50 Hz: 1500 us (7.5 %) es la orden nominal de parada indicada por el operador.
1480/1520 us son ordenes de baja velocidad, cercanas a la parada.
El arco de prueba queda limitado por los extremos verificados por el operador.
"""

from time import monotonic, sleep

from leer_as5600_tca import AS5600Reader, SENSORS
from pca9685_seguro import PCA9685Seguro


# Canal PCA9685: (articulacion, descripcion)
ARTICULACIONES = {
    0: ("front_right_coxa_joint", "Pata 1 delantera derecha - Coxa 1, servo 1"),
    1: ("front_left_coxa_joint", "Pata 2 delantera izquierda - Coxa 2, servo 2"),
    2: ("rear_right_coxa_joint", "Pata 3 trasera derecha - Coxa 3, servo 3"),
    3: ("rear_left_coxa_joint", "Pata 4 trasera izquierda - Coxa 4, servo 4"),
    4: ("front_right_femur_joint", "Pata 1 delantera derecha - Femur 1, servo 5"),
    5: ("front_left_femur_joint", "Pata 2 delantera izquierda - Femur 2, servo 6"),
    6: ("rear_right_femur_joint", "Pata 3 trasera derecha - Femur 3, servo 7"),
    7: ("rear_left_femur_joint", "Pata 4 trasera izquierda - Femur 4, servo 8"),
    8: ("front_right_tibia_joint", "Pata 1 delantera derecha - Tibia 1, servo 9"),
    9: ("front_left_tibia_joint", "Pata 2 delantera izquierda - Tibia 2, servo 10"),
    10: ("rear_right_tibia_joint", "Pata 3 trasera derecha - Tibia 3, servo 11"),
    11: ("rear_left_tibia_joint", "Pata 4 trasera izquierda - Tibia 4, servo 12"),
}

PARADA_US = 1500
ORDEN_LENTA_MENOR_US = 1480
ORDEN_LENTA_MAYOR_US = 1520
MARGEN_EXTREMO_DEG = 80.0
DURACION_MOVIMIENTO_S = 0.05
PERIODO_LECTURA_S = 0.05

# Máximos de recorrido indicados por el operador: pareja de posturas que
# delimita el arco angular útil del sensor, en grados RAW del AS5600.
EXTREMOS_DEG = {
    "front_right_coxa_joint": (138.867, 128.036),
    "front_left_coxa_joint": (147.026, 164.883),
    "rear_right_coxa_joint": (174.381, 185.992),
    "rear_left_coxa_joint": (135.791, 167.081),
    "front_right_femur_joint": (246.288, 117.916),
    "front_left_femur_joint": (152.767, 148.441),
    "rear_right_femur_joint": (183.020, 30.772),
    "rear_left_femur_joint": (69.500, 103.638),
    "front_right_tibia_joint": (240.557, 75.497),
    "front_left_tibia_joint": (77.959, 233.965),
    "rear_right_tibia_joint": (239.955, 256.468),
    "rear_left_tibia_joint": (73.813, 301.904),
}


def leer_angulo(lector, sensor):
    """Lee el AS5600 asociado, reintentando hasta tres veces."""
    for _ in range(3):
        resultado = lector.read_sensor(sensor)
        if resultado["status"] == "ok":
            return resultado["angle_deg"]
    raise RuntimeError(
        f"No responde el AS5600 en 0x{sensor.tca:02X}/canal {sensor.channel}")


def diferencia_circular(actual, anterior):
    """Cambio firmado entre angulos consecutivos, incluso al cruzar 0/360."""
    return (actual - anterior + 180.0) % 360.0 - 180.0


def posicion_en_arco(angulo, extremo_a, extremo_b):
    """Devuelve (dentro, distancia al extremo más cercano) en arco menor."""
    paso_ab = (extremo_b - extremo_a) % 360.0
    if paso_ab <= 180.0:
        inicio, longitud = extremo_a, paso_ab
    else:
        inicio, longitud = extremo_b, 360.0 - paso_ab
    progreso = (angulo - inicio) % 360.0
    if progreso > longitud:
        return False, min(progreso - longitud, 360.0 - progreso)
    return True, min(progreso, longitud - progreso)


def main():
    print("PRUEBA DE UN SERVO CONTINUO + LECTURA AS5600")
    print("PCA9685 0x40 a 50 Hz; orden nominal de parada: 1500 us.")
    try:
        canal = int(input("Canal PCA9685 que probaras (0-11; empieza por CH0): "))
    except ValueError:
        print("Canal invalido; no se activo ningun servo.")
        return
    if canal not in ARTICULACIONES:
        print("Canal fuera de rango; no se activo ningun servo.")
        return

    sentido = input(
        f"Orden lenta: escribe M para {ORDEN_LENTA_MENOR_US} us o "
        f"Y para {ORDEN_LENTA_MAYOR_US} us: "
    ).strip().upper()
    if sentido not in ("M", "Y"):
        print("Orden invalida; no se activo ningun servo.")
        return
    pulso_movimiento = (ORDEN_LENTA_MENOR_US if sentido == "M"
                        else ORDEN_LENTA_MAYOR_US)
    articulacion, descripcion = ARTICULACIONES[canal]
    extremos = EXTREMOS_DEG[articulacion]
    sensor = next((item for item in SENSORS if item.joint == articulacion), None)
    if sensor is None:
        print("No hay sensor AS5600 asociado en el mapa; cancelado.")
        return

    print(f"CH{canal}: {descripcion}")
    print(f"AS5600: 0x{sensor.tca:02X}, canal {sensor.channel}")
    print(f"La orden {pulso_movimiento} us durara como maximo "
          f"{DURACION_MOVIMIENTO_S:.2f} s; despues se envia parada 1500 us.")
    print(f"Arco AS5600 permitido: {extremos[0]:.3f}° / {extremos[1]:.3f}°; "
          f"margen de {MARGEN_EXTREMO_DEG:.1f}°.")
    print("Robot sostenido, un MG996R conectado y parada fisica accesible.")
    if input(f"Escribe PROBAR CH{canal} para empezar: ").strip() != f"PROBAR CH{canal}":
        print("Cancelado; ningun servo se activo.")
        return

    controlador = None
    lector = None
    try:
        controlador = PCA9685Seguro(
            bus_number=1, address=0x40, frequency_hz=50, oe_bcm_gpio=None)
        lector = AS5600Reader(bus_number=1)
        # OE está físicamente a GND: limpiar FULL_OFF antes de permitir el
        # movimiento y mantener el corte físico accesible. La plataforma está
        # suspendida para que los otros canales apagados no soporten su peso.
        for otro_canal in range(16):
            controlador.prepare_channel_off(otro_canal)
        controlador.arm()
        controlador.set_pulse_us(canal, PARADA_US)
        sleep(0.5)
        angulo_anterior = leer_angulo(lector, sensor)
        dentro, margen = posicion_en_arco(angulo_anterior, *extremos)
        print(f"Inicio AS5600: {angulo_anterior:.3f}°; margen al extremo: "
              f"{margen:.3f}°")
        if not dentro or margen < MARGEN_EXTREMO_DEG:
            print("Prueba cancelada: lectura fuera del arco seguro o demasiado "
                  "cerca de un extremo verificado.")
            return

        controlador.set_pulse_us(canal, pulso_movimiento)
        inicio = monotonic()
        angulo_acumulado = 0.0
        while monotonic() - inicio < DURACION_MOVIMIENTO_S:
            sleep(PERIODO_LECTURA_S)
            actual = leer_angulo(lector, sensor)
            dentro, margen = posicion_en_arco(actual, *extremos)
            if not dentro or margen < MARGEN_EXTREMO_DEG:
                controlador.set_pulse_us(canal, PARADA_US)
                print("Parada preventiva: margen angular alcanzado.")
                break
            angulo_acumulado += diferencia_circular(actual, angulo_anterior)
            angulo_anterior = actual
            print(f"AS5600: {actual:.3f} grados; cambio acumulado: "
                  f"{angulo_acumulado:+.3f} grados; margen: {margen:.2f}°")

        controlador.set_pulse_us(canal, PARADA_US)
        print("Orden de parada enviada (1500 us).")
        sleep(0.5)
        print(f"Lectura final AS5600: {leer_angulo(lector, sensor):.3f} grados")
    except KeyboardInterrupt:
        print("\nInterrumpido; enviando orden de parada.")
    except Exception as error:
        print("ERROR durante la prueba:", error)
    finally:
        if controlador is not None:
            try:
                if controlador.armed:
                    controlador.set_pulse_us(canal, PARADA_US)
                    sleep(0.3)
            except Exception as error:
                print("No se pudo enviar parada por I2C:", error)
            controlador.close()  # OE alto y canales apagados al salir.
        print("Canales apagados por FULL_OFF. OE sigue conectado a GND; "
              "usa el corte fisico si hace falta.")
        if lector is not None:
            lector.close()


if __name__ == "__main__":
    main()
