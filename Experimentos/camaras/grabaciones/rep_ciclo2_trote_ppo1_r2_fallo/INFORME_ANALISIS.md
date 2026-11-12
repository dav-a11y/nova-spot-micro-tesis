# Análisis de grabación — trote PPO1 R2 (fallo)

## Registro

- Fecha local: 21 de octubre de 2026.
- Inicio configurado de la caminata: 19:34:03 (hora de Bogotá).
- Inicio de captura de cámaras: aproximadamente 19:33:40–19:33:41; la cámara remota tiene un desfase registrado de 9 s.
- Tipo: **trote**, ciclo configurado de 1,0 s; duración solicitada 180 s.
- Política indicada por la configuración: `ppo_v10_robot/ppo_v15_trote_semilla_307_100k/policy.zip`.
- Cámaras: HP-PC1, HP-PC2/remota, general, Logitech y Windows.
- Fuente de métricas: `video_analisis.json`; el análisis visual separa pares diagonales P2+P3 y P1+P4 porque ambas patas de cada par comparten orden en este trote.

## Resultados visuales por cámara

| Cámara | Retardo estimado | P2+P3 (correlación media; CV amplitud) | P1+P4 (correlación media; CV amplitud) | Ciclos no explicados marcados |
|---|---:|---:|---:|---|
| HP-PC1 | 0 ms | r=0,847; CV=7,1% | r=0,840; CV=6,4% | Ninguno |
| HP-PC2/remota | 0 ms | No visible | No visible | Ninguno |
| General | 400 ms | r=0,982; CV=1,5% | r=0,977; CV=4,3% | Ninguno |
| Logitech | 400 ms | r=0,939; CV=39,3% | r=0,889; CV=50,5% | 1–36 |
| Windows | 200 ms | r=0,977; CV=2,7% | r=0,975; CV=3,5% | Ninguno |

## Lectura y límites

En las vistas HP-PC1, general y Windows, las señales visuales de ambos pares diagonales siguen razonablemente las órdenes del trote. Logitech presenta variabilidad de amplitud y movimiento no explicado elevados; conviene tratar esa vista como inestable. HP-PC2 no permite observar los pares en esta grabación. Los ciclos marcados son alertas estadísticas del análisis visual de esa cámara, no prueba por sí solos de una falla mecánica.

El archivo `invalida.txt` registra: “femur2 no sigue la orden (r=0.7498156548370138): posible bus I2C bloqueado”. Esa es una hipótesis anotada por el sistema de diagnóstico. El análisis de video de esta corrida agrupa las patas en pares diagonales y **no confirma ni descarta individualmente** el fémur 2 ni el bloqueo I²C. Mantener esta grabación marcada como ensayo fallido.

## Archivos conservados

`video_analisis.json`, cinco imágenes `video_analisis_<cámara>.png`, `diagnostico.json`, `diagnostico.png`, `invalida.txt`, `caminata.config.json` y `caminata.csv`. No incluir los archivos de video en la carpeta de resultados transferida.
