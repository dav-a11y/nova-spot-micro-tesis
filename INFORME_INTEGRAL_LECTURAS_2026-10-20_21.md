# Informe integral de lecturas, marcha y cámaras

## Cuadrúpedo — 20 y 21 de octubre de 2026

**Equipo de origen:** este PC, `/home/pavilion/Documentos/Cuadrupedo/Experimentos/camaras/grabaciones/`  
**Zona horaria:** America/Bogota (UTC−05:00)  
**Corte de revisión:** 21 de octubre de 2026, aproximadamente 20:40.  
**Anexo:** [resumen métrico por sesión, 94 filas](/home/pavilion/Documentos/Cuadrupedo/ANEXO_METRICO_SESIONES_2026-10-20_21.csv)

## Resumen ejecutivo

Se revisaron **94 carpetas de registro** con datos fechados en estos dos días: **44 del 20 de octubre** y **50 del 21 de octubre**. Se completó el diagnóstico y el análisis visual de la grabación más reciente, `rep_ciclo2_gateo_base_r2`, antes de cerrar este informe.

Hay **79 diagnósticos cinemáticos** con lecturas de sensores: 43 del día 20 y 36 del día 21. En las repeticiones no marcadas como fallidas, los fémures siguen las órdenes con correlaciones medianas altas. La diferencia de calidad más llamativa entre días está en la temporización: el 21 hay muchos más intervalos de control mayores de 40 ms que el 20. En paralelo, varias cámaras —en especial celular/logitech el día 20 y general/logitech el día 21— registran huecos de cuadros, así que la precisión temporal del video no es uniforme.

Hay dos limitaciones de realimentación que no deben confundirse con una pata inmóvil: **tibia 1 / ENC_T1 no tuvo lecturas válidas en los 79 diagnósticos**, y en 24 de los 36 diagnósticos del 21 la tibia 3/C11 aparece marcada sin sensor según la configuración usada. Por lo tanto, las conclusiones sobre esas tibias no pueden basarse en su encoder/potenciómetro en esas corridas.

Los ensayos marcados fallidos sí muestran señales concretas que ameritan revisión. El trote PPO1 R2 del 21 de octubre marcado `fallo` tiene femures 2–4 con correlaciones de aproximadamente 0,75, 0,76 y 0,73; la repetición `fallo_degradado` registra aproximadamente 0,705, 0,710 y 0,682. Esas cifras respaldan que la realimentación no siguió bien las órdenes en esos ensayos, pero **no prueban por sí solas que el bus I²C estuviera bloqueado**. Hay tres registros del 20 que anotan explícitamente SDA a 0 durante la caminata; son evidencia del evento anotado por el sistema, no una causa confirmada para los otros ensayos.

## Alcance e inventario

| Día | Carpetas con `caminata.csv` | Tipo de actividad | Diagnóstico JSON | Análisis visual JSON | Observación |
|---|---:|---|---:|---:|---|
| 20/10 | 44 | 18 gateo, 21 paso, 5 trote | 43 | 37 | Seis carpetas marcadas inválidas; una quedó sin diagnóstico por fallo de disco. |
| 21/10 | 50 | 19 gateo, 17 trote, 11 calibraciones de color y 3 identificaciones de patas | 36 | 50 | Dos trotes marcados inválidos/degradados; todas las grabaciones incluidas tienen análisis visual. |
| **Total** | **94** | 37 gateos, 21 pasos, 22 trotes, 14 actividades de calibración/identificación | **79** | **87** | Las actividades de calibración e identificación no se interpretan como caminatas periódicas. |

Las cuentas de “análisis visual” incluyen la clasificación de patas y pruebas de color/identificación. En trote, el algoritmo agrupa las patas en pares diagonales P2+P3 y P1+P4 porque las patas de cada par comparten orden; no es una medición independiente de cuatro patas.

Los registros brutos (`caminata.csv`), configuraciones, diagnósticos y análisis visuales originales permanecen en sus carpetas de sesión. El anexo CSV agrega los indicadores principales de cada una de las 94 carpetas, el estado de cada modalidad, las notas de invalidez, las métricas por fémur/cámara y las rutas a los JSON fuente.

## Cómo leer estas mediciones

- **r (correlación):** cuánto sigue la lectura del sensor o el movimiento extraído del video a la orden programada. No mide desplazamiento del robot en el piso, fuerza, estabilidad dinámica ni calidad de contacto de las patas.
- **RMSE/error RMS (°):** error angular promedio respecto de la señal de orden bajo el cálculo del diagnóstico. Un valor menor es mejor dentro de una misma articulación/configuración; no debe compararse sin más entre sensores con distintas calibraciones.
- **Deriva de desfase (°):** cambio entre el desfase medio inicial y final de la corrida. No equivale a desgaste mecánico por sí solo.
- **Intervalo >40 ms:** el diagnóstico cuenta separaciones de muestreo superiores a 40 ms. La consigna habitual es `dt=0,03 s` (aprox. 33 ms); demasiados intervalos largos indican temporización irregular de lectura/control, pero no identifican por sí mismos la causa.
- **Sensor “caído”:** el código de diagnóstico lo marca así si más de la mitad de las muestras son negativas o si la configuración declara explícitamente que no hay sensor. Significa que no se pudo evaluar la realimentación; no significa necesariamente que el servo no se movió.
- **Ciclos anómalos del video:** son ciclos cuyo movimiento no explicado supera el umbral estadístico del script (tres veces la mediana de esa vista). Son candidatos para revisar, no fallas confirmadas.
- **CV de amplitud:** variación relativa entre ciclos de la señal visual extraída. Durante una calibración o identificación deliberada no debe interpretarse como estabilidad de una marcha.

Los umbrales usados por el protocolo del proyecto son r≥0,90 para gateo/paso y r≥0,80 para trote; para corridas incompletas el protocolo también revisa si la duración alcanza el 90% de la solicitada. Esos umbrales sirven para el filtro interno, no son una norma universal de seguridad.

## Comparación de telemetría entre días

| Indicador | 20/10 | 21/10 | Lectura |
|---|---:|---:|---|
| Diagnósticos con sensores | 43 | 36 | El día 21 hay menos diagnósticos que carpetas porque incluye calibración/identificación sin diagnóstico de marcha. |
| Muestras procesadas | 214.195 | 184.877 | Conteo agregado de filas reportadas por diagnóstico, no número de ciclos. |
| Tiempo acumulado diagnosticado | 7.029,7 s (117,2 min) | 6.163,3 s (102,7 min) | Corridas en su mayoría cercanas a 180 s; incluye ensayos fallidos. |
| Ciclos agregados | 3.170 | 3.748 | El trote produce más ciclos por minuto que gateo/paso. |
| Corridas con algún intervalo >40 ms | 12/43 | 28/36 | Aumenta claramente la frecuencia de irregularidad temporal el día 21. |
| Intervalos >40 ms acumulados | 412 | 3.879 | El 21 se concentra una parte importante en trotes PPO y gateos PPO. |
| Mediana entre corridas del percentil 99 del intervalo | 33 ms | 37,5 ms | La cola de latencia empeora el día 21; la mediana no es el máximo de cada muestra. |
| Máximo p99 observado | 46 ms | 54 ms | El máximo del día 21 corresponde a `rep_ciclo2_trote_ppo1_r2_fallo_degradado`. |

El salto de intervalos largos no demuestra que el robot caminara peor: indica que la cadencia de registro/control fue menos regular. Puede estar relacionado con carga de procesos, cámara, disco, comunicación u otras condiciones; estos registros no permiten aislar causalidad. Conviene comparar la misma política con carga de cámara constante y repetir la medición.

### Seguimiento de fémures en corridas no marcadas inválidas

Medianas de r por articulación, calculadas entre sesiones diagnósticas no marcadas inválidas/degradadas:

| Día y marcha | n | Fémur 1 | Fémur 2 | Fémur 3 | Fémur 4 | p99 de intervalo mediano | Intervalos >40 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20/10 gateo | 15 | 0,993 | 0,978 | 0,978 | 0,975 | 34 ms | 7 en 3 sesiones |
| 20/10 paso | 18 | 0,989 | 0,972 | 0,969 | 0,966 | 33,5 ms | 404 en 8 sesiones |
| 20/10 trote | 5 | 0,981 | 0,910 | 0,904 | 0,904 | 33 ms | 0 |
| 21/10 gateo | 19 | 0,992 | 0,991 | 0,981 | 0,983 | 35 ms | 1.591 en 13 sesiones |
| 21/10 trote | 15 | 0,990 | 0,983 | 0,986 | 0,974 | 37 ms | 1.126 en 13 sesiones |

Dentro de los registros limpios del 20, el trote tiene r algo menor en fémures 2–4 que gateo/paso (medianas 0,90–0,91), pero todavía por encima del umbral interno de 0,80. El 21 los trotes limpios muestran r alta; sus p99 y conteos de intervalos largos, sin embargo, señalan temporización menos regular. La política, amplitudes y calibraciones varían entre sesiones, por lo que esta tabla describe asociación orden–lectura y no una comparación experimental perfectamente controlada.

Las medianas de error RMS en los 43 diagnósticos del 20 fueron 1,38°, 2,24°, 2,29° y 2,42° para fémures 1–4. En los 36 del 21 fueron 1,20°, 2,29°, 2,47° y 2,25°. No se observa una pérdida general de correlación en las corridas limpias; las alertas de fémures 2–4 se concentran en los dos trotes fallidos del final del día.

### Desplazamiento común C0

En corridas limpias, el máximo absoluto del canal común C0 tuvo mediana de 35 cuentas para gateo, 56 para paso y 49 para trote el día 20; el 21 fue 38 para gateo y 58 para trote. Los máximos del 21 alcanzaron 161 cuentas (p95 de gateo limpio) y 170 (p95 de trote limpio). En algunos fallos del 20 C0 superó 200 cuentas, con un máximo de 478.

Estas unidades son **cuentas del sensor**, no grados ni milímetros; el movimiento puede reflejar inclinación del cuerpo o cambio común de lectura. Sirve para localizar episodios de cambio brusco y comparar corridas con idéntica calibración, no para afirmar un desplazamiento físico preciso.

## Sensores y realimentación

| Lectura en diagnóstico | 20/10 | 21/10 | Interpretación correcta |
|---|---:|---:|---|
| Tibia 1, `ENC_T1`, marcada `caido` | 43/43 | 36/36 | No hubo suficientes lecturas válidas para evaluar la trayectoria de esta articulación por ese encoder. No demuestra que el servo se quedara quieto. |
| Tibia 2, `ENC_T2`, marcada `caido` | 5/43 | 0/36 | Los cinco casos del 20 se concentran en corridas fallidas/sospechosas anotadas abajo. |
| Tibia 3, `C11`, marcada `caido` | 0/43 | 24/36 | En parte de las configuraciones del 21 se declaró C11 sin sensor; la nota del proyecto indica que C11 no cambió al mover la tibia 3 y sugiere revisar el cable del potenciómetro. |
| Tibia 4, `C10`, marcada `caido` | 0/43 | 0/36 | El diagnóstico sí contó con lecturas suficientes en las corridas incluidas. |
| Lecturas perdidas en los cuatro fémures evaluados | 0 acumuladas en ambos días | 0 acumuladas en ambos días | La alerta en fémures es de seguimiento/correlación baja, no de huecos registrados en el canal femoral. |

Los cinco casos con tibia 2 no evaluable el 20 fueron: `rep_20261019_gateo_base_r2_fallo`, `rep_20261019_gateo_base_r2_sospechosa`, `rep_20261019_gateo_ppo_r3_fallo_i2c`, `rep_20261019_paso_base_r3_fallo_i2c` y `rep_20261019_paso_ppo_r3_fallo_i2c`.

El algoritmo de diagnóstico considera un sensor caído si más de la mitad de sus valores son negativos o si `caminata.config.json` contiene `sin_sensor`. Por eso la repetición de `ENC_T1` en todos los informes es una carencia de realimentación sistemática del conjunto de datos, no 79 eventos independientes de avería mecánica. Revisar primero el origen eléctrico/configuración de ENC_T1 y C11 antes de usar esas tibias para decidir si el movimiento real fue correcto.

## Calidad y cobertura de cámaras

### Métricas de grabación del diagnóstico

El campo interno de cámara cambia según la sesión/día; por eso se conserva el nombre de clave registrado, sin asumir que `camara1` o `camara2` representan siempre el mismo dispositivo físico.

| Día | Clave de cámara | Registros con métrica | FPS mediano | Registros con huecos >50 ms | Mediana de huecos por registro | Nitidez mediana |
|---|---|---:|---:|---:|---:|---:|
| 20/10 | camara1 | 43 | 32,3 | 5 | 0 | 261,7 |
| 20/10 | camara2 | 35 | 31,2 | 26 | 1 | 170,6 |
| 20/10 | camara_celular | 42 | 7,5 | 39 | 1.152 | 272,5 |
| 20/10 | camara_logitech | 42 | 29,4 | 42 | 1.942 | 879,2 |
| 20/10 | camara_tablet | 3 | 25,0 | 3 | 52 | 803,6 |
| 21/10 | camara1 | 34 | 31,2 | 13 | 0 | 246,5 |
| 21/10 | camara2 | 19 | 31,2 | 17 | 1 | 289,4 |
| 21/10 | camara_general | 34 | 19,6 | 34 | 2.590 | 83,5 |
| 21/10 | camara_logitech | 34 | 30,3 | 34 | 1.224 | 289,0 |
| 21/10 | camara_windows | 21 | 30,3 | 21 | 17 | 233,7 |

Los huecos corresponden a separaciones de fotogramas mayores de 50 ms; son acumulados por captura y pueden depender del sincronismo/flujo de cámara. No deben confundirse con huecos de lecturas de los sensores del robot. La combinación celular a 7,5 fps el día 20 y cámara general a 19,6 fps el 21 limita cualquier comparación visual fina de tiempos. En la Logitech aparecen huecos según esta métrica pese al FPS mediano cercano a 30; se recomienda mirar también su video/CSV individual.

### Correlación visual en señales visibles

Medianas de r de las señales de pata/par que el analizador pudo identificar. `visibles/posibles` expresa cuántas señales de patas por sesión quedaron detectables; estas cifras no equivalen a un porcentaje de fotogramas buenos.

| Día | Marcha | Vista | r mediana | CV amplitud mediano | Señales visibles |
|---|---|---|---:|---:|---:|
| 20/10 | Gateo | HP-PC1 | 0,89 | 3,0% | 37/56 |
| 20/10 | Gateo | HP-PC2 | 0,96 | 1,8% | 36/44 |
| 20/10 | Gateo | Logitech | 0,91 | 1,9% | 44/56 |
| 20/10 | Gateo | Celular | 0,83 | 9,6% | 26/52 |
| 20/10 | Paso | HP-PC1 | 0,89 | 2,8% | 64/72 |
| 20/10 | Paso | HP-PC2 | 0,98 | 2,3% | 52/56 |
| 20/10 | Paso | Celular | 0,82 | 7,1% | 37/68 |
| 20/10 | Paso | Logitech | 0,95 | 1,7% | 72/72 |
| 20/10 | Trote | HP-PC1 | 0,90 | 5,2% | 9/10 |
| 20/10 | Trote | HP-PC2 | 0,98 | 4,0% | 4/10 |
| 20/10 | Trote | Logitech | 0,98 | 1,8% | 10/10 |
| 21/10 | Gateo | HP-PC1 | 0,92 | 3,4% | 49/76 |
| 21/10 | Gateo | HP-PC2 | 0,96 | 2,8% | 45/52 |
| 21/10 | Gateo | Logitech | 0,92 | 3,4% | 68/76 |
| 21/10 | Gateo | Windows | 0,94 | 2,6% | 51/52 |
| 21/10 | Gateo | General | 0,91 | 2,3% | 65/72 |
| 21/10 | Trote | HP-PC1 | 0,97 | 5,8% | 32/34 |
| 21/10 | Trote | General | 0,98 | 2,3% | 32/32 |
| 21/10 | Trote | Windows | 0,99 | 3,5% | 20/20 |
| 21/10 | Trote | HP-PC2 | 0,99 | 3,9% | 8/18 |
| 21/10 | Trote | Logitech | 0,98 | 3,4% | 20/34 |

La señal visible del trote del día 21 es alta en las vistas generales, pero no todas las cámaras muestran todos los pares. Las calibraciones e identificaciones del día 21 tuvieron CV muy alto en algunas vistas, lo esperado cuando se ejecutan movimientos deliberados que no son ciclos regulares; esas 14 actividades se excluyen de la tabla de marcha.

El contador de anomalías visuales marcó candidatos en varias sesiones, incluso en corridas con alta correlación. Por ejemplo, en el trote del día 21 el analizador marcó al menos una sesión con anomalías en HP-PC1 en 10/17 registros, en Logitech 10/17, Windows 6/17 y cámara general 3/17; en gateo fueron HP-PC1 8/19, HP-PC2 4/19 y Logitech 6/19. Esto amerita revisar esos clips/figuras, no descartar automáticamente la caminata. El criterio identifica movimiento no explicado en la imagen, que también puede provenir de vibración, exposición, cámara o sincronía.

## Ensayos que requieren atención

| Fecha/hora local | Sesión | Nota del registro | Lectura cuantitativa disponible | Conclusión prudente |
|---|---|---|---|---|
| 20/10 08:56 | `rep_20261019_paso_base_r3_fallo_i2c` | SDA a 0 / bus I²C bloqueado anotado | Sin seguimiento útil de ENC_T2 | El registro marca bloqueo; mantener como corrida interrumpida, no usar para comparar marcha normal. |
| 20/10 08:57 | `rep_20261019_paso_ppo_r3_fallo_i2c` | SDA a 0 / bus I²C bloqueado anotado | Sin seguimiento útil de ENC_T2 | Igual; alerta de bus anotada. |
| 20/10 09:02 | `rep_20261019_gateo_ppo_r3_fallo_i2c` | SDA a 0 / bus I²C bloqueado anotado | Sin seguimiento útil de ENC_T2 | Igual; corrida no comparable. |
| 20/10 09:20 | `rep_20261019_gateo_base_r2_fallo` | Fémur 3 r≈0,876; “posible I²C” | r bajo el umbral de gateo/paso 0,90 | Señal de seguimiento débil, no confirmación del bus. |
| 20/10 19:22 | `rep_20261020real_gateo_base_r1_fallo` | Fémur 1 r≈−0,394; “posible I²C” | RMSE≈9,78° y r negativo; C0 máximo 44 cuentas | Respuesta medida muy discordante en esa corrida; requiere inspección del sensor/cableado, configuración y clip. |
| 20/10 10:56 | `rep_20261020_paso_ppo_r1_fallo_disco` | Fallo de disco | No hay diagnóstico JSON | No puede evaluarse el comportamiento con las métricas disponibles. |
| 21/10 19:34 | `rep_ciclo2_trote_ppo1_r2_fallo` | Fémur 2 r≈0,750; posible I²C | Fémur 2/3/4 r≈0,75/0,76/0,73; p99=48 ms; 448 intervalos >40 ms | Seguimiento bajo en tres fémures y temporización irregular. El video visual por pares no permite aislar el fémur 2. |
| 21/10 19:51 | `rep_ciclo2_trote_ppo1_r2_fallo_degradado` | Fémures 2–4 r≈0,7 | r≈0,705/0,710/0,682; p99=54 ms; 714 intervalos >40 ms; C0 máximo 199 cuentas | Evidencia más fuerte de degradación de seguimiento en ese ensayo, no prueba única de causa. |

Los informes con tablas por cámara de las dos corridas PPO1 R2 están en sus carpetas de sesión: [fallo](/home/pavilion/Documentos/Cuadrupedo/Experimentos/camaras/grabaciones/rep_ciclo2_trote_ppo1_r2_fallo/INFORME_ANALISIS.md) y [degradado](/home/pavilion/Documentos/Cuadrupedo/Experimentos/camaras/grabaciones/rep_ciclo2_trote_ppo1_r2_fallo_degradado/INFORME_ANALISIS.md).

## Grabaciones destacadas del 21/10

- **`comprobacion_trote_2024` (20:24, 60,6 s):** 1.848 muestras, 55 ciclos, mediana/p99 de muestreo 33/33 ms, sin intervalos >40 ms; C0 máximo 108 cuentas. El video dio r≈0,95 y CV≈7% para P2+P3 y r≈0,79/CV≈2% para P1+P4 en HP-PC1; general 0,99/0,98; Windows 0,98/0,96; Logitech no permitió identificar patas. No hubo ciclos estadísticamente anómalos en las cuatro vistas analizadas.
- **`rep_ciclo2_trote_ppo1_r2` (20:27, 180,6 s):** 5.511 muestras, 166 ciclos; mediana/p99/máximo de intervalo 33/41/41 ms y solo 1 intervalo >40 ms. Fémures 1–4: r≈0,988/0,973/0,968/0,964. Tibia 2/ENC_T2 y tibia 4/C10 se evaluaron; tibia 1/ENC_T1 y tibia 3/C11 no fueron evaluables. El video general y Windows mostró r≈0,98–0,99 en ambos pares; HP-PC1 solo identificó P1+P4; Logitech no identificó pares; Windows marcó el ciclo 1 como candidato estadístico.
- **`rep_ciclo2_gateo_base_r2` (20:33, 180,1 s):** 5.489 muestras, 62 ciclos, p99=35 ms y ningún intervalo >40 ms; C0 máximo 98 cuentas. Fémures 1–4: r≈0,992/0,980/0,965/0,979. Tibia 2 y 4 evaluables; tibias 1/ENC_T1 y 3/C11 sin realimentación. El video Windows detectó las cuatro patas con r≈0,95–0,98 y sin anomalías; HP-PC1 marcó ciclos 1–3, general no identificó P3, y Logitech mostró las cuatro patas con r≈0,87–0,93 sin anomalías. Los mínimos por ciclo bajan más que el promedio (por ejemplo fémur 3 r mínimo≈0,691 y tibia 4≈0,540), por lo que vale la pena revisar esos ciclos aunque la media de la corrida sea alta.
- **Pruebas de color e identificación:** 11 sesiones `calib_colores...` y tres `identificar_patas...`; el analizador produjo resultados visuales pero no hay diagnóstico de marcha. Son útiles para validar visibilidad/color, no para juzgar el rendimiento locomotor.
- **`prueba_5camaras_20261021`:** tiene análisis visual, no diagnóstico de sensores; se cuenta como prueba de adquisición, no como repetición completa de marcha.

## Cierre de la grabación más reciente

`rep_ciclo2_gateo_base_r2` inició a las **20:33:38 del 21/10**, con configuración gateo, apertura de 8°, fémur 15° y tibia 10°. Se incluyó su telemetría y las cuatro vistas disponibles (HP-PC1, general, Logitech y Windows) en los totales finales de hoy. La vista Windows no marcó anomalías; los ciclos 1–3 de HP-PC1 quedan como candidatos visuales a revisar, no como fallas confirmadas.

## Conclusiones y próximos pasos recomendados

1. **Priorizar el problema de realimentación de tibias.** ENC_T1 queda sin datos válidos en todas las sesiones diagnosticadas; C11, asignado a tibia 3 en los informes, aparece sin sensor en 24 diagnósticos de hoy. Revisar cableado, alimentación, dirección/conexión del encoder y la asignación sensor–articulación antes de atribuirlo a un bloqueo I²C o a una pata trabada.
2. **Separar “servo se mueve” de “sensor informa”.** Una cámara puede mostrar movimiento mientras `caido` indica que no hay señal de posición. Para tibias no observables eléctricamente, cotejar video sincronizado y, si hace falta, una prueba de rango controlada.
3. **Reducir jitter del registro/control.** En el día 21 se dispararon los intervalos >40 ms. Repetir algunas corridas con cámaras/comprensión detenidas o carga fija, y guardar timestamps, CPU y errores de bus para distinguir latencia de hardware de carga de procesamiento.
4. **Mejorar cobertura temporal de video.** Revisar por qué el celular quedó en 7,5 fps el 20 y por qué cámara general promedió 19,6 fps con huecos el 21. Mantener un mapeo fijo cámara física ↔ etiqueta de archivo y usar un patrón de sincronización común.
5. **No comparar políticas mezclando configuraciones.** Mantener marcha, amplitudes, política, duración, suelo, batería y calentamiento constantes; alternar el orden de las condiciones como indica el protocolo del proyecto.
6. **Revisar manualmente los clips marcados.** En particular, los fémures 2–4 de los trotes degradados y los ciclos visuales anómalos. Ver el patrón temporal completo y comparar contra CSV; no usar un único ciclo o correlación para declarar falla.
7. **Archivar la sesión gateo iniciada a las 20:33** con su diagnóstico y las cuatro figuras visuales, y revisar los ciclos candidatos de HP-PC1 contra el CSV.

## Límites del informe

Este análisis es un resumen del material local disponible en los JSON/CSV y carpetas de sesión al corte indicado. No se volvieron a procesar todos los videos antiguos: para las corridas que ya no conservan video se usaron sus resultados `video_analisis.json` existentes; para los dos trotes PPO1 R2, la comprobación de trote y el último gateo de hoy se revisaron las salidas presentes. Las 14 calibraciones/identificaciones no se incluyen como pasos de marcha. No se infiere fuerza, desplazamiento físico, estabilidad en el piso, falla de hardware ni causa I²C solamente a partir de r/correlación.
