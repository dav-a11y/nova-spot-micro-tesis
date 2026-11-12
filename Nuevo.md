# Nuevo — pruebas de estabilidad y referencias extremas AS5600

**Fecha de incorporación:** 7 de octubre de 2026  
**Fuente:** mediciones entregadas por el operador  
**Muestras:** 100 por sensor y postura  
**Unidades:** grados absolutos del imán medidos por AS5600

## Interpretación y seguridad

El operador indica que las patas/servos 1 y 2 son delanteros; patas 3 y 4 son
traseros. Los sentidos/posturas evaluados fueron fémur hacia atrás/adelante,
coxa hacia arriba/abajo y tibia hacia adelante/atrás.

Los extremos de estas posturas se guardan como **referencias angulares
observadas**, candidatas a describir el recorrido de los 12 grados de libertad.
No se deben tratar todavía como topes mecánicos certificados, límites seguros
de control ni límites PWM: son lecturas magnéticas RAW, no se aportaron pulsos
PWM, calibración cero/sentido, márgenes mecánicos ni validación de repetición
entre ciclos. La estabilidad describe la dispersión de 100 lecturas en cada
postura, no la exactitud de la posición mecánica.

No convertir estos valores automáticamente a radianes articulares ni usarlos
para mandar servos. Mantener la autorización de control desactivada. FEMUR 3
presenta una señal especialmente variable hacia adelante.

## Referencias extremas por articulación

Los intervalos en las columnas son los mínimos y máximos de las muestras para
esa postura. Se conserva el promedio y la variación total comunicados por el
operador; no se recalculan, aunque el redondeo pueda producir pequeñas
diferencias entre `máximo - mínimo` y la variación reportada.

### Fémures — hacia atrás y hacia adelante

| DOF | Lado | Hacia atrás: mínimo–máximo ° | Media ° | Variación ° | Estado reportado | Hacia adelante: mínimo–máximo ° | Media ° | Variación ° | Estado reportado |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| Fémur 1 | Delantero | 246.182–246.357 | 246.288 | 0.176 | Se mantiene muy estable | 117.861–117.949 | 117.916 | 0.088 | Se mantiene muy estable |
| Fémur 2 | Delantero | 152.666–153.105 | 152.767 | 0.439 | Se mantiene estable | 148.359–148.447 | 148.441 | 0.088 | Se mantiene muy estable |
| Fémur 3 | Trasero | 182.373–184.043 | 183.020 | 1.670 | El valor está variando mucho | 23.730–39.551 | 30.772 | 15.820 | El valor está variando mucho |
| Fémur 4 | Trasero | 69.434–69.697 | 69.500 | 0.264 | No indicado | 103.184–103.887 | 103.638 | 0.703 | El valor varía |

### Coxas — hacia arriba y hacia abajo

| DOF | Lado | Hacia arriba: mínimo–máximo ° | Media ° | Variación ° | Estado reportado | Hacia abajo: mínimo–máximo ° | Media ° | Variación ° | Estado reportado |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| Coxa 1 | Delantera | 138.867–138.867 | 138.867 | 0.000 | Se mantiene muy estable | 127.969–128.057 | 128.036 | 0.088 | Se mantiene muy estable |
| Coxa 2 | Delantera | 146.953–147.041 | 147.026 | 0.088 | Se mantiene muy estable | 164.883–164.883 | 164.883 | 0.000 | Se mantiene muy estable |
| Coxa 3 | Trasera | 174.287–175.078 | 174.381 | 0.791 | El valor varía moderadamente | 185.273–186.064 | 185.992 | 0.791 | El valor varía moderadamente |
| Coxa 4 | Trasera | 135.791–135.791 | 135.791 | 0.000 | No indicado | 167.080–167.168 | 167.081 | 0.088 | No indicado |

### Tibias — hacia adelante y hacia atrás

| DOF | Lado | Hacia adelante: mínimo–máximo ° | Media ° | Variación ° | Estado reportado | Hacia atrás: mínimo–máximo ° | Media ° | Variación ° | Estado reportado |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| Tibia 1 | Delantera | 240.557–240.557 | 240.557 | 0.000 | Se mantiene muy estable | 75.410–75.498 | 75.497 | 0.088 | Se mantiene muy estable |
| Tibia 2 | Delantera | 77.959–78.047 | 78.012 | 0.088 | Se mantiene muy estable | 233.965–233.965 | 233.965 | 0.000 | Se mantiene muy estable |
| Tibia 3 | Trasera | 239.941–240.029 | 239.955 | 0.088 | Se mantiene muy estable | 256.465–256.553 | 256.468 | 0.088 | Se mantiene muy estable |
| Tibia 4 | Trasera | 73.740–73.828 | 73.813 | 0.088 | Se mantiene muy estable | 301.904–301.904 | 301.904 | 0.000 | Se mantiene muy estable |

## Lectura de estabilidad

- Fémures 1 y 2: lecturas concentradas en ambas posturas según las etiquetas
  reportadas (variación máxima comunicada: 0.439°).
- Fémur 3: requiere revisión antes de emplear su lectura; variación de 1.670°
  hacia atrás y 15.820° hacia adelante.
- Fémur 4: variación reportada de 0.264° hacia atrás y 0.703° hacia adelante;
  el operador clasificó solo la postura hacia adelante como variable.
- Coxas 1 y 2: variaciones de 0.000–0.088° en las dos posturas.
- Coxas 3: variación moderada reportada, 0.791° en ambas posturas.
- Coxa 4 y tibias: se registran todos los valores; donde no se envió etiqueta de
  estado se deja expresamente como “No indicado”.

## Qué falta para convertir referencias en topes válidos

1. Confirmar el mapa físico de cada sensor y cada canal TCA, especialmente la
   discrepancia previa entre FEMUR 2 y COXA 2 en canales 5/6 del TCA `0x71`.
2. Repetir la adquisición en ciclos independientes y verificar estabilidad,
   retorno y cruce circular de 0°/360°.
3. Identificar topes mecánicos sin forzar los servos y fijar márgenes seguros.
4. Medir por separado la relación entre posición/lectura magnética y pulsos
   PWM, con pruebas autorizadas y protección mecánica.
5. Solo después establecer límites de control; hasta entonces, este documento
   es un registro de observaciones, no una autorización de movimiento.
