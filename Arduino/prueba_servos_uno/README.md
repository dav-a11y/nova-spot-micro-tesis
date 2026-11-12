# Escáner I²C con Arduino Uno

El archivo `prueba_servos_uno.ino` actualmente escanea el bus I²C del Uno. No
controla servos ni corresponde a la prueba de Thonny de la Raspberry.

El operador confirmó que los servomotores del proyecto son de rotación
continua: a 50 Hz, el pulso nominal de parada es 1500 µs (7,5 %); pulsos
menores y mayores controlan sentido y velocidad. No deben interpretarse como
órdenes de posición angular.

Para la prueba individual con realimentación AS5600 desde Raspberry Pi, usa
`Raspberry/codigo/prueba_servo_individual_thonny.py` y sigue las condiciones
de `Raspberry/seguridad/ANTES_DE_CONECTAR_SERVOS.md`.
