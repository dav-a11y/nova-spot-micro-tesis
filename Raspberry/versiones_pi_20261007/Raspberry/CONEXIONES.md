# Conexiones Raspberry Pi 4, PCA9685 y MG996R

## Raspberry Pi 4 hacia PCA9685

| Raspberry (pin físico) | Señal BCM | PCA9685 | Función |
|---:|---|---|---|
| 1 | 3V3 | VCC | Alimentación lógica de 3,3 V |
| 3 | GPIO2 / SDA1 | SDA | Datos I2C |
| 5 | GPIO3 / SCL1 | SCL | Reloj I2C |
| 6 | GND | GND | Tierra lógica común |
| 11 | GPIO17 | OE | HIGH apaga; LOW habilita PWM |

Se recomienda una resistencia pull-up externa de 10 kΩ entre `OE` y 3,3 V para
que las salidas permanezcan deshabilitadas durante el arranque.

## Alimentación de servos

- Fuente externa regulada de 5--6 V: positivo a `V+` del PCA9685.
- Negativo de la fuente: `GND` del PCA9685 y tierra común con Raspberry.
- No conectar `V+` al pin de 5 V de la Raspberry.
- No alimentar los servos desde `VCC`; `VCC` es solo lógica.
- Añadir fusible, parada física y cableado dimensionado después de medir
  corriente real de un MG996R asegurado.

## Conector de cada servo

- Marrón o negro: GND.
- Rojo: V+ externo de 5--6 V.
- Naranja, amarillo o blanco: señal PWM del canal.

Confirma los colores del fabricante antes de energizar.

## Mapa confirmado por imagen del operador — 7 de octubre de 2026

La imagen compartida por el operador confirma el número de servo y su salida
del **PCA9685**. Los nombres de los AS5600 (Coxa 1, Fémur 1, etc.) corresponden
a esas mismas articulaciones. CH son canales del PCA9685, no pines GPIO. Las
rutas I2C de los sensores están registradas en
[`MAPA_CONEXIONES_CONFIRMADO.md`](MAPA_CONEXIONES_CONFIRMADO.md) y coinciden con
las etiquetas de la caracterización confirmada por el operador.

| Pata | Ubicación | Segmento | N.º servo | Canal PCA9685 |
|---|---|---|---:|---:|
| 1 | Delantera derecha | Coxa 1 | 1 | CH0 |
| 1 | Delantera derecha | Fémur 1 | 5 | CH4 |
| 1 | Delantera derecha | Tibia 1 | 9 | CH8 |
| 2 | Delantera izquierda | Coxa 2 | 2 | CH1 |
| 2 | Delantera izquierda | Fémur 2 | 6 | CH5 |
| 2 | Delantera izquierda | Tibia 2 | 10 | CH9 |
| 3 | Trasera derecha | Coxa 3 | 3 | CH2 |
| 3 | Trasera derecha | Fémur 3 | 7 | CH6 |
| 3 | Trasera derecha | Tibia 3 | 11 | CH10 |
| 4 | Trasera izquierda | Coxa 4 | 4 | CH3 |
| 4 | Trasera izquierda | Fémur 4 | 8 | CH7 |
| 4 | Trasera izquierda | Tibia 4 | 12 | CH11 |

Los canales CH12--CH15 quedan libres. Este mapa documenta el cableado nominal;
las pruebas de movimiento anteriores que contradigan una asociación quedan
registradas hasta verificarlas físicamente. No equivale a calibración: los
límites PWM y mecánicos por servo siguen pendientes.
