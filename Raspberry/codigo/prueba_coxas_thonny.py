"""Prueba individual de las cuatro coxas según el mapa de conexiones.

Canales del PCA9685: CH0=Pata 1 (delantera derecha), CH1=Pata 2
(delantera izquierda), CH2=Pata 3 (trasera derecha) y CH3=Pata 4
(trasera izquierda). Ejecutar con el robot elevado y con alimentación externa
de los servos.
"""

from time import sleep

from pca9685_seguro import PCA9685Seguro


COXAS = {
    0: "Pata 1 - delantera derecha",
    1: "Pata 2 - delantera izquierda",
    2: "Pata 3 - trasera derecha",
    3: "Pata 4 - trasera izquierda",
}
CENTRO_US = 1500
RECORRIDO_US = 150
PASO_US = 5
ESPERA_S = 0.04


def barrer(controlador, canal):
    """Recorre un canal alrededor del centro y vuelve a dejarlo centrado."""
    for pulso in range(CENTRO_US, CENTRO_US + RECORRIDO_US + 1, PASO_US):
        controlador.set_pulse_us(canal, pulso)
        sleep(ESPERA_S)
    for pulso in range(CENTRO_US + RECORRIDO_US, CENTRO_US - RECORRIDO_US - 1, -PASO_US):
        controlador.set_pulse_us(canal, pulso)
        sleep(ESPERA_S)
    for pulso in range(CENTRO_US - RECORRIDO_US, CENTRO_US + 1, PASO_US):
        controlador.set_pulse_us(canal, pulso)
        sleep(ESPERA_S)


def main():
    controlador = None
    try:
        controlador = PCA9685Seguro(
            bus_number=1,
            address=0x40,
            frequency_hz=50,
            oe_bcm_gpio=None,
        )
        print("Coxas detectadas en CH0, CH1, CH2 y CH3.")
        print("Asegure el robot elevado, la parada física y la fuente externa de 5-6 V.")
        if input("Escriba PROBAR COXAS para comenzar: ").strip() != "PROBAR COXAS":
            print("Operación cancelada sin mover servos.")
            return

        for canal in range(16):
            controlador.prepare_channel_off(canal)
        for canal in COXAS:
            controlador.prepare_pulse_us(canal, CENTRO_US)
        controlador.arm()

        print("Las cuatro coxas están centradas. Pulse Ctrl+C para detener.")
        for canal, nombre in COXAS.items():
            print(f"Probando CH{canal}: {nombre}")
            barrer(controlador, canal)
            controlador.set_pulse_us(canal, CENTRO_US)
            sleep(1.0)
        print("Prueba terminada; coxas centradas.")
    except (KeyboardInterrupt, EOFError):
        print("\nParada solicitada.")
    except Exception as error:
        print("ERROR:", error)
        print("Revise I2C, dirección 0x40, alimentación y dependencias.")
    finally:
        if controlador is not None:
            controlador.close()
        print("PWM deshabilitado y salidas apagadas.")


if __name__ == "__main__":
    main()
