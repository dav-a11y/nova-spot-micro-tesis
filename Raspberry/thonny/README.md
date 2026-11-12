# Control desde la Raspberry con Thonny (sin Arduino)

Desde el 18 de octubre de 2026 la Raspberry Pi 4 controla el PCA9685 directamente.
- `robot_nova.py`: librería con el mapa de canales, los topes, el equilibrio de las coxas, la caminata base y la política PPO en NumPy. Es la misma lógica que el firmware `movimiento_suspendido_11_servos` del Uno.
- `caminata_thonny.py`: menú para Thonny (equilibrio, postura, caminata de 4 o 10 ciclos, soltar, apagar). Pide escribir `MOVER` antes de habilitar el PWM.
- `politica_v4_semilla37.npz`: política PPO v4 semilla 37 exportada con `exportar_politica_numpy.py` (en el PC). Coincide con SB3 con un error de 2,4·10⁻⁷.

## Conexión del PCA9685 a la Pi
VCC → pin 1 (3,3 V), SDA → pin 3, SCL → pin 5, GND → pin 6, OE → pin 11 (GPIO17). V+ va a la fuente de servos, con GND común. Comprobar `i2cdetect -y 1` → `0x40`.

## Pendiente
- La Pi no tiene entradas analógicas. Para leer los potenciómetros (MUX 16CH) hace falta un ADC I²C (p. ej. ADS1115) y los selectores S0–S3 en GPIO. Sin eso, la caminata base funciona en lazo abierto, pero la política PPO no se puede ejecutar (necesita F2, F4 y T2 medidos).
- La corrección de las coxas por sensor del Uno tampoco está disponible sin ADC; las coxas se sostienen en su ángulo fijo.
