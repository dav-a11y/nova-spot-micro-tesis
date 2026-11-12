# Resumen de caracterización AS5600 — 28 de septiembre de 2026

## Estado de cierre — 29 de septiembre de 2026

La adquisición de grados absolutos del imán queda finalizada como dataset:
20 muestras por articulación y sentido en los extremos manuales registrados.
Se conservan medias, rangos y marcas de estabilidad sin descartar las señales
inestables. “Finalizada” se refiere al registro magnético; no significa que los
valores sean ángulos articulares calibrados ni que autoricen PWM o marcha.
La lectura única posterior de 29 de septiembre no se mezcla con estas muestras.

El operador fijó como referencias finales los siguientes intervalos absolutos
del imán. Se guardaron por separado en `operator_fixed_reference_ranges_deg`
del YAML; no sustituyen los mínimos, máximos y medias medidos en las ventanas
originales.

| Pata / articulación | Horario ° | Antihorario ° |
|---|---:|---:|
| 1 — Coxa | 308,782–310,782 | 111,373–113,373 |
| 1 — Fémur | 231,831–233,831 | 131,460–133,460 |
| 1 — Tibia | 83,672 | 203,379 |
| 2 — Coxa | 114,604–116,604 | 145,162–147,162 |
| 2 — Fémur | 299,795 | 288,809 |
| 2 — Tibia | 83,232 | 248,811–250,811 |
| 3 — Coxa | 35,290–37,290 | 182,863–184,863 |
| 3 — Fémur | 46,039–48,039 | 97,126–99,126 |
| 3 — Tibia | 299,968–301,968 | 36,446–38,446 |
| 4 — Coxa | 216,562 | 191,484–193,484 |
| 4 — Fémur | 291,797 | 66,006 |
| 4 — Tibia | 74,472–76,472 | 303,047 |

Son intervalos de referencia magnética definidos por el operador, no límites
mecánicos ni una conversión calibrada a radianes articulares. La autorización
de control permanece desactivada.

## Alcance

Se conectó a la Raspberry Pi 4 por SSH con la identidad previamente verificada de `cuadrupedo-pi.local`. Durante la sesión la IP cambió de `192.168.0.101` a `172.18.81.198`; se comparó la clave SSH de la nueva IP con la conocida antes de reconectar. El repositorio Git de la Raspberry presentaba un objeto local corrupto, por lo que el lector y el YAML se copiaron directamente por SSH.

El escaneo de I2C-1 mostró PCA9685 `0x40` y TCA9548A `0x70`/`0x71`. El usuario aclaró que `0x70` canales 6--7 y `0x71` canal 2 están vacíos. Con el mapa corregido respondieron las doce rutas ocupadas. El operador movió manualmente las articulaciones con la alimentación de servos desconectada. Para cada condición se obtuvieron veinte muestras I2C. No se ordenó PWM ni marcha.

## Mapa físico confirmado

| Pata | Articulación | Variable ROS | TCA/canal |
|---:|---|---|---|
| 1 delantera derecha | Tibia | `front_right_tibia_joint` | `0x71`/0 |
| 1 | Fémur | `front_right_femur_joint` | `0x71`/1 |
| 1 | Coxa | `front_right_coxa_joint` | `0x71`/3 |
| 2 delantera izquierda | Tibia | `front_left_tibia_joint` | `0x71`/4 |
| 2 | Fémur | `front_left_femur_joint` | `0x71`/5 |
| 2 | Coxa | `front_left_coxa_joint` | `0x71`/6 |
| 3 trasera derecha | Tibia | `rear_right_tibia_joint` | `0x70`/3 |
| 3 | Fémur | `rear_right_femur_joint` | `0x70`/4 |
| 3 | Coxa | `rear_right_coxa_joint` | `0x70`/5 |
| 4 trasera izquierda | Tibia | `rear_left_tibia_joint` | `0x70`/0 |
| 4 | Fémur | `rear_left_femur_joint` | `0x70`/1 |
| 4 | Coxa | `rear_left_coxa_joint` | `0x70`/2 |

Los TCA y PCA9685 comparten I2C-1: SDA GPIO2/pin físico 3 y SCL GPIO3/pin físico 5, con tierra común.

## Resultados

Ángulos absolutos del imán, en grados de 0 a 360. La columna de rango es el máximo menos el mínimo en veinte muestras. Los nombres horario y antihorario indican el extremo manual seguro señalado por el operador.

| Articulación | TCA/canal | Referencia inicial | Horario: media (rango) | Antihorario: media (rango) |
|---|---|---:|---:|---:|
| Coxa 1 | `0x71`/3 | 266,623° (31,201°) | 309,782° (0,791°) | 112,373° (1,142°) |
| Fémur 1 | `0x71`/1 | 185,061° (0,088°) | 232,831° (0,176°) | 132,460° (0,176°) |
| Tibia 1 | `0x71`/0 | 139,570° (0,000°) | 83,672° (0,000°) | 203,379° (0,000°) |
| Coxa 2 | `0x71`/6 | 128,635° (14,326°) | 115,604° (18,633°) | 146,162° (9,580°) |
| Fémur 2 | `0x71`/5 | 255,586° (0,000°) | 299,795° (0,000°) | 288,809° (0,000°) |
| Tibia 2 | `0x71`/4 | 60,000° (0,000°) | 83,232° (0,000°) | 249,811° (0,088°) |
| Coxa 3 | `0x70`/5 | 142,866° (5,801°) | 36,290° (16,435°) | 183,863° (0,615°) |
| Fémur 3 | `0x70`/4 | 195,827° (0,088°) | 47,039° (0,088°) | 98,126° (0,176°) |
| Tibia 3 | `0x70`/3 | 330,959° (4,483°) | 300,968° (8,877°) | 37,446° (5,713°) |
| Coxa 4 | `0x70`/2 | 210,586° (0,000°) | 216,562° (0,000°) | 192,484° (0,088°) |
| Fémur 4 | `0x70`/1 | 312,979° (0,000°) | 291,797° (0,000°) | 66,006° (0,000°) |
| Tibia 4 | `0x70`/0 | 338,994° (0,000°) | 75,472° (0,088°) | 303,047° (0,000°) |

La coxa 1 tuvo otra ventana inicial de referencia con rango 25,401°; ambas lecturas iniciales muestran que esa referencia visual no es repetible todavía.

## Calidad y limitaciones

Las doce direcciones responden I2C con el mapa corregido. Las capturas de coxa 2 presentan dispersión grande en los tres estados. Coxa 3 presenta alta dispersión en referencia y extremo horario, aunque la captura antihoraria fue más estable. Tibia 3 presentó dispersión apreciable en los tres estados. Coxa 1 tuvo una referencia inicial inestable y extremos manuales comparativamente más concentrados. Las demás lecturas se mantuvieron concentradas en estas ventanas.

La variación observada puede proceder de juego o movimiento mecánico, fijación del imán/encoder, alimentación/tierra o ruido. Esta sesión no identifica la causa. Los grados son absolutos del imán y aún no expresan los ángulos articulares del modelo. El YAML `Raspberry/configuracion/as5600_caracterizacion_provisional.yaml` conserva las medias, mínimos, máximos, rangos y marcas de estabilidad por condición; el informe cronológico detallado está en `Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`.

## Siguiente trabajo

Falta medir sentido y cero de cada articulación respecto al modelo, considerar el cruce circular 0°/360°, comprobar repetibilidad durante movimiento, fijar márgenes antes de topes mecánicos y resolver las señales variables antes de usarlas para realimentación. Esta caracterización no habilita control de postura, marcha ni PPO físico.

## Captura adicional por posturas — 7 de octubre de 2026

El operador aportó 100 muestras por sensor en seis condiciones de postura. Según
su aclaración, las patas 1 y 2 son delanteras. Se conservan mínimo, máximo,
promedio, variación y, cuando fue indicada, la etiqueta de estado reportada.
Los datos están también en `operator_posture_samples_2026_10_07` del YAML.
Son grados absolutos del imán AS5600; las posturas no representan extremos
mecánicos ni pulsos PWM calibrados. Estas estadísticas no habilitan control.

| Articulación | Fémur atrás: min–max / media / variación ° | Fémur adelante: min–max / media / variación ° |
|---|---:|---:|
| Fémur 1 (delantera) | 246,182–246,357 / 246,288 / 0,176 | 117,861–117,949 / 117,916 / 0,088 |
| Fémur 2 (delantera) | 152,666–153,105 / 152,767 / 0,439 | 148,359–148,447 / 148,441 / 0,088 |
| Fémur 3 (trasera) | 182,373–184,043 / 183,020 / 1,670 | 23,730–39,551 / 30,772 / 15,820 |
| Fémur 4 (trasera) | 69,434–69,697 / 69,500 / 0,264 | 103,184–103,887 / 103,638 / 0,703 |

| Articulación | Coxa arriba: min–max / media / variación ° | Coxa abajo: min–max / media / variación ° |
|---|---:|---:|
| Coxa 1 (delantera) | 138,867–138,867 / 138,867 / 0,000 | 127,969–128,057 / 128,036 / 0,088 |
| Coxa 2 (delantera) | 146,953–147,041 / 147,026 / 0,088 | 164,883–164,883 / 164,883 / 0,000 |
| Coxa 3 (trasera) | 174,287–175,078 / 174,381 / 0,791 | 185,273–186,064 / 185,992 / 0,791 |
| Coxa 4 (trasera) | 135,791–135,791 / 135,791 / 0,000 | 167,080–167,168 / 167,081 / 0,088 |

| Articulación | Tibia adelante: min–max / media / variación ° | Tibia atrás: min–max / media / variación ° |
|---|---:|---:|
| Tibia 1 (delantera) | 240,557–240,557 / 240,557 / 0,000 | 75,410–75,498 / 75,497 / 0,088 |
| Tibia 2 (delantera) | 77,959–78,047 / 78,012 / 0,088 | 233,965–233,965 / 233,965 / 0,000 |
| Tibia 3 (trasera) | 239,941–240,029 / 239,955 / 0,088 | 256,465–256,553 / 256,468 / 0,088 |
| Tibia 4 (trasera) | 73,740–73,828 / 73,813 / 0,088 | 301,904–301,904 / 301,904 / 0,000 |

El operador reportó FEMUR 3 como muy variable en ambas posturas (especialmente
adelante: 15,820°) y FEMUR 4 como variable al frente (0,703°); también describió
COXA 3 como variación moderada en ambas posturas (0,791°). Para COXA 4 y algunas
tibias no se incluyó etiqueta textual, por lo que no se infiere una. Se copian
las estadísticas comunicadas sin recalcularlas, incluso si el redondeo de
mínimo/máximo no coincide exactamente con la variación informada.
