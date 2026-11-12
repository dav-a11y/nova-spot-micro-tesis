"""Prueba manual de 12 servos con Raspberry Pi 4 y PCA9685.

Conexiones I2C de la Raspberry Pi 4:
  pin físico 3  (GPIO2/SDA1) -> SDA del PCA9685
  pin físico 5  (GPIO3/SCL1) -> SCL del PCA9685
  pin físico 1  (3V3)        -> VCC del PCA9685
  pin físico 6  (GND)        -> GND del PCA9685
  OE puede quedar sin conectar; el programa usa el apagado interno FULL_OFF.

Los servos requieren una fuente externa adecuada de 5--6 V conectada a V+.
Nunca deben alimentarse desde el pin de 5 V de la Raspberry Pi.

Ejecutar desde Thonny únicamente después de asegurar mecánicamente los servos.
El programa no habilita ninguna salida hasta recibir la orden ARMAR.
"""

from time import sleep

from pca9685_seguro import PCA9685Seguro


NUM_SERVOS = 12
CANAL_PRUEBA = 6
PULSO_CENTRO_US = 1500
PULSO_MIN_US = 1300
PULSO_MAX_US = 1700
PASO_US = 10
ESPERA_S = 0.03


def main():
    controlador = None
    try:
        controlador = PCA9685Seguro(
            bus_number=1,
            address=0x40,
            frequency_hz=50,
            # Sin OE físico no se necesita /dev/mem ni ejecutar como root.
            oe_bcm_gpio=None,
        )

        print("PCA9685 detectado. Las salidas permanecen DESHABILITADAS.")
        print("Prueba continua únicamente en el canal CH6.")
        if input("Escriba PROBAR 6 para comenzar: ").strip() != "PROBAR 6":
            print("Operación cancelada sin mover servos.")
            return

        # Apaga expresamente todos los canales, luego precarga solo CH6.
        for canal in range(16):
            controlador.prepare_channel_off(canal)
        controlador.prepare_pulse_us(CANAL_PRUEBA, PULSO_CENTRO_US)
        controlador.arm()

        print("CH6 activo. Pulse Ctrl+C para detenerlo.")
        while True:
            for pulso in range(PULSO_MIN_US, PULSO_MAX_US + 1, PASO_US):
                controlador.set_pulse_us(CANAL_PRUEBA, pulso)
                sleep(ESPERA_S)
            for pulso in range(PULSO_MAX_US, PULSO_MIN_US - 1, -PASO_US):
                controlador.set_pulse_us(CANAL_PRUEBA, pulso)
                sleep(ESPERA_S)

    except (KeyboardInterrupt, EOFError):
        print("\nParada solicitada.")
    except Exception as error:
        print("ERROR:", error)
        print("Revise I2C, dirección 0x40, alimentación y dependencias.")
    finally:
        if controlador is not None:
            controlador.close()
        print("PWM deshabilitado y OE puesto en estado seguro.")


if __name__ == "__main__":
    main()
