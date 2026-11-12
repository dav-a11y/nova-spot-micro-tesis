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

## Verificación de comunicación — 19 de octubre de 2026
- El Uno respondía, pero tenía una versión antigua del firmware de caminata, sin el modo `@` ni los topes nuevos. Se respaldó en `CODIGO/respaldo_flash/uno_version_antigua_20261019.bin` y se grabó la versión del 16 de octubre.
- Sesión 137, pasiva en OFF: comunicación correcta (83 tramas), pero C0–C11 leían todos ~127. `diagnostico_mux_pines` mostró que los selectores del MUX ahora están cableados en D4–D7, no en D8–D11.
- El firmware se ajustó a S0=D7, S1=D6, S2=D5, S3=D4 (orden del diagrama del operador). Sesión 138: orden `6` (CH1, coxa 2, 20–60°); ningún canal siguió el movimiento (variación ≤ 10 cuentas).
- 12:45:10: el Uno se desconectó del USB (`usb 1-1: USB disconnect`) y no volvió a aparecer. Queda grabado el firmware con selectores D7–D4.
- 13:05: el Uno volvió a aparecer por USB. Bus I²C (A4/A5): las líneas están en reposo alto, pero el PCA9685 no responde (MODE1 = 0xFF, ningún dispositivo en el bus), así que los servos no reciben órdenes del Uno.
- Selectores del MUX: S0=D4 (bit de menor peso), S1=D5, S2=D6, S3=D7. Sesión 139 (pasiva, OFF): lecturas distintas por canal y estables (rango ≤ 2 cuentas en C0–C12): C3=482, C4=479, C5=351, C6=306 y C7=25 (vacío), coherentes con las referencias del 16 de octubre. Mapeo de selectores confirmado. Firmware grabado con ese orden.
- Diagnóstico del PCA9685 (19 de octubre): A4 y A5 tienen pull-up externo, sin cruce ni cortocircuito, pero el bus por hardware no ve nada. Un escaneo I²C por software con las líneas al revés (SDA=A5, SCL=A4) encuentra 0x40 y 0x70: **los cables SDA y SCL del PCA9685 están intercambiados**. Corrección: intercambiar los dos cables en el Uno. Se volvió a grabar el firmware de caminata (selectores D4–D7, D4 = bit de menor peso).
- Causa del fallo de comunicación (19 de octubre): la línea SDA (A4) estaba flotando, sin conexión. Volvía a 1 solo con el pull-up interno y no tiraba a tierra; SCL sí tenía pull-up. El operador reconectó el cable: SDA vuelve a 1 en 8–12 µs y el PCA9685 responde en 0x40. Los TCA 0x70/0x71 no están en el bus del Uno.
- Sesión 141: orden `6` (coxa 2, CH1, 20–60°, 3 oscilaciones). C1 siguió las 3 oscilaciones (451–543 cuentas, ≈92 cuentas para 40°); terminó en OFF. Esto confirma servos, PCA9685, MUX y selectores (S0=D4…S3=D7).
- Mapa nuevo indicado por el operador (19 de octubre): tibia 1 = CH8 (servo reparado, vuelve a usarse), tibia 2 = CH9, tibia 3 = CH10, tibia 4 = CH11; CH12 vacío. Equilibrio de las coxas ajustado mecánicamente en 150/45/55/150. Firmware actualizado (servos, topes por canal; reposo, `@` y `b` incluyen la tibia 1). Nueva orden `&` = reposo sostenido de las 12 articulaciones. Sesión 144: HOLD_REPOSO con las 12 articulaciones en su base. `robot_nova.py` actualizado con el mismo mapa (pendiente de copiar a la Pi). Pendiente: reidentificar qué canal del MUX corresponde a cada sensor tras el recableado (orden `%`).
- Sesiones 145 y 146 (19 de octubre): al abrir el puerto, el Uno no se reinició y seguía en HOLD_REPOSO; tras un rato sostenido, los sensores leían 10–30 cuentas (salvo C8), compatible con una caída de la alimentación de los potenciómetros bajo carga. Se envió `x`: todas las salidas en OFF y lecturas normales.
- Posición libre (servos sin PWM) frente a la sostenida en reposo (sesión 144), con ≈2,45 cuentas/°: coxa 1 (C0) +14°, coxa 2 (C1) −11°, coxa 3 (C3) −9°, coxa 4 (C2) −19°, fémur 2 (C5) +6,5°, fémur 4 (C6) −20°, C9 −14,5°, C4 +5°, C10–C12 ≤ 4°. C7 vacío, C8 fijo en 743 (sin señal).
- Equilibrio nuevo de las coxas (19 de octubre), medido con los sensores tras colocarlas a mano: C1 = 159°, C2 = 45°, C3 = 54°, C4 = 112° (tope mínimo de CH3 bajado a 105°). Aplicado en el firmware, en `ejecutar_politica_robot.py` y en `robot_nova.py`.
- Caminata base de 10 ciclos (fémur 15°, tibia 10°, 30 ms, sin PPO; `registros_robot/caminata_equilibrio_nuevo_20261019.csv`): 913 pasos. Coxas estables (desviación media 1,0–1,3°, p95 ≤ 3,7°). Seguimiento: F2 → C5 (r = −0,99), F4 → C6 (r = −0,98), T2 (ahora CH9) → C9 (r = −0,89). El mapa de sensores que usa la política PPO vuelve a coincidir.
- Coxa 4 (19 de octubre): con 112° quedaba caída hacia abajo y con 150° pasó su límite hacia el otro lado (el operador desconectó el servo). Se apagó todo con `x` (sesión 149) y, a petición del operador, se grabó en el Uno un sketch vacío (`CODIGO/sketch_vacio`): no controla nada y el PCA9685 queda con todas las salidas en OFF. El firmware de caminata quedó compilado, sin grabar, con la coxa 4 en 131° (punto medio) y su tope máximo en 145°, pendiente de ajustarla a ojo.
- Coxa 4 (19 de octubre): el operador confirma como equilibrio la posición actual (C2 = 375, ≈74°, extrapolada desde 112° → 301 y 150° → 228). Firmware, ejecutor del PC y robot_nova.py con coxa 4 = 74° y topes provisionales 60–105° hasta medir sus límites nuevos. Equilibrio de las coxas: 159/45/54/74.
- Caminata base de 10 ciclos con coxas 159/45/54/74 (19 de octubre, 14:04; registros_robot/caminata_coxa4_74_20261019.csv): coxas estables (desviación media 0,7–1,6°, p95 ≤ 2,9°). F4 C6 r = −0,99 y T2 C9 r = −0,87. F2 (C5) no siguió la orden en el primer 40 % (C5 359–451, r ≈ 0) y después siguió perfecto (295–371, r = −1,00): posible traba mecánica o tirón al inicio.
- Tibia 4 en CH14 (corrección del operador, 19 de octubre); CH11 y CH12 vacíos. Firmware y robot_nova.py actualizados (tope de CH14 15–105°). Caminata de 10 ciclos (14:07, registros_robot/caminata_tibia4_ch14_20261019.csv): F2 C5 |r| = 1,00, F4 C6 |r| = 1,00, T2 C9 |r| = 0,98; coxas con desviación media 0,40–0,56°. El sensor de T4 no está entre los canales que registra el modo @.
- Caminata con PPO v4 semilla 37 (19 de octubre, 14:10; registros_robot/caminata_ppo_20261019.csv) frente a la base (caminata_completa_r2): corrección realizada F2 100 % (3,2°), F4 108 % (1,6°), T2 77 % (0,8°). Coxas más estables con PPO: desviación media 0,46/0,45/0,49° frente a 1,77/0,99/0,61° en la base (p95 ≤ 1,2°).
- Repeticiones base/PPO alternadas (19 de octubre, 14:13–14:16, rep_*_r3/r4). Desviación media de las coxas 2/3/4 en las 3 rondas: base 1,15/0,69/0,64°, PPO 0,67/0,59/0,56°. Con PPO es menor en promedio, pero la diferencia varía entre rondas (en la ronda 2 la PPO fue algo peor en coxa 2 y 3). Sensores leídos y confirmados: C1 = coxa 2, C3 = coxa 3, C2 = coxa 4, C5 = fémur 2, C6 = fémur 4, C9 = tibia 2. Sin confirmar tras el recableado: coxa 1, fémur 1, fémur 3 y tibias 1, 3 y 4.
- Identificación una por una (19 de octubre, orden '!'+índice, ±10°): coxa 1 → C0 (r = −1,00, 53 cuentas), tibia 3 → C11 (r = −1,00, 52 cuentas; C12–C14 la copian con amplitud decreciente porque son entradas al aire que arrastran la carga de C11), tibia 4 → C10 (r = −1,00, 54 cuentas). Sin sensor que responda: tibia 1 (como dijo el operador), fémur 1 y fémur 3 (ningún canal varía más de 9 cuentas). Pendiente: revisar el cableado de los potenciómetros de los fémures 1 y 3 (probablemente C4 y C7: C4 queda fijo en ~450 y C7 en ~0–25).
- TCA9548A en el bus del Uno (19 de octubre): tras corregir el cableado, el PCA9685 responde en 0x40 y los TCA en 0x70 y 0x71. AS5600 presentes en 11 rutas (falta 0x70/2, coxa 4). Imán válido (MD=1, ML=0, MH=0) en 5: 0x70/0 tibia 4 (157,0°), 0x70/1 fémur 4 (356,0°), 0x70/4 fémur 3 (332,1°), 0x70/5 coxa 3 (156,1°), 0x71/4 tibia 2 (10,6°). Imán débil o sin detectar en 6: 0x70/3 tibia 3, 0x71/0 tibia 1, 0x71/1 fémur 1, 0x71/3 coxa 1, 0x71/5 fémur 2, 0x71/6 coxa 2 (según el mapa del 28 de septiembre).
- Mapa servo → AS5600 verificado moviendo cada articulación ±10° (19 de octubre, CODIGO/mapa_as5600). Coincide con el mapa del operador: 0x70/0 tibia 1 (−17,8°), 0x70/1 fémur 1 (−30,1°), 0x70/3 tibia 2 (−12,8°), 0x70/4 fémur 2 (+9,8°), 0x71/4 tibia 4 (+16,7°), 0x71/5 fémur 4 (+8,4°). Sin respuesta al mover: coxa 1 (0x70/2 no aparece), coxa 2 (0x70/5 responde pero no cambia), coxa 3 (0x71/2 no aparece), coxa 4 (0x71/6, imán débil), tibia 3 (0x71/0, imán débil), fémur 3 (0x71/1, sin imán). Todas las salidas en OFF al terminar.
- Barrido combinado potenciómetros + AS5600 (19 de octubre, CODIGO/barrido_sensores; cobertura_sensores_20261019.json). Cobertura por articulación: coxa 1 → pot C0; coxa 2 → pot C1; coxa 3 → pot C3; coxa 4 → pot C2; fémur 1 → pot C8 + AS5600 0x70/1; fémur 2 → pot C5 + AS5600 0x70/4 (débil, 6°); fémur 3 → NINGUNO; fémur 4 → pot C6 + AS5600 0x71/5; tibia 1 → AS5600 0x70/0; tibia 2 → pot C9 + AS5600 0x70/3; tibia 3 → pot C11; tibia 4 → pot C10 + AS5600 0x71/4. Los encoders 0x70/1 y 0x70/4 que aparecen al mover las coxas 1 y 4 son los de los fémures (arrastre mecánico o lectura errática), no de las coxas. Total: 11 de 12 articulaciones con al menos un sensor; falta el fémur 3.
- Tras pasar el potenciómetro de la tibia 2 al fémur 3 (19 de octubre), barrido con el encoder propio de cada articulación (cobertura_sensores_20261019_v2.json). Las 12 articulaciones tienen al menos un sensor. Potenciómetros: coxas C0/C1/C3/C2, fémur 1 C8, fémur 2 C5, fémur 3 C9, fémur 4 C6, tibia 3 C11, tibia 4 C10. Encoders útiles: fémur 1 0x70/1 (−29°), fémur 4 0x71/5 (+7,7°), tibia 1 0x70/0 (−18°), tibia 2 0x70/3 (−13°). Encoders sin señal útil: coxa 1 (0x70/2) y coxa 3 (0x71/2) no responden; coxa 2, coxa 4, fémur 2, fémur 3 y tibia 3 no cambian (imán); tibia 4 (0x71/4) no respondió en esta pasada, aunque sí en las dos anteriores.
- PPO actualizada para leer la tibia 2 por su AS5600 0x70/3 (19 de octubre): el firmware devuelve el ángulo crudo en el modo @ y desactiva el ALLCALL del PCA9685; el ejecutor convierte con −0,66 °encoder/°servo. Caminatas base y PPO (16:21–16:22, *_enc_t2_20261019.csv), periodo 36,6–36,9 ms. En el paso 837 de la PPO todos los potenciómetros saltaron a la vez +40–50 cuentas (caída de la referencia, no movimiento). Hasta el paso 836: corrección realizada F2 101 %, F4 95 %, T2 71 % (el encoder sigue la corrección). Coxas: base 0,33/0,39/0,48°, PPO 0,78/0,78/0,62°, así que en esta pasada la base fue más estable.
- Primera grabación con las dos cámaras laterales (19 de octubre, `Experimentos/camaras/grabaciones/prueba_dos_camaras`): caminata base de 4 ciclos (385 pasos) terminada bien; 765 y 757 fotogramas; desfase de reloj +0,085 s.
