# Política de *pace* elegida el 6 de noviembre de 2026

Marcha nueva **pace** (ambladura pura). Las dos patas de un mismo lado se mueven a la vez: primero
delantera y trasera izquierdas, luego delantera y trasera derechas. Medio ciclo en el aire y medio apoyadas.

Las cuatro coxas se mueven ±8° en contrafase por lado: la de la pata en el aire abre y la de la pata apoyada
cierra. Así el cuerpo se carga sobre el lado apoyado y no se vence hacia el lado en el aire.

Se pidió porque el paso v24 se veía casi igual que el gateo. Las dos marchas levantan las patas en el mismo
orden y de a una; la única diferencia es que el paso no hace pausas.

Las rutas son relativas a `Experimentos/entrenamiento_real_20261016/`.

## La política

| | |
|---|---|
| Carpeta | `ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k` (`policy.zip` + `metadata.json`) |
| Origen | copia intermedia de 1 600 000 pasos de `ppo_v34_pace_desde_trote/semilla_9517`. Continúa el trote v32 elegido (`ppo_v32_trote_semilla_9209_650k`), así que unos 0,95 M son pasos de pace |
| Marcha base | `--marcha pace --ciclo-trote 0.45 --femur 12 --tibia 12 --apertura 5 --coxa 8`, periodo de control 0,03 s |
| Modelo de servos | `actuadores_trote_articulacion.json`. Es el del trote ajustado por articulación (v32); no hay datos del robot haciendo pace |
| Viabilidad (sim.) | **100 %** en 60 episodios (semillas 1001–1060, con aleatorización). 40 de esos episodios no se usaron para elegirla |
| Avance en 20 s | 3,75 m (marcha base 3,27 m) |
| Deriva lateral | 0,22 m (marcha base 0,58 m) |
| Caídas / inclinación máxima | 0 de 60 / 7,9° |

La viabilidad usa el criterio de `evaluar_viabilidad.py`: no cae, avanza al menos el 90 % de la marcha base, se
desvía menos que ella o menos de 0,5 m, e inclina menos de 15°.

- `viabilidad_todas_ppo_v34_pace.txt`: las 292 copias de la campaña con 20 episodios.
- `viabilidad_confirmacion_ppo_v34_pace_60ep.txt`: las mejores con 60 episodios.

## Cómo se entrenó (campaña v34)

`cola_pace.sh` usa el mismo PPO y los mismos pesos de recompensa que el trote en v32/v33:

```
--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --dt 0.03
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-avance 10 --w-lateral 20
```

Hay dos diferencias con el trote:

- **`--w-coxas 0.1`, en lugar de 1.0.** Con las coxas moviéndose cada 0,45 s y el retardo de 0,1 s del servo, la
  coxa siempre va detrás de la orden. La política no controla las coxas, y con 1.0 ese castigo sumaba unos
  −7500 por episodio, así que caerse pronto le daba más retorno.
- **`--ciclos-episodio 27`.** Son unos 12 s por episodio, como los 12 ciclos de 1 s del trote.

Semillas y resultados:

- **Desde cero:** 9501, 9503, 9505 y 9507, 3 M de pasos (`ppo_v34_pace`).
- **Continuando el trote v32:** 9511 a 9525, 1 M de pasos (`ppo_v34_pace_desde_trote`). Las semillas 9519 a
  9525 se lanzaron a mano con los mismos argumentos (`cola_pace_extra.txt`).
- **Segunda parte:** como la 9517 y la 9521 seguían subiendo, `cola_pace_parte2.sh` las continúa 2 M de pasos
  más (`ppo_v34_pace_desde_trote_parte2`). Solo sirve para ver la convergencia; la copia elegida no cambia.

La marcha base se eligió en MuJoCo con un barrido. Con ciclo de 1 s el robot solo se balanceaba (0,4 m en
20 s); con 0,45 s avanza 3,5 m en 20 s sin caídas. Las coxas en el sentido contrario hacen retroceder al robot.

Las órdenes de servo de la marcha base quedan dentro de los topes del firmware, salvo la tibia 2. Esa tibia
pide más de 180 y el firmware la recorta, igual que en el trote.

## Gráficas de convergencia

`graficas_pace_v34.py` las guarda en `graficas/convergencia_v34_pace/`, una figura por semilla: 9501 desde cero
y 9517 continuando el trote, con sus dos partes unidas. Cada figura tiene 9 paneles:

- **Recompensa:** frente a pasos, frente a episodios y frente a épocas.
- **Castigo total.**
- **Pérdidas de PPO:** total, del crítico, de la política, entropía y KL.

La línea discontinua marca el punto de convergencia. Ese criterio está explicado en el encabezado del script.

| | Desde cero (9501) | Continúa el trote (9517, la elegida) |
|---|---|---|
| Recompensa converge en | 2,03 M pasos · 4646 episodios · 9926 épocas | 0,96 M pasos · 2187 episodios · 4667 épocas |
| Pérdidas total y del crítico | 2,26 M | no convergen: suben desde ~2,5 M |
| Pérdida de la política / KL | 2,30 M / 2,37 M | 0,56 M / 2,33 M |
| Entropía | sigue bajando (normal en PPO) | sigue bajando |

En la 9517 la recompensa queda plana desde 0,96 M hasta unos 2,5 M de pasos de pace. Después empeora un poco:
la recompensa baja de −700 a −770, el castigo sube y vuelven a subir el error del crítico y la pérdida total.
Por eso la copia elegida, con ~0,95 M de pasos de pace, está en el punto de convergencia, y entrenar más no
aporta. La segunda parte también dio copias de la 9521 al 100 % con 20 episodios
(`viabilidad_todas_ppo_v34_pace_parte2.txt`), sin ventaja sobre la elegida.

## Reproducirlo mañana en el robot

1. **Obtener el código** de esta fecha:
   ```
   git fetch && git checkout politica-pace-20261106
   ```
2. **Entorno:** el mismo de `politicas_elegidas_20261105/requirements.txt`. Se usó Python 3.10.12 con
   mujoco 3.9.0, stable_baselines3 2.3.2, torch 2.3.1+cpu, gymnasium 0.29.1 y numpy 2.2.6.
3. **Verificar** los archivos y repetir la viabilidad (`--rapido`: 4 episodios):
   ```
   PY=.venv-mujoco/bin/python Experimentos/entrenamiento_real_20261016/politica_pace_20261106/verificar.sh
   ```
4. **Verla en MuJoCo** antes del robot, desde `Experimentos/entrenamiento_real_20261016/`:
   ```
   ../../.venv-mujoco/bin/python ver_politica_mujoco.py ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k              # en el piso
   ../../.venv-mujoco/bin/python ver_politica_mujoco.py ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k --suspendido # colgado
   ```
5. **En el robot**, con el mismo firmware del 5 de noviembre
   (`politicas_elegidas_20261105/firmware_movimiento_suspendido_11_servos_20261105.hex`):
   ```
   ../../.venv-mujoco/bin/python ejecutar_politica_robot.py \
       --politica ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k/policy.zip --duracion-s 60
   ```
   El programa lee la marcha, el ciclo de 0,45 s y las coxas de `metadata.json`. Como `coxa_deg` es mayor que 0,
   activa el modo `+` del firmware, que aplica las órdenes de las coxas, como en el galope. Para grabar con las
   cámaras: `Experimentos/camaras/grabar_caminata.py --nombre robot07_pace_v34_9517_60s -- <mismos argumentos>`.

## Precauciones para la primera prueba física

- **Empezar con el robot colgado de la barra.** El pace es más rápido (0,45 s por ciclo) que cualquier marcha
  probada en el robot hasta ahora.
- **Coxas:** se mueven las cuatro. El 27 de octubre la coxa 2 rebotaba al apoyar en el galope y por eso se dejó
  fija. Además, su potenciómetro (C1) no la sigue.
- **Modelo de servos:** es el del trote. El parecido entre el robot y la simulación del pace todavía no se ha
  medido.
- **Estado del robot:** el mismo de `politicas_elegidas_20261105/README.md`: postura del 27 de octubre y tope de
  la tibia 1 en 12°.
