# Historial de grabaciones analizadas — 21/10/2026

Zona horaria: America/Bogota. Cada entrada identifica fecha, hora de inicio y tipo de caminata para que los resultados no queden separados de su contexto experimental.

El índice cronológico completo de las **108 sesiones que tienen `video_analisis.json`** se conserva en `HISTORIAL_GRABACIONES_ANALIZADAS.csv`, con hora local, tipo de marcha/actividad y origen de la etiqueta. Para registros antiguos donde el tipo no consta, queda expresamente como “no especificado en metadatos”; calibraciones e identificaciones se etiquetan como actividades que no son caminatas.

| Inicio de caminata | Ensayo | Tipo de caminata | Resultado del análisis | Informe |
|---|---|---|---|---|
| 2026-10-21 19:34:03 | `rep_ciclo2_trote_ppo1_r2_fallo` | Trote PPO1 R2, marcado fallo | Cinco vistas analizadas; evidencia visual buena en HP-PC1/general/Windows; Logitech inestable; pares no visibles en HP-PC2. El video no confirma la hipótesis individual del fémur 2/I²C. | `rep_ciclo2_trote_ppo1_r2_fallo/INFORME_ANALISIS.md` |
| 2026-10-21 19:51:37 | `rep_ciclo2_trote_ppo1_r2_fallo_degradado` | Trote PPO1 R2 degradado | Cinco vistas analizadas; señal consistente en general/Windows; más variabilidad en HP-PC1; HP-PC2 y Logitech sin patas visibles. | `rep_ciclo2_trote_ppo1_r2_fallo_degradado/INFORME_ANALISIS.md` |

Los archivos `video_analisis.json` y `caminata.config.json` de cada sesión contienen las métricas y metadatos originales. Las imágenes son vistas derivadas del análisis. Los videos fuente se excluyen de los paquetes de resultados; no se borran de origen hasta verificar la transferencia al otro PC.

## Adenda: ciclo 3 (21/10/2026, 21:04–22:21)

Se añadieron seis sesiones posteriores al corte inicial. El índice CSV registra el tipo de marcha/actividad y el estado de cada una. `prueba_nucleos_2104` es una prueba técnica de gateo PPO, no una repetición comparativa; se completó su análisis visual. `rep_ciclo3_gateo_base_r1` y `rep_ciclo3_trote_base_r1` tienen evidencia visual generalmente consistente. `rep_ciclo3_gateo_ppo1_r1` tiene cobertura incompleta y sensores ENC_T1/C11 estimados; `rep_ciclo3_gateo_ppo2_r1` tiene temporización irregular (12,4 % de pasos >40 ms) además de ENC_T1/C11 sin respuesta. `rep_ciclo3_trote_ppo1_r1_fallo_222251` se cortó a los 44,9 s y queda como intento fallido: su análisis visual parcial no lo hace comparable con una repetición completa. El informe detallado es `../../Caminata final/INFORME_CICLO3_2026-10-21.md`.
