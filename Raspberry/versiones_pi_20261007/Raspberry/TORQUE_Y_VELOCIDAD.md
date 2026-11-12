# Control de los servomotores de rotación continua

**Corrección confirmada por el operador (7 de octubre de 2026):** los
servomotores instalados son de rotación continua. A 50 Hz, el operador reporta
1500 µs (7,5 % de ciclo útil) como parada; pulsos menores hacen girar en un
sentido y mayores en el contrario. Cuanto más se aleja el pulso de la parada,
mayor es la velocidad. La relación exacta y la zona muerta deben medirse por
unidad; el rango indicado por el operador no se debe barrer sin calibración.

La orden PWM controla **sentido y velocidad**, no una posición angular. El
servomotor no informa su posición por la entrada PWM; el AS5600 montado en cada
articulación proporciona la lectura angular. Para alcanzar una postura, el
control deberá comparar continuamente el AS5600 con una referencia, reducir
la velocidad al aproximarse y ordenar parada. Hay que resolver el cruce de
0°/360° y fijar márgenes antes de mover cerca de los extremos verificados.

La primera prueba usa un solo servo, un pulso próximo a 1500 µs, duración corta,
y lectura simultánea del AS5600 asociado. Debe verificarse el pulso de parada,
sentido y cambio angular de cada unidad antes de controlar varias articulaciones.

El torque no se ordena por PWM. `torque_limit_nm` será un umbral del supervisor;
la medición requiere instrumentación externa o estimación con corriente y
modelo dinámico. `hardware_ready` permanece en `false`, y el controlador ROS 2
de posición directa debe quedar deshabilitado hasta implementar un lazo de
velocidad con realimentación AS5600.
