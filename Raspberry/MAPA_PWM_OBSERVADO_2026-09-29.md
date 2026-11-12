# Identificación física de canales — 29 de septiembre de 2026

**Corrección del operador:** el mensaje sobre tibia 1 era una petición de
movimiento, no una observación sobre CH4. La identificación descrita debajo
fue una interpretación incorrecta y queda invalidada. Se mantiene el mapa
del proyecto: CH4=fémur 1, CH8=tibia 1. Las lecturas previas corresponden al
sensor previsto de fémur 1; no se invalida su asociación por ese mensaje.
La prueba individual permite seleccionar CH4 o CH8 con su sensor respectivo.

## Nota anterior invalidada, conservada por trazabilidad

El operador confirmó que los pulsos enviados a CH4 movieron únicamente la
tibia de la pata 1 (delantera derecha), hacia dentro. Se aplicaron 1500 µs
durante 0,2 s por prueba, con apagado de PWM al terminar.

Por tanto, CH4 corresponde a `front_right_tibia_joint` en esta identificación
física. Contradice el mapa provisional de `configuracion/servos.yaml`, donde
CH4 figura como fémur 1 y CH8 como tibia 1. CH8 queda pendiente de identificación;
no se presupone un intercambio entre ambos canales. El mapa completo todavía
no está validado y `hardware_ready` debe permanecer en false.

Las pruebas iniciales registraron el AS5600 del fémur 1 (0x71/canal 1).
Sus ángulos no corresponden a la articulación observada y no deben utilizarse
para calibrar CH4. Se conserva el registro original en
`datos/pulsos_observados.jsonl`. La última lectura posterior falló con error I2C.

La prueba `codigo/pulso_individual_observado.py` queda vinculada a tibia 1 y su
AS5600 en 0x71/canal 0 para próximas capturas. Sigue pendiente confirmar
ausencia de tope, zumbido o atasco, tipo de servo, límites PWM y cero del modelo.
