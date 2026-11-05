# Análisis de pruebas restantes (21-oct-2026)

Este paquete contiene únicamente resultados y datos auxiliares; no incluye videos.

## Prueba de postura — 2026-10-20

Archivo cuantitativo original: `POSTURA_20261020/inclinaciones.json`.

- Patas 2 y 4: inclinaciones medidas de **+18,87°** y **+18,88°**.
- La diferencia entre ambas es **0,01°**: prácticamente iguales en esta medición.
- Límite: el JSON no indica cuál corresponde al fémur/tibia ni incluye incertidumbre; no se debe interpretar como error absoluto frente a simulación.
- Se conserva `ordenes.npz` como registro auxiliar de órdenes. Las tres cámaras grabaron a 30 fps (HP PC2 1280×720, Logitech 640×480, tablet 1280×720); los videos se excluyeron de este paquete.

## Prueba de sentido de movimiento — 2026-10-20

Resultados originales en `SENTIDOS_20261020/sentidos.json`:

| Articulación | Correlación horizontal | Correlación vertical | Resultado guardado |
|---|---:|---:|---|
| Fémur 1 | -0,78 | +0,56 | Adelante (correcto) |
| Fémur 2 | +0,97 | -0,84 | Adelante (correcto) |
| Fémur 3 | -0,91 | -0,88 | Adelante (correcto) |
| Fémur 4 | +0,94 | -0,62 | Adelante (correcto) |
| Tibia 1 | -0,19 | +0,07 | No concluyente |
| Tibia 2 | -0,85 | +0,27 | No concluyente |
| Tibia 3 | -0,49 | -0,45 | Sube (correcto) |
| Tibia 4 | -0,64 | +0,16 | No concluyente |

Interpretación: las cuatro pruebas de fémur respaldan el sentido “adelante”. La tibia solo resulta concluyente para la pata 3; patas 1, 2 y 4 requieren repetir la prueba con mejor visibilidad/señal. Esto no es una recomendación sobre marcha ni una prueba de contacto con el suelo.

## Cuatro clips antiguos: inspección visual, no marcha cuantificable

Metadatos de los archivos y revisión de fotogramas muestreados:

| Archivo de origen (solo referencia) | Duración | Fotogramas | Observación visual |
|---|---:|---:|---|
| ProyectoII_Clases/24_08_2026/WhatsApp Video 2026-08-24 at 6.05.09 PM.mp4 | 19,92 s | 1.191 | Robot en banco/soporte; no se aprecia desplazamiento de marcha libre. |
| ProyectoII_Clases/24_08_2026/WhatsApp Video 2026-08-24 at 6.05.18 PM.mp4 | 20,88 s | 1.245 | Inspección del robot/electrónica sobre banco; no es una caminata medible. |
| Descargas/Comportamiento/WhatsApp Video 2026-10-19 at 6.32.32 PM.mp4 | 38,05 s | 2.260 | Robot suspendido/sujeto durante prueba de patas; no hay locomoción libre sobre el piso. |
| Descargas/Comportamiento/WhatsApp Video 2026-10-19 at 6.33.47 PM.mp4 | 14,70 s | 873 | Robot sujeto durante prueba; no hay locomoción libre sobre el piso. |

Por falta de `caminata.csv`, reloj sincronizado y calibración geométrica en estos clips, no se calculan ángulos articulares, frecuencia de paso, velocidad ni contacto de patas. Las observaciones son cualitativas y se basan en fotogramas muestreados, no en seguimiento completo de cada pata.

## Alcance y borrado

Los nueve videos de origen (cinco MKV de las pruebas del 20-oct y cuatro MP4 anteriores) no se incluyen. Antes de retirarlos del PC de origen, este informe, los JSON y el NPZ auxiliar deben quedar copiados y verificados en `Documents/Cuadrupedo/Caminata final/PRUEBAS_NO_CAMINATA/` del otro PC. Los originales se eliminan únicamente tras esa verificación. No borrar ni modificar otros videos no relacionados.
