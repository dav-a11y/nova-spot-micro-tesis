# Antes de conectar los servos

No conectes simultáneamente los doce MG996R hasta completar estos puntos:

1. Fuente independiente para servos, dimensionada con mediciones reales.
2. Tierra común controlada entre lógica y potencia.
3. Fusible, cableado adecuado y parada física accesible.
4. Estado seguro y probado del pin `OE` del PCA9685.
5. Parada (pulso neutral), sentido, zona muerta y respuesta de velocidad PWM
   calibrados por servo, junto con su realimentación AS5600.
6. Prueba sin servos, luego con un servo y después con una pata suspendida.
7. Interfaz física `ros2_control` revisada y con límites por articulación.

Los programas de esta carpeta solo publican nombres de marcha en ROS 2. Una
orden `parar` no sustituye el corte físico de potencia.
