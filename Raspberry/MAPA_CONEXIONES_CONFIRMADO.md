# Mapa de conexiones confirmado

Confirmado por el operador el 29 de septiembre de 2026. El 7 de octubre, el
operador reconfirmó mediante imagen el número de servo y el canal PCA9685 de
cada articulación; la tabla ordenada está en `CONEXIONES.md`. También confirmó
que los nombres de los sensores AS5600 (Coxa 1, Fémur 1, etc.) corresponden a
esas articulaciones.
Actualización posterior por prueba física: un pulso enviado a CH8 de 1500 µs
durante 0,2 s movió únicamente coxa 2 hacia dentro, confirmado por el operador.
Por tanto, la tabla siguiente es la conexión declarada originalmente y
presenta una discrepancia: CH8 se observó en coxa 2, no en tibia 1.
En la prueba posterior, el operador confirmó CH1=coxa 3 (trasera derecha),
con 1500 µs durante 0,2 s. El operador confirmó movimiento hacia fuera
y libre, sin zumbido, tope ni atasco según la pregunta realizada.
El canal real de tibia 1 y CH2 quedan pendientes de identificación física.
No se presupone un intercambio de canales. El operador confirmó después
que el movimiento de coxa 2 fue libre, al preguntarle por zumbido, tope o atasco.
CH identifica el canal del PCA9685 (0x40). Cada ruta de sensor indica
dirección del TCA9548A y canal; los AS5600 usan dirección 0x36.

| Pata | Ubicación | Coxa: servo / sensor | Fémur: servo / sensor | Tibia: servo / sensor |
|---|---|---|---|---|
| 1 | Delantera derecha | CH0 / `0x71:3` | CH4 / `0x71:1` | CH8 / `0x71:0` |
| 2 | Delantera izquierda | CH1 / `0x71:6` | CH5 / `0x71:5` | CH9 / `0x71:4` |
| 3 | Trasera derecha | CH2 / `0x70:5` | CH6 / `0x70:4` | CH10 / `0x70:3` |
| 4 | Trasera izquierda | CH3 / `0x70:2` | CH7 / `0x70:1` | CH11 / `0x70:0` |

La tabla original coincide con los canales de `configuracion/servos.yaml` y las rutas
de `codigo/leer_as5600_tca.py`. Confirma conexiones, no calibración de pulsos,
ceros, sentidos o límites. `hardware_ready` permanece en false.

La confirmación del 7 de octubre respalda la correspondencia entre
articulación, servo, salida CH y etiqueta de sensor. La caracterización
verificada identifica Fémur 2 en `0x71:5` y Coxa 2 en `0x71:6`. Una lectura
aislada anterior de 226,14° atribuyó preliminarmente Fémur 2 a `0x71:6`; queda
como observación histórica superada por la caracterización verificada.

La atribución anterior CH4=tibia 1 fue una interpretación incorrecta del
asistente, corregida por el operador. CH4=fémur 1 y CH8=tibia 1.

## Conflicto pendiente en CH0 y CH1

El operador reportó que CH0, a 1500 µs durante 0,2 s, movió coxa 3 hacia
dentro. Previamente reportó CH1=coxa 3 hacia fuera. Ambas asociaciones
quedan pendientes de aclaración física: no se asigna definitivamente la
misma articulación a dos canales. Coxa 1 sigue sin identificar por esta
prueba. No se confirmó movimiento libre de CH0.
