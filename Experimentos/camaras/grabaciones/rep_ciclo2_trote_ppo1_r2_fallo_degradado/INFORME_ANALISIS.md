# Análisis de grabación — trote PPO1 R2 degradado

## Registro

- Fecha local: 21 de octubre de 2026.
- Inicio configurado de la caminata: 19:51:37 (hora de Bogotá).
- Inicio de captura de cámaras: aproximadamente 19:51:13–19:51:15; la cámara remota tiene un desfase registrado de 10 s.
- Tipo: **trote**, ciclo configurado de 1,0 s; duración solicitada 180 s.
- Política indicada por la configuración: `ppo_v10_robot/ppo_v15_trote_semilla_307_100k/policy.zip`.
- Cámaras: HP-PC1, HP-PC2/remota, general, Logitech y Windows.
- Fuente de métricas: `video_analisis.json`; el análisis visual separa pares diagonales P2+P3 y P1+P4 porque ambas patas de cada par comparten orden en este trote.

## Resultados visuales por cámara

| Cámara | Retardo estimado | P2+P3 (correlación media; CV amplitud) | P1+P4 (correlación media; CV amplitud) | Ciclos no explicados marcados |
|---|---:|---:|---:|---|
| HP-PC1 | 0 ms | r=0,830; CV=12,9% | r=0,834; CV=3,5% | Ninguno |
| HP-PC2/remota | 0 ms | No visible | No visible | Ninguno |
| General | 400 ms | r=0,977; CV=2,1% | r=0,970; CV=2,7% | Ninguno |
| Logitech | 0 ms | No visible | No visible | Ninguno |
| Windows | 200 ms | r=0,969; CV=3,3% | r=0,969; CV=2,9% | Ciclo 108 |

## Lectura y límites

Las vistas general y Windows muestran correlación alta y amplitud relativamente estable para ambos pares; HP-PC1 muestra más variabilidad en P2+P3. HP-PC2 y Logitech no permiten aislar visualmente los pares. El ciclo 108 de Windows es un candidato estadístico a movimiento no explicado, no una confirmación de avería.

El archivo `invalida.txt` anota: “fémures 2-4 r≈0,7: robot degradado tras horas de trote”. Es una observación de diagnóstico asociada a la corrida, no una medición independiente de daño. Como el análisis de video agrupa patas por pares diagonales, no identifica cuál fémur individual produjo esa observación. Mantener la grabación marcada como ensayo degradado.

## Archivos conservados

`video_analisis.json`, las cinco imágenes `video_analisis_<cámara>.png`, `diagnostico.json`, `diagnostico.png`, `invalida.txt`, `caminata.config.json` y `caminata.csv`. No incluir los archivos de video en la carpeta de resultados transferida.
