"""Prueba individual de los cuatro fémures según el mapa confirmado.

CH4=Pata 1, CH5=Pata 2, CH6=Pata 3 y CH7=Pata 4. Ejecutar con el robot elevado.
"""

from time import sleep

from pca9685_seguro import PCA9685Seguro


FEMURES = {
    4: "Pata 1 - delantera derecha",
    5: "Pata 2 - delantera izquierda",
    6: "Pata 3 - trasera derecha",
    7: "Pata 4 - trasera izquierda",
}
CENTRO_US = 1500
RECORRIDO_US = 120
PASO_US = 5
ESPERA_S = 0.04


def barrer(controlador, canal):
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
        controlador = PCA9685Seguro(bus_number=1, address=0x40,
                                    frequency_hz=50, oe_bcm_gpio=None)
        print("Fémures detectados en CH4, CH5, CH6 y CH7.")
        print("Robot elevado, parada física y fuente externa de 5-6 V listas.")
        if input("Escriba PROBAR FEMURES para comenzar: ").strip() != "PROBAR FEMURES":
            print("Operación cancelada sin mover servos.")
            return
        for canal in range(16):
            controlador.prepare_channel_off(canal)
        for canal in FEMURES:
            controlador.prepare_pulse_us(canal, CENTRO_US)
        controlador.arm()
        print("Fémures centrados. Pulse Ctrl+C para detener.")
        for canal, nombre in FEMURES.items():
            print(f"Probando CH{canal}: {nombre}")
            barrer(controlador, canal)
            controlador.set_pulse_us(canal, CENTRO_US)
            sleep(1.0)
        print("Prueba terminada; fémures centrados.")
    except (KeyboardInterrupt, EOFError):
        print("\nParada solicitada.")
    except Exception as error:
        print("ERROR:", error)
    finally:
        if controlador is not None:
            controlador.close()
        print("PWM deshabilitado y salidas apagadas.")


if __name__ == "__main__":
    main()
