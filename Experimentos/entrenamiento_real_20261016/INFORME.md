# Entrenamiento PPO ajustado al robot real — 16 de octubre de 2026

## Datos reales usados
Las caminatas `b` del robot suspendido (sesiones 131, 135 y 136 de `~/CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite`) se registraron con los potenciómetros leídos por el MUX 16CH (selectores D8–D11, SIG A0). Con `identificar_actuadores_reales.py` se obtuvo lo siguiente (`actuadores_reales.json`):

| Articulación | Sensor | r | Retardo | Ganancia |
|---|---|---:|---:|---:|
| Fémur 2 (FL) | C5 | −0,81 | 100 ms | 0,88 |
| Fémur 4 (RL) | C6 | −0,84 | 100 ms | 0,92 |
| Tibia 2 (FL) | C9 | −0,88 | 100 ms | 0,98 |
| Tibia 4 (RL) | C10 | −0,01 | — | 0,04 (casi no se mueve en la caminata) |
| Tibia 3 (RR) | C11 | −0,10 | — | señal no fiable |

La tibia 1 (FR, CH8) tiene un servo dañado (tramo muerto en su potenciómetro) y queda sin PWM. Las coxas se mantienen fijas en su equilibrio: 150°, 45°, 55° y 150°.

## Simulación ajustada (`entrenar_ppo_real.py`)
- Marcha nominal: la caminata `b` real, gateo FL→RR→FR→RL, fémures ±15°, tibias 14°, 0,5 s + 0,15 s por fase (ciclo de 2,64 s).
- Actuador: retardo de 5 pasos (100 ms) y ganancia por articulación según la tabla; tibia FR sin rigidez.
- Observación (17): ángulos de fémur 2, fémur 4 y tibia 2 con ruido de 1°, más seno y coseno de la fase y el residual previo. Son señales que el Uno sí puede medir.
- Acción: residual ±0,08 rad con cambio máximo de 0,02 rad por paso, aplicado solo a fémures y tibias útiles (coxas y tibia FR en cero).
- Aleatorización de la fricción del suelo y del amortiguamiento. Sin cambios en el entrenador ni en el MJCF originales.

## Resultados (150 000 pasos por semilla; evaluación con escenarios de desarrollo 801–805, 6 ciclos)

| Semilla | Avance (m) | Deriva lateral (m) | Inclinación máx. (rad) | Caídas |
|---|---:|---:|---:|---:|
| Nominal | 0,173 | 0,111 | 0,128 | 0 |
| 11 | **0,299** | **0,046** | **0,097** | 0 |
| 23 | 0,214 | 0,126 | 0,140 | 0 |
| 37 | 0,245 | 0,070 | 0,108 | 0 |
| 53 | 0,249 | 0,080 | 0,153 | 0 |
| 71 | 0,237 | 0,064 | 0,112 | 0 |

Las cinco políticas avanzan más que la nominal. Las semillas 11, 37 y 71 mejoran a la vez el avance, la deriva y la inclinación. La semilla 11 es la mejor: +73 % de avance, −58 % de deriva y −24 % de inclinación.

## Límites
- La evaluación es en simulación, con escenarios de desarrollo; las semillas finales 101–505 no se usaron.
- Los signos de fémur y tibia del modelo se asumieron a partir de la marcha nominal del proyecto, sin calibración ángulo-servo.
- No se ha transferido ninguna política al robot (`hardware_transfer=false`). Para probarla falta un modo del firmware que reciba residuales desde el PC por el puerto serie y envíe C5, C6 y C9 como observación.

## Primera ejecución en el robot real (16 de octubre, robot suspendido)
Modo `@` del firmware: el PC envía los 12 ángulos en cada paso y el Uno aplica los límites (fémur ±20°, tibia ±18°, 3° por paso), mantiene las coxas fijas con corrección y deja la tibia 1 sin PWM. Programa: `ejecutar_politica_robot.py`; análisis: `analizar_ejecucion_robot.py`.

| Ejecución | Pasos | Periodo real | F2 r / error | F4 r / error | T2 r / error |
|---|---:|---:|---|---|---|
| Nominal (`robot_nominal_20261016_183944.csv`) | 578 | 28,7 ms | 1,00 / 0,5° | 1,00 / 0,5° | 0,99 / 0,4° |
| PPO semilla 11 (`robot_ppo_20261016_184028.csv`) | 578 | 28,9 ms | 1,00 / 0,5° | 1,00 / 0,6° | 0,98 / 0,5° |

La política corre en tiempo real sobre el robot y aplica correcciones de hasta ±4,6° (el límite de 0,08 rad) en fémures y tibias. El seguimiento articular se mantiene. Límites de esta prueba:
- el periodo real (~29 ms) es mayor que el de entrenamiento (20 ms);
- el robot no tiene IMU ni contactos, así que no se puede medir avance ni estabilidad del cuerpo; la valoración física depende del operador y de pruebas apoyadas posteriores.

## Más marchas, identificación del sistema y reentrenamientos v2 y v3 (16 de octubre, tarde)

**Ronda 1 en el robot** (`registros_robot/ronda1_*.csv`, 8 ciclos): nominal y PPO v1 con las semillas 11, 37 y 71. F2, F4 y T2 siguieron la orden con r ≥ 0,98 y error ≤ 0,6°. Reidentificación con estos registros (`identificar_desde_registros.py`): ganancia ≈ 1,0, retardo de 87 ms y periodo de 29 ms (`actuadores_reales_v2.json`).

**Identificación articulación por articulación** (`identificar_sistema_robot.py` y `analizar_identificacion.py`; datos en `identificacion_robot/`, resumen en `identificacion_sistema.json`). Pruebas: escalones de ±1, ±2, ±6 y ±12° y senoides de 8° a 0,5, 1 y 2 Hz.

| Articulación | Escala | Escalón de ±1° | Escalón de +12° | Ganancia a 2 Hz | Retardo |
|---|---|---|---|---|---|
| F2 (C5) | −2,47 cuentas/° | +0,5 / −1,1° | 12,2° (subida en 132 ms) | 0,87 | 80–85 ms |
| F4 (C6) | −2,48 | +0,2 / −1,0° | 11,9° (163 ms) | 0,89 | 77 ms |
| T2 (C9) | −2,47 | +0,3 / −0,9° | 12,1° (165 ms) | 0,92 | 75 ms |
| T4 (C10) | −2,45 | +0,2 / −0,6° | 12,1° (99 ms) | 0,74 | 65 ms |
| T3 (C11) | Sensor inservible (R² = 0,008) | — | — | — | — |

Conclusiones:
- Zona muerta de ~0,5–1° con histéresis.
- Buen seguimiento hasta 1 Hz.
- Sin acoplamiento entre canales.
- **T4 sí se mueve** (la ganancia de 0,04 del modelo v1 era errónea).

**Entrenamiento v2** (periodo de 30 ms y actuador v2, que todavía tenía T4 en 0,04): la semilla 37 obtuvo 0,332 m de avance frente a 0,190 m de la nominal, con deriva de 0,073 frente a 0,138 m.

**Entrenamiento v3** (actuador v3: T4 con ganancia 1,0 y zona muerta de 0,75°):

| | Avance | Deriva | Inclinación |
|---|---:|---:|---:|
| Nominal | 0,163 m | **0,010 m** | **0,116 rad** |
| PPO semilla 71 | **0,284 m** | 0,052 m | 0,124 rad |
| PPO semilla 11 | 0,226 m | 0,048 m | 0,118 rad |

Con el actuador bien modelado, la nominal camina casi recta y ninguna política la supera en las tres métricas a la vez: el PPO cambia rectitud por velocidad. Buena parte de la mejora de v1 compensaba el error de modelado de T4.

**Ronda 2 en el robot** (`registros_robot/ronda2_v3_*.csv`, 8 ciclos a 30 ms; periodo real 32,8 ms con 8 canales): nominal y PPO v3 semilla 71 con error ≤ 0,5° en F2, F4 y T2.

## Búsqueda de estabilidad (16 de octubre, noche)

**Barrido de la caminata base** (`barrido_estabilidad_nominal.py`, actuador v3, 5 escenarios por combinación; resultados en `barrido_estabilidad_nominal.csv`).
- La elevación de la tibia es lo que más desestabiliza: con 18° y fémur ≥ 15° cae en 5 de 5 escenarios.
- Las fases de 0,8 s son menos estables que las de 0,5 s.
- La mejor combinación es **fémur 15°, tibia 10° y fase de 0,5 s**: avance 0,204 m (antes 0,163), inclinación RMS 0,049 rad (antes 0,064) y deriva 0,019 m, sin caídas.

**PPO v4 orientado a estabilidad**: sobre la base nueva, 200 000 pasos y recompensa con pesos avance 10, actitud 30, lateral 20 y giro 10.

| | Avance | Deriva | Inclinación máx. |
|---|---:|---:|---:|
| Base fémur 15° / tibia 10° | 0,204 m | 0,019 m | 0,099 rad |
| **PPO v4 semilla 37** | 0,184 m | **0,009 m** | **0,069 rad** |
| PPO v4 semilla 11 | 0,150 m | 0,005 m | 0,064 rad |

La semilla 37 reduce un 54 % la deriva y un 31 % la inclinación, a cambio de un 10 % menos de avance. Las semillas 23, 53 y 71 no son útiles.

**Ronda 3 en el robot** (`registros_robot/ronda3_*.csv`, 8 ciclos, robot suspendido): la base nueva y la PPO v4 semilla 37 se ejecutaron con un error ≤ 0,7° en F2, F4 y T2. La estabilidad corporal debe confirmarse con el robot apoyado.

## Corrección medida por los sensores (ronda 5, 16 de octubre)
`ejecutar_politica_robot.py` guarda ahora también la orden nominal. `cuantificar_correccion.py` compara paso a paso la base (tibia 10°) con la PPO v4 semilla 37 (`registros_robot/ronda5_*.csv`, 703 pasos sin la rampa):

| Articulación | Corrección ordenada (media / máx.) | Corrección realizada medida | Realizado | r | Retardo |
|---|---|---|---:|---:|---:|
| Fémur 2 | 3,23° / 5,0° | 3,31° / 6,5° | 99 % | 0,97 | 99 ms |
| Fémur 4 | 1,57° / 3,0° | 1,63° / 4,9° | 94 % | 0,90 | 99 ms |
| Tibia 2 | 0,85° / 2,0° | 1,02° / 3,3° | 79 % | 0,77 | 99 ms |

Los fémures ejecutan casi toda la corrección. En la tibia 2 se pierde parte, porque sus correcciones (~1°) están en la zona muerta del servo. Las coxas se mantienen dentro de ±0,3° de media con la base y la PPO (p95 ≤ 1,2°).

## Topes absolutos en el firmware (16 de octubre)
`escribirServo()` limita ahora cada canal PCA según los límites medidos por el operador, con 10° de margen: C1 105–170, C2 10–85, C3 25–90, C4 125–170, F1 30–140, F2 45–170, F3 40–160, F4 25–170, T1 (CH8) 25–160, T2 (CH12) 25–90 (límite trasero de T2 = 100, confirmado), T3 (CH9) 11–160, T4 (CH11) 15–150. Verificado con 4 ciclos de PPO v4 semilla 37 (`registros_robot/verificacion_topes.csv`): todas las órdenes quedan dentro de los topes y el seguimiento no cambia.

## Barrido de rango con sensores (16 de octubre)
`barrido_rango_robot.py`: cada articulación recorre su base ±40° (dentro de los topes) en pasos de 3°, subiendo y bajando. Análisis en `analizar_barrido_rango.py` y `barrido_rango/modelo_rango.json`.

| Articulación | Rango probado | Escala | No linealidad RMS (máx.) | Histéresis media (máx.) | Saturación |
|---|---|---:|---|---|---|
| F2 (C5) | 60–140° | −2,52 cuentas/° | 0,62° (1,9°) | 0,89° (2,0°) | Deja de seguir por encima de ~135° |
| F4 (C6) | 60–140° | −2,51 | 0,68° (1,7°) | 0,98° (2,4°) | Por encima de ~135° |
| T2 (C9) | 40–88° | −2,59 | 0,44° (0,8°) | 0,64° (0,8°) | — |
| T4 (C10) | 30–110° | −2,52 | 1,1° (3,9°) | 1,51° (3,7°) | Por encima de ~105° (coincide con la parada de la sesión 74) |

Aplicado:
- topes del firmware F2 y F4 ≤ 135° y T4 ≤ 105°;
- escalas por articulación en `ejecutar_politica_robot.py`;
- `actuadores_reales_v4.json` con histéresis, saturación y zona muerta de 1°.

## Reentrenamiento v5 con el actuador v4 y política elegida (16 de octubre)
PPO v5 (actuador v4: zona muerta de 1°, histéresis; misma base y misma recompensa de estabilidad): ninguna semilla mejora la estabilidad de la base. La deriva es de 0,035–0,075 m frente a 0,013 m.

Evaluación cruzada con el actuador v4 en 10 escenarios (801–810):

| | Avance | Deriva | Inclinación máx. |
|---|---:|---:|---:|
| Base fémur 15° / tibia 10° | 0,206 m | 0,009 m | 0,097 rad |
| **PPO v4 semilla 37** | 0,188 m | 0,009 m | **0,069 rad** |
| PPO v4 semilla 11 | 0,157 m | 0,006 m | 0,068 rad |
| PPO v5 semilla 23 | 0,114 m | 0,034 m | 0,079 rad |

**Política elegida: v4 semilla 37.** Es robusta frente al actuador más realista: −28 % de inclinación con la misma deriva y −9 % de avance.

Ronda 6 en el robot (`registros_robot/ronda6_*.csv`, escalas por articulación). Corrección realizada frente a la ordenada:
- F2: 100 % (3,2° de media);
- F4: 99 % (1,6°);
- T2: 71 % (0,8°, dentro de la zona muerta).

Las coxas se mantienen a ≤ 0,5° de media de su equilibrio (p95 ≤ 1,2°).
