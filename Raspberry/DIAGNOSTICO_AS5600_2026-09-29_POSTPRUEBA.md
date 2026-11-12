# Diagnóstico pasivo AS5600 y prueba mínima de tibia 1 — 29 de septiembre de 2026

## Alcance

Se conectó a `cuadrupedo-pi` mediante SSH. Se ejecutó una sola prueba con PWM
en tibia 1 (`PCA CH8`, AS5600 `0x71`/canal 0): `1500 → 1505 → 1500 µs`. Luego
se hicieron 20 barridos pasivos de los doce sensores. El sondeo I²C no generó
PWM. La alimentación externa V+ de los servos no se puede verificar por SSH.

## Prueba de movimiento

| Fase | Ángulo AS5600 |
|---|---:|
| Antes de habilitar, posición leída | 144,756° |
| Referencia inicial 1500 µs | 144,756° (sin cambio visible) |
| Paso 1505 µs | 150,645° (+5,889° desde 1500 µs) |
| Retorno 1500 µs | 161,455° (+16,699° desde el punto de 1500 µs) |
| Lectura posterior, PWM deshabilitado | 170,947° |

El AS5600 mantuvo `status=0x67` (MD=1, ML=0, MH=0), pero la posición siguió
cambiando después del retorno y con PWM deshabilitado. El retorno no es
repetible; la prueba se abortó sin probar otra articulación ni ejecutar marcha.
No inferir una conversión PWM/grados ni usar 1500 µs como centro calibrado.

## Barrido pasivo de 20 ciclos

Se tomaron veinte lecturas por ruta, aproximadamente cada 0,1 s. El rango es la
dispersión circular relativa a la primera muestra; `magnético_OK` exige MD=1,
ML=0 y MH=0 en todas las muestras.

| Articulación | Inicio | Final | Rango | Magnético OK | Estados observados |
|---|---:|---:|---:|---:|---|
| Tibia 4 | 0,791° | 0,791° | 0,000° | 20/20 | `0x67` |
| Fémur 4 | 321,855° | 321,855° | 0,000° | 20/20 | `0x67` |
| Coxa 4 | 148,359° | 148,359° | 0,000° | 0/20 | `0x33` |
| Tibia 3 | 341,279° | 341,279° | 26,191° | 0/20 | `0x33` |
| Fémur 3 | 192,041° | 192,041° | 0,000° | 0/20 | `0x37` |
| Coxa 3 | 151,523° | 145,986° | 39,902° | 0/20 | `0x13` |
| Tibia 1 | 170,947° | 170,947° | 0,000° | 20/20 | `0x67` |
| Fémur 1 | 195,293° | 195,293° | 0,088° | 0/20 | `0x13` |
| Coxa 1 | 333,721° | 307,441° | 59,678° | 0/20 | `0x13` |
| Tibia 2 | 12,832° | 12,920° | 0,088° | 20/20 | `0x27` |
| Fémur 2 | 267,451° | 267,451° | 0,000° | 20/20 | `0x27` |
| Coxa 2 | 152,930° | 152,930° | 27,070° | 20/20 | `0x27` |

Aunque seis rutas detectaron un imán válido en las veinte muestras, coxa 2
varió 27,070° y no proporciona una posición estable. Cinco señales fueron
estables dentro de 2° y magnéticamente válidas. Las otras siete no son aptas
para realimentación articular. El ángulo absoluto del imán tampoco equivale al
ángulo articular del modelo.

## Estado de salidas y cambio de software

Tras la prueba se dejó OE BCM17 en HIGH y se verificaron los dieciséis canales
individualmente en `FULL_OFF`. La lectura de `ALL_LED_OFF_H` no confirmó el bit
global; no se confía en ese bit como única parada. La salida física se mantuvo
bloqueada por OE y por los bits `FULL_OFF` por canal.

Se encontró que la implementación local de `PCA9685Seguro.close()` liberaba OE
y que `all_off()` no marcaba individualmente cada canal. La corrección local en
`Raspberry/codigo/pca9685_seguro.py` ahora fuerza primero OE alto, fija
`FULL_OFF` en los 16 canales y deja OE configurado en alto al cerrar. También
añade los métodos `prepare_channel_off` y `set_channel_off`, requeridos por los
scripts de prueba. Cuatro pruebas unitarias y `py_compile` pasaron. Después se
instaló en la Pi con respaldo del archivo anterior
`pca9685_seguro.py.codex-backup-20260929`. El SHA-256 instalado es
`a92e47aa75139f42b04cead746112818cddb6e1cdc35abdb22ef747eca8321e1`; en la Pi
pasó `compile()` y se verificó OE alto, 16/16 canales en `FULL_OFF` y servicio
de hardware inactivo.

## Decisión

No ejecutar más PWM ni entrenamiento físico hasta comprobar mecánicamente la
articulación/cople de tibia 1 y resolver la variación de sensores. Los extremos AS5600 documentados el 28
de septiembre son muestras de posición del imán, no límites PWM; no bastan
para habilitar una marcha.

## Revisión pasiva adicional — 29 de septiembre de 2026

El operador indicó que no había movido el robot. Se repitieron quince barridos
sin comandos PWM; el patrón se mantuvo. Tibia 1 permaneció en 170,947° (`0x67`),
mientras rutas débiles o sin detección variaron ampliamente: tibia 3 26,191°
(`0x33`), coxa 3 28,389° (`0x13`), coxa 1 58,359° (`0x13`) y coxa 2 27,070°
pese a `0x27`. Esto no demuestra movimiento físico del operador ni identifica
una causa única. Se deben revisar alineación y fijación del imán/sensor,
cableado y alimentación I²C, además de holgura o caída mecánica sin par.

Se confirmó por SSH por qué el robot no se mueve: OE BCM17=HIGH, los 16 canales
PCA están individualmente en `FULL_OFF`, `hardware_ready: false`, cero servos
marcados calibrados y servicio `nova-hardware.service` inactivo. El driver
corregido sí está instalado (SHA-256
`a92e47aa75139f42b04cead746112818cddb6e1cdc35abdb22ef747eca8321e1`). Ningún
PWM está siendo aceptado o ejecutado; es un bloqueo deliberado de seguridad.

## Confirmación de estabilidad — 60 barridos pasivos

Se completaron 60 barridos adicionales sin comandos al PCA9685. Las doce rutas
I²C respondieron 60/60 veces; por tanto el bus y el mapa de multiplexores están
operativos. Solo seis sensores mantuvieron estado de imán válido, y coxa 2
presentó 34,805° de dispersión aun con estado `0x27`. Cinco señales fueron
válidas y estables dentro de 2°; las demás no sirven como realimentación
articular.

| Articulación | Lecturas | Magnético OK | Rango circular | Estado |
|---|---:|---:|---:|---|
| Tibia 4 | 60/60 | 60/60 | 0,000° | `0x67` |
| Fémur 4 | 60/60 | 60/60 | 0,088° | `0x67` |
| Coxa 4 | 60/60 | 0/60 | 0,088° | `0x33` débil |
| Tibia 3 | 60/60 | 0/60 | 26,191° | `0x33` débil |
| Fémur 3 | 60/60 | 0/60 | 0,000° | `0x37` débil |
| Coxa 3 | 60/60 | 0/60 | 39,639° | `0x13` sin detección |
| Tibia 1 | 60/60 | 60/60 | 0,000° | `0x67` |
| Fémur 1 | 60/60 | 0/60 | 0,264° | `0x13` sin detección |
| Coxa 1 | 60/60 | 0/60 | 72,861° | `0x13` sin detección |
| Tibia 2 | 60/60 | 60/60 | 0,088° | `0x27` |
| Fémur 2 | 60/60 | 60/60 | 0,000° | `0x27` |
| Coxa 2 | 60/60 | 60/60 | 34,805° | `0x27` |

La causa directa de ausencia de movimiento sigue siendo la inhibición deliberada:
OE alto, canales `FULL_OFF`, hardware no listo y servicio inactivo. El defecto
de adquisición es separado: la ruta I²C responde, pero señal magnética/posición
no es confiable en siete sensores. Falta inspeccionar físicamente posición y
fijación de cada imán, separación axial, orientación/alineación y alimentación
del módulo; el software no puede reparar ese ajuste mecánico.

## Lectura pasiva mientras el operador enviaba pulsos — 29 de septiembre de 2026

Se leyó AS5600 `0x71`/canal 1 (fémur 1) durante 60 muestras, a intervalos de
aprox. 0,15 s, mientras el operador indicó que enviaba pulsos por su cuenta.
No se emitió PWM desde esta sesión. El ángulo RAW informado osciló entre
167,607° y 167,783° (0,176° de dispersión); las 60 muestras tuvieron estado
`0x13` (`MD=0`, `ML=1`, `MH=0`: campo magnético débil). Por tanto, no se puede
confirmar con este sensor que el fémur se haya movido ni asociar los pulsos con
ángulos. Tampoco se recibieron aquí los valores/tiempos de esos pulsos. La
captura es observación inconclusa, no calibración ni prueba de límites.
