# Intento de pruebas — 16 de octubre de 2026

- El Uno (`2341:0043`, serie 854363236313517140D0) estaba en `/dev/ttyACM0`. Las capturas a 115200 baudios (sesiones 80 y 81) guardaron 0 tramas: solo llegaban bytes `0x00`.
- `avrdude -n` confirmó que el ATmega328P respondía (firma 0x1e950f). La verificación contra `movimiento_suspendido_11_servos.ino.hex` falló: la flash contenía otro sketch.
- La lectura de la flash mostró un sketch sin fuente local, "Lectura de servos y feedback", que transmite a 9600 baudios. Al arrancar ordena PWM sin esperar comandos: PCA CH0 = 150°, CH4 = 40°, CH8 = 55°. Lectura observada: MUX 0/4/8, ADC entre 113 y 326. No acepta `x`. Cada apertura del puerto lo reiniciaba y repetía esas órdenes.
- Respaldo de esa flash: `CODIGO/respaldo_flash/uno_lectura_servos_feedback_20261016.bin` (SHA-256 `0449acfca2e013ad19647e7325cfeb95e9436676fff2801edfbea7b3209a646b`). Incluye restos del firmware anterior al final.
- Se grabó `movimiento_suspendido_11_servos.ino.hex`, que arranca con todas las salidas OFF. avrdude verificó 16470 bytes.
- A las 14:11:46 el kernel registró `usb 7-1: USB disconnect` y el Uno no volvió a enumerarse. No se ejecutó ninguna orden de movimiento (`q`, `z`, etc.) en esta sesión.
- Pendiente: revisar físicamente el cable USB y la alimentación del Uno, y si la desconexión coincidió con una caída de tensión de la fuente de servos.

## Diagnóstico I²C y prueba `q` — tarde del 16 de octubre

- `lecturasensores-i2c.ino` (del usuario) compiló y se cargó, pero todos los canales dieron "Encoder no detectado". Con un diagnóstico canal por canal, y tras desactivar el bit ALLCALL del PCA9685 (MODE1 0x11→0x10), el bus del Uno mostró solo `0x40`. `0x70` era la dirección All Call del PCA, no un TCA9548A. Ningún TCA ni AS5600 respondió durante 3 minutos de vigilancia (30 ciclos).
- Se volvió a grabar `movimiento_suspendido_11_servos`. Sesión 82, pasiva en OFF: C0–C11 = 85, 512, 135, 478, 483, 355, 321, 0, 569, 318, 366, 318.
- Sesión 83, orden `q`: rampa de coxas 2–3 hasta ±16° y sostén. Antes de que empezara el movimiento, el ADC ya había caído a 0–9 cuentas en todos los canales: los potenciómetros perdieron alimentación o referencia entre las sesiones 82 y 83. La rampa se ejecutó en lazo abierto y sus datos no sirven para calibración.
- Sesión 84, orden `x`: todas las salidas OFF; el ADC sigue en 0–2 cuentas, excepto C4 ≈ 84.
- No se ejecutó la prueba `z` de tibia 3. Pendiente: restaurar VCC/GND de los potenciómetros y del multiplexor analógico.

## Gateo en el aire, orden `b` — sesión 85

- Se añadió al firmware la orden `b`. Copia previa: `movimiento_suspendido_11_servos.ino.bak_20261016`. Es un gateo en el aire, en lazo abierto, con orden de patas FL → RR → FR → RL y 3 ciclos.
- Amplitudes: fémures ±6°; tibias 2 y 4 hasta 3°; tibias 1 y 3 hasta 2°, en sentido "delante". Coxas 2–4 sostenidas en el centro. Coxa 1 y CH8 sin PWM. Las articulaciones se energizan una por una al arrancar.
- Se guardaron 349 tramas y la sesión terminó en `OFF`. Órdenes registradas: fémures 104–116 (F1) y 94–106 (F2–F4); T1 98–100; T2 77–80; T3 98–100; T4 70–73.
- Sin realimentación válida: ADC caído desde la sesión 83. La respuesta física solo se puede evaluar por observación del operador. No validada para el suelo.

## Selectores MUX D7–D4 y caminata `b` ampliada — sesiones 86 y 88

- Según el diagrama del operador, los selectores van en S0=D7, S1=D6, S2=D5, S3=D4, y no en D8–D11. Se ajustó el firmware. Sesión 86 en OFF: los 16 canales en 0, compatible con potenciómetros sin 5 V.
- La orden `b` se amplió a fémures ±10° y tibias 8° hacia "delante", con 4 ciclos. Órdenes registradas en la sesión 88: F1 100–120, F2–F4 90–110, T1 92–100, T2 72–80, T3 92–100, T4 70–78; coxas 2–4 fijas. Terminó en `OFF`, con 398 tramas.
- ADC de la sesión 88: los 12 canales con la misma mediana (≈84) y el mismo rango (≈345 cuentas). Es una señal común a todos los canales, no una realimentación individual. No sirve para medir posición.
- El operador informó que la caminata de la sesión 88 "se movió bien". Sesión 89: fémures ±15° y tibias 14°. Órdenes registradas: F1 95–125, F2–F4 85–115, T1 86–100, T2 66–80, T3 86–100, T4 70–84. Terminó en `OFF`, con 401 tramas. La observación física queda pendiente.

## Selectores reales y aprendizaje de la caminata — sesiones 90 a 92

- `diagnostico_mux_pines` demostró que los selectores reales están en D8–D11; el diagrama D7–D4 no corresponde. Se restauró D8–D11 en el firmware.
- Sesión 91 (orden `b`, fémures ±15°, 0,8 s/fase): F2 → C5 y F4 → C6 con r = −0,998, −2,5 cuentas/° y 100 ms de retardo. El recorrido medido es de ~31° para 30° ordenados.
- C4 reproduce C5 (r = 0,993, desfase +132 cuentas): probable cruce de cables; F1 y F3 siguen sin canal propio.
- Tibias: C8–C11 sin respuesta al levantarlas 14° (se esperaban ~26 cuentas y se midieron 0–8).
- Sesión 92: fase de 0,5 s; F2 y F4 mantienen seguimiento completo. Modelo guardado en `modelo_aprendido_caminata_20261016.json`; script de análisis en `aprender_caminata.py`.
- Confirmado por el operador (sesión 95): PCA CH9 = tibia 2, sensor C9 (101 cuentas para 40°).
- Sesión 96: con PCA CH10 el operador no vio movimiento. C8 varió 363 cuentas (probable ruido/picos de C8).
- Sesiones 97 y 98: con PCA CH11 el operador no vio movimiento en ninguna de las dos pruebas; sin respuesta en los sensores.
- Sesión 99: con PCA CH12 (donde se trasladó la tibia 1) el operador no vio movimiento; C8 solo 13 cuentas.
- Confirmado por el operador (sesión 100): PCA CH13 = tibia 4 (se movió hacia atrás), sensor C10 (216 cuentas para el recorrido 50–90°).
- Sesión 101: con PCA CH14 el operador vio un movimiento brusco. C8 cae de ~550 a ~70, sube en rampa hasta ~370 y vuelve a ~600, en el mismo punto de cada una de las 3 oscilaciones. Compatible con un tramo dañado en el potenciómetro del servo (probable tibia 1, pendiente de confirmar). CH14 bloqueado hasta revisión.
- Sesión 102: PCA CH15 sin respuesta en sensores.
- Tras la reconexión de tibias (sesiones 115–120): el operador confirmó PCA CH8 = tibia 1 (sesión 120, prueba 40–120°). C8 solo mostró saltos al inicio y luego se quedó fijo en ~475; su señal no sigue el movimiento de forma fiable. CH1 (coxa 2) movido 20–60° con C1 respondiendo ~100 cuentas (sesión 117); con CH0 (coxa 1, 130–170°), C0 quedó al aire en ~745 (sesión 118).
- Sesión 121: el operador confirmó PCA CH9 = tibia 3 (tras la reconexión); C11 varió ~110 cuentas, coherente con su sensor.
- Sesión 122: PCA CH10 sin conectar (el operador confirma que no hay nada en ese canal).
- Sesiones 123 y 124: el operador confirmó PCA CH11 = tibia 4; sensor C10 con 3 oscilaciones suaves (341–444, ~2,5 cuentas/°).
- Sesión 125: el operador confirmó PCA CH12 = tibia 2; sensor C9 con ~100 cuentas para 40°.

### Mapa de tibias tras la reconexión (16 de octubre, confirmado visualmente)

| Tibia | Pata | PCA | Sensor MUX |
|---|---|---:|---|
| 1 | Delantera derecha | CH8 | C8 (poco fiable) |
| 2 | Delantera izquierda | CH12 | C9 |
| 3 | Trasera derecha | CH9 | C11 |
| 4 | Trasera izquierda | CH11 | C10 |

CH10, CH13, CH14 y CH15 quedan sin servo. El firmware se actualizó con este mapa.
- Sesión 126: caminata `b` con las tibias en sus canales reales (4 ciclos, 0,5 s/fase), terminada en OFF. Seguimiento: F2 r=−0,91 (30,4° de 30°), F4 r=−0,59 (≈21° de 30°; en la sesión 92 era −1,00), T2 r=−0,57 (≈14° de 14°), T3 r=+0,10, T4 r=+0,11, T1 sin señal fiable. Peor seguimiento que en las pruebas suspendidas: pendiente saber si el robot estaba apoyado o si hubo caída de tensión con 11 servos activos.
- Puntos de equilibrio de las coxas indicados por el operador: C1=150°, C2=40°, C3=55°, C4=147°, siempre fijas durante la caminata. Sesión 127: `b` con las 4 coxas fijas (incluida la coxa 1 en CH0). F2 r=−0,91 (28,5° de 30°); F4 r=−0,27 (~8° de 30°); T2 r=−0,58 (13° de 14°); T3: C11 con saltos (el recorrido aparente de 128° es ruido o salto del sensor); T4 sin seguimiento.
- Coxa 4: el operador cambió su punto de equilibrio de 147° a 150°. Coxas 2 y 3 se mantienen en 40° y 55°.
- Sesión 128: `b` con coxas 150/40/55/150, terminada en OFF. F2 r=−0,88 (27° de 30°), F4 r=−0,70 (23° de 30°; mejoró respecto a la sesión 127), T2 r=−0,81 (13,4° de 14°), T3 con saltos en C11 (lectura no válida), T4 sin seguimiento (1,5° de 14°).
- Sesión 129: el operador confirma la coxa 2 en 45° como punto de equilibrio. Equilibrio vigente de las coxas: C1=150°, C2=45°, C3=55°, C4=150°. Nueva orden `#`: sostener solo las coxas en equilibrio.
- Sesión 130: `b` con equilibrio de coxas 150/45/55/150, terminada en OFF. F2 r=−0,65 (23° de 30°), F4 r=−0,96 (29° de 30°), T2 r=−0,68 (12,5° de 14°), T4 sin seguimiento (2° de 14°), aunque sola en CH11 se movió bien (sesión 124, 50–90°).
- Sesión 131: `b` con 10 ciclos y tibia 4 invertida (orden 56–70°); terminada en OFF, 377 tramas de caminata. F2 24° de 30°, F4 25° de 30°, T2 15° de 14°; T4 sigue sin respuesta en C10 (1,3° de 14°).
- Caminata `b` modificada: al terminar deja las 4 coxas sostenidas en equilibrio (la coxa 2 caía al apagar todo); solo apaga fémures y tibias.
- Sesiones 133 y 134: se probó corrección realimentada de las coxas 2–4 durante \`b\` (±6° máximo; la segunda versión con filtro y una corrección cada 200 ms). No mejoró: variación lenta filtrada de coxa 2 ≈33° (antes 35°), coxa 3 ≈28° (antes 22°), coxa 4 ≈8° (igual). La perturbación (~30°) supera la autoridad de ±6°; además, en C1 aparecen caídas breves (533→413) una vez por ciclo. Pendiente confirmar visualmente si la coxa 2 se mueve realmente ~30° o si es interferencia en la lectura.
- Sesión 135: `b` con corrección filtrada. Coxa 2 estable: mediana de C1 entre 465 y 468 en los 10 tramos de la caminata (≈±1°), orden corregida entre 42 y 49°. Las caídas breves de C1 (<440) aparecen en todas las fases por igual, no al dar el paso la pata FL: son picos de lectura, no movimiento real. Terminó en HOLD_EQUILIBRIO.
- El operador confirma que la coxa 2 mejoró muchísimo con la corrección filtrada. Versión estable guardada: `movimiento_suspendido_11_servos.ino.estable_caminata_20261016` y `caminata_estable_20261016.hex`.
- Tibia 1 (CH8) excluida de `b` por tirones (tramo dañado en su potenciómetro interno); queda sin PWM. Recomendación: reemplazar ese MG996R.
