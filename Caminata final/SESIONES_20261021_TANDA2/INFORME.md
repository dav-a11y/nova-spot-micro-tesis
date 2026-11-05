# Tanda de 3 sesiones nuevas — 21-oct-2026

Paquete de análisis únicamente: JSON por cámara y pata/par diagonal, bitácoras y superposiciones PNG. No contiene videos originales.

## `rep_ciclo2_gateo_ppo1_r2`

- Cinco vistas (HP-PC1, HP-PC2, general, Logitech y Windows) procesadas.
- Correlaciones por pata entre **0,72 y 0,98**; CV de amplitud **1–8%**.
- No se detectaron ciclos anómalos en ninguna vista.
- Pata 4 no quedó visible en HP-PC1 ni Logitech; sí fue visible en las otras tres.
- Retardos estimados 0–100 ms.

## `rep_ciclo2_trote_ppo1_r1`

El trote se evalúa por pares diagonales porque cada par comparte órdenes; no permite separar las patas individuales.

| Vista | r P2+P3 / P1+P4 | CV P2+P3 / P1+P4 | Anomalías detectadas |
|---|---|---|---|
| HP-PC1 | 0,97 / 0,94 | 22% / 12% | ciclos 136–143 y 147–158 (20) |
| HP-PC2 | ambos grupos no visibles | — | ninguna |
| General | 0,86 / 0,90 | 12% / 10% | ninguna |
| Logitech | 0,82 / 0,95 | 36% / 20% | ninguna |
| Windows | 0,86 / 0,87 | 22% / 15% | ciclos 134–143 y 150–158 (19) |

CV elevados indican variación de la señal visual entre ciclos; los ciclos marcados son candidatos a inspección, no fallas confirmadas. “No visible” no equivale a “no se movió”. Retardos estimados 300–900 ms.

## `rep_ciclo2_gateo_ppo2_r2`

- Cinco vistas procesadas, incluida la remota/HP-PC2, que llegó después de iniciar el primer análisis; se repitió el análisis completo con todos los archivos cerrados.
- HP-PC1: r P1/P2/P3 = 0,91/0,95/0,96, CV 8/3/4%; P4 no visible. Anomalías en ciclos 13–16 y 54–60 (11).
- HP-PC2: P1 no visible; r P2/P3/P4 = 0,96/0,97/0,78, CV 4/2/1%; sin anomalías.
- General: r P1–P4 = 0,90/0,94/0,90/0,93, CV 1/3/2/1%; sin anomalías.
- Logitech: r P1/P2/P3 = 0,91/0,94/0,95, CV 1/2/3%; P4 no visible; sin anomalías.
- Windows: r P1–P4 = 0,98/0,95/0,97/0,97, CV 2/6/2/2%; anomalías en ciclos 49–59 (11).
- Retardos estimados 0–200 ms.

Las señales visibles correlacionan bien con las órdenes. La detección de movimiento no explicado es sensible a oclusiones, iluminación y cambios del soporte; no demuestra por sí sola un problema mecánico.

## Borrado

Los 15 archivos originales de cámara se eliminarán únicamente después de verificar por checksum este paquete en `Documents/Cuadrupedo/Caminata final/SESIONES_20261021_TANDA2/`.
