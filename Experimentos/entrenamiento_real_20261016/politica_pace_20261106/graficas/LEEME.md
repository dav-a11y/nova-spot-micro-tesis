# Gráficas de convergencia del pace v34

Generadas el 6-nov-2026 con `graficas_pace_v34.py` y el entrenamiento completo, incluida la segunda parte de la semilla 9517.

| Archivo | Entrenamiento |
|---|---|
| `politica_elegida_9517_convergencia.png` | Semilla 9517, que continúa el trote v32. De ella sale la política elegida `ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k` (100 % viable en 60 episodios). Une las dos partes del entrenamiento: 3,0 M de pasos de pace. |
| `desde_cero_9501_convergencia.png` | Semilla 9501, entrenada desde cero (3 M de pasos), como comparación. |
| `convergencia_pace_v34.csv` | Punto de convergencia de cada curva. |

Cada figura tiene 9 paneles: recompensa frente a pasos, episodios y épocas, castigo total y las pérdidas de PPO. La recompensa de la 9517 converge en 0,96 M de pasos, 2 187 episodios y 4 667 épocas.
