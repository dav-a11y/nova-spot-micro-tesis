"""Abrir en Thonny y pulsar F5. Ejemplo: MUEV CH0.

Requiere pca9685_seguro.py en esta misma carpeta. Solo controla canales;
la articulación conectada debe identificarse observando el robot.
"""
import math
import re
from time import sleep

from pca9685_seguro import PCA9685Seguro


def main():
    controlador = None
    pulso_us = 1500
    duracion_s = 0.2
    print('Robot suspendido; corte de alimentación accesible.')
    print('MUEV CH0 .. MUEV CH15: prueba un único canal y apaga al terminar.')
    print('PULSO 1500: cambia el pulso (1450..1550 microsegundos).')
    print('TIEMPO 0.2: cambia la duración (0.1..2 segundos).')
    print('PARAR: apaga salidas. SALIR: apaga y termina.')
    try:
        controlador = PCA9685Seguro(bus_number=1, address=0x40,
                                    frequency_hz=50, oe_bcm_gpio=17)
        while True:
            orden = input('\nOrden > ').strip().upper()
            if orden in ('SALIR', 'EXIT'):
                break
            if orden in ('PARAR', 'STOP'):
                controlador.all_off()
                print('Todos los canales apagados.')
                continue
            movimiento = re.fullmatch(r'(?:MUEV|MUEVE|MOVER)\s+CH\s*(\d{1,2})', orden)
            if movimiento:
                canal = int(movimiento.group(1))
                if not 0 <= canal <= 15:
                    print('Canal válido: CH0..CH15.')
                    continue
                print(f'CH{canal}: {pulso_us} us durante {duracion_s} s.', flush=True)
                try:
                    controlador.all_off()
                    controlador.arm()
                    controlador.set_pulse_us(canal, pulso_us)
                    sleep(duracion_s)
                finally:
                    controlador.all_off()
                print('PWM apagado. Observa qué articulación respondió.')
                continue
            partes = orden.split()
            if len(partes) == 2 and partes[0] in ('PULSO', 'TIEMPO'):
                try:
                    valor = float(partes[1].replace(',', '.'))
                except ValueError:
                    print('Escribe un número válido.')
                    continue
                if not math.isfinite(valor):
                    print('Escribe un número finito.')
                    continue
                if partes[0] == 'PULSO':
                    if not 1450 <= valor <= 1550:
                        print('Rango de prueba: 1450..1550 us.')
                        continue
                    pulso_us = valor
                else:
                    if not 0.1 <= valor <= 2:
                        print('Duración permitida: 0.1..2 segundos.')
                        continue
                    duracion_s = valor
                print(f'Configurado: {pulso_us} us, {duracion_s} s. Sin movimiento.')
                continue
            print('Ejemplo: MUEV CH0. Otros comandos: PULSO, TIEMPO, PARAR, SALIR.')
    except (KeyboardInterrupt, EOFError):
        print('\nParada solicitada.')
    except Exception as error:
        print(f'ERROR: {error}')
    finally:
        if controlador is not None:
            controlador.close()
        print('Programa terminado; PWM apagado.')


if __name__ == '__main__':
    main()
