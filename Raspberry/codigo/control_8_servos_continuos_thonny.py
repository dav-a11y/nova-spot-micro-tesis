"""Rutina histórica de barrido multicanal del PCA9685.

No usar para la primera prueba: activa varios canales y los MG996R del proyecto
son de rotación continua. Sus pulsos ordenan velocidad/dirección, no posición.
Usa prueba_servo_individual_thonny.py para un canal y lectura AS5600.
"""

from time import sleep

from pca9685_seguro import PCA9685Seguro


CANALES = list(range(11))
PULSO_MAXIMO_PRUEBA_US = 1900
PULSO_MINIMO_PRUEBA_US = 1100
PASO_US = 5
ESPERA_S = 0.02
REPETICIONES = 3


def main():
    controlador = None
    try:
        controlador = PCA9685Seguro(
            bus_number=1,
            address=0x40,
            frequency_hz=60,
            # OE está conectado directamente a GND en este montaje.
            oe_bcm_gpio=None,
        )
        for canal in range(16):
            controlador.prepare_channel_off(canal)

        controlador.arm()
        # Habilitación escalonada para evitar que siete servos arranquen en el
        # mismo instante y provoquen una caída de tensión.
        for canal in CANALES:
            print(f"Habilitando CH{canal} en 1500 us")
            controlador.set_pulse_us(canal, 1500)
            sleep(3.0)

        print("CH0--CH10 habilitados; iniciando rampa simultánea")
        for _ in range(REPETICIONES):
            for pulso_us in range(
                    PULSO_MINIMO_PRUEBA_US,
                    PULSO_MAXIMO_PRUEBA_US + 1,
                    PASO_US):
                for canal in CANALES:
                    controlador.set_pulse_us(canal, pulso_us)
                sleep(ESPERA_S)

            for pulso_us in range(
                    PULSO_MAXIMO_PRUEBA_US,
                    PULSO_MINIMO_PRUEBA_US - 1,
                    -PASO_US):
                for canal in CANALES:
                    controlador.set_pulse_us(canal, pulso_us)
                sleep(ESPERA_S)

        for canal in CANALES:
            controlador.set_channel_off(canal)

    except (KeyboardInterrupt, EOFError):
        pass
    except Exception as error:
        # Los errores sí se muestran para no ocultar fallos eléctricos o I2C.
        print("ERROR:", error)
    finally:
        if controlador is not None:
            controlador.close()


if __name__ == "__main__":
    main()
sev  
