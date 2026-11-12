# Documento final de tesis

Esta carpeta reúne, desde el 1 de septiembre de 2026, el material que se
convertirá en la entrega final de la tesis sobre el robot cuadrúpedo Nova Spot
Micro. Es distinta del anteproyecto ubicado en `tesis_overleaf`: aquel archivo
sirve como antecedente y fuente revisable, pero no debe confundirse con el
documento final.

## Criterio de redacción

El texto final describirá el trabajo ejecutado y la evidencia obtenida. Se
emplearán formulaciones como:

- «se diseñó», «se implementó» y «se verificó» para actividades terminadas;
- «se analizó» y «se obtuvo» para resultados respaldados por datos;
- «se encontró» o «los resultados indicaron» para interpretaciones;
- «permaneció pendiente» o «no se demostró» cuando una actividad no esté
  cerrada.

No se transformarán automáticamente expresiones del anteproyecto como «se
realizará» en afirmaciones de cumplimiento. Cada afirmación en pasado deberá
estar respaldada por código, configuración, protocolo, registro, tabla, figura,
prueba o medición identificable.

## Cadena obligatoria de trazabilidad

Cada resultado del documento debe poder recorrerse en ambos sentidos:

`problema → pregunta → objetivo → actividad → método → evidencia → resultado → conclusión`

Una conclusión sin resultado verificable se tratará como una interpretación no
demostrada. Una simulación incluirá modelo, supuestos, parámetros, condiciones,
configuración, resultados, contraste e identificación explícita de sus
limitaciones.

## Organización inicial

- `Presentacion_PartiendoCronograma.pdf`: orientación de Proyecto de Grado II
  sobre ejecución, evidencia, criterios de aceptación y productos documentales.
- `MATRIZ_OBJETIVO_EVIDENCIA.md`: mapa vivo entre objetivos, métodos, evidencia,
  resultados y secciones finales.
- `PLAN_DOCUMENTO_FINAL.md`: estructura y reglas para migrar contenido del
  anteproyecto sin afirmar resultados todavía inexistentes.
- `../Documentacion/PROTOCOLO_CARACTERIZACION_FISICA.md`: procedimiento y
  criterios para obtener geometría, masas, mapa de canales y calibraciones sin
  confundir valores nominales con mediciones.

Los capítulos editables en LaTeX se incorporarán progresivamente cuando se
revise cada sección. Los datos pesados de rosbag2 permanecen en
`Experimentos/rosbag2`; dentro de esta carpeta se citarán sus registros, hashes,
tablas y gráficas reproducibles sin duplicar las bases de datos.

## Primera versión compilable

La fuente principal es `Thesis.tex` y el PDF generado se publica como
`Documento_TESIS_PRELIMINAR.pdf`. Esta versión integra el contenido reutilizable
del anteproyecto con capítulos nuevos de metodología ejecutada, desarrollo,
resultados, discusión, conclusiones provisionales y trabajo pendiente.

El capítulo 7 documenta el modelo matemático efectivamente implementado:
cinemática directa e inversa, jacobiano, dinámica nominal, actuadores,
contacto y estabilidad. Sus verificaciones computacionales son reproducibles,
pero se distinguen expresamente de la validación física aún pendiente.

Para compilar desde esta carpeta:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Thesis.tex
```

El PDF es preliminar porque todavía faltan la caracterización y validación
física y una comparación experimental final emparejada. PPO fue entrenado y
evaluado, pero la política obtenida se rechazó porque ninguna escala positiva
cumplió el criterio conjunto; deberá rediseñarse antes de repetir la campaña.
La palabra «preliminar» no autoriza a completar apartados con resultados
esperados.

## Evidencia visual

El PDF incorpora gráficas procedentes de ensayos aceptados, resultados
negativos trazables y dos diagramas de arquitectura. La trazabilidad entre figura, datos,
conclusión y limitación se mantiene en `INDICE_EVIDENCIAS_VISUALES.md`.

Las figuras específicas de contacto y MuJoCo se regeneran desde los CSV con:

```bash
python3 generar_figuras_resultados.py
./compilar.sh
```

No se incorporarán capturas de una simulación como sustituto de datos. Las
capturas futuras podrán documentar montaje o contexto, mientras que las
afirmaciones cuantitativas deberán apoyarse en tablas y gráficas reproducibles.

## Regla permanente para cada avance

Después de cada avance técnico se aplicará este flujo:

1. identificar qué objetivo y requisito atiende;
2. ejecutar una verificación proporcional al cambio;
3. conservar configuración, versión, datos, pruebas y posibles fallos;
4. decidir explícitamente si el criterio de aceptación se cumplió;
5. actualizar `CONTINUIDAD.md`, el seguimiento y GitHub;
6. incorporar al documento de tesis únicamente los métodos y resultados
   respaldados, junto con sus gráficas, limitaciones y conclusión permitida;
7. recompilar y revisar visualmente el PDF cuando cambie su contenido.

Si un ensayo falla o el resultado es inconcluso, se documentará como tal para
la trazabilidad, pero no se presentará en la tesis como cumplimiento. Si aporta
una decisión técnica o una limitación relevante, podrá aparecer en metodología
o discusión con esa clasificación explícita.

## Fuente recibida

La presentación fue copiada desde
`/home/pavilion/Descargas/Presentacion_PartiendoCronograma.pdf`. Ambas copias
tenían el SHA-256:

`200ed2f5ada680325b5bbbd9efd83e2e906b9bdb65c609715d209c7a88cdc160`

## Objetivos vigentes al 7 de septiembre de 2026

Se adoptó literalmente el objetivo general y los cuatro específicos suministrados por el usuario. OE1: hardware/software; OE2: modelado; OE3: control aprendido; OE4: margen de estabilidad estática, seguimiento de posición articular y repetibilidad del patrón de marcha. Matriz y referencias internas sincronizadas. PDF recompilado de 72 páginas.

## Unificación con el anteproyecto (22 de octubre de 2026)

El contenido de `tesis_overleaf` que no estaba en este documento quedó
integrado: el alcance y los productos esperados del anteproyecto con su estado
(capítulo 5), el plan metodológico de ocho fases con su diagrama y su
correspondencia con la ejecución (capítulo 10), y el cronograma Gantt y el
presupuesto con su conciliación (capítulo 18). `tesis_overleaf` se conserva sin
cambios como antecedente; el documento de entrega es este.
