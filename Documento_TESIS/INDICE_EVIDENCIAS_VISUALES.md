# Índice de evidencias visuales

Actualización: 2 de septiembre de 2026.

| Figura del PDF | Archivo | Datos de origen | Qué evidencia | Limitación explícita |
|---|---|---|---|---|
| Arquitectura funcional | `Figures` mediante TikZ en `Chapters/11 Desarrollo.tex` | Nodos y tópicos implementados | Flujo entre mando, controlador, simuladores, sensores, análisis, supervisor y registro | Es arquitectura lógica; no demuestra integración eléctrica completa |
| Transición física segura | TikZ en `Chapters/11 Desarrollo.tex` | Estado documentado de Raspberry, PCA9685 y puertas F0--F4 | Separa bloques comprobados de calibración, OE, marcha e instrumentación pendientes | Es una secuencia de validación, no un circuito eléctrico ni autorización para energizar |
| Workspace y singularidades | `Figures/Resultados/workspace_singularidades.png` | 52.111 configuraciones generadas por `Experimentos/generar_graficas_cinematica.py` | Alcance por límites, ubicación de baja $\sigma_{\min}$ y distribución de $\kappa$ | No incluye autocolisión ni calibración física |
| Velocidades articulares | `Figures/Resultados/velocidades_articulares.png` | Referencias nominales de gateo y paso | Envolventes por tipo articular y máximo entre 12 articulaciones | El límite URDF no equivale a capacidad física bajo carga |
| Series del gateo | `Figures/Resultados/gateo_series_temporales.png` | `linea_base_cadencia_corregida_20260814_1049` | Avance y comportamiento periódico de posición, altura, roll y pitch | Un ensayo en Gazebo; no representa hardware |
| Reproducibilidad del gateo | `Figures/Resultados/gateo_reproducibilidad.png` | Dos bolsas de cadencia corregida | Similitud ciclo a ciclo y transitorio inicial | Dos ejecuciones no demuestran equivalencia estadística formal |
| Series de marcha paso | `Figures/Resultados/paso_series_temporales.png` | `paso_linea_base_20260814` | Avance y respuesta periódica de la marcha paso en Gazebo | No contiene mediciones físicas |
| Reproducibilidad de marcha paso | `Figures/Resultados/paso_reproducibilidad.png` | Línea base y repetición de paso | Comparación de dos ensayos independientes | Se limita a la configuración simulada ensayada |
| Seguimiento en MuJoCo | `Figures/Resultados/paso_mujoco_seguimiento.png` | `metricas_mujoco_por_ciclo.csv` | Error RMS/máximo articular y error de cadencia en 12 ciclos | El adaptador no publicó pose o estabilidad corporal equivalente |
| Persistencia del contacto | `Figures/Resultados/contacto_persistencia_cruda.png` | `episodios_sin_contacto_crudo.csv` | Las pérdidas RL/RR permanecen debajo de 0,12 s | Contacto de Gazebo; no sustituye un sensor físico calibrado |
| Entrenamiento PPO residual | `Figures/Resultados/ppo_residual_entrenamiento.png` | Cinco semillas del entorno reducido | Convergencia del flujo preparatorio de entrenamiento | No demuestra mejora dinámica ni transferencia |
| Revalidación PPO | `Figures/Resultados/comparacion_reentrenada_ppo.png` | Cuatro nominales válidos y cinco PPO | Degradación observada con la política reentrenada | Comparación descriptiva no completamente emparejada |
| Comparación final descriptiva PPO | `Figures/Resultados/comparacion_final_ppo.png` | Referencia nominal corregida y campañas PPO | Sustenta el rechazo de escalas positivas | No satisface la campaña final emparejada de cinco ensayos por marcha |

Las gráficas cinemáticas se regeneran mediante
`Experimentos/generar_graficas_cinematica.py`; las de contacto y MuJoCo mediante
`generar_figuras_resultados.py`. Las series y comparaciones restantes son
salidas directas de los analizadores reproducibles conservados en
`Experimentos/`.
