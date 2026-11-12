"""Prueba manual en Thonny: Raspberry Pi 4 + PCA9685.

Dependencia: adafruit-circuitpython-pca9685.
Detener otros controladores antes de ejecutar: apaga las 16 salidas.
Sujetar la pata sin carga. El primer pulso puede provocar un salto.
Buscar límites de movimiento libre, sin alcanzar el tope mecánico.
1500 µs no es un centro ni una posición segura validada.
No lee los AS5600 ni modifica los multiplexores o la inhibición por OE.
Stop de Thonny no sustituye un corte físico de alimentación.
"""

import time
import board
import busio
from adafruit_pca9685 import PCA9685

DIRECCION = 0x40
FRECUENCIA = 50
CANALES = {0: "Coxa 1", 4: "Fémur 1", 8: "Tibia 1"}

# Envolvente del programa, NO límites seguros calibrados.
PULSO_MIN = 500
PULSO_MAX = 2500

# Después de cada orden se retira PWM: la pata puede perder sujeción.
# Este tiempo no garantiza que el servo complete el movimiento.
TIEMPO_ACTIVO = 0.4

i2c = None
pca = None
registros = {}


def apagar():
    if pca is not None:
        for salida in pca.channels:
            salida.duty_cycle = 0


def probar(canal, pulso):
    if not PULSO_MIN <= pulso <= PULSO_MAX:
        raise ValueError(
            f"Pulso fuera de la envolvente {PULSO_MIN}–{PULSO_MAX} µs"
        )
    duty = round(pulso * pca.frequency * 65535 / 1_000_000)
    try:
        pca.channels[canal].duty_cycle = duty
        print(f"{CANALES[canal]} / CH{canal}: {pulso} µs")
        time.sleep(TIEMPO_ACTIVO)
    finally:
        pca.channels[canal].duty_cycle = 0
    print("PWM apagado.")


try:
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c, address=DIRECCION)
    apagar()
    pca.frequency = FRECUENCIA
    canal = 0
    pulso = None
    paso = 10
    sentido = 1

    print("""
PRUEBA MANUAL — PATA 1

c 0       Seleccionar coxa
c 4       Seleccionar fémur
c 8       Seleccionar tibia
p 1450    Aplicar un pulso de 1450 µs (solo ejemplo)
+         Avanzar un paso
-         Retroceder un paso
i         Invertir el sentido de + y -
paso 10   Cambiar el paso en µs (entre 5 y 50)
r         Repetir el último pulso
min       Anotar el último pulso como mínimo
max       Anotar el último pulso como máximo
lista     Mostrar valores anotados
off       Apagar todas las salidas
q         Apagar y salir

Cada orden de movimiento dura 0.4 segundos.
No hay pulso inicial automático.
Escribe cada orden y pulsa Enter.
""")

    while True:
        orden = input(f"[{CANALES[canal]}] > ").strip().lower().split()
        if not orden:
            continue
        comando = orden[0]
        try:
            if comando == "q":
                break
            elif comando == "off":
                apagar()
                print("Todas las salidas apagadas.")
            elif comando == "c" and len(orden) == 2:
                nuevo = int(orden[1])
                if nuevo not in CANALES:
                    raise ValueError("Elige 0, 4 u 8.")
                apagar()
                canal = nuevo
                pulso = None
                print("Introduce el pulso inicial con: p VALOR")
            elif comando == "paso" and len(orden) == 2:
                nuevo = int(orden[1])
                if not 5 <= nuevo <= 50:
                    raise ValueError("El paso debe estar entre 5 y 50 µs.")
                paso = nuevo
                print(f"Paso: {paso} µs")
            elif comando == "i":
                sentido *= -1
                print(
                    "Ahora + aumenta el pulso." if sentido == 1
                    else "Ahora + disminuye el pulso."
                )
            elif comando == "p" and len(orden) == 2:
                nuevo = int(orden[1])
                probar(canal, nuevo)
                pulso = nuevo
            elif comando in ("+", "-", "r"):
                if pulso is None:
                    raise ValueError("Primero indica un pulso con: p VALOR")
                nuevo = pulso
                if comando == "+":
                    nuevo += paso * sentido
                elif comando == "-":
                    nuevo -= paso * sentido
                probar(canal, nuevo)
                pulso = nuevo
            elif comando in ("min", "max"):
                if pulso is None:
                    raise ValueError("Todavía no has aplicado ningún pulso.")
                valores = registros.setdefault(canal, {})
                otro = valores.get("max" if comando == "min" else "min")
                if otro is not None:
                    if comando == "min" and pulso >= otro:
                        raise ValueError("El mínimo debe ser menor al máximo.")
                    if comando == "max" and pulso <= otro:
                        raise ValueError("El máximo debe ser mayor al mínimo.")
                valores[comando] = pulso
                print(f"Anotado {comando}: {pulso} µs")
            elif comando == "lista":
                for ch, nombre in CANALES.items():
                    valores = registros.get(ch, {})
                    print(
                        f"{nombre} CH{ch}: "
                        f"mínimo {valores.get('min', '___')} µs, "
                        f"máximo {valores.get('max', '___')} µs"
                    )
            else:
                print("Orden desconocida o argumentos incorrectos.")
        except ValueError as error:
            print(error)

except KeyboardInterrupt:
    print("\nPrueba interrumpida.")
finally:
    try:
        apagar()
    finally:
        if pca is not None:
            pca.deinit()
        if i2c is not None:
            i2c.deinit()
    print("\nValores anotados:")
    for ch, valores in registros.items():
        print(f"{CANALES[ch]} CH{ch}: {valores}")
