# Control discreto del cuadrúpedo NovaSM3

Este workspace controla las 12 articulaciones del modelo NovaSM3 mediante una
máquina de estados finitos. El alcance principal incluye:

- **Gateo (`crawl`)**: ciclo cartesiano de 24 referencias, con orden previsto
  FL--RR--FR--RL.
- **Marcha paso (`step`)**: ciclo cartesiano de 32 referencias con transferencia
  lateral de peso, validado en Gazebo y MuJoCo.

El **galope (`gallop`)** conserva cinco estados dinámicos únicamente como
experimento opcional de simulación. Está deshabilitado por defecto, no forma
parte de la validación principal y no está autorizado para hardware.

## Compilar

```bash
cd ~/Documentos/Cuadrupedo
source /opt/ros/humble/setup.bash
source ~/nova_spot_ws/install/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Ejecutar

```bash
ros2 launch nova_gait_controller demo.launch.py
```

Para ejecutar el mismo cuadrúpedo y controlador en MuJoCo 3.9.0:

```bash
ros2 launch nova_gait_controller mujoco_demo.launch.py
```

Agrega `headless:=true` para simular sin abrir la ventana gráfica. El entorno
Python independiente de MuJoCo está en `.venv-mujoco`.

En otra terminal, selecciona una marcha:

```bash
ros2 topic pub --once /nova/gait_command std_msgs/msg/String "{data: gateo}"
ros2 topic pub --once /nova/gait_command std_msgs/msg/String "{data: paso}"
ros2 topic pub --once /nova/gait_command std_msgs/msg/String "{data: stand}"
ros2 topic pub --once /nova/gait_command std_msgs/msg/String "{data: stop}"
```

Para una prueba opcional exclusivamente en Gazebo o MuJoCo:

```bash
ros2 param set /gait_controller enable_experimental_gallop true
ros2 topic pub --once /nova/gait_command std_msgs/msg/String "{data: galope}"
```

El parámetro vuelve a `false` al reiniciar con la configuración normal.

Los tiempos se ajustan en `src/nova_gait_controller/config/gaits.yaml`. Antes de
usar estas marchas en hardware real deben calibrarse límites, sentido de cada
servo, centro PWM, ganancias y detección de contacto.

La validación física inicial en Raspberry Pi 4 ya confirmó comunicación I2C con
el PCA9685 en `0x40`, PWM manual a 50 Hz y pruebas secuenciales de los canales
`CH0`--`CH4`. Esto todavía no habilita las marchas en el robot: las
calibraciones individuales y `hardware_ready` permanecen bloqueadas. El detalle
de las pruebas está en `Raspberry/README.md`.

El gateo cartesiano dispone de estos parámetros seguros:

- `crawl_phase_duration`: tiempo entre muestras; entre 0,08 y 1,0 s.
- `crawl_samples`: muestras por ciclo; múltiplo de 4 entre 8 y 80.
- `crawl_step_length`: longitud del paso; entre 0,002 y 0,040 m.
- `crawl_step_height`: elevación del pie; entre 0,004 y 0,030 m.

Los valores se validan al recibir el comando `gateo`. Si una configuración es
inválida o produce un objetivo cinemático inalcanzable, el controlador rechaza
la marcha y conserva la postura. La línea base probada en Gazebo es 24 muestras,
0,18 s por muestra, paso de 0,018 m y elevación de 0,014 m.

## Métricas y supervisor de simulación

`demo.launch.py` inicia también `nova_metrics` y `nova_safety_supervisor`. Las
muestras sincronizadas de pose 3D y las 12 articulaciones se publican en:

```bash
ros2 topic echo /nova/metrics/json
ros2 topic echo /nova/metrics/diagnostics
```

Los umbrales provisionales están en `config/monitoring.yaml`: altura entre
0,16 y 0,32 m e inclinación absoluta máxima de 20 grados, con tres muestras
inseguras consecutivas y ocho segundos de gracia al arrancar. Al activarse, el
supervisor publica `stand` y enclava `/nova/safety/triggered`. Son valores para
Gazebo, no criterios validados ni autorización para operar el robot físico.

`demo.launch.py` también inicia dos procesos de contacto. `contact_monitor`
consolida los cuatro sensores de Gazebo en `/nova/foot_contacts` y
`contact_comparator` publica la comparación con el plan en
`/nova/contact_diagnostics`. El controlador publica la fase sincronizada en
`/nova/gait_phase`. Esta comparación sigue siendo informativa y no detiene la
marcha.

Para registrar una prueba reproducible nueva:

```bash
ros2 bag record /world/empty/dynamic_pose/info /joint_states \
  /nova/metrics/json /nova/metrics/diagnostics /nova/safety/triggered \
  /nova/gait_command /nova/gait_phase /nova/foot_contacts \
  /nova/contact_diagnostics
```

## Modelo matemático

Además de FK/IK, el módulo `mathematical_model.py` implementa Jacobianos,
matriz de masa, Coriolis, gravedad, dinámica inversa, transformación
fuerza-par, centro de masa, actuadores MG996R, contacto con fricción y margen
estático del polígono de apoyo. La formulación multicuerpo, parámetros,
resultados nominales, supuestos y protocolo de identificación están en
`Documentacion/MODELO_MATEMATICO_LATEX/main.pdf`. Es un modelo nominal
computable: los parámetros físicos estimados deben medirse antes de llamarlo
gemelo digital.

## Estado experimental

La cadencia corregida del gateo fue reproducida en dos ensayos independientes
con ciclos de 4,32 s y diferencias menores al 0,2 % en las medias comparadas.
La marcha paso completó dos ensayos de 12 ciclos en Gazebo y 12 ciclos en
MuJoCo. La medición posterior de contactos mostró una limitación importante del
gateo actual: coincidencia simultánea del 32,550 %, retardos en las patas
delanteras y ausencia de despegue de las traseras. Por ello, el gateo camina y
avanza, pero aún no cumple el patrón ideal de tres apoyos que declara su plan.

El estado, las evidencias y el orden de trabajo vigentes están en
`Seguimiento/Seguimiento.md` y `CONTINUIDAD.md`.
