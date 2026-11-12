# Avance Raspberry Pi, PCA9685 y servos CH0--CH10

Fecha: 27 de agosto de 2026, America/Bogota.

## Resultado

Se ejecutó satisfactoriamente desde Thonny una prueba de movimiento de once
servos conectados a los canales `CH0`--`CH10` del PCA9685. Primero se comprobó
el movimiento de canales individuales y luego se aumentó progresivamente la
cantidad de canales.

La prueba simultánea con cambios bruscos produjo poco o ningún movimiento. Al
reproducir la estrategia gradual empleada anteriormente con Arduino Mega, los
servos respondieron. Esto confirma la comunicación I2C, la generación de PWM y
el movimiento manual de `CH0`--`CH10`.

## Configuración que funcionó

- Raspberry Pi 4 y PCA9685 en el bus I2C 1.
- Dirección del PCA9685: `0x40`.
- Pin `OE` conectado directamente a tierra; en el programa se usa
  `oe_bcm_gpio=None`.
- Frecuencia PWM: 60 Hz.
- Canales activos: `CH0`--`CH10`.
- Centro de habilitación: 1500 microsegundos.
- Habilitación escalonada: un canal nuevo cada 3 segundos.
- Rango de barrido: 1100--1900 microsegundos.
- Incremento: 5 microsegundos.
- Intervalo entre referencias: 20 milisegundos.
- Repeticiones: tres ciclos completos.
- Apagado individual y global al finalizar o interrumpir la ejecución.

Programa utilizado: `Raspberry/codigo/control_8_servos_continuos_thonny.py`.

Controlador utilizado: `Raspberry/codigo/pca9685_seguro.py`.

## Interpretación

La respuesta mejoró al sustituir saltos grandes de PWM por una rampa. La
habilitación escalonada también reduce el pico de corriente inicial. La prueba
demuestra movimiento, pero no mide corriente ni confirma que la fuente soporte
una marcha bajo carga mecánica.

## Límites de lo validado

- `CH11` no formó parte de esta prueba.
- No se han medido los centros y extremos seguros de cada articulación.
- No se ha confirmado el sentido individual de los once servos.
- El barrido común no representa una caminata del cuadrúpedo.
- No se ha validado movimiento con el robot apoyado en el suelo.
- `hardware_ready` debe permanecer en `false`.

## Siguiente paso

Completar `CH11` y registrar por articulación el canal, centro, sentido, mínimo
y máximo mecánico seguro. Después se debe probar una pata suspendida mediante
una secuencia coordinada antes de intentar una marcha de las cuatro patas.
