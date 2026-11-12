# Campaña PPO MuJoCo: step, 80 semillas

Campaña ejecutada en el segundo PC el 28 de septiembre de 2026. Estado final:
80 semillas completadas y 160 filas de evaluación (nominal y PPO por semilla).
No se ha aceptado ninguna política ni transferido al hardware; queda pendiente
comparar con la campaña del PC principal y validar las políticas candidatas.
El análisis agregado, la distribución por semillas y las limitaciones de
evaluación están documentados en `INFORME_ANALISIS_80_SEMILLAS.md`.

**Auditoría posterior (28-09-2026):** se encontró un error temporal en la
versión de entorno con la que se entrenó y evaluó esta campaña. `nominal_index`
avanzaba en cada paso de 20 ms, mientras que el horizonte asumía nueve pasos por
muestra. Cada episodio de cinco ciclos declarados ejecutó en realidad 45 ciclos
de referencia. Se conservan íntegros políticas y trazas como evidencia de esa
versión exploratoria, pero sus cifras no son evidencia válida para los ciclos
de 5,76 s definidos en el modelo; no seleccionar ni desplegar estas políticas.

## Configuración y procedencia

- Código base: `2854673bc9c7c5cced981c40142a21d82cd5e7a5`.
- Algoritmo: Stable-Baselines3 PPO, `MlpPolicy`, simulador MuJoCo, marcha `step`.
- Semillas: `23` y `1001` a `1079` (80 entrenamientos independientes).
- Pasos solicitados por semilla: 200.000. PPO completa bloques de 1.024,
  por lo que cada ejecución alcanza 200.704 pasos; la traza registra cada 1.000.
- Cinco ciclos por episodio; cinco episodios de evaluación por condición.
- Evaluación sin aleatorización de dominio, con semillas de episodios 100–104.
- Python 3.10; versiones instaladas en `requirements-lock.txt`.
- La semilla 23 se entrenó primero y se conservó al ampliar a 80 semillas.
- `ampliar_campana_80.py` incorpora reanudación y evaluación incremental;
  `campana_ppo_completa.py` permite seleccionar las semillas que se evalúan.

## Archivos

- `mujoco/step_semilla_<N>/policy.zip`: política de cada semilla.
- `mujoco/step_semilla_<N>/metadata.json`: configuración del entrenamiento.
- `mujoco/step_semilla_<N>/training_trace.jsonl`: evolución de recompensa.
- `mujoco_evaluation.csv`: evaluación agregada nominal contra PPO.
- `campaign_manifest.json`: configuración ampliada a 80 semillas.
- `campaign_manifest.original.json`: manifiesto inicial de la semilla 23.
- `campaign.log`: entrenamiento y evaluación originales de la semilla 23.
- `training_seed_<N>.log`: registro de cada entrenamiento adicional.
- `expansion.log` y `expansion_status.json`: progreso y estado final del lote.
- `execution_context.json`: commit y fecha de inicio de la ejecución original.
- `exit_code.txt`: código de salida de la ejecución original, no del lote ampliado.
- `SHA256SUMS`: sumas de comprobación de los archivos de evidencia.

La fecha `2026-09-24` del manifiesto procede de una constante del script original.
La ejecución real fue el 28 de septiembre; véanse `execution_context.json` y
`expanded_at` en el manifiesto. Las rutas absolutas y el identificador de sesión
en los registros son contexto del PC de ejecución.

## Reproducción

Desde la raíz del repositorio, con Python 3.10:

```bash
python3 -m venv .venv-mujoco
.venv-mujoco/bin/pip install -r Experimentos/campana_distribuida_step_s23_20260928/requirements-lock.txt
export PYTHONPATH="src/nova_gait_controller:${PYTHONPATH:-}"
.venv-mujoco/bin/python Experimentos/ampliar_campana_80.py
```

Con los resultados presentes, el script conserva las políticas y evaluaciones
completadas. Para una campaña nueva, usar otra copia y cambiar `OUT` en el script;
este ampliador espera un manifiesto inicial como el conservado en esta carpeta.
No eliminar la evidencia existente para repetir el experimento.

Comprobar la integridad desde esta carpeta:

```bash
sha256sum -c SHA256SUMS
```

Las evaluaciones son promedios de cinco episodios, no una validación independiente
de robustez ni una autorización de despliegue en el robot.
