# Informe completo de videos de caminatas y movimiento de patas

Fecha de consolidación: 21 de octubre de 2026.

Se consolidaron los análisis por cámara y pata/par diagonal en `RESUMEN_METRICAS_POR_CAMARA_Y_PATA.csv`; los JSON por sesión y las imágenes de máscaras están junto a sus datos de contexto. El análisis usa OpenCV y el script existente `analizar_video_patas.py`, que ajusta el movimiento visible a las órdenes registradas, estima el retardo, la correlación (r) y el CV de amplitud entre ciclos.

Consolidación inicial: 92 sesiones y 1186 filas de métricas/captura. Se añadieron después ocho sesiones suplementarias: tres en `SESIONES_20261021/INFORME_SESIONES_NUEVAS.md`, tres en `SESIONES_20261021_TANDA2/INFORME.md`, una en `SESIONES_20261021_TANDA3/INFORME.md` y una tanda de pruebas cualitativas en `PRUEBAS_NO_CAMINATA/`. La entrega contiene análisis para 100 sesiones; las ocho sesiones suplementarias no están incluidas en el CSV consolidado original.

En el barrido actual se analizaron 182 archivos de cámara de 45 sesiones; junto con los 32 ya procesados en la tanda anterior, son 214 videos de cámara de 53 sesiones. La copia está verificada por checksum y los originales de esas 214 grabaciones se retiraron después del análisis; se liberaron aproximadamente 39,65 GB. No quedan videos en las carpetas con `caminata.csv`.

## Sesiones incluidas

- `base_v6_compensada`
- `calib_colores_20261021_125123_v1`
- `calib_colores_20261021_125326_v2`
- `calib_colores_20261021_125530_v3`
- `calib_colores_20261021_125738_v4`
- `calib_colores_20261021_130031_v1`
- `calib_colores_20261021_130255_v2`
- `calib_colores_20261021_130545_v3`
- `calib_colores_20261021_130758_v4`
- `calib_colores_20261021_131113_v1`
- `calib_colores_20261021_131343_v2`
- `calib_colores_20261021_131609_v3`
- `gateo_apertura8_1min`
- `gateo_base_3min`
- `gateo_base_r1`
- `gateo_mejor_20261021`
- `gateo_ppo_v10_s23_3min`
- `gateo_ppo_v10_s71_final_3min`
- `gateo_ppo_v6_s11_3min`
- `gateo_ppo_v6_s11_r1`
- `gateo_ppo_v6_s11_r2`
- `gateo_topes_1min_20261021`
- `identificar_patas_20261021`
- `identificar_patas_rojo2_20261021`
- `identificar_patas_rojo_20261021`
- `paso_base_01`
- `paso_base_3min`
- `paso_ppo_v10_s71_3min`
- `prueba_5camaras_20261021`
- `rep_20261019_gateo_base_r1`
- `rep_20261019_gateo_base_r2`
- `rep_20261019_gateo_base_r3`
- `rep_20261019_gateo_ppo_r1`
- `rep_20261019_gateo_ppo_r2`
- `rep_20261019_gateo_ppo_r3`
- `rep_20261019_paso_base_r1`
- `rep_20261019_paso_base_r2`
- `rep_20261019_paso_base_r3`
- `rep_20261019_paso_ppo_r1`
- `rep_20261019_paso_ppo_r2`
- `rep_20261019_paso_ppo_r3`
- `rep_20261020_gateo_base_r1`
- `rep_20261020_gateo_base_r2`
- `rep_20261020_gateo_base_r2_3cam`
- `rep_20261020_gateo_base_r3`
- `rep_20261020_gateo_ppo_r1`
- `rep_20261020_gateo_ppo_r2`
- `rep_20261020_gateo_ppo_r3`
- `rep_20261020_paso_base_r1`
- `rep_20261020_paso_base_r2`
- `rep_20261020_paso_base_r2_3cam`
- `rep_20261020_paso_base_r3`
- `rep_20261020_paso_base_r3_3cam`
- `rep_20261020_paso_ppo_r1`
- `rep_20261020_paso_ppo_r2`
- `rep_20261020_paso_ppo_r2_3cam`
- `rep_20261020_paso_ppo_r3`
- `rep_20261020real_gateo_base_r1`
- `rep_20261020real_gateo_base_r1_fallo`
- `rep_20261020real_gateo_v12_r1`
- `rep_20261020real_trote_base_r1`
- `rep_20261020real_trote_base_r2`
- `rep_20261020real_trote_ppo_r1`
- `rep_20261020v11_paso_base_r1`
- `rep_20261020v11_paso_base_r1_3cam`
- `rep_20261020v11_paso_base_r2`
- `rep_20261020v11_paso_base_r3`
- `rep_20261020v11_paso_v11_r1`
- `rep_20261020v11_paso_v11_r2`
- `rep_20261020v11_paso_v11_r3`
- `rep_20261021_gateo_base_r1`
- `rep_20261021_gateo_base_r2`
- `rep_20261021_gateo_base_r3`
- `rep_20261021_gateo_v14_r1`
- `rep_20261021_gateo_v14_r2`
- `rep_20261021_gateo_v14_r3`
- `rep_20261021_trote_base_r1`
- `rep_20261021_trote_base_r2`
- `rep_20261021_trote_base_r3`
- `rep_ciclo1_gateo_base_r1`
- `rep_ciclo1_gateo_base_r2`
- `rep_ciclo1_gateo_ppo1_r1`
- `rep_ciclo1_gateo_ppo1_r2`
- `rep_ciclo1_trote_base_r1`
- `rep_ciclo1_trote_base_r2`
- `rep_ciclo1_trote_ppo1_r1`
- `rep_ciclo1_trote_ppo1_r2`
- `rep_ciclo1_trote_ppo2_r1`
- `rep_ciclo1_trote_ppo2_r2`
- `trote_apertura5_1min`
- `trote_base_prueba_1min`
- `trote_mejor_20261021`

## Alcance y límites

- El trote se analiza por pares diagonales, porque las órdenes de las patas de cada par son iguales.
- Las series `calib_colores_*` y `identificar_patas_*` tienen registros de órdenes y se procesaron como ensayos de movimiento de patas; no son automáticamente pruebas de marcha estable. Sus CV altos reflejan variación marcada entre ciclos y deben interpretarse como tales.
- `rep_20261020real_gateo_base_r1_fallo` se conserva etiquetada como fallo: las tres vistas válidas no proporcionan patas identificables. `rep_ciclo1_gateo_base_r2` se reprocesó porque su JSON anterior estaba incompleto. `rep_20261021_trote_base_r2` se reprocesó para incluir la vista remota.
- Las cámaras con error o sin patas visibles quedan señaladas en el CSV/JSON. No se interpreta `no visible` como ausencia de movimiento.
- El detector de movimiento no explicado es sensible a iluminación, oclusión y medianas cercanas a cero: sus ciclos marcados son candidatos a revisar, no fallas confirmadas.
- Los clips de `Descargas/Comportamiento` muestran el robot suspendido en un soporte, sin apoyo en el piso ni registro sincronizado de órdenes; son pruebas de patas, no caminatas. No se les atribuyen ángulos ni ciclos de marcha inventados. Los clips de agosto muestran el prototipo quieto sobre soporte/mesa. `calibracion_postura_*` y `sentidos_*` son también pruebas de postura/sentido, no caminatas.
- Los nueve clips de pruebas restantes (postura/sentidos, clips suspendidos y prototipo de agosto) se inspeccionaron, se documentaron en `PRUEBAS_NO_CAMINATA/INFORME_PRUEBAS_RESTANTES.md`, se copiaron con sus datos auxiliares y se retiraron después de verificar la copia. Los videos de fondo de escritorio no pertenecen al cuadrúpedo y no se tocaron.
- No se incluyen videos originales en la carpeta final; los datos CSV, configuraciones, diagnósticos, JSON e imágenes de análisis se conservan.
