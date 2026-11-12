# Protocolo de diagnóstico pasivo AS5600

## Propósito y límite

Este protocolo separa una señal I2C que responde de una señal apta para
proseguir a calibración. Solo selecciona canales candidatos para el siguiente
paso; no calcula ángulos articulares, no cambia `hardware_ready` y no autoriza
PWM, postura ni marcha.

El lector `codigo/leer_as5600_tca.py` selecciona un canal TCA y lee los
registros `STATUS` y `RAW_ANGLE` de cada AS5600. No importa el controlador
PCA9685 ni modifica OE. El analizador
`codigo/analizar_estabilidad_as5600.py` trabaja sobre el JSONL ya producido y
tampoco abre el bus I2C.

## Antes de medir

1. Mantener la alimentación V+ de servos desconectada.
2. Confirmar OE BCM17 alto, los 16 canales del PCA9685 en `FULL_OFF`,
   `hardware_ready: false` y `nova-hardware.service` inactivo.
3. No mover manualmente el robot durante la ventana de 60 muestras.
4. Corregir físicamente, una articulación a la vez, solo la fijación, alineación
   y separación del imán respecto al AS5600 que vaya a revisarse. No inferir
   la causa desde software ni forzar topes.

## Adquisición y análisis

Con la Raspberry disponible y desde la raíz del proyecto:

```bash
mkdir -p Raspberry/evidencias/as5600
timeout 15 python3 Raspberry/codigo/leer_as5600_tca.py --period 0.10 \
  --jsonl Raspberry/evidencias/as5600/pasivo_YYYYMMDD_HHMM.jsonl
python3 Raspberry/codigo/analizar_estabilidad_as5600.py \
  Raspberry/evidencias/as5600/pasivo_YYYYMMDD_HHMM.jsonl \
  --output Raspberry/evidencias/as5600/informe_YYYYMMDD_HHMM.json
```

El `timeout` deja aproximadamente 150 barridos, por encima del mínimo de 60.
Puede detenerse con `Ctrl-C`; el lector deselecciona ambos TCA al cerrar. No
ejecutar scripts `prueba_*`, `thonny_marcha_nova.py` ni ningún script que arme
el PCA9685 durante esta campaña.

## Criterio de la ventana pasiva

Una articulación queda como **candidata solo para calibración** cuando tiene al
menos 60 lecturas, cero errores I2C, `MD=1`, `ML=0`, `MH=0` en todas, y una
dispersión circular no mayor de 2°. El cálculo circular evita clasificar como
inestable una señal que cruce 0°/360°.

Incluso una candidata requiere, en una sesión posterior y con autorización
explícita, determinar cero, sentido, recorrido útil, margen a topes, holgura y
retorno repetible. Una señal que no cumpla estos criterios se mantiene fuera de
realimentación y control.

## Estado de partida

El diagnóstico pasivo del 29 de septiembre mostró que las 12 rutas TCA/I2C
respondían, pero solo cinco señales eran simultáneamente válidas y estables.
La tibia 1 no tuvo retorno repetible en la única prueba de 5 µs; permanece
bloqueada aunque sus lecturas pasivas fueran estables. La fuente de estos
resultados es `DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.
