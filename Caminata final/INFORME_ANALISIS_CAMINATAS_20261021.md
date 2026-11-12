# Análisis de videos de caminatas

Fecha de análisis: 21 de octubre de 2026.

Se analizaron ocho carpetas pendientes (32 grabaciones de cámara) que no tenían `video_analisis.json`. Se usó `analizar_video_patas.py`: relaciona los cambios de imagen con las órdenes de los actuadores, estima retardo de cámara, correlación (r) y variación de amplitud entre ciclos (CV). En el trote, las mediciones agrupan pares diagonales porque las órdenes de cada par coinciden.

## Resumen por caminata

| Grabación | Hallazgo principal |
|---|---|
| `trote_mejor_20261021` | En HP PC y General Webcam, ambos pares diagonales se ven claramente: r=0,98–1,00; CV=1,9–3,5 %. Logitech y cámara remota no permiten medir los pares. |
| `trote_apertura5_1min` | HP PC, Logitech y tablet registran los dos pares: r=0,92–0,99; CV=2,4–6,0 %. |
| `rep_ciclo1_trote_ppo1_r2` | HP PC y Logitech muestran los pares con r=0,97–0,99; CV=2,6–6,9 %. General Webcam: r=0,91–0,93 y CV≈18,5 %, mayor variación que las otras vistas. |
| `rep_20261020v11_paso_base_r1_3cam` | Logitech ve las cuatro patas (r=0,96–0,99; CV=0,9–4,6 %). HP PC ve P1/P2 (r=0,85–0,90; CV≈2,4 %); P3/P4 no son visibles en esa vista. |
| `rep_20261020real_trote_base_r2` | Logitech y tablet miden ambos pares con r=0,97–0,99 y CV=1,2–3,5 %. HP PC y las otras vistas son parciales. |
| `gateo_topes_1min_20261021` | Las vistas HP PC, portátil 2, General y Logitech registran las patas visibles con r=0,77–0,99 y CV=0,6–4,9 %. Algunas patas quedan fuera de cuadro según la cámara. |
| `gateo_mejor_20261021` | Portátil 2 y General Webcam dan cobertura amplia (r=0,81–0,99; CV=1,3–14,6 %). HP PC y Logitech son parciales. |
| `gateo_apertura8_1min` | Logitech y tablet registran las cuatro patas (r=0,86–0,98; CV=1,3–5,4 %). La vista del celular solo permite medir P1 (r=0,87; CV=12,7 %); las demás patas no se ven con suficiente claridad. |

## Precauciones de interpretación

- `r` alto indica que el movimiento de los píxeles identificados sigue la orden registrada; no es por sí mismo una medida de velocidad, avance o éxito global de la marcha.
- `CV` resume cuánto cambia la amplitud entre ciclos en esa vista; iluminación, oclusión, encuadre y movimiento del cuerpo también influyen.
- El detector de “movimiento no explicado” marca ciclos candidatos a anomalía, pero no identifica la causa. Se encontraron secuencias consecutivas en algunas cámaras y un umbral muy sensible cuando la mediana es casi cero; no deben interpretarse como fallas confirmadas del robot.
- “No visible” significa que el video no ofrece píxeles suficientes para aislar esa pata, no que la pata no se moviera.

Para cada grabación se guardan el JSON de métricas, las imágenes de las máscaras/cámaras, la configuración de la caminata, el registro de órdenes (`caminata.csv`) y el diagnóstico disponible. No se incluyen los videos originales en esta carpeta de resultados.

## Otros videos revisados

- `Descargas/Comportamiento/WhatsApp Video 2026-10-19 at 6.32.32 PM.mp4` (38,1 s) y `...6.33.47 PM.mp4` (14,7 s): se ve el robot suspendido en un soporte mientras mueve las patas, sin apoyo en el suelo. No son ensayos de locomoción; además, no tienen `caminata.csv` sincronizado. Se revisaron visualmente, pero no se les asignaron métricas de marcha ni se borraron.
- Los dos clips de `ProyectoII_Clases/24_08_2026/` muestran el prototipo en una mesa/soporte, sin una caminata identificable; no se incluyeron como ensayos.
- `rep_20261020real_gateo_base_r1_fallo` quedó fuera porque está marcado como fallo y no representa una caminata válida.
