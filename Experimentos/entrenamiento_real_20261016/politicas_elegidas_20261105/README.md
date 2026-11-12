# Políticas PPO elegidas para el robot — 5 de noviembre de 2026

A esta fecha, y con los ensayos hechos, estas son las mejores políticas de cada marcha del Nova Spot Micro.
Se eligieron por su viabilidad en simulación y por su parecido entre robot y simulación, medido con el robot
**suspendido** de una barra. No se han probado con el robot apoyado en el suelo.

Repositorio: rama `entrenamiento/ppo-robot-real-20261016`, etiqueta `politicas-elegidas-20261105`.

## Las cinco políticas

Las rutas son relativas a `Experimentos/entrenamiento_real_20261016/`. Cada carpeta tiene `policy.zip`
(Stable-Baselines3 2.3.2) y `metadata.json`, con la marcha, los pesos de la recompensa y el modelo del
actuador con el que se entrenó.

| Marcha | Política (`ppo_v10_robot/…`) | Modelo de servos para evaluarla | Viabilidad (sim.) | Parecido robot–sim. |
|---|---|---|---|---|
| Gateo | `ppo_v27_gateo_semilla_7013_4100k` | `actuadores_ciclo2.json` | 100 % | 90 % |
| Paso | `ppo_v24_paso_semilla_4109_200k` | `actuadores_ciclo2.json` | 100 % | 85 % |
| Carrera | `ppo_v32_carrera_semilla_9301_500k` | `actuadores_carrera_articulacion.json` | 95 % | 83 % |
| Galope | `ppo_v32_galope_semilla_9407_475k` | `actuadores_galope_articulacion.json` | 60 % | 82 % |
| Trote | `ppo_v32_trote_semilla_9209_650k` | `actuadores_trote_articulacion.json` | 60 % | 80 % |

- **Viabilidad.** Porcentaje de 20 episodios simulados (semillas 1001 a 1020, con aleatorización) en que la
  política no cae, avanza al menos el 90 % de la marcha nominal, se desvía menos que ella o menos de 0,5 m, e
  inclina menos de 15°. Las copias se eligieron con esos mismos episodios, así que el valor es optimista.
- **Parecido.** Fórmula: 100 · r · mín(A, 1/A), donde r es la correlación del ciclo medio y A el cociente de
  amplitudes entre robot y simulación. Es la media de los fémures y tibias con sensor, sin la tibia 4, cuyo
  potenciómetro C10 dejó de seguir al servo el 5 de noviembre. Se midió en una sola toma de 60 s por política.
- **Modelos de servos.** Trote, carrera y galope (campaña v32) se reentrenaron con un modelo de servos
  ajustado a cada marcha (`ajustar_ganancia_marcha.py`). En ese modelo, la ganancia de cada articulación es
  igual al cociente de amplitudes medido en el robot suspendido. Con ese modelo, hasta la marcha nominal de
  trote, carrera y galope empeora en simulación (la carrera nominal cae en 19 de 20 episodios). Por eso su
  viabilidad no es comparable con la de paso y gateo.

## Caminatas de evidencia en el robot (suspendido)

En `Experimentos/camaras/grabaciones/<carpeta>/` están `caminata.csv` (órdenes y sensores cada ~33 ms),
`caminata.config.json` y `comparacion_sim_real.json`. Los videos no están en el repositorio.

| Marcha | Carpeta | Fecha |
|---|---|---|
| Gateo | `robot05_gateo_v27_7013_60s_r2_1822` | 5-nov-2026 |
| Paso | `robot28_paso_v24_4109_60s_cx42_1613` | 28-oct-2026 |
| Carrera | `robot05_carrera_v32_60s_1927` | 5-nov-2026 |
| Galope | `robot05_galope_v32_60s_r2_1936` | 5-nov-2026 |
| Trote | `robot05_trote_v32_60s_1925` | 5-nov-2026 |

## Cómo reproducirlo en otro PC

1. Clonar el repositorio y fijar la versión:
   ```
   git clone https://github.com/davidediaz/nova-spot-micro-tesis.git
   cd nova-spot-micro-tesis
   git checkout politicas-elegidas-20261105
   ```
2. Crear el entorno. Se usó Python 3.10.12 en Ubuntu 22.04.
   ```
   python3.10 -m venv .venv-mujoco
   .venv-mujoco/bin/pip install -r Experimentos/entrenamiento_real_20261016/politicas_elegidas_20261105/requirements.txt \
       --extra-index-url https://download.pytorch.org/whl/cpu
   ```
3. Verificar los archivos y repetir la viabilidad. Primero comprueba con `SHA256SUMS` que las políticas,
   los modelos, el código, el firmware y las caminatas son exactamente los de esta fecha. Después vuelve a
   evaluar las 5 políticas; con 20 episodios deben salir los valores de la tabla.
   ```
   PY=.venv-mujoco/bin/python Experimentos/entrenamiento_real_20261016/politicas_elegidas_20261105/verificar.sh
   ```
   Con `--rapido` usa 4 episodios.
4. Repetir el parecido de una caminata grabada, por ejemplo la del galope:
   ```
   cd Experimentos/entrenamiento_real_20261016
   ../../.venv-mujoco/bin/python comparar_sim_real.py ../camaras/grabaciones/robot05_galope_v32_60s_r2_1936 \
       --calibracion-actual --actuador actuadores_galope_articulacion.json --salida comparacion_repetida.json
   ```
5. En el robot:
   - Cargar el firmware `firmware_movimiento_suspendido_11_servos_20261105.hex` (fuente en
     `Arduino/movimiento_suspendido_11_servos/`), por ejemplo con
     `avrdude -p atmega328p -c arduino -P /dev/ttyACM0 -b 115200 -D -U flash:w:<hex>:i`.
   - Ejecutar la política con el robot colgado:
     ```
     ../../.venv-mujoco/bin/python ejecutar_politica_robot.py --politica ppo_v10_robot/<política>/policy.zip --duracion-s 60
     ```
     Con cámaras se usa `Experimentos/camaras/grabar_caminata.py --nombre <n> -- <mismos argumentos>`.
   - El programa lee la marcha y la apertura de `metadata.json`. El galope activa las coxas (modo `+` del
     firmware).

## Estado del robot en esta fecha

- **Postura:** la del 27 de octubre. Bases de los servos `[159, 42, 64, 82, 110, 100, 100, 100, 100, 166, 100, 144]`.
- **Topes y calibración:** tope mínimo de la tibia 1 en 12° (CH12). Calibración de sensores en `sensores_robot.json`.
- **Sensores sin lectura útil:**
  - tibia 1, sin sensor;
  - tibia 3, su potenciómetro responde en C12, pero el firmware no lo transmite;
  - tibia 4, el potenciómetro C10 no sigue al servo;
  - coxa 2, el potenciómetro C1 no sigue a la coxa.
  En el galope, además, los potenciómetros de los fémures 2 y 4 se alteran.
- **Limitaciones:** una toma por política; robot suspendido; viabilidad optimista.

## Ver las políticas en MuJoCo (sin el robot)

`ver_politica_mujoco.py` reproduce en la simulación la marcha nominal más la corrección de una política. Usa la
misma marcha, los mismos pesos y el mismo modelo de servos con que se entrenó; todo eso sale de su `metadata.json`.
Puede mostrarla en una ventana en vivo o guardarla en video, con el robot en el piso o colgado como en la barra.

Para verla, la política sola no basta: hacen falta también `metadata.json`, `entrenar_ppo_real.py`,
`Experimentos/entrenar_ppo_mujoco.py`, el modelo `src/nova_sm3_description/mujoco/nova_sm3_real.xml` y
`calibracion_postura.json`. Todos están en el repositorio.

Desde `Experimentos/entrenamiento_real_20261016/`, con el entorno de `requirements.txt` y ffmpeg instalado
(`sudo apt install ffmpeg`):
```
P=../../.venv-mujoco/bin/python
$P ver_politica_mujoco.py ppo_v10_robot/ppo_v32_trote_semilla_9209_650k                       # ventana, en el piso
$P ver_politica_mujoco.py ppo_v10_robot/ppo_v32_trote_semilla_9209_650k --suspendido          # ventana, colgado
$P ver_politica_mujoco.py ppo_v10_robot/ppo_v27_gateo_semilla_7013_4100k --video gateo.mp4 --segundos 30
$P ver_politica_mujoco.py ppo_v10_robot/ppo_v24_paso_semilla_4109_200k --nominal              # solo la marcha base
```
- La ventana en vivo usa `ffplay`. `--visor` abre en cambio el visor interactivo de MuJoCo, que permite girar la
  cámara con el ratón; en el PC del laboratorio se colgaba por el controlador gráfico.
- En un PC sin pantalla, `--video` funciona con `MUJOCO_GL=egl` o `MUJOCO_GL=osmesa`.
- En el piso, el programa imprime al final cuánto avanzó el robot.

## Videos de evidencia del 5-nov-2026 (robot suspendido)

Las 5 políticas se ejecutaron 60 s seguidas, a partir de las 19:45: gateo, paso, trote, carrera y galope, en ese
orden. Las grabaron 4 cámaras sincronizadas. Los datos de sensores de esas tomas están en
`Experimentos/camaras/grabaciones/evidencia_<marcha>_<política>_1945/`. Los videos se armaron con
`Experimentos/camaras/video_evidencia.py`.
