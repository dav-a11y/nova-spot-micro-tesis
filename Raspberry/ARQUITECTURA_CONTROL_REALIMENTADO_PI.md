# Control realimentado final en Raspberry Pi

La Raspberry ejecuta los dos niveles; no se requiere Arduino en la cadena de
control. El planificador nominal y la corrección inteligente producen una
referencia `q_ref[12]`. Antes de llegar al PCA9685, `interfaz_pwm_ros2.py`
adquiere los doce AS5600 y aplica `filtro_control_realimentado.py`.

```text
trayectoria nominal + corrección inteligente
                 -> q_ref[12]
                 -> filtro AS5600: límites, velocidad y seguimiento
                 -> PWM calibrado PCA9685 -> servos
                       ^
                       +---- AS5600: q medida y calidad magnética
```

El filtro solo deja pasar una referencia si: hay una ventana reciente de los
doce sensores, cada una tiene `MD=1`, `ML=0`, `MH=0`, el ángulo medido y el
objetivo están dentro del rango calibrado, el cambio solicitado respeta la
velocidad máxima y el error entre objetivo limitado y medición no excede el
umbral configurado. Una falla desarma PWM mediante el mecanismo existente de
OE alto y `FULL_OFF`.

La tabla `joint_feedback` de `configuracion/servos.yaml` se mantiene nula a
propósito. No se autoriza PWM hasta completar por cada articulación: cero y
sentido AS5600, límites útiles en radianes, velocidad medida y error máximo de
seguimiento. Esto no corrige sensores inestables ni convierte una ficha de
MG996R ambigua en calibración.

Para servos posicionales, la velocidad se regula limitando la pendiente de
`q_ref`, no con una orden independiente de velocidad. Si la caracterización
confirma giro continuo, se sustituirá la conversión a pulso por un controlador
PI de velocidad/posición, conservando exactamente las mismas puertas AS5600 y
de seguridad.
