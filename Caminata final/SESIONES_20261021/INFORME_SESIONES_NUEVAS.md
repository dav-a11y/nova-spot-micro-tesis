# Análisis de cuatro sesiones nuevas — 21-oct-2026

Se guardan exclusivamente resultados, bitácoras e imágenes de análisis; no se incluye ningún video.

## Gateo

Los datos detallados por pata y cámara están en `video_analisis.json`; las superposiciones, en los PNG correspondientes.

- `rep_ciclo2_gateo_base_r1`: correlaciones promedio observadas por cámara entre 0,81 y 0,97. Pata 2 no visible en dos vistas. La vista HP-PC1 marcó ciclos 1–15 como anomalías; las otras vistas no marcaron anomalías. Retardos estimados: 0–900 ms.
- `rep_ciclo2_gateo_ppo1_r1`: correlaciones 0,79–0,99 donde las patas fueron visibles. Pata 4 no visible en HP-PC1 y Logitech. Logitech marcó ciclos 56–60 como anomalías. Hubo errores de decodificación MJPEG puntuales. Retardos: 0–200 ms.
- `rep_ciclo2_gateo_ppo2_r1`: correlaciones 0,88–0,99 donde las patas fueron visibles. Pata 3/4 no visibles en algunas cámaras. Anomalías en HP-PC2 (50, 51, 58–60), Logitech (49–52, 59–60) y Windows (16, 18–28, 46). Retardos: 0–200 ms.

“No visible” significa que la señal de esa pata no pudo aislarse con confianza en esa cámara, no que la pata no se moviera. Las anomalías son ciclos candidatos a inspección (movimiento no explicado por las órdenes), no prueba por sí solas de una falla mecánica.

## Trote marcado originalmente como fallido

`rep_ciclo2_trote_base_r1_fallo` tenía `invalida.txt` indicando “sin diagnóstico (caminata sin datos)”. El análisis visual adicional sí pudo comparar las órdenes de trote y el movimiento en cuatro cámaras:

| Cámara | Retardo estimado | r P2+P3 | CV P2+P3 | r P1+P4 | CV P1+P4 | Ciclos anomalía |
|---|---:|---:|---:|---:|---:|---:|
| HP-PC1 | 400 ms | 0,99 | 31,4% | 0,97 | 14,0% | 27 |
| HP-PC2 | 300 ms | 0,99 | 3,0% | 0,99 | 7,1% | 39 |
| Logitech | 400 ms | 0,99 | 25,0% | 0,98 | 22,2% | 27 |
| Windows | 800 ms | 0,99 | 8,5% | 0,99 | 8,0% | 27 |

Los grupos son pares diagonales (P2+P3 y P1+P4), no patas individuales: recibieron órdenes compartidas en este trote. CV elevada en HP-PC1 y Logitech sugiere variación visible fuerte; anomalías detectadas en su mayoría desde los ciclos 89–115. La cámara `general` no entregó fotogramas decodificables (“solo 0 fotogramas”); además FFmpeg reportó cuadros MJPEG inválidos. El archivo `invalida.txt` se refiere al diagnóstico/telemetría ausente: estos resultados visuales no sustituyen esos datos ni validan la salud de sensores.

## Referencia de eliminación

Los originales de estas cuatro sesiones solo se retirarán después de copiar y verificar este paquete en `Documents/Cuadrupedo/Caminata final/SESIONES_20261021/`. No se incluyen otros archivos del proyecto ni videos ajenos.
