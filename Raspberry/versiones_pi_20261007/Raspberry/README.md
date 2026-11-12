# Control de marchas Nova desde Raspberry Pi

Esta carpeta reúne el planificador de marchas ROS 2 y herramientas de prueba.
Los nodos de marcha publican órdenes ROS 2; los programas independientes de
prueba de actuadores sí controlan PWM del PCA9685 cuando se ejecutan.

## Contenido

- `codigo/panel_marchas.py`: ventana con botones para postura, gateo y paso.
- `codigo/control_marchas_ros2.py`: publica una orden en `/nova/gait_command`.
- `marchas/tipos_de_marcha.py`: catálogo legible de las marchas disponibles.
- `configuracion/marchas.yaml`: parámetros nominales congelados.
- `configuracion/servos.yaml`: canales y calibraciones, bloqueadas inicialmente.
- `codigo/pca9685_seguro.py`: controlador PWM con `OE` y apagado global.
- `codigo/thonny_12_as5600_estabilidad.py`: captura desde Thonny de 100 muestras
  por cada uno de los doce AS5600; muestra estabilidad y guarda CSV en
  `Raspberry/datos/` sin generar PWM.
- `codigo/prueba_servo_individual_thonny.py`: prueba un servo continuo a baja
  velocidad durante 0,6 s y muestra el AS5600 asociado en vivo.
- `codigo/control_8_servos_continuos_thonny.py`: rutina histórica de movimiento
  multicanal; no usar para la primera prueba de servos continuos.
- `codigo/prueba_coxas_thonny.py`: prueba individual y limitada de las cuatro
  coxas en `CH0`--`CH3`, según el mapa de conexiones recibido el 15-09-2026.
- `codigo/prueba_femures_thonny.py`: prueba individual y limitada de los cuatro
  fémures en `CH4`--`CH7`.
- `codigo/prueba_tibias_thonny.py`: prueba individual y limitada de las cuatro
  tibias en `CH8`--`CH11`.
- `AVANCES_PRUEBA_CH0_CH10_2026-08-27.md`: registro de la prueba física
  satisfactoria de once canales desde Raspberry Pi y Thonny.
- `AVANCES_PRUEBA_COXAS_2026-09-15.md`: registro de la primera prueba de coxas.
- `codigo/interfaz_pwm_ros2.py`: conversión de trayectorias ROS 2 a PWM.
- `CONEXIONES.md`: mapa confirmado por imagen de patas, segmentos, números de
  servo y canales CH0--CH11 de la PCA9685.
- `conexiones_servo_cuadrupedo_2026-09-15.jpeg`: referencia visual de la
  numeración de patas y canales (`CH0`--`CH11`).
- `CONEXIONES_ELECTRONICAS_NOVASM3.pdf`: guía ilustrada de pines, materiales,
  alimentación, sensores y secuencia segura de puesta en marcha.
- `diagrama_conexion_servos.svg`: imagen vectorial revisada del cableado.
- `vista_cuadrupedo_servos.png`: seis vistas del robot con los canales CH0--CH11.
- `vista_cuadrupedo_servos_novasm3.png`: versión fiel al Nova Spot Micro 3
  amarillo y morado conservado en las referencias del proyecto.
- `mapa_articulaciones_novasm3_corregido.svg`: mapa autoritativo de los ejes,
  construido desde la cadena cinemática del URDF para evitar puntos ambiguos.
- `configuracion/calibracion_servos.csv`: hoja para registrar PWM, velocidad y torque.
- `seguridad/ANTES_DE_CONECTAR_SERVOS.md`: requisitos obligatorios de hardware.

El generador matemático utilizado realmente por ROS 2 permanece en
`../src/nova_gait_controller/nova_gait_controller/kinematics.py`, evitando
mantener dos copias que puedan divergir.

## Abrir en Thonny

En el computador actual:

```bash
cd /home/pavilion/Documentos/Cuadrupedo
source /opt/ros/humble/setup.bash
source install/setup.bash
thonny Raspberry/codigo/panel_marchas.py
```

En la Raspberry Pi, cambia la primera ruta por aquella donde copies el
proyecto. Selecciona el intérprete **Python 3 del sistema** en Thonny.

Para probar solamente el catálogo, sin ROS 2 ni movimiento:

```bash
python3 Raspberry/marchas/tipos_de_marcha.py
```

Para capturar una ronda de estabilidad de los doce AS5600 en Thonny, abre
`Raspberry/codigo/thonny_12_as5600_estabilidad.py`, describe la postura fija y
pulsa Enter. Guarda un CSV fechado en `Raspberry/datos/`; no controla los
servos. Las rutas de sensor usan el mapa confirmado, incluido Fémur 2 en
`0x71:5` y Coxa 2 en `0x71:6`.

## Estado actual del hardware

El archivo `Arduino/prueba_servos_uno/prueba_servos_uno.ino` es actualmente un
escáner I2C, no un controlador de movimiento. Para la prueba inicial de un
servomotor continuo usa el programa individual de Thonny descrito arriba.

El planificador `gateo` y `paso` funciona en simulación. La interfaz PWM inicial
queda incluida, pero arranca deshabilitada. Aún debe integrarse formalmente
como hardware `ros2_control` y validarse progresivamente.
La interfaz de trayectoria existente convierte posición angular directamente a
pulsos y rechaza la configuración `continuous_rotation`; falta implementar un
controlador de velocidad con realimentación AS5600 antes de ejecutar marchas.

El 7 de octubre de 2026, el operador confirmó mediante imagen la asignación
servo/canal de `CONEXIONES.md` y que las etiquetas Coxa/Fémur/Tibia de los
AS5600 corresponden a esas articulaciones. Las observaciones físicas previas
que no coincidan con el cableado nominal se mantienen pendientes de verificación;
la confirmación del mapa no calibra los servos ni habilita movimiento.

### Pruebas en Raspberry Pi 4 del 25 de agosto de 2026

Se conectó una Raspberry Pi 4 Model B Rev. 1.5 con un PCA9685 en el bus I2C 1.
El escaneo detectó la dirección principal `0x40` y la dirección All Call `0x70`.
Se comprobó la generación de PWM a 50 Hz y el apagado de las salidas al terminar
cada prueba.

Durante las pruebas se corrigieron dos detalles de `pca9685_seguro.py`:

- La inicialización limpia el bit `SLEEP` antes de reactivar el oscilador del
  PCA9685, incluso si otro programa dejó el chip dormido.
- La escritura de cada pulso comprueba también el byte alto del contador para
  evitar pulsos truncados en la placa ensayada.

**Corrección del operador (7 de octubre de 2026):** los servomotores son de
rotación continua. A 50 Hz, 1500 us (7,5 % de ciclo útil) es la orden nominal
de parada; pulsos menores y mayores ordenan giro en sentidos opuestos, con
velocidad creciente al alejarse de la parada. Por tanto, los barridos PWM
históricos de 1000 a 2000 us fueron órdenes de sentido/velocidad, no posiciones
angulares. Las capturas AS5600 proporcionan la realimentación angular.

Estas pruebas comprueban comunicación y movimiento manual, pero **no equivalen
a una calibración completa**. Para cada servo falta medir la parada exacta,
sentido, zona muerta y velocidad frente al PWM, además de corriente y torque.
Por esa razón `configuracion/servos.yaml` conserva
`hardware_ready: false` y las calibraciones en `false`.

Para repetir la prueba manual actual desde Thonny, abre y ejecuta:

```text
Raspberry/codigo/control_8_servos_continuos_thonny.py
```

Para probar un servo y observar su AS5600, abre en Thonny el programa individual.
Empieza con un servo, la plataforma sostenida y la parada física disponible:

```text
Raspberry/codigo/prueba_servo_individual_thonny.py
```

La prueba pide un canal y una orden cercana al neutro (`1480` o `1520 us`), la
mantiene como máximo 0,05 s, imprime las lecturas AS5600, exige 80° de margen a
los extremos y vuelve a `1500 us`. Con OE a GND, el cierre apaga canales con
`FULL_OFF`; el corte físico sigue siendo la parada de emergencia. Este margen
se amplió tras observar que el movimiento continuó durante la desaceleración.

La asignación de la imagen recibida el 15-09-2026 quedó confirmada como
cableado físico y se reflejó en `CONEXIONES.md`, `servos.yaml` y la hoja CSV.
Los diagramas antiguos pueden conservar etiquetas previas y deben actualizarse
antes de usarlos como guía de cableado.

El 27 de agosto de 2026 se amplió esta prueba hasta `CH10`. Los once canales
respondieron con PWM a 60 Hz, habilitación escalonada en 1500 us y barrido
gradual conjunto entre 1100 y 1900 us. Este resultado valida movimiento manual,
pero no sustituye la calibración individual ni autoriza todavía una marcha.

La Raspberry debe usar su propia alimentación. Los servos requieren una fuente
externa regulada de 5--6 V con capacidad de corriente suficiente y tierra común
con el PCA9685 y la Raspberry.

Para lanzar la interfaz en una Raspberry ya preparada:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 Raspberry/codigo/interfaz_pwm_ros2.py
```

La habilitación posterior se publica separadamente y solo será aceptada tras
completar la configuración:

```bash
ros2 topic pub --once /nova/hardware/enable std_msgs/msg/Bool "{data: true}"
```
