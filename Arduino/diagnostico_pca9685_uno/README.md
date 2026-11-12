# Diagnóstico Uno → PCA9685 sin movimiento

Conserva el escáner existente en `../prueba_servos_uno/prueba_servos_uno.ino`.
Ese archivo actualmente solo escanea I2C; ya no contiene el barrido de servos
descrito en su README anterior.

Con la fuente de servos apagada y la Raspberry desconectada del PCA9685:

| Uno | PCA9685 |
|---|---|
| 5V | VCC |
| GND | GND |
| A4 | SDA |
| A5 | SCL |
| D7 | OE |

Retira los puentes temporales RESET–GND y RX–TX de la prueba USB, si existen.
OE no debe estar conectado a GND. Se recomienda la resistencia de 10 kohm
entre OE y VCC para mantener las salidas deshabilitadas durante el reinicio.
Sin esa resistencia, mantén V+ sin alimentación durante toda esta prueba.

1. Conecta el Uno por USB al equipo.
2. Abre `diagnostico_pca9685_uno.ino`, selecciona Arduino Uno y su puerto USB.
3. Carga y abre el Monitor serie a 115200 baudios.
4. Envía `I`: debe responder 0x40 con los puentes de dirección por defecto.
   Puede aparecer también 0x70, dirección All Call, del mismo PCA9685.
5. Envía `R`: consulta MODE1, MODE2 y PRE_SCALE en 0x40 sin configurar PWM.

Una respuesta I2C y la lectura de registros comprueban comunicación con el
dispositivo; no son una identificación inequívoca del chip, ni confirman
alimentación V+, pulsos reales o servos conectados. El MG996R estándar no
devuelve posición por su cable PWM. Eso requiere observar una prueba individual
o instrumentación adicional. Este diagnóstico nunca ordena movimiento.

Referencia: https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
