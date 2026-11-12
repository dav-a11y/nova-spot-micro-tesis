# Identificación física inicial del cuadrúpedo — 15 de octubre de 2026

## Mapa de actuadores confirmado

El operador confirmó que las coxas y los fémures se movieron en el orden
esperado. Se conserva el esquema de canales PCA9685:

| Pata | Ubicación | Coxa | Fémur | Tibia |
|---|---|---:|---:|---:|
| 1 | Delantera derecha | CH0 | CH4 | CH8 |
| 2 | Delantera izquierda | CH1 | CH5 | CH9 |
| 3 | Trasera derecha | CH2 | CH6 | CH10 |
| 4 | Trasera izquierda | CH3 | CH7 | CH11 |

Los números de servo son PCA CH + 1: 1–4 coxas, 5–8 fémures y 9–12 tibias.
Este mapa se guarda además en la tabla `conexion_confirmada` de
`datos_cuadrupedo.sqlite`.

## Referencias angulares por articulación

Valores declarados por el operador, en grados de orden del servo (0–180°).
“Arriba/abajo” o “delante/atrás” conservan el sentido indicado para cada
articulación; no se asume que los sentidos sean iguales entre servos.

| Articulación | PCA | Límite A | Centro estático | Límite B | Observación |
|---|---:|---:|---:|---:|---|
| Coxa 1 | CH0 | Arriba: 95° | 150° | Abajo: 180° | — |
| Coxa 2 | CH1 | Arriba: 95° | 40° | Abajo: 0° | — |
| Coxa 3 | CH2 | Arriba: 100° | 55° | Abajo: 15° | — |
| Coxa 4 | CH3 | Arriba: 115° | 147° | Abajo: 180° | — |
| Fémur 1 | CH4 | Delante: 20° | 110° | Atrás: 180° | El extremo trasero choca con el poste; no llevarlo allí. |
| Fémur 2 | CH5 | Delante: 180° | 100° | Atrás: 15° | El extremo trasero choca con el poste; no llevarlo allí. |
| Fémur 3 | CH6 | Delante: 30° | 100° | Atrás: 170° | — |
| Fémur 4 | CH7 | Delante: 180° | 100° | Atrás: 15° | — |
| Tibia 1 | CH8 | Delante: 15° | 100° | Atrás: 170° | — |
| Tibia 2 | CH9 | Delante: 15° | 80° | Atrás: 100° | Límites corregidos por el operador; extremos aún no validados mecánicamente. |
| Tibia 3 | CH10 | Delante: 1° | 100° | Atrás: 170° | — |
| Tibia 4 | CH11 | Delante: 160° | 70° | Atrás: 5° | Se reportó contacto con un límite; mantener bloqueada en rutinas automáticas. |

Estos son topes declarados, no necesariamente límites seguros ya validados.
Las pruebas automáticas deben usar márgenes conservadores y no dirigirse a
los extremos señalados como interferencia mecánica.

## Datos adquiridos

La rutina `c` llevó un servo por vez a ±8° respecto a la posición estática,
con pausas de medida. Se hicieron campañas separadas para coxas, fémures y
tibia 1/tibia 3. El firmware transmite las órdenes y los 16 valores ADC. Las
capturas quedaron en la tabla `trama` con sus sesiones y marcas temporales.

| Campaña | Sesión SQLite | Tramas guardadas |
|---|---:|---:|
| Coxas CH0–CH3 | 10 | 235 |
| Fémures CH4–CH7 | 11 | 335 |
| Tibias CH8 y CH10 | 12 | 312 |
| Coxas CH0–CH3 (repetición) | 13 | 351 |
| Fémures CH4–CH7 (repetición) | 14 | 351 |
| Tibias CH8 y CH10 (repetición) | 15 | 360 |
| Los diez servos habilitados, orden `c` | 16 | 625 |
| Tibia 2, orden `t`, excursión ±2° | 17 | 265 |
| Orden `x` antes del diagnóstico I²C | 18 | 42 |
| Verificación pasiva de arranque apagado | 19 | 33 |

Los resúmenes `+8°`/`−8°` no identifican canales ADC exclusivos: en las
campañas aparecen niveles comunes entre canales y variación amplia dentro de
cada meseta. No se asignó ningún `canal_mux` a una articulación y ninguna de
estas sesiones se marcó válida para entrenamiento de posición.

### Resultado cuantitativo del mapeo MUX

Se compararon las medianas ADC de las mesetas `−8°` y `+8°` y se restó el
desplazamiento común entre canales. Los candidatos de mayor diferencial
quedaron por debajo del ruido observado; por tanto, son solo candidatos
estadísticos y no deben guardarse como conexiones confirmadas.

| Campaña | Articulación | Canal MUX candidato | Diferencial | Ruido | Resultado |
|---|---|---:|---:|---:|---|
| Coxas | Coxa 1 | CH4 | +29 cuentas | 81 | No concluyente |
| Coxas | Coxa 2 | CH5 | −4 cuentas | 80 | No concluyente |
| Coxas | Coxa 3 | CH3 | +7 cuentas | 76 | No concluyente |
| Coxas | Coxa 4 | CH1 | −19 cuentas | 78 | No concluyente |
| Fémures | Fémur 1 | CH15 | −11 cuentas | 26 | No concluyente |
| Fémures | Fémur 2 | CH7 | −1 cuenta | 27 | No concluyente |
| Fémures | Fémur 3 | CH15 | 0 cuentas | 27 | Sin respuesta detectable |
| Fémures | Fémur 4 | CH15 | 0 cuentas | 28 | Sin respuesta detectable |
| Tibias | Tibia 1 | CH12 | +5 cuentas | 28 | No concluyente |
| Tibias | Tibia 3 | CH15 | 0 cuentas | 61 | Sin respuesta detectable |

En síntesis: el movimiento de los actuadores ya está asociado al PCA9685,
pero aún no se ha identificado la realimentación de los potenciómetros. No es
posible ajustar una conversión ADC→ángulo ni entrenar una caminata con la
realimentación real hasta resolver esto. En una primera revisión posterior no
se encontró el puerto serie; el Uno se reconectó después y permitió ejecutar
la segunda ronda documentada a continuación.

### Segunda ronda con la placa reconectada

Se reconectó el Uno y se ejecutaron nuevamente las tres campañas por grupos,
con movimientos de ±8° y retorno al centro. El análisis adicional de
correlación entre la orden angular y cada una de las 16 lecturas ADC tampoco
encontró una señal consistente: el mayor coeficiente absoluto por articulación
fue 0,23. Los canales que quedaron como candidatos variaron entre campañas,
por lo que no se asignó ninguno como realimentación.

| Articulación | Mejor correlación absoluta | Canal candidato | Evaluación |
|---|---:|---:|---|
| Coxa 1 | 0,17 | CH3 | No concluyente |
| Coxa 2 | 0,07 | CH4 | No concluyente |
| Coxa 3 | 0,08 | CH10 | No concluyente |
| Coxa 4 | 0,14 | CH14 | No concluyente |
| Fémur 1 | 0,08 | CH6 | No concluyente |
| Fémur 2 | 0,06 | CH14 | No concluyente |
| Fémur 3 | 0,10 | CH1 | No concluyente |
| Fémur 4 | 0,10 | CH2 | No concluyente |
| Tibia 1 | 0,23 | CH14 | No concluyente |
| Tibia 3 | 0,22 | CH6 | No concluyente |

Este resultado repetido sugiere que la limitación ya no es la cantidad de
movimientos: en las entradas del MUX no aparece una respuesta que siga las
órdenes de servo. Antes de seguir ampliando excursiones, revisar el cableado
del cursor analógico de cada potenciómetro hacia C0–C15, la referencia común
de GND y que `SIG` llegue a A0. La rutina de adquisición continúa dejando
deshabilitadas tibias 2 y 4.

### Ronda conjunta y prueba de tibia 2

Después se ejecutó `c`, que movió individualmente los diez servos habilitados
±8° y volvió cada uno a su centro (sesión 16). También se repitió únicamente
la prueba ya usada de tibia 2, ±2° alrededor de 80° (sesión 17); no se usaron
sus extremos declarados. En la campaña conjunta, la mayor correlación
absoluta por cada servo habilitado estuvo entre 0,03 y 0,12; en la prueba de
tibia 2 fue 0,10. Los mejores canales cambiaron y no son una asociación
repetible, por lo que siguen sin asignarse entradas MUX.

La ronda confirma que los actuadores sí responden a las órdenes, pero la
telemetría ADC disponible no está registrando una relación utilizable con sus
ángulos. Tibia 4 se mantuvo apagada por el límite mecánico observado. Para
seguir identificando realimentación hace falta comprobar que cada cursor
analógico llega realmente a una entrada C0–C15 del multiplexor (además de GND
común) y que SIG llega a A0; repetir movimiento sin esa señal no permite
estimar el ángulo.

### Comprobación del bus I²C del Uno

Con todos los PWM apagados se cargó temporalmente el escáner I²C de
`CODIGO/diagnostico_i2c/diagnostico_i2c.ino`. Respondieron el PCA9685 (`0x40`)
y un TCA9548A (`0x70`); no respondió `0x71`. El TCA `0x70` respondió, pero
ninguno de sus ocho canales presentó un AS5600 (`0x36`). Esto confirma que los
doce AS5600 descritos en el registro histórico no están actualmente visibles
en el bus del Uno; ese conjunto no puede usarse en esta configuración.

Luego se restauró y verificó el firmware
`movimiento_suspendido_11_servos.ino`. Una captura pasiva de 33 tramas confirmó
estado `OFF` tras el arranque. La lectura ADC en reposo tampoco es uniforme:
CH0–CH3 y CH8–CH11 quedaron clavados en 98 cuentas, CH14 en 316, y varias
entradas restantes fluctuaron ampliamente. Junto con la ausencia de
correlación durante las pruebas, esto indica que todavía no hay una entrada
analógica estable y atribuible a cada servo; no se asignó ningún canal.

## Límites mecánicos y estado

- Tibia 2 (PCA CH9): el valor trasero fue corregido posteriormente por el
  operador de 10° a 100°. Se mantiene excluida de rutinas generales; su ensayo
  dedicado vigilado por C9 completó 90° y 25° en la sesión 76.
- Tibia 4 (PCA CH11): se informó contacto con límite en una dirección; el
  operador la regresó a centro. Queda excluida de rutinas automáticas.
- Fémur 1 tiene contacto reportado en su extremo trasero; no se ordenó ese
  extremo. Fémur 2 también tiene contacto reportado.
- La base contiene posiciones estáticas y límites declarados, pero los trata
  como referencias sin validar.

## Próximo paso de identificación

Mantener el esquema PCA confirmado y resolver las entradas analógicas: medir
cada señal del cursor del potenciómetro en el MUX en reposo y durante una
articulación individual. Solo después de obtener una asociación uno-a-uno y
una variación repetible se ajustará el modelo ADC–ángulo y se entrenarán las
trayectorias `crawl` y `step`.

## Revisión con selectores D8–D11 — sesión 21

El operador aclaró que los selectores S0–S3 del multiplexor están conectados a
los pines digitales D8–D11 y SIG a A0. Se actualizó y cargó
`movimiento_suspendido_11_servos.ino` con ese pinout. Las lecturas anteriores
hechas con selectores D4–D7 no describen esta conexión y quedan superadas.

Se repitió la calibración individual de los diez servos habilitados con una
excursión de ±8° y 70 s de captura. La sesión 21 guardó 673 tramas y terminó
en estado `STAND`, con los servos habilitados en sus posiciones centrales.
Tibia 2 y tibia 4 permanecieron desactivadas. El análisis de mesetas y
correlación confirmó estas asociaciones:

| Articulación | PCA | Canal MUX | Correlación orden/ADC | Resultado |
|---|---:|---:|---:|---|
| Coxa 1 | CH0 | C0 | −0,96 | Señal clara y repetible |
| Coxa 2 | CH1 | C1 | −0,93 | Señal clara y repetible |
| Coxa 3 | CH2 | C3 | −0,92 | Señal clara y repetible |
| Coxa 4 | CH3 | C2 | −0,96 | Señal clara y repetible |
| Fémur 1 | CH4 | — | +0,01 (máxima absoluta) | Sin asociación concluyente |
| Fémur 2 | CH5 | C5 | −0,96 | Señal clara y repetible |
| Fémur 3 | CH6 | — | −0,07 (máxima absoluta) | Sin asociación concluyente |
| Fémur 4 | CH7 | C6 | −0,96 | Señal clara y repetible |
| Tibia 1 | CH8 | — | −0,04 (máxima absoluta) | Sin asociación concluyente |
| Tibia 2 | CH9 | — | — | No probada; permanece desactivada |
| Tibia 3 | CH10 | — | +0,43, con ruido alto | Sin asociación concluyente |
| Tibia 4 | CH11 | — | — | No probada; permanece desactivada |

Los seis canales indicados como claros presentaron cambios de aproximadamente
33–39 cuentas entre mesetas y ruido de 2–3 cuentas. Se confirma así que al
menos seis potenciómetros sí entregan una señal legible por el multiplexor.
Los demás canales no se marcan como desconectados: todavía falta una prueba
individual más larga o revisar su cableado. La sesión queda cruda y no válida
para entrenamiento hasta completar ese mapeo y calibrar ADC→ángulo.

## Prueba de tibia 2 — sesión 22

Con los selectores D8–D11 se ejecutó la prueba aislada de tibia 2 alrededor de
80°, entre 78° y 82° (±2°), sin usar sus extremos declarados. Se guardaron
215 tramas, de las cuales 194 corresponden al movimiento. La lectura C9
respondió de forma repetible: mediana de 374 cuentas a 78° y 366 cuentas a
82°; la correlación fue −0,94. Se registró tibia 2 → C9 en la base de datos.

Después se restableció la postura central de los servos habilitados (sesión
23). Tibia 2 y tibia 4 quedaron con PWM apagado. Tibia 4 aún no se probó: se
mantiene el antecedente de contacto mecánico, pero no está documentado si
ocurrió al aumentar o disminuir el ángulo. No se ordenará movimiento a esa
articulación hasta identificar el sentido que debe evitarse.

## Prueba secuencial controlada — sesión 25

Se añadió la orden `s` al firmware para mover una articulación por vez,
agrupando coxa, fémur y tibia por pata, con excursión de ±2° y pausas de
600 ms entre posiciones. Tibia 2 y tibia 4 permanecieron desactivadas. La
sesión guardó 312 tramas y terminó en `STAND`, con los servos habilitados en
sus centros. Fue una prueba de movimiento suspendido, no una marcha. La
excursión pequeña no basta para reasignar canales; se conserva el mapeo
confirmado en las sesiones 21 y 22.

## Límite mecánico de tibia 1 y parada — sesión 26

El operador confirmó que la vibración observada provenía de tibia 1 (PCA
CH8), que había llegado a su tope mecánico. Se apagaron las salidas PWM con
`x`; la sesión 26 terminó en estado `OFF`. Tibia 1 quedó deshabilitada en el
firmware para excluirla de pruebas `m`, `s` y `c` hasta validar un intervalo
seguro. No volver a mover CH8 por ±2° alrededor de 100° ni usar el extremo
declarado como límite sin revisión mecánica.

## Estimación local de posición desde ADC — sesión 27

Se hizo una captura pasiva de 33 tramas con el PWM apagado. Para las
articulaciones con canal ya mapeado, se interpoló entre las lecturas ADC
medidas en el centro y a ±8° (tibia 2: ±2°). La pendiente local observada es
aproximadamente −2,0 a −2,4 cuentas ADC por grado. Esta conversión es válida
solo cerca del intervalo medido; no se extrapola a topes.

| Articulación | MUX | ADC actual (mediana) | Posición local estimada | Nota |
|---|---:|---:|---:|---|
| Coxa 1 | C0 | 93 | Fuera del intervalo calibrado | No extrapolar; inspeccionar posición física. |
| Coxa 2 | C1 | 481 | 41,3° | Referencia central declarada: 40°. |
| Coxa 3 | C3 | 447 | 55,4° | Referencia central declarada: 55°. |
| Coxa 4 | C2 | 196 | 148,1° | Referencia central declarada: 147°. |
| Fémur 2 | C5 | 318 | 101,2° | Referencia central declarada: 100°. |
| Fémur 4 | C6 | 319 | 100,8° | Referencia central declarada: 100°. |
| Tibia 2 | C9 | 370 | 80,0° | Referencia central declarada: 80°. |

Las medianas crudas de C0–C11 en esa captura fueron: 93, 481, 196, 447,
456, 318, 319, 0, 612, 370, 393 y 319 cuentas, respectivamente. C4, C7, C8,
C10 y C11 todavía no tienen una asociación servo–canal confirmada. La señal
actual C8 de tibia 1 no se convierte a ángulo porque CH8 quedó bloqueado tras
alcanzar su tope y no se calibró un intervalo seguro.

## Pulsos pequeños de coxas — sesiones 28 y 29

La sesión 28 volvió a confirmar, con 71 tramas en estado `OFF`, las señales
en reposo: C0=93, C1≈481, C3≈447 y C2≈196. C0 sigue fuera de la calibración
local de coxa 1; por seguridad se deshabilitó PCA CH0 en el firmware.

Se añadió la orden `q`, que no llama a la rutina de postura general: centra y
mueve solo coxas 2–4, individualmente, primero a +2°, después a −2° y
finalmente a la referencia declarada, con pausas para observar el ADC. La
sesión 29 registró 259 tramas: 134 durante la prueba (`COXA`) y el resto con
PWM apagado (`OFF`). Coxa 1 no se movió; al finalizar, PCA CH0–CH15 quedó
apagado. Respuesta de las señales en las posiciones ordenadas:

| Articulación | PCA | MUX | −2° | Centro | +2° | Observación |
|---|---:|---:|---:|---:|---:|---|
| Coxa 2 | CH1 | C1 | 38°: 482,6 (n=13) | 40°: 482,0 (n=234) | 42°: 478,8 (n=12) | Cambio pequeño, tendencia descendente; conviene ampliar la meseta para mejorar la resolución. |
| Coxa 3 | CH2 | C3 | 53°: 448,7 (n=12) | 55°: 445,5 (n=233) | 57°: 443,4 (n=13) | Cambio repetible y consistente con el mapeo previo. |
| Coxa 4 | CH3 | C2 | 145°: 202,2 (n=12) | 147°: 197,2 (n=233) | 149°: 192,6 (n=13) | Cambio repetible y consistente con el mapeo previo. |

Los valores de centro incluyen la mayor parte de la captura en reposo central;
no deben interpretarse como cientos de mediciones independientes de una
meseta exclusiva. Esta prueba confirma movimiento y respuesta local, pero no
valida los extremos mecánicos declarados ni permite extrapolar ADC a todo el
rango. Mantener coxa 1 bloqueada hasta revisar por qué C0 permanece en 93 y
no probar los límites completos sin ampliar progresivamente el intervalo con
observación física y parada disponible.

## Rampa de coxas hasta ±4° — sesión 30

La orden `q` se amplió para probar cada una de las coxas 2–4 en secuencia
−4°, −2°, centro, +2°, +4° y centro, con pasos de mando de 1° y mesetas.
Se guardaron 280 tramas: 215 en `COXA` y 65 en `OFF`. La respuesta ADC
acompañó el movimiento en las tres señales:

| Articulación | MUX | −4° | −2° | +2° | +4° | Tendencia |
|---|---:|---:|---:|---:|---:|---|
| Coxa 2 | C1 | 36°: 486,8 (n=13) | 38°: 482,4 (n=10) | 42°: 479,4 (n=9) | 44°: 474,8 (n=13) | Descendente con el ángulo; señal clara. |
| Coxa 3 | C3 | 51°: 451,8 (n=13) | 53°: 447,8 (n=10) | 57°: 442,4 (n=10) | 59°: 437,5 (n=13) | Descendente y consistente con pruebas anteriores. |
| Coxa 4 | C2 | 143°: 206,2 (n=13) | 145°: 200,6 (n=10) | 149°: 192,9 (n=10) | 151°: 188,8 (n=13) | Descendente y consistente mientras PWM estaba activo. |

Advertencia: durante la meseta final con PWM activo, coxa 4 volvió a su
referencia (147°, C2≈198–199). Después de apagar PWM, C2 cambió de forma
persistente a 145 cuentas, mientras los otros canales permanecieron estables.
Esto puede indicar desplazamiento al liberar el servo o una anomalía de la
señal/conexión. No se debe continuar ampliando coxa 4 hasta verificar
visualmente su posición y confirmar que el valor C2 volvió a ser coherente.
Las tres coxas terminaron con PWM apagado; no se ejecutó otra orden después
de detectar este cambio.

## Coxas 2–3 con PWM de sostén — sesiones 31 y 32

El operador confirmó visualmente que el cambio de C2 ocurrió por gravedad al
apagar el servo. Para evitar repetirlo, se ajustó la orden `q`: mueve solo
PCA CH1 (coxa 2) y CH2 (coxa 3), y deja ambos canales energizados en el centro.
Coxa 4 permanece sin PWM y no se mueve en esta rutina.

La sesión 31 guardó 235 tramas durante una rampa hasta ±4° y terminó en
`HOLD_COXA`; C1 y C3 siguieron el movimiento y quedaron estables cerca de 481
y 446 cuentas. C2 de coxa 4 permaneció cerca de 143 cuentas mientras su PWM
estuvo apagado.

En la sesión 32 se amplió la rampa por pasos de 2° hasta ±6°. Se registraron
273 tramas y las mesetas extremas fueron:

| Articulación | MUX | −6° | −4° | −2° | +2° | +4° | +6° |
|---|---:|---:|---:|---:|---:|---:|---:|
| Coxa 2 | C1 | 34°: 492,1 | 36°: 486,4 | 38°: 482,5 | 42°: 477,9 | 44°: 474,7 | 46°: 470,8 |
| Coxa 3 | C3 | 49°: 457,5 | 51°: 451,9 | 53°: 448,2 | 57°: 442,0 | 59°: 437,0 | 61°: 433,3 |

El ADC descendió monótonamente con el aumento del ángulo en ambas
articulaciones, coherente con las sesiones previas. Al terminar, las órdenes
estaban en 40° y 55°, con lecturas C1=483 y C3=447; estado `HOLD_COXA`.
Esto valida respuesta local hasta ±6°, no los límites mecánicos. Coxa 1
continúa bloqueada por discrepancia de C0 y coxa 4 permanece sin PWM hasta
recuperar/confirmar su posición física.

## Rampa de coxas 2–3 hasta ±8° — sesión 33

Se amplió el barrido por pasos de 2° hasta ±8°. La captura reunió 338 tramas
y terminó con estado `HOLD_COXA`, órdenes 40°/55° y PWM activo en CH1/CH2.
Las lecturas de meseta para coxa 2 (C1) fueron 497,8 cuentas a 32°, 492,8 a
34°, 486,2 a 36°, 481,6 a 38°, 479,2 a 42°, 474,8 a 44°, 471,1 a 46° y
464,8 a 48°. Para coxa 3 (C3): 463,3 a 47°, 457,8 a 49°, 452,1 a 51°,
448,8 a 53°, 442,3 a 57°, 435,7 a 59°, 432,6 a 61° y 427,0 a 63°.
Se conserva la tendencia descendente; los pasos individuales muestran unos
pocos ADC de dispersión.

## Rampa de coxas 2–3 hasta ±10° — sesión 34

Se amplió la rampa por pasos de 2° hasta ±10°. La sesión quedó con 416
tramas y finalizó en `HOLD_COXA`: coxa 2=40°, coxa 3=55°, lecturas finales
C1≈481 y C3≈447. Las mesetas de extremos fueron C1≈502 cuentas a 30° y
≈466 a 50°; C3≈469 a 45° y ≈422 a 65°. Ambas señales muestran la tendencia
esperada; coxa 2 presenta una pequeña inversión de 1–2 cuentas entre algunas
mesetas, dentro de la dispersión observada. C2 de coxa 4 siguió en ≈143 con
su PWM apagado. No se han validado topes ni se extrapola el modelo hasta
ellos.

## Rampa de coxas 2–3 hasta ±12° — sesión 35

Se recorrieron posiciones en pasos de 2° hasta coxa 2: 28–52° y coxa 3:
43–67°. La captura guardó 502 tramas y terminó en `HOLD_COXA`, con 40°/55°
ordenados y PWM de sostén en CH1/CH2. En coxa 2, C1 pasó de 507,5 cuentas a
28° a 457,2 a 52°; en coxa 3, C3 pasó de 474,8 a 43° a 417,9 a 67°. La
tendencia fue descendente y consistente con el ángulo en ambas. C2 de coxa 4
permaneció alrededor de 143–144; su articulación sigue sin PWM.

## Rampa de coxas 2–3 hasta ±14° — sesión 36

Se probaron posiciones cada 2° hasta coxa 2: 26–54° y coxa 3: 41–69°.
La sesión guardó 528 tramas y terminó en `HOLD_COXA`, con órdenes 40°/55°,
C1≈481, C3≈447 y C2≈143. Las señales conservaron su tendencia descendente
con el ángulo. En los extremos, C1 midió 512,7 cuentas a 26° y 450,1 a 54°;
C3 midió 478,5 cuentas a 41° y 413,1 a 69°. No se detectó contacto reportado
ni se alcanzaron los topes declarados. Estas observaciones siguen siendo de
posición suspendida y no validan aún el movimiento bajo carga de marcha.

## Recuperación gradual de coxa 4 — sesión 37

Se usó la orden `r` para recuperar PCA CH3 hacia el centro desde la lectura
caída C2=143. La calibración local estimó aproximadamente 170° como punto de
partida; el primer movimiento a 168° elevó C2 a 146 (+4 cuentas). El siguiente
paso, a 166°, no produjo incremento (C2≈146), por lo que el firmware se
detuvo automáticamente y dejó CH3 energizado en `COXA4_HOLD_CHECK`, orden
166°, lectura final C2≈147–148. No se asume que haya llegado a un tope: la
respuesta nula puede deberse a holgura, contacto mecánico o problema de señal.
No continuar sin inspección visual; el PWM sigue activo para que la gravedad
no vuelva a desplazar la articulación.

## Recuperación con pasos de 1° — sesión 38

El operador observó movimiento en la recuperación anterior, aunque pequeño.
Se permitió una lectura ADC sin cambio aislada y se redujo el paso a 1°,
deteniéndose solo tras tres pasos consecutivos sin respuesta. Desde C2=146,
la estimación inicial fue 169°; C2 respondió en general de forma creciente
hacia el centro: 168°=144, 167°=147, 165°=150, 162°=159, 158°=168,
153°=181, 149°=191 y 147°=197. La coxa alcanzó la referencia y quedó
sostenida con PWM. Esto confirma que la pausa previa se debía a respuesta
pequeña/deadband, no a un tope confirmado.

## Barrido de coxa 4 alrededor del centro — sesión 39

Tras recuperar automáticamente el centro, se probó PCA CH3 individualmente
entre 139° y 155° en incrementos de 2°, regresando a 147° entre ambos
sentidos. C2 respondió en el sentido esperado: a 139° la media fue 216,4;
141° 210,4; 143° 206,3; 145° 201,1; centro 147° 197,4; 149° 192,3;
151° 187,5 y 155° 176,8 cuentas. Al final CH3 quedó energizado en 147°,
C2≈197–198, estado `HOLD_COXA4`. No se observó señal plana ni se alcanzaron
los límites mecánicos.

## Primera prueba individual de fémures — sesión 42

Se añadieron pulsos de ±2° individuales para CH4–CH7, centrando cada fémur
por separado y dejando PWM activo en los cuatro centros. Se guardaron 255
tramas y terminó en `HOLD_FEMURES` con órdenes 110°/100°/100°/100°.

En el MUX, fémur 2 (CH5) respondió en C5: media 321,9 cuentas a 98° y 314,5
a 102°; se confirma el mapeo previo. Fémur 4 (CH7) respondió en C6: 323,3 a
98° y 314,1 a 102°; también confirma el mapeo previo. Para fémur 1 (CH4),
ninguno de C0–C11 varió más de ~0,3 cuentas de media con ±2°; fémur 3 (CH6)
tampoco mostró respuesta clara en C0–C11 (cambios máximos menores a una
cuenta). Hubo variaciones mayores en C14/C15, fuera del bloque C0–C11 que el
operador indicó como conectado; no se atribuyen a ningún servo. Se ampliará
la prueba de forma gradual antes de concluir que F1/F3 no tienen señal.

## Barrido de fémures hasta ±8° — sesión 43

Se recorrieron en secuencia, uno por uno, los cuatro fémures entre ±2°, ±4°,
±6° y ±8°, regresando al centro entre sentidos. La sesión guardó 462 tramas
y terminó con CH4–CH7 energizados en sus referencias (estado `HOLD_FEMURES`).
Comparando las mesetas a centro±8° en C0–C11:

| Articulación | PCA | Canal con respuesta | ADC a centro−8° | ADC a centro+8° | Conclusión |
|---|---:|---:|---:|---:|---|
| Fémur 1 | CH4 | Ninguno claro | C4=461,9 | C4=461,2 | Cambio <1 cuenta; no asignar canal todavía. |
| Fémur 2 | CH5 | C5 | 337,6 | 299,1 | Confirmado; variación de −38,4 cuentas. |
| Fémur 3 | CH6 | Ninguno claro | C7=0 | C7=0 | Cambio <1 cuenta; no asignar canal todavía. |
| Fémur 4 | CH7 | C6 | 336,7 | 299,1 | Confirmado; variación de −37,6 cuentas. |

En F1 y F3 los mandos cambiaron por ±8° y regresaron al centro, pero no se
observó correlación suficiente en las doce entradas conectadas declaradas.
Las variaciones vistas en C13–C15 no se atribuyen a articulaciones. La
siguiente prueba ampliará únicamente F1 y F3, aún lejos de los topes, para
confirmar movimiento e intentar localizar su señal.

## Barrido de coxa 4 hasta ±10° — sesión 40

La rutina recuperó coxa 4 desde C2=144, alcanzó centro (147°, C2≈199) y
barrió 137–157° en pasos de 2°, volviendo al centro entre sentidos. Se
guardaron 341 tramas y terminó en `HOLD_COXA4`, con C2≈198 y CH3 activo.
Las medias de C2 fueron 221,2 cuentas a 137°, 217,1 a 139°, 210,8 a 141°,
206,5 a 143°, 200,7 a 145°, 197,3 a 147°, 192,1 a 149°, 187,9 a 151°,
182,2 a 153°, 176,8 a 155° y 172,7 a 157°. La respuesta fue consistente
en ambos sentidos, sin meseta anómala ni contacto observado.

## Barrido de coxa 4 hasta ±12° — sesión 41

La rutina recuperó la articulación y recorrió 135–159° en pasos de 2°,
regresando al centro después de cada sentido. Se almacenaron 409 tramas y
finalizó en `HOLD_COXA4`, 147°, C2≈197–198. Las medias de C2 fueron 226,3 a
135°, 220,6 a 137°, 216,6 a 139°, 211,4 a 141°, 207,1 a 143°, 201,6 a
145°, 197,4 a 147°, 192,0 a 149°, 187,9 a 151°, 182,6 a 153°, 176,8 a
155°, 172,6 a 157° y 167,0 a 159°. Se mantiene una relación monotónica y
aproximadamente lineal en este intervalo, sin evidencia de tope.

## Prueba de tibia 3 — sesión 46

Después de dejar terminar la rutina de fémures, se ejecutó `l`. Como tibia 1
(CH8) permanece deshabilitada por el tope mecánico previo y tibia 2 (CH9) y
tibia 4 (CH11) también están excluidas, el único actuador movido fue tibia 3
(PCA CH10), de 100° a 108°, luego a 92° y de vuelta a 100°. Se guardaron 134
tramas; la articulación regresó al centro. C8, C9 y C10 del multiplexor se
mantuvieron prácticamente constantes (≈612, 370 y 393 cuentas,
respectivamente). C11 mostró un cambio durante el movimiento, pero fue
inestable en la meseta de 108° (mediana 448; rango 298–747; n=13), frente a
319–325 cuentas en el centro y 338–341 a 92°. Por esa dispersión todavía no
se asigna C11 como señal de tibia 3: hace falta repetir la prueba para separar
una señal real de una lectura espuria o conexión intermitente.

La sesión 45 de fémures, que terminó antes de iniciar esta campaña, sí quedó
completa en la base de datos: 499 tramas, con F1 entre 94° y 126°, F3 entre
84° y 116°, y regreso de ambos al centro (estado `HOLD_FEMURES`). No se usa
para ampliar el mapa de sensores porque no apareció respuesta concluyente en
C0–C11.

## Prueba corta de tibia 2 — sesión 47

Se movió únicamente PCA CH9 (tibia 2), dos ciclos entre 78° y 82° alrededor
del centro declarado de 80°, y terminó en 80° con PWM de sostén. Aunque los
extremos declarados de esta tibia siguen siendo contradictorios, el pequeño
intervalo local se completó sin reportarse choque. Se guardaron 214 tramas.
La respuesta más clara fue MUX C9: mediana 374 cuentas a 78°, 370 a 80° y
366 a 82°; C8, C10 y C11 permanecieron estables. Esto confirma localmente el
mapeo tibia 2 → C9 y el sentido decreciente en ese intervalo, pero no valida
sus límites ni autoriza barridos amplios.

## Repetición de tibia 3 — sesión 48

Se repitió el recorrido aislado de CH10 entre 92° y 108°, con regreso a 100°;
se guardaron 135 tramas. La variación de MUX C11 se reprodujo: alrededor de
100° fue ≈320 cuentas, entre 101° y 104° se mantuvo cerca de 310–321, y saltó
a 747–748 cuentas desde 105° hasta 108°. A 92° quedó en 337–340. C8–C10 no
cambiaron de forma apreciable. Por moverse solo CH10, C11 queda como candidato
a señal de tibia 3, pero el salto abrupto y asimétrico requiere revisar la
conexión o el potenciómetro; no debe extrapolarse esa lectura ni usarse todavía
como realimentación de posición. La prueba regresó el servo a 100°.

## Preparación de pruebas locales para tibias 1 y 4

El operador confirmó que ambas articulaciones volvieron manualmente a su
posición central. Se añadieron al firmware las órdenes `e` (CH8, centro 100°)
y `g` (CH11, centro 70°), cada una con un recorrido aislado de ±2° y retorno
al centro; los demás canales no se alteran deliberadamente. El sketch compila
y el binario quedó actualizado en `movimiento_suspendido_11_servos/build`.
Arduino CLI, instalado como Snap, no pudo acceder al puerto por su confinamiento
AppArmor; no era un proceso serial que lo tuviera ocupado. La carga se completó
con `avrdude` del sistema y se verificaron los 13 092 bytes de flash.

## Pruebas cortas de tibias 1 y 4 — sesiones 49 y 50

Tras la confirmación del operador de que ambas patas estaban centradas, se
ejecutó primero CH8 entre 98° y 102° y después CH11 entre 68° y 72°, siempre
por separado y volviendo al centro. Sesión 49: 121 tramas; terminó en CH8=100°
(`HOLD_TIBIA1`). C8 dio aproximadamente 589 cuentas a 98° y 586 a 102°, una
variación pequeña que aún requiere repetición antes de confirmar el mapeo.
Sesión 50: 138 tramas; terminó en CH11=70° (`HOLD_TIBIA4`). C10 respondió de
forma más clara y decreciente al aumentar el ángulo: mediana 399 a 68°, 394 a
70° y 390 a 72°. Esto identifica localmente tibia 4 → C10 en ese intervalo.
No se observó choque en estos recorridos cortos. No se validan los límites
amplios de ninguna tibia con estas pruebas.

## Parada tras movimiento reportado de tibia 1 — sesión 51

Ante el reporte de movimiento persistente de tibia 1, se envió `x` para cortar
el PWM de los doce canales. El Uno reportó estado `OFF`; se almacenaron 60
tramas, incluidas 40 posteriores a la parada. En ellas la lectura de C8 quedó
estable entre 590 y 591 cuentas. Como el firmware no ofrece todavía un corte
individual por canal, se apagaron las salidas PWM; al momento de la orden solo
CH8 y CH11 seguían energizados tras las pruebas.

## Repetición observada de tibia 1 y parada — sesiones 52 y 53

Se volvió a probar CH8 en 98°, 100° y 102°, regresando a 100°; sesión 52,
108 tramas. La orden pasó a `HOLD_TIBIA1` con 100° y permaneció allí durante
31 muestras antes de la parada. C8 tuvo medianas de 591 cuentas en 98°, 591
en 102° y 591 durante la espera a 100°, sin una tendencia reproducible que
permita convertir ADC a posición. Hubo picos aislados (hasta 688) mientras
las lecturas normalmente estaban cerca de 590–596, por lo que la señal queda
clasificada como inestable/no confirmada. Inmediatamente después se envió `x`;
sesión 53 guardó 51 tramas y terminó en `OFF`, con C8 estable en 574 cuentas
durante 29 muestras. No se amplió el recorrido.

## Sostén fijo de tibia 1 y comparación con PWM apagado — sesiones 54 y 55

Se añadió y cargó la orden `h`, que aplica 100° solo a CH8 sin barrido. En la
sesión 54, las 80 muestras de `HOLD_TIBIA1` conservaron orden CH8=100°; C8
tuvo mediana 590, rango 568–687 y 10 lecturas fuera de 580–610. La mayor
parte de las muestras estuvo entre 590–601, con picos aislados. Al apagar
PWM con `x` (sesión 55), C8 quedó estable en 571–572 durante 30 muestras.
Esto descarta que el sketch siga cambiando la consigna y muestra que la
lectura/anomalía aparece principalmente con el servo energizado. Los datos
son compatibles con vibración/caza del servo o ruido/intermitencia en su
potenciómetro, cableado o alimentación; no permiten distinguir cuál. Para
separarlo hace falta observarlo sin carga o probar un servo/alimentación
conocidos. El robot quedó con PWM apagado.

## Comparación con coxa y fémur de pata 1 sostenidos — sesiones 56 y 57

Para comprobar si la pata se balanceaba por tener las articulaciones vecinas
sin PWM, se mandó solo la pata 1 a los centros declarados: CH0=150°,
CH4=110° y CH8=100°, sin barrido. Al reactivar CH0, C0 pasó de 93 a 189
cuentas, evidencia de que la coxa también cambió de posición al volver a
sostenerla; no se convierte ese cambio directamente a grados. Durante las 55
muestras de `HOLD_PATA1`, las órdenes permanecieron fijas. C8 tuvo mediana
584 y rango 570–653, aún con saltos. Después se envió `x`; sesión 57 confirma
estado `OFF`, y C8 quedó en 582–583 durante 30 tramas. La pata queda sin PWM.
La prueba apoya que el balanceo de la cadena con coxa/fémur sueltos contribuye
al movimiento observado; la señal inestable con tibia 1 energizada sigue
pendiente de separar entre servo/potenciómetro y alimentación/cableado.

## Comparación de tibia 1 por CH12 — sesiones 58 y 59

El operador trasladó la tibia 1 de PCA CH8 a CH12. Con firmware específico se
repitió la misma prueba con CH0=150° y CH4=110° sosteniendo la pata, y la tibia
en CH12 entre 98° y 102°, regresando a 100°. En el sostén `HOLD_PATA1_CH12`,
C8 (sensor, sin cambiar su conexión) quedó entre 591 y 608 cuentas, sin
lecturas fuera de 580–610 en 16 muestras. En el barrido hubo 3 valores
atípicos entre 42 muestras; el resto se mantuvo mayormente cerca de 587–608.
Como comparación, con CH8 y la pata sostenida (sesión 56), C8 varió 570–653,
con 21 de 55 lecturas fuera de 580–610. La mejoría al usar CH12 apunta al
trayecto de salida/conector de CH8 del PCA9685 como causa probable del
movimiento brusco; el cambio de conector también puede haber corregido un
contacto. No demuestra por sí solo un daño interno del PCA. Tras la captura se
envió `x`: sesión 59 terminó en `OFF`, y C8 quedó estable en 594–595 cuentas.

## Repetición de tibia 1 por CH12 — sesiones 60 y 61

Se repitió el recorrido con soporte de CH0=150° y CH4=110°, y tibia 1 por
CH12 entre 98° y 102°, regresando a 100°. La orden quedó constante en cada
meseta y terminó en `HOLD_PATA1_CH12`; sesión 60 guardó 118 tramas. En la
meseta de sostén, C8 estuvo entre 595 y 618 (mediana 596); en el barrido su
mediana fue 595 a los tres ángulos, con tres valores atípicos en 42 muestras.
El resultado es compatible con la ausencia del latigazo observada por el
operador al usar CH12, aunque C8 todavía no proporciona una relación angular
clara. Se envió `x` después de la prueba; sesión 61 confirmó `OFF` y C8 quedó
en 595–596 durante 29 muestras. Mantener tibia 1 en CH12 por ahora; el ensayo
apunta a CH8/conector como causa del movimiento brusco, pero para confirmar
si falla el canal PCA o el contacto físico se necesita probar otro servo
conocido en CH8.

## Corrección de ruta de tibia 1 y causa de tirón de activación

La revisión del firmware encontró que la tibia 1 ya se había trasladado
físicamente a CH12, pero las órdenes antiguas `e` y `h` y el sostén `j`
seguían dirigiéndose a CH8. Se cambió la configuración fuente para que la
tibia 1 use CH12 de forma consistente y CH8 quede fuera de uso. El firmware
compila, pero no se cargó al Arduino para evitar reiniciarlo durante la
posición actual.

También se identificó una fuente probable de los tirones en las pruebas más
recientes: el capturador abre el puerto USB, lo que reinicia el Uno; al iniciar,
el firmware apaga todas las salidas y luego la rutina vuelve a ordenar de golpe
CH0=150°, CH4=110° y tibia 1 CH12=100°. Por tanto, aunque el barrido de fémur
fuera de solo 2°, la secuencia completa no era de solo 2°. La sesión 64 terminó
con CH4 ordenado a 112° y sin orden de retorno; el ADC registrado no permite
confirmar el pulso eléctrico ni asignar un ángulo absoluto. Las siguientes
pruebas deberán evitar reiniciar la placa y no reubicar automáticamente las
articulaciones de soporte.

## Repetición corta de tibia 4 — sesiones 66 y 67

Se ejecutó la rutina aislada `g` en CH11: 70° → 72° → 70° → 68° → 70°.
La sesión 66 guardó 109 tramas. En las mesetas, MUX C10 promedió 315 cuentas
a 72° (12 muestras; rango 309–322) y 346,6 a 68° (13; 338–354); a 70° hubo
dos grupos de transición, con promedio combinado 344,5 (17; 325–367). C11 se
mantuvo cerca de 318–320 cuentas, sin respuesta apreciable. En la espera final
a 70°, C10 derivó de 370 hasta 539 cuentas, por lo que la señal todavía no es
estable ni permite una calibración fiable. No se amplió el recorrido. Luego se
envió `x`; sesión 67 terminó en `OFF` (20 tramas), con PWM de todos los canales
apagado. Falta confirmación visual del operador de que la articulación se movió
sin rozar durante esta repetición.

## Segunda repetición corta de tibia 4 — sesiones 68 y 69

Se repitió el recorrido CH11 de 70° → 72° → 70° → 68° → 70°. Sesión 68
guardó 110 tramas. Esta vez MUX C10 respondió de forma monotónica y estable:
promedio 397,6 cuentas a 68° (13 muestras; 397–404), 393,3 a 70° (17;
391–399) y 388,2 a 72° (12; 387–391). En la meseta final a 70°, C10 quedó
exactamente en 393 durante 30 muestras. C11 permaneció en 318–319. Se envió
`x` al terminar; sesión 69 terminó en `OFF` (20 tramas). Este resultado
confirma una relación local repetible entre CH11 y MUX C10 en el intervalo
68°–72°; no valida los topes amplios ni sustituye la confirmación visual de
que no hubo contacto mecánico.

## Barrido local ampliado de tibia 4 — sesiones 70 y 71

La orden `g` se amplió de forma conservadora a 66°–74° en pasos de 2° y
regreso a 70°, manteniendo solo CH11 activo. Sesión 70 guardó 122 tramas. MUX
C10 mostró promedios descendentes al aumentar la orden: 402,6 a 66° (10
muestras; rango 402–408), 399,0 a 68° (10; 397–409), 394,0 a 70° (20;
391–407), 389,6 a 72° (11; 388–404) y 383,6 a 74° (9; 383–387). En la
meseta final a 70° quedó entre 394 y 395 durante 46 muestras. C11 permaneció
en 318–319. La tendencia local es consistente en 66°–74°; no se probaron los
topes y sigue pendiente confirmar visualmente ausencia de roce. Se envió `x`;
sesión 71 terminó en `OFF` (19 tramas), con salidas apagadas.

## Barrido escalonado de tibia 4 entre 62° y 78° — sesiones 72 y 73

Tras el reporte de poco movimiento visual, se amplió el recorrido a ±8° desde
70°, en pasos lentos de 2°, y se regresó al centro. Sesión 72 guardó 160
tramas. MUX C10 respondió monotónicamente: 412,9 cuentas a 62° (7 muestras;
412–418), 409,8 a 64° (14; 408–417), 403,5 a 66° (14; 402–408), 399,9 a
68° (14; 398–409), 394,1 a 70° (14; 392–404), 388,1 a 72° (14; 386–395),
383,7 a 74° (14; 381–390), 378,8 a 76° (14; 376–391) y 375,3 a 78° (7;
373–389). Al sostener 70° al final, C10 quedó en 394 durante 33 muestras;
C11 permaneció en 318–319. Se envió `x`; sesión 73 terminó en `OFF` (19
tramas). La respuesta eléctrica es consistente en 62°–78°, pero la ausencia
de contacto mecánico sigue pendiente de observación visual del operador.

## Aproximación vigilada de tibia 4 a 150° y 15° — sesiones 74 y 75

Se cargó una rutina para avanzar en pasos de 2° usando C10 como guarda: en el
rango local probado, C10 disminuye al aumentar el ángulo. La rutina se detuvo
automáticamente en 104° y apagó CH11 porque el cambio de C10 en el último paso
fue inferior al umbral de 3 cuentas (102°: lecturas 311–317; 104°: 312–313,
promedio 312,5). Por seguridad no continuó hacia 150° ni intentó 15°. La
meseta posterior con CH11 apagado quedó cerca de 305–306 cuentas, compatible
con que la articulación se asentara al perder torque; los datos no distinguen
por sí solos un tope mecánico de holgura, atascamiento o respuesta anómala del
potenciómetro. Se envió `x` para asegurar todos los canales apagados; sesión
75 reportó `OFF` en las últimas 20 tramas. No repetir la aproximación hasta
inspeccionar tibia 4 y revisar manualmente el tramo alrededor de 102°–104°.

## Corrección de límites y recorrido vigilado de tibia 2 — sesión 76

El operador corrigió el límite trasero declarado de tibia 2 de 10° a 100°.
Con centro 80°, los objetivos solicitados quedan en 90° (10° antes de 100°)
y 25° (10° después de 15°). Se corrigió el registro de articulaciones y se
cargó una rutina dedicada que verifica C9 en cada tramo de 2°; si C9 no avanza
en el sentido medido, corta CH9. La rutina alcanzó 90° (C9=344), continuó hasta
25° (C9=511) y apagó todas las salidas al completar; no se ordenó regreso al
centro. La sesión 76 guardó 191 tramas y terminó en `OFF`. Esto confirma
respuesta continua del potenciómetro durante el recorrido, pero aún requiere
confirmación visual de que no hubo roce. Tibia 3 no se amplió: su señal
candidata C11 presenta un salto repetido alrededor de 105°.

## Prueba local de tibia 3 — sesiones 77 y 78

Se añadió y cargó una orden aislada `z` para mover únicamente tibia 3 (PCA
CH10): 100°→102°→100°→98°→100°. En la sesión 77, la lectura candidata C11
permaneció aproximadamente entre 313 y 322 cuentas durante el movimiento;
no se cruzó 104° y no se reprodujo el salto. La lectura C10 quedó alrededor
de 747 cuentas durante casi toda la captura. Esta prueba confirma estabilidad
local de C11 alrededor del centro, pero no determina qué ocurre por encima de
104° ni valida por sí sola el mapeo del sensor. La sesión 78 se usó para apagar
las salidas: últimas 20 tramas en `OFF`.
## Secuencia parcial tipo paso sin tibias — sesión 79

A petición del operador se implementó la orden `y`, de amplitud ±2° y dos
alternancias diagonales. Solo se ordenaron PCA CH1–CH7 (coxas 2–4 y fémures
1–4); CH0 (coxa 1), CH8–CH11 (tibias 1–4) y CH12 quedaron apagados. La
telemetría de la sesión 79 registró `PASO_PARCIAL_CENTRO`, las fases
`PASO_PARCIAL_DIAGONAL_A/B` y concluyó en `OFF`; se guardaron 101 tramas.
Esto es únicamente una demostración articular con el robot suspendido: no es
una caminata apoyada ni una política PPO, y la postura no se valida para
locomoción porque las tibias no levantan/apoyan las patas.

## Verificación de comunicación MUX/Arduino — sesión 87 (16 de octubre)

Se abrió `/dev/ttyACM0` sin enviar orden de movimiento; el Uno reinició y su
firmware reportó `OFF`. Llegaron 71 tramas `DATA` válidas por serial. Sin
embargo, las lecturas ADC de C0–C15 quedaron entre 0 y 1 cuentas (71 muestras
por canal), mientras las órdenes reportadas permanecieron en sus centros
lógicos. La comunicación USB/serial funciona, pero en esta captura no llegaron
señales analógicas útiles del multiplexor. No se puede concluir únicamente con
estos datos si falta alimentación de servos/MUX, tierra común, señal SIG, canal
habilitado o hay un problema de cableado. No se movieron servos.
