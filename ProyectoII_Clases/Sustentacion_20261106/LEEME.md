# Sustentación de Proyecto de Grado II (6-nov-2026)

## Archivos

- `Sustentacion_Proyecto_Grado_II_v3.odp`: **versión vigente**, con 33 diapositivas sobre la plantilla USTA del
  anteproyecto. Es la versión .odp que el usuario editó a mano, más la diapositiva 16, «Conexión del hardware».
  Copia de `~/Downloads/Sustentacion_Proyecto_Grado_II_v3.odp`.
- `graficas/`: las 4 gráficas de presentación por marcha (recompensa frente a pasos, episodios y épocas, y castigo
  frente a pasos) y su resumen. Copia de `~/Escritorio/Graficas_presentacion_marchas/`.
  - `pace_v34_9517/`: líneas de convergencia puestas a mano por el usuario (1,1 M de pasos, 2 400 episodios,
    5 000 épocas y 1,25 M para el castigo).
  - `gateo_v33_desde_cero/`, `trote_v33_desde_cero/` y `galope_v33_desde_cero/`: entrenamientos v33 desde cero
    (semilla 9900), con la línea calculada por el criterio de ±3 %. El usuario las aprobó y no quiere reentrenar.
- `scripts/`:
  - `construir.py`: generó la primera versión .pptx a partir de la plantilla `Presentaciones_Anteproyectos mi parte.pptx`.
    **Ya no se usa**: el usuario editó la versión .odp a mano.
  - `esquema.py`: dibujó la diapositiva de hardware.
  - `insertar_odp.py`: la insertó en el .odp del usuario sin convertir el archivo.
- Gráficas regenerables con `Experimentos/entrenamiento_real_20261016/graficas_presentacion_pace_v34.py`
  (`--semilla carpeta:semilla --nombre ... --banda 0.03 --linea PASOS_M EPISODIOS EPOCAS CASTIGO_M --salida DIR`).

## Reglas acordadas con el usuario

- Cambiar **solo** lo que pida. Nunca regenerar ni convertir toda la presentación: una conversión .odp → .pptx → .odp
  alteró varias diapositivas (v2, descartada).
- Trabajar sobre la última versión que el usuario guardó. Si la edita a mano, leer primero su archivo.
- La pregunta problema de la diapositiva 5 es la literal del anteproyecto (`tesis_overleaf/Chapters/2 Planteamiento.tex`).

## Pendientes

- Diapositiva 15, «Arquitectura del sistema»: muestra la Raspberry Pi como controlador, pero en los ensayos el
  control corrió en un PC con un Arduino Uno (diapositiva 16). Hay que preguntar al usuario si cambia el título a
  «Arquitectura objetivo» o se ajusta la diapositiva.
- Se propuso devolver al marco teórico la diapositiva «Polígono de soporte y estabilidad», porque el OE4 usa el
  margen de estabilidad estática. El usuario no ha respondido.
- En el modelo sí se usó la dinámica nominal (Lagrange, capítulo 9 de la tesis); el número de Froude no se usó.
