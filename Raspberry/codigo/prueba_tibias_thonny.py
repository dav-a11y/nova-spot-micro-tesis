"""Prueba individual de las cuatro tibias según el mapa confirmado.

CH8=Pata 1, CH9=Pata 2, CH10=Pata 3 y CH11=Pata 4. Ejecutar con el robot elevado.
"""

from time import sleep

from pca9685_seguro import PCA9685Seguro


TIBIAS = {
    8: "Pata 1 - delantera derecha",
    9: "Pata 2 - delantera izquierda",
    10: "Pata 3 - trasera derecha",
    11: "Pata 4 - trasera izquierda",
}
CENTRO_US = 1500
RECORRIDO_US = 100
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
        print("Tibias detectadas en CH8, CH9, CH10 y CH11.")
        print("Robot elevado, parada física y fuente externa de 5-6 V listas.")
        if input("Escriba PROBAR TIBIAS para comenzar: ").strip() != "PROBAR TIBIAS":
            print("Operación cancelada sin mover servos.")
            return
        for canal in range(16):
            controlador.prepare_channel_off(canal)
        for canal in TIBIAS:
            controlador.prepare_pulse_us(canal, CENTRO_US)
        controlador.arm()
        print("Tibias centradas. Pulse Ctrl+C para detener.")
        for canal, nombre in TIBIAS.items():
            print(f"Probando CH{canal}: {nombre}")
            barrer(controlador, canal)
            controlador.set_pulse_us(canal, CENTRO_US)
            sleep(1.0)
        print("Prueba terminada; tibias centradas.")
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
