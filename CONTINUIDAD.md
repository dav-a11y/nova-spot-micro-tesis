# Continuidad histórica de la tesis Nova Spot Micro

Última actualización: 14 de octubre de 2026, America/Bogota.


## Objetivos vigentes — corrección del usuario del 7 de septiembre de 2026

Rigen el objetivo general y los cuatro objetivos específicos suministrados
literalmente por el usuario: OE1 hardware/software; OE2 modelado cinemático y
dinámico; OE3 control aprendido con estabilidad y continuidad en paso/gateo;
OE4 evaluación mediante margen estático, seguimiento articular y repetibilidad.
La clasificación histórica de cinco objetivos queda como antecedente y no debe
reutilizarse en documentos vigentes. Texto fuente: `Documento_TESIS/Chapters/3 Objetivos.tex`.

## Repositorio público de seguimiento

Desde el 19 de agosto de 2026 el proyecto tiene un repositorio público para
que el profesor pueda revisar el progreso semanal, la ruta de trabajo, la
bitácora, el código y las evidencias:

- Repositorio: <https://github.com/davidediaz/nova-spot-micro-tesis>
- Panel web: <https://davidediaz.github.io/nova-spot-micro-tesis/>
- Bitácora visual: `Github/BITACORA.html`
- Cronograma semanal: `Github/CRONOGRAMA_SEMANAL.md`
- Ruta completa: `Github/RUTA_TRABAJO.md`

Regla permanente de trazabilidad: cada cambio relevante del proyecto debe
quedar registrado en este archivo y en el repositorio público mediante un
commit descriptivo. La actualización debe indicar fecha, archivos modificados,
motivo, pruebas o evidencia, resultado y siguiente acción. No se deben
reescribir silenciosamente resultados históricos ni mezclar bolsas producidas
con configuraciones diferentes.

Regla permanente de integración con la tesis, acordada el 1 de septiembre de
2026: después de cada avance se debe comprobar qué objetivo atiende, qué prueba
se ejecutó, cuál fue el criterio de aceptación y si realmente se cumplió. Los
resultados válidos se incorporarán también a `Documento_TESIS` con método,
configuración, datos, gráfica o tabla, interpretación y limitaciones; después se
recompilará y revisará el PDF. Los ensayos fallidos o inconclusos conservarán su
trazabilidad, pero no se presentarán como cumplimiento. Un resultado negativo
podrá incluirse cuando sustente una decisión técnica o una limitación.

Regla de trabajo colaborativo: cada cambio realizado por cualquiera de los
integrantes debe notificarse en GitHub mediante un commit descriptivo y quedar
subido al repositorio público. La notificación debe identificar qué se cambió,
por qué, qué pruebas o evidencia se obtuvieron y cuál es la siguiente acción.
Los cambios se compartirán preferiblemente mediante ramas y Pull Requests;
`main` debe conservar únicamente cambios trazables y revisados.

### Inicio del documento final de tesis — 1 de septiembre de 2026

Se creó `Documento_TESIS` como espacio independiente para construir la entrega
final sin sobrescribir ni presentar `tesis_overleaf` como si ya fuera el
resultado definitivo. La nueva redacción describirá trabajo efectivamente
ejecutado mediante expresiones como «se diseñó», «se implementó» o «se
analizó», pero solo cuando exista evidencia; no se cambiará mecánicamente el
futuro del anteproyecto por pasado.

La carpeta contiene una guía inicial, el plan del documento final y la matriz
objetivo--método--evidencia con el estado real de los cinco objetivos. También
se copió `Presentacion_PartiendoCronograma.pdf`, fuente de 31 diapositivas usada
para adoptar la cadena problema--objetivo--método--evidencia--resultado--
conclusión. SHA-256 de la presentación:
`200ed2f5ada680325b5bbbd9efd83e2e906b9bdb65c609715d209c7a88cdc160`.

La primera versión compilable quedó en
`Documento_TESIS/Documento_TESIS_PRELIMINAR.pdf`: 41 páginas en formato A4 y
SHA-256
`71ab44fc869fbb04f8460258a794f24d0e715714607c3aa72acf867bacb84f01`.
La fuente LaTeX reutiliza la plantilla y el contenido válido del anteproyecto,
pero usa `Proyecto de Grado II` e incorpora resumen, abstract, metodología
ejecutada, desarrollo, resultados verificados, discusión, conclusiones
provisionales y trabajo pendiente. Compiló sin citas ni referencias
indefinidas.

Esta versión no es la entrega definitiva: declara explícitamente que la
caracterización física, seguridad eléctrica, calibración, validación en el
robot, entrenamiento RL y comparación final permanecen abiertas. Es la base
documental que se actualizará a medida que se produzca evidencia.

Actualización visual del 1 de septiembre: el PDF preliminar pasó a 48 páginas e
incorporó un diagrama de arquitectura y seis gráficas de ensayos aceptados:
series y reproducibilidad de gateo, series y reproducibilidad de marcha paso,
seguimiento/cadencia de MuJoCo y persistencia del contacto crudo. El nuevo
SHA-256 del PDF es
`dde27238bab109c669241fadf5fc59f1dd4afdb12fac303e9ea8bb6076114589`.
`Documento_TESIS/INDICE_EVIDENCIAS_VISUALES.md` relaciona cada figura con sus
datos, significado y limitación. Las figuras nuevas de contacto y MuJoCo son
regenerables mediante `Documento_TESIS/generar_figuras_resultados.py`.

Corrección editorial posterior: el diagrama de arquitectura redujo el grosor
de las flechas, eliminó la etiqueta superpuesta `referencias`, amplió los nodos
y fijó saltos de línea para que ningún texto excediera los cuadros. El PDF se
recompiló y la página corregida fue inspeccionada visualmente.

Actualización documental del 15 de septiembre de 2026: se retomó la línea de
tesis leyendo este archivo y `Seguimiento/Seguimiento.md`. Se amplió
`Documento_TESIS/Chapters/1 Introducción.tex` para explicar con claridad la
comparación entre marcha nominal y marcha nominal con corrección aprendida,
acotada y supervisada. La introducción quedó alineada con los cuatro objetivos
vigentes y con las tres pruebas de OE4: margen de estabilidad estática,
seguimiento articular y repetibilidad. También se dejó explícito que las
campañas PPO disponibles constituyen evidencia negativa y no habilitan la
transferencia al prototipo físico. La tesis recompiló correctamente y
`Documento_TESIS/Documento_TESIS_PRELIMINAR.pdf` quedó en 78 páginas.
Siguiente acción: integrar resultados comprobados y depurar el alcance del
modelo dinámico sin declararlo gemelo digital.

### Reentrenamiento PPO extendido de gateo y paso — 25 de septiembre de 2026

Se creó la campaña independiente
`Experimentos/reentrenamiento_ppo_extendido_20260925` para no sobrescribir las
campañas del 24 de septiembre. Se reinstaló el entorno aislado de entrenamiento
con Gymnasium 0.29.1, Stable-Baselines3 2.3.2, PyTorch CPU 2.3.1 y MuJoCo 3.9.0.

Se reentrenaron las dos marchas en MuJoCo con la geometría medida, el contrato
de 27 observaciones y 12 acciones residuales, límite de `±0,08 rad`, cambio
máximo de `0,02 rad` por paso y `hardware_transfer=false`:

- gateo (`crawl`, semilla 53): 200.704 pasos efectivos;
- paso (`step`, semilla 71): 200.704 pasos efectivos.

La evaluación emparejada de cinco episodios por condición mostró más avance con
PPO, pero también mayor inclinación. Gateo pasó de `0,4917 m` nominales a
`1,2860 m` con PPO y de `0,00993` a `0,03505 rad` de inclinación máxima; paso
pasó de `0,0155 m` a `3,5561 m` y de `0,01392` a `0,04289 rad`. Estos resultados
son evidencia de simulación y no aceptación: la recompensa y la inclinación
deben analizarse con más condiciones antes de seleccionar una política.

Se intentó continuar la adaptación en Gazebo con 50.000 pasos por marcha,
inicializando desde estas políticas MuJoCo. La primera corrida de gateo se
detuvo en 500 pasos porque Gazebo opera aproximadamente en tiempo real y el
presupuesto completo requería varias horas; no dejó una política final y no se
usa para conclusiones. No se inició la corrida de paso en Gazebo. El intento,
su traza parcial y la razón de detención quedan conservados en la carpeta de la
campaña. Siguiente acción: ejecutar la adaptación Gazebo en una sesión dedicada
o definir con los directores un entorno acelerado que conserve la dinámica.

Ninguna política se transfirió a la Raspberry Pi, se envió a PWM o se conectó a
servos. El hardware continúa bloqueado hasta cerrar calibración, alimentación,
supervisión y pruebas físicas controladas.

### Reinstalación de la memoria Raspberry Pi — 19 de agosto de 2026

Se borró y reinstaló la memoria USB/microSD de 32 GB identificada de forma
inequívoca como `/dev/sda`, modelo `Storage Device`, 28,9 GiB. El SSD interno
`/dev/nvme0n1` no fue utilizado como destino. Se empleó la imagen oficial
`ubuntu-22.04.5-preinstalled-desktop-arm64+raspi.img.xz`, cuyo SHA-256 fue
`74764944dd4a96bdddd30cf1ffc133ecbe5ebb1d1f2eaa34cd5f8fbb57211c86`.

La escritura terminó con 9.269.411.840 bytes y sincronización completada. La
tabla resultante muestra `system-boot` (512 MiB, FAT) y `writable` (8,1 GiB,
ext4). El script reproducible y protegido por comprobación de modelo, tamaño,
hash y confirmación explícita está en
`Raspberry/reinstalar_ubuntu22_desktop_pi.sh` y en el repositorio público.

Estado: imagen grabada y verificada en el computador. Falta arrancar la
Raspberry y confirmar Ubuntu 22.04, escritorio gráfico, red, SSH y expansión de
la partición `writable`. No conectar ni energizar todavía los servos.

Verificación offline posterior: la partición `writable` contiene
`Ubuntu 22.04.5 LTS (Jammy Jellyfish)`, paquetes `ubuntu-desktop`,
`ubuntu-desktop-minimal`, `ubuntu-standard` y `gnome-shell`, además de sesiones
gráficas Xorg y Wayland. La comprobación confirma la imagen y la interfaz
gráfica instaladas; aún falta el primer arranque físico de la Raspberry para
validar red, SSH y funcionamiento real del escritorio.

Este archivo es la memoria persistente para continuar el proyecto en sesiones
posteriores. Antes de realizar nuevas tareas se debe leer este documento y el
seguimiento operativo ubicado en `Seguimiento/Seguimiento.md`.

## Estado general confirmado

El proyecto se encuentra en:

`/home/pavilion/Documentos/Cuadrupedo`

Workspace ROS 2 principal:

- `src/nova_gait_controller`
- `src/nova_sm3_description`
- `build/`
- `install/`
- `log/`

El robot cuadrúpedo Nova Spot Micro ya camina mediante gateo cartesiano en
Gazebo Sim con ROS 2 Humble. También existen el modelo de MuJoCo, la cinemática
propia, el control articular, el nodo de métricas y el supervisor de seguridad.

La referencia externa de Mike4192 se conserva en:

`referencias/spotMicro_mike4192`

Repositorio de referencia:

`https://github.com/mike4192/spot_micro_kinematics_python`

Se usa como apoyo conceptual; la implementación del proyecto es propia y está
adaptada al modelo NovaSM3.

## Configuración nominal congelada del gateo

Archivo de configuración:

`src/nova_gait_controller/config/gaits.yaml`

Parámetros utilizados en el ensayo de línea base:

- marcha: `gateo` / `crawl`;
- muestras por ciclo: 24;
- longitud de paso: 0,018 m;
- elevación del pie: 0,014 m;
- duración por muestra: 0,18 s;
- duración nominal del ciclo: 4,32 s;
- tópico de órdenes: `/nova/gait_command`;
- tópico de trayectoria: `/joint_trajectory_controller/joint_trajectory`.

SHA-256 del archivo `gaits.yaml` empleado:

`0772d57faab20f8da50176f4e94fc9d885e618211e230c34511c18256a71990a`

## Registro rosbag2 realizado el 14 de agosto de 2026

Se completó el primer registro válido de la línea base en Gazebo:

`Experimentos/rosbag2/linea_base_gateo_limpia_20260814_0925`

Resultados de integridad:

- comienzo de la bolsa: 09:25:40;
- final de la bolsa: 09:28:34;
- duración total: 174,227692248 s;
- ventana continua entre `gateo` y `stand`: 98,978769031 s;
- ciclos ejecutados completos, delimitados cada 24 referencias: 20;
- duración configurada por ciclo: 4,32 s;
- duración observada media por ciclo: 4,797996 s;
- requisito mínimo solicitado: 10 ciclos / 43,2 s;
- mensajes almacenados: 83.442;
- tamaño aproximado: 96,4 MiB;
- muestras de métricas dentro de la ventana válida: 5.813;
- activaciones del supervisor: 0.

No se modificaron paso, elevación ni velocidad durante el ensayo. La diferencia
entre duración configurada y observada se debe a que el temporizador de control
de 20 ms publicó las referencias aproximadamente cada 0,20 s. Los ciclos se
segmentan mediante grupos de 24 referencias registradas y no dividiendo
únicamente el tiempo entre 4,32 s.

Resumen preliminar dentro de la ventana válida:

| Magnitud | Inicio | Final | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| x (m) | -0,001811 | 0,493510 | -0,014817 | 0,493510 |
| y (m) | 0,000000 | 0,005190 | -0,009581 | 0,013473 |
| altura (m) | 0,222356 | 0,224245 | 0,222356 | 0,224272 |
| roll (grados) | 0,000000 | 0,020540 | -2,255451 | 2,255240 |
| pitch (grados) | 0,027241 | 0,015405 | -4,412489 | 0,391404 |

El registro detallado está en:

`Experimentos/rosbag2/linea_base_gateo_limpia_20260814_0925/REGISTRO_ENSAYO.md`

SHA-256 de la base SQLite3 válida:

`d4a7b5dd7780170591537ef560d106ad99a36629164bb091ce0d61573526b772`

### Tópicos registrados

- `/clock`
- `/joint_states`
- `/dynamic_joint_states`
- `/joint_trajectory_controller/controller_state`
- `/joint_trajectory_controller/joint_trajectory`
- `/nova/gait_command`
- `/nova/metrics/diagnostics`
- `/nova/metrics/json`
- `/nova/safety/triggered`
- `/tf`
- `/tf_static`
- `/world/empty/dynamic_pose/info`

`/joint_trajectory_controller/controller_state` no produjo mensajes. El tópico
`/nova/safety/triggered` tuvo cero mensajes porque no hubo activaciones. Las dos
órdenes, `gateo` y `stand`, quedaron almacenadas en la bolsa válida.

La verificación formal de este requisito quedó guardada en
`Experimentos/rosbag2/linea_base_gateo_limpia_20260814_0925/AUDITORIA_TOPICOS.md`.
Se confirmó: 10.232 mensajes de pose 3D, 17.372 estados articulares, 10.231
mensajes de métricas, dos órdenes de marcha y ninguna activación del
supervisor. El punto correspondiente quedó marcado como completado en
`Seguimiento/Seguimiento.md`.

## Incidencia encontrada y corregida

La primera grabación fue:

`Experimentos/rosbag2/linea_base_gateo_20260814_0918`

No debe utilizarse para resultados. Al inspeccionarla se descubrieron dos
instancias simultáneas de `gait_controller`, `nova_metrics`,
`nova_safety_supervisor`, `robot_state_publisher` y `ros_gz_bridge`. Esto
duplicaba mensajes de métricas y pose.

Se detuvo la instancia antigua iniciada a las 07:59, se vació el grafo ROS 2 y
se relanzó `demo.launch.py`. Antes de repetir se confirmó exactamente una
instancia de cada nodo. La primera bolsa se conservó únicamente como evidencia
y contiene `ENSAYO_INVALIDO.md`.

Regla para futuras pruebas: antes de grabar, ejecutar `ros2 node list | sort |
uniq -c` y comprobar que ninguna instancia aparezca duplicada.

## Documentación matemática en LaTeX

El modelado convertido y corregido se encuentra en:

`Documentacion/MODELO_MATEMATICO_LATEX`

Archivos principales:

- `main.tex`: fuente LaTeX editable;
- `main.pdf`: PDF compilado de 11 páginas;
- `README.md`: contenido e instrucciones;
- `compilar.sh`: compilación automatizada.

El documento incorpora ecuaciones nativas de LaTeX para cinemática directa e
inversa, transformaciones homogéneas, Jacobiano, singularidades, dinámica,
actuadores, contacto, estabilidad, trayectorias, marcha, identificación,
validación e incertidumbre.

## Seguimiento operativo

La lista completa de trabajo pendiente se mantiene en:

`Seguimiento/Seguimiento.md`

Los puntos de grabación, tópicos, análisis automático y repetición independiente
ya están completados. La primera fase de línea base en Gazebo queda cerrada.

## Análisis automático completado

El script reproducible es `Experimentos/analizar_gateo_rosbag.py`. Los
resultados están en
`Experimentos/analisis/linea_base_gateo_limpia_20260814_0925`: CSV por ciclo,
series temporales, resumen gráfico e informe. Se analizaron 20 ciclos completos.
El avance medio fue 0,022908 m/ciclo, la velocidad media 0,004775 m/s y el salto
articular máximo medio 0,018005 rad. El primer ciclo contiene el transitorio de
arranque y debe conservarse y señalarse, no eliminarse silenciosamente.

## Repetición y reproducibilidad completadas

La repetición ya fue completada. La bolsa válida es
`Experimentos/rosbag2/repeticion_gateo_limpia_20260814_0956`, con 36 ciclos
completos, duración observada media de 4,793341 s y cero eventos del supervisor.
La tentativa `repeticion_gateo_20260814_0948` quedó inválida por perder la orden
inicial `gateo`.

La comparación reproducible está en
`Experimentos/comparacion_reproducibilidad_20260814`. Sobre los primeros 20
ciclos equivalentes y usando ciclos 2--20 para las medias, las diferencias entre
ensayos fueron -0,102 % en avance, -0,036 % en velocidad, 0,193 % en excursión
lateral, -0,001 % en altura, -0,000 % en roll y -0,002 % en pitch. Esto respalda
una repetibilidad muy alta en simulación, sin declarar equivalencia estadística
formal con solo dos ejecuciones.

## Próxima acción exacta

Revisar la semántica temporal de los contactos traseros y distinguir un
despegue físico sostenido de la ausencia de mensajes durante el timeout de
0,10 s. El intento acotado de acelerar el ascenso trasero a 0,80 fue rechazado:
solo mejoró el adelanto unos 0,016 s y redujo la coincidencia global. No aumentar
este parámetro porque 0,85 ya excede el límite de 0,20 rad. En paralelo, cerrar
la caracterización física y las decisiones del protocolo con las fichas creadas
el 31 de agosto.

Preparación del 1 de septiembre de 2026: el diagnóstico sincronizado incorpora
ahora `raw_observed_contacts` y `filtered_observed_contacts`, conservando
`observed_contacts` como alias compatible del estado filtrado. El analizador de
bolsas distingue ambos estados, informa su coincidencia por separado y sigue
aceptando las bolsas históricas que no contienen el campo crudo. Pasaron 49
pruebas y se reprodujo sin cambio numérico el resultado histórico de la bolsa
del 31 de agosto (23,643955 %). La próxima acción sigue siendo grabar una bolsa
nueva de al menos diez ciclos para cuantificar el efecto real del timeout y el
debounce; esta preparación no valida todavía sus valores provisionales.

Ensayo completado el 1 de septiembre de 2026: la bolsa válida
`contactos_debounce_nominal_valido_20260901_0828` contiene 24 ciclos completos,
105,522328 s entre marcadores, 79.790 mensajes y cero eventos del supervisor.
La coincidencia simultánea fue 20,638810 % para el estado crudo y 13,621271 %
para el filtrado. FL/FR presentaron pérdidas crudas cercanas a 0,94 s; RL/RR
solo interrupciones de 0,074645/0,073803 s de media y máximos menores de 0,09 s.
Ningún episodio trasero superó los 0,12 s exigidos para confirmar vuelo.

Conclusión vigente: las transiciones traseras observadas anteriormente eran
interrupciones breves asociadas a la semántica timeout/recontacto y no evidencia
de despegue físico sostenido. El gateo avanzó 0,023558 m/ciclo a 0,005453 m/s,
pero el patrón físico todavía no coincide con el plan FL--RR--FR--RL. La
redacción preparada para la tesis está en
`Documentacion/RESULTADOS_CONTACTO_CRUDO_FILTRADO_2026-09-01.md`. La tentativa
`contactos_debounce_nominal_20260901_0823` es inválida por no contener fases y
se conserva únicamente para trazabilidad.

## Preparación reciente de la Raspberry Pi

El 18 de agosto de 2026 se verificó una Raspberry Pi con arquitectura `arm64`,
usuario `pavilion` y dos interfaces de red activas:

- Ethernet `eth0`: `192.168.0.132/24`;
- Wi-Fi `wlan0`: `192.168.0.134/24`.

El servicio SSH fue instalado, habilitado al arranque y verificado escuchando en
el puerto 22. El sistema encontrado fue Ubuntu 24.04.4 LTS (`noble`) y no tenía
ROS 2 instalado. Esta instalación se descartó para el proyecto porque el
computador de Gazebo, los paquetes existentes y los scripts preparatorios usan
ROS 2 Humble sobre Ubuntu 22.04.

Decisión operativa: reinstalar en la unidad de la Raspberry Ubuntu Desktop
22.04 LTS ARM64, con interfaz gráfica, habilitar SSH y después ejecutar
`scripts/preparar_raspberry_pi_ros2.sh`. Antes de grabar la imagen se debe
identificar inequívocamente la unidad extraíble conectada al computador y
confirmar el destino; no se debe sobrescribir ningún disco basándose solo en
una letra o nombre supuesto. No conectar ni energizar todavía los servos.

El 19 de agosto de 2026 se identificó la unidad extraíble como `/dev/sda`, USB
de 28,9 GiB con modelo `Storage Device` y serie `150101v01`; el sistema del
computador se confirmó separado en `/dev/nvme0n1`. Se descargó la imagen oficial
`ubuntu-22.04.5-preinstalled-desktop-arm64+raspi.img.xz`. Su SHA-256 calculado,
`74764944dd4a96bdddd30cf1ffc133ecbe5ebb1d1f2eaa34cd5f8fbb57211c86`,
coincidió con el listado de Canonical. La imagen Desktop se grabó en `/dev/sda`:
9.269.411.840 bytes, salida cero y sincronización completada. La tabla resultante
mostró `system-boot` (512 MiB, FAT) y `writable` (8,1 GiB, ext4). Falta arrancar
la Raspberry y confirmar Ubuntu 22.04, la interfaz gráfica, red y SSH; por ello
la instalación todavía no se considera validada.

## Temporizador corregido: nueva versión experimental

El 14 de agosto de 2026 se corrigió `gait_controller.py` para avanzar la fecha
de cada fase desde el vencimiento planificado anterior y no desde la ejecución
tardía del callback. Pasaron 24 pruebas. Una bolsa ligera con 152 referencias y
seis ciclos midió 0,180003383 s por fase y 4,320106573 s por ciclo. El registro
está en `Experimentos/validacion_temporizador_20260814/VALIDACION_TEMPORIZADOR.md`.

Esta modificación no cambia paso ni altura, pero sí corrige la velocidad
ejecutada y constituye una nueva versión. La próxima acción técnica es levantar
una línea base nueva en Gazebo con al menos diez ciclos, analizarla y repetirla;
no se deben mezclar sus resultados con las bolsas anteriores de ciclo cercano a
4,80 s.

### Nueva línea base en Gazebo completada

Se creó `Experimentos/rosbag2/linea_base_cadencia_corregida_20260814_1049` con
13 ciclos completos, 57,014709 s de gateo, 32.352 mensajes y cero activaciones
del supervisor. El ciclo medio observado fue 4,320013 s. En los ciclos 2--13,
el avance medio fue 0,023338 m/ciclo, la velocidad 0,005402 m/s, la excursión
lateral 0,015133 m, el roll máximo 2,233112 grados y el pitch máximo 4,365442
grados. El registro y los hashes están dentro de la bolsa.

La repetición indicada a continuación completó la reproducibilidad de esta nueva
línea base.

### Repetición de la cadencia corregida completada

La bolsa `Experimentos/rosbag2/repeticion_cadencia_corregida_20260814_1100`
contiene 13 ciclos completos, 32.395 mensajes y cero eventos del supervisor.
La comparación en `Experimentos/comparacion_cadencia_corregida_20260814` usa
los 13 ciclos equivalentes y los ciclos 2--13 para las medias. Las diferencias
relativas fueron -0,001 % en duración, 0,194 % en avance, 0,195 % en velocidad,
0,014 % en excursión lateral, -0,000 % en altura, 0,031 % en roll, 0,037 % en
pitch y 0,035 % en salto articular. La nueva versión corregida queda reproducida
con diferencias menores al 0,2 % en todas estas medias.

La fase de línea base corregida y su repetición queda cerrada. La próxima acción
es formalizar con los directores las definiciones experimentales de paso, ciclo,
fallo e intervención antes de diseñar la marcha `paso`.

## Protocolo experimental redactado

Se creó `Documentacion/PROTOCOLO_EXPERIMENTAL_BORRADOR.md`. El borrador define
paso como la oscilación completa de una pata y ciclo de gateo como 24 referencias
con una oscilación por pata, en orden FL--RR--FR--RL. También define ensayo,
ciclo válido, transitorio, fallo, intervención, caída, datos obligatorios,
métricas y criterios provisionales. Propone cinco ensayos de 20 ciclos por
condición y cinco semillas de RL para la comparación final, sujetos a revisión.

Este punto no está cerrado administrativamente: los directores deben aprobar
cantidades, semillas, métrica primaria, umbrales y la declaración de que el
modelo es nominal computable, no un gemelo digital identificado.

## Marcha paso: implementación inicial

Se añadió el comando `paso/step` con generador cartesiano propio. Usa 32
referencias, 0,18 s por referencia, longitud de 0,016 m, elevación de 0,008 m y
transferencia lateral sinusoidal de 0,004 m; el orden es FL--RR--FR--RL. Las 26
pruebas pasan y el paquete fue recompilado. El diseño está en
`Documentacion/MARCHA_PASO_DISENO.md`.

El ensayo `Experimentos/rosbag2/paso_exploratorio_20260814` completó cuatro
ciclos en Gazebo con cero eventos del supervisor, ciclo medio de 5,759993 s,
roll máximo medio de 1,275 grados y pitch máximo medio de 2,497 grados. La
próxima acción técnica es grabar al menos diez ciclos continuos de `paso`,
analizarlos, repetirlos y después validar el patrón en MuJoCo.

### Marcha paso validada

La acción anterior quedó completada. Gazebo ejecutó dos ensayos independientes
de 12 ciclos con cero eventos del supervisor; las diferencias de medias fueron
menores al 0,4 %. En ciclos 2--12, el avance fue 0,022031 m/ciclo, la velocidad
0,003825 m/s, el roll máximo 1,281777 grados y el pitch máximo 2,483731 grados.

MuJoCo headless completó 12 ciclos con duración media de 5,759999 s, error RMS
articular de 0,026232 rad y error máximo de 0,054983 rad. Su adaptador no publica
pose corporal equivalente a Gazebo, así que esta validación cubre cadencia y
articulaciones, no avance o estabilidad corporal. El informe consolidado está
en `Documentacion/MARCHA_PASO_VALIDACION.md`.

La próxima acción técnica recomendada es publicar fase de marcha y patas
previstas en contacto, requisito necesario para incorporar contactos y margen
de estabilidad en línea.

## Fase y contactos previstos publicados

La acción anterior quedó completada. `/nova/gait_phase` publica JSON sincronizado
con cada referencia: modo, muestra, total de muestras, ciclo, pata en oscilación,
contactos previstos y disponibilidad del plan. `crawl` y `step` siguen
FL--RR--FR--RL; `gallop` declara que todavía no dispone de plan formal. Pasaron
29 pruebas y se observó un mensaje ROS 2 real. El contrato está en
`Documentacion/FASE_Y_CONTACTOS_PREVISTOS.md`.

Las bolsas históricas anteriores no contienen este tópico porque preceden la
modificación. Toda bolsa nueva debe grabar `/nova/gait_phase`. La próxima acción
es añadir contactos medidos de los cuatro pies y comparar contacto previsto
frente a contacto observado.

## Contactos medidos de los cuatro pies en Gazebo

La acción anterior quedó completada para Gazebo. El URDF contiene cuatro
sensores de contacto de 100 Hz y conserva las uniones fijas de los pies durante
la conversión a SDF. El puente publica los flujos crudos en
`/nova/contacts/front_left`, `front_right`, `rear_left` y `rear_right`.

El nodo `contact_monitor` consolida las mediciones en `/nova/foot_contacts` y
el proceso independiente `contact_comparator` compara fase prevista frente a
contacto observado en `/nova/contact_diagnostics`. Tras recibir la primera
muestra de cada sensor, la ausencia de mensajes por más de 0,10 s significa
`contact=false`, porque Gazebo deja de publicar al desaparecer la colisión. El
comparador informa apoyos faltantes o inesperados y no activa paradas.

La validación real confirmó cuatro apoyos válidos en `stand`. En `crawl` se
detectó correctamente `rr` como contacto inesperado en una fase que esperaba
`fl`, `fr` y `rl`; en `step` se detectó `rl` como inesperado cuando se esperaban
`fl`, `fr` y `rr`. Esto revela una diferencia temporal entre la ventana discreta
de oscilación y el despegue físico que debe medirse, no ocultarse. Pasaron 32
pruebas y los paquetes compilaron. El diseño y las limitaciones están en
`Documentacion/CONTACTOS_MEDIDOS_GAZEBO.md`.

La próxima acción exacta es grabar al menos diez ciclos de gateo con
`/nova/gait_phase`, `/nova/foot_contacts` y `/nova/contact_diagnostics`, y
calcular retardos de despegue/aterrizaje y porcentaje de coincidencia por pata.
Después se añadirán contactos equivalentes en MuJoCo y el polígono de soporte.

## Ensayo cuantitativo de contactos completado

La acción anterior quedó completada con la bolsa válida
`Experimentos/rosbag2/contactos_gateo_validado_20260814_1410`: 76 ciclos
completos, 329,856750 s entre marcadores, 176.657 mensajes y cero activaciones
del supervisor. Se conservaron cuatro tentativas inválidas que permitieron
detectar y corregir saturación por contactos crudos, omisión de fases y pérdida
de marcadores efímeros.

El agregador y el comparador quedaron separados en dos procesos. La salida se
limita a 100 Hz, usa QoS de profundidad 1 para los contactos crudos y publica un
diagnóstico inmediatamente con cada fase. La prevalidación confirmó las cuatro
combinaciones FL--RR--FR--RL.

El resultado fue 32,550 % de coincidencia simultánea. FL y FR despegaron en
promedio 0,380297 s y 0,381066 s tarde, y aterrizaron 1,364317 s y 1,364194 s
tarde. RL y RR no mostraron transiciones de despegue: permanecieron apoyadas y
deslizaron. La marcha mantuvo ciclo medio de 4,320002 s, avance de 0,022970
m/ciclo y cero eventos del supervisor, pero no cumple el patrón de contactos
supuesto aunque visualmente camine.

Informes:
`Experimentos/analisis/contactos_gateo_validado_20260814_1410/INFORME_CONTACTOS.md`
y
`Experimentos/analisis_movimiento/contactos_gateo_validado_20260814_1410/INFORME_ANALISIS.md`.

La próxima acción técnica es corregir el generador de gateo para producir
despegue real de RL y RR y reducir los retardos delanteros, manteniendo por
ahora el supervisor solo informativo. La nueva trayectoria constituirá otra
versión experimental y deberá repetir el ensayo de contactos.

### Cierre de sesión y trazabilidad de las tentativas

Se conservaron deliberadamente las bolsas descartadas, cada una con su archivo
`ENSAYO_INVALIDO.md`:

- `contactos_gateo_20260814_1323`: saturación por más de 400.000 diagnósticos y
  acumulación de contactos crudos;
- `contactos_gateo_valido_20260814_1350`: el ejecutor atendía solo fases
  alternas;
- `contactos_gateo_final_20260814_1354`: no almacenó órdenes de marcha y aún
  omitía fases;
- `contactos_gateo_definitivo_20260814_1359`: almacenó 23 ciclos y marcadores,
  pero el diagnóstico publicado desde contactos podía omitir estados de fase.

Las correcciones resultantes fueron QoS `best effort` con profundidad 1,
limitación del agregado a 100 Hz, separación de agregador y comparador en dos
procesos, publicación inmediata al recibir fase y marcadores redundantes. La
bolsa aceptada es únicamente `contactos_gateo_validado_20260814_1410`.

El analizador reproducible es `Experimentos/analizar_contactos_rosbag.py`; crea
`transiciones_contacto.csv`, `resumen_por_pata.csv` e
`INFORME_CONTACTOS.md`. Los pares de transición usan una ventana de ±1,8 s para
capturar los aterrizajes delanteros tardíos y los porcentajes se ponderan por
tiempo, no por cantidad de mensajes.

Estado al cerrar: Gazebo y rosbag2 detenidos, robot devuelto a `stand`, 32
pruebas aprobadas, fuentes Python verificadas y ejecutables `contact_monitor` y
`contact_comparator` instalados. El registro detallado con hashes está en
`Experimentos/rosbag2/contactos_gateo_validado_20260814_1410/REGISTRO_ENSAYO.md`.

## Galope relegado a experimento opcional

Se cerró el punto pendiente de alcance: `gallop/galope` se conserva en el
código únicamente como experimento opcional de simulación. El parámetro
`enable_experimental_gallop` vale `false` por defecto; mientras esté desactivado,
el controlador rechaza el comando y conserva el modo actual.

El galope queda excluido de líneas base, comparación nominal frente a RL,
criterios principales de éxito y hardware. Solo puede habilitarse explícitamente
en Gazebo o MuJoCo. Continúa sin plan formal de contactos y publica
`contact_plan_available=false`. La decisión está en
`Documentacion/EXPERIMENTO_GALOPE_OPCIONAL.md` y cuenta con prueba automatizada
del bloqueo y la habilitación explícita.

## Cantidades experimentales y semillas RL fijadas

Se aprobó y adoptó la matriz para la comparación final. Para cada una de las
marchas `gateo` y `marcha paso` se ejecutarán cinco ensayos nominales y cinco
ensayos nominales más RL, con 20 ciclos programados por ensayo. Son 100 ciclos por condición, 200
por marcha y 400 ciclos finales en total.

El ciclo 1 se conserva como transitorio y los ciclos 2--20 describen régimen
permanente. La unidad independiente es el ensayo (`n=5` por condición); los
ciclos no se tratarán como réplicas independientes.

Las semillas de entrenamiento RL quedan congeladas en `11`, `23`, `37`, `53` y
`71`. Los escenarios/semillas de evaluación emparejada serán `101`, `202`,
`303`, `404` y `505`. Se reportarán las cinco políticas; la política final se
seleccionará con validación separada después de aprobar la métrica primaria y
se bloqueará antes de abrir los resultados finales.

Los fallos permanecen contabilizados aunque exista una repetición adicional.
La decisión completa y congelada está en
`Documentacion/DECISION_TAMANO_MUESTRAL_Y_SEMILLAS_RL.md`. Cualquier cambio
posterior deberá registrarse antes de iniciar los ensayos finales.

No se deben mezclar estas bolsas con ensayos producidos después de modificar el
temporizador, el paso, la altura o la velocidad.

## Actualización documental integral del 16 de agosto de 2026

Se sincronizaron con el estado experimental vigente el README principal, el
README del modelo, el protocolo, el seguimiento y la documentación de código,
ROS 2, cinemática, modelado matemático, marcha paso y contactos. Las fuentes
LaTeX dejan de presentar como futuros los nodos de métricas, supervisor, fase y
contactos que ya existen, e incorporan la cadencia corregida, la validación de
la marcha paso y el ensayo cuantitativo de 76 ciclos.

La actualización documental no modifica código de control, configuraciones ni
datos históricos. Tampoco declara resuelta la limitación de contacto: la
próxima acción técnica continúa siendo corregir el gateo y validar una nueva
versión experimental sin mezclarla con las bolsas anteriores.

Tras la actualización, la suite vigente ejecutó 33 pruebas aprobadas y los
cuatro PDF técnicos recompilaron correctamente: explicación del código (6
páginas), cinemática de marcha (5), estado ROS 2 (7) y modelo matemático (11).

### Ampliación del modelo con control discreto

El 16 de agosto de 2026 se amplió
`Documentacion/MODELO_MATEMATICO_LATEX/main.tex` con una explicación paso a
paso equivalente al temario de un curso de control discreto. Se incorporaron
muestreo, transformada Z, discretización, estabilidad, diseño PID y por estados,
observadores, frecuencia, robustez, efectos digitales, control híbrido y su
aplicación explícita a Nova. Se distingue en una tabla lo implementado de lo
propuesto para evitar presentar LQR, Kalman o MPC como funciones existentes.
El PDF resultante compila sin referencias indefinidas y tiene 25 páginas.

### Ejemplos desarrollados y presentación matemática

A petición del usuario, el 16 de agosto de 2026 se volvió a ampliar el modelo
para que no omita sustituciones ni pasos intermedios. Se añadieron cajas de
ejemplo con FK e IK, Jacobiano, condición y fuerza--par, dinámica inversa por
términos, envolvente del MG996R, COM y margen, oscilación discreta, cadencia,
linealización, discretización ZOH, LQR y análisis experimental de contactos y
reproducibilidad. Los valores se generan con
`scripts/generar_ejemplos_modelo.py` usando el código y parámetros del proyecto.
El PDF pasó de 25 a 31 páginas. Las formulaciones nominales continúan claramente
separadas de mediciones físicas todavía pendientes.

Verificación: 33 pruebas aprobadas. SHA-256 del PDF ampliado:
`bf1097e5d8511ea9ec9384c834ffa2a09474ced9ee521b2d6cdd950d209f0b68`.
SHA-256 del generador reproducible:
`d8d879df7d51e6639923908be3f89c3bf5e2778c4a1f5cd5cb17967126755f20`.

### Trazabilidad matemática y diccionario de variables

El 16 de agosto de 2026 se extendió nuevamente
`Documentacion/MODELO_MATEMATICO_LATEX/main.tex` para responder de forma
explícita qué significa cada variable, por qué se necesita, de dónde procede
cada familia matemática y qué resultado de tesis permite obtener. Se añadió
una cadena de trazabilidad teoría--adaptación Nova--código--evidencia, fuentes
base identificadas T01--T11, adaptaciones A01--A12, archivos C01--C12 y
evidencias E01--E09.

El documento contiene ahora tres diccionarios razonados (geometría y
cinemática; dinámica, actuador, contacto y estabilidad; marcha, control
discreto y experimento), cajas de trazabilidad junto a las derivaciones y un
registro final que enlaza todas las ecuaciones numeradas con su método,
variables entregadas, adaptación específica y uso verificable. También fija
un protocolo de siete pasos para cada ejemplo: objetivo, fuente, datos,
hipótesis, sustitución, comprobación e interpretación.

El PDF resultante tiene 39 páginas y compila sin errores, referencias
indefinidas ni desbordamientos. Los valores numéricos siguen siendo
reproducibles con `scripts/generar_ejemplos_modelo.py`; los parámetros de
catálogo y simulación permanecen separados de la identificación física aún
pendiente.

Verificación final: 33 pruebas aprobadas. SHA-256 de `main.tex`:
`a34780eff35a4b87931ac04355b890faa1b0a751be4bef23d697c10be3f05e12`.
SHA-256 de `main.pdf`:
`a146b360da969703f478e4692a037cfd179772a86da09fc74c967bc92a90389c`.
SHA-256 del generador:
`d8d879df7d51e6639923908be3f89c3bf5e2778c4a1f5cd5cb17967126755f20`.

### Punto exacto de reanudación

Este es el cierre vigente de la sesión. El modelo matemático ampliado se
considera documentalmente terminado en su versión nominal de 39 páginas. No se
debe volver a la versión anterior de 11, 25 o 31 páginas ni sobrescribir el PDF
sin recompilar y actualizar sus hashes.

Al reanudar, leer primero este archivo y después
`Seguimiento/Seguimiento.md`. La siguiente acción técnica del proyecto no es
añadir más teoría genérica: es corregir el generador de gateo para conseguir
despegue real de RL y RR y reducir los retardos de FL y FR; posteriormente se
debe grabar una bolsa nueva, analizar contactos y compararla sin mezclarla con
`contactos_gateo_validado_20260814_1410`.

En paralelo quedan pendientes la identificación física de geometría, masas,
inercias, fricción y MG996R; la validación de $\dot J$; las gráficas de workspace
y singularidad; contactos e IMU equivalentes en MuJoCo; y la aprobación con los
directores de métricas y umbrales experimentales. LQR, Kalman, MPC y la
corrección RL continúan documentados como diseño propuesto, no como funciones
ya implementadas o validadas en hardware.

### Iteración exploratoria de transferencia de peso (17 de agosto de 2026)

Se modificó el generador cartesiano de gateo para incorporar transferencia
común lateral y longitudinal, manteniendo sin cambios 24 referencias, paso de
0,018 m, elevación máxima de 0,014 m y 0,18 s por referencia. También se hizo
explícito el aterrizaje en la última muestra discreta de cada oscilación y se
añadieron pruebas de continuidad cíclica, altura y secuencia. Pasan 35 pruebas
y el paquete compila.

Tres ejecuciones exploratorias temporales en Gazebo compararon transferencia
longitudinal de 4, 8 y 12 mm. Las traseras pasaron de no despegar a presentar
transiciones medidas, y el despegue delantero mejoró de aproximadamente 0,38 s
a 0,34 s. El mejor porcentaje simultáneo fue 35,787 % con 8 mm (13 ciclos),
frente a 31,974 % con 4 mm y 34,879 % con 12 mm. Sin embargo, RL y RR aún
despegaron unos 1,17--1,19 s tarde: se descargan durante la oscilación delantera
del mismo lado, no en su ventana prevista. No se congela ni valida todavía una
nueva línea base.

El valor candidato queda en 8 mm. La próxima acción exacta es separar dentro de
cada cuarto de ciclo una etapa previa de transferencia de peso y otra de
oscilación, y hacer que `/nova/gait_phase` represente esas subfases. Después se
deben repetir pruebas unitarias y una comparación exploratoria antes de grabar
la bolsa formal de al menos diez ciclos. Las bolsas usadas en esta iteración
están en `/tmp` y no constituyen evidencia permanente.

### Gateo con subfases explícitas (17 de agosto de 2026)

Se completó la separación anterior conservando las 24 muestras y los parámetros
nominales. Cada cuarto usa `transfer_start`, `preload`, `liftoff`, `flight`,
`landing` y `touchdown`. `/nova/gait_phase` añade `planned_leg` y
`gait_subphase`; durante precarga y contacto final `swing_leg=null` y se esperan
cuatro apoyos. La trayectoria y el plan de contactos comparten la misma función
de perfil para evitar divergencias. Pasan 36 pruebas y el paquete compila.

Una ejecución exploratoria temporal de 15 ciclos en Gazebo confirmó todas las
subfases, avance de 0,376516 m, altura de 0,222356--0,224356 m, roll absoluto
máximo de 2,074764 grados, pitch absoluto máximo de 4,103346 grados y cero
eventos del supervisor. Los retardos medios de despegue fueron 0,135193 s (FL),
0,132697 s (FR), 0,137536 s (RL) y 0,140653 s (RR). Esto corrige el defecto de
las traseras, que antes no despegaban o lo hacían 1,17--1,19 s tarde.

El aterrizaje aún requiere ajuste diferenciado: FL y FR contactan unos 0,50 s
tarde, mientras RL y RR lo hacen unos 0,33 s antes de `touchdown`. La
coincidencia simultánea de 20,927 % no es directamente comparable con la
anterior porque el plan ahora exige cuatro apoyos en tres de cada seis muestras.
No se congela todavía la nueva línea base. La próxima acción exacta es ajustar
el descenso/aterrizaje por eje sin degradar los despegues ya corregidos y repetir
la exploración. La bolsa de esta prueba permanece en `/tmp` y no es evidencia
experimental permanente.

### Ajuste exploratorio de aterrizaje por eje (18 de agosto de 2026)

Se parametrizó la altura de la penúltima referencia (`landing`) por eje, sin
alterar paso, elevación máxima, 24 muestras ni cadencia. El contraste seguro
más amplio compatible con el límite de continuidad de 0,20 rad fue 0,20 de la
elevación máxima para FL/FR y 0,80 para RL/RR. En 22 ciclos completos los
despegues se conservaron entre 0,135 y 0,141 s tarde, pero los aterrizajes solo
cambiaron a 0,446 s y 0,455 s tarde delante, y -0,327 s y -0,323 s detrás. La
coincidencia simultánea fue 22,548 %.

El contraste se rechazó por mejora insuficiente y no constituye una nueva
línea base. Los parámetros quedaron disponibles, pero sus valores nominales se
restauraron a 0,70710678, equivalentes al perfil sinusoidal anterior. La bolsa
y el análisis permanecen en `/tmp`; falta el marcador `stand` en la bolsa, por
lo que se analizaron explícitamente como ventana exploratoria abierta. El
analizador admite ahora `--allow-open-window`, mientras su modo normal conserva
la exigencia estricta de ambos marcadores. Pasan 37 pruebas y el paquete
compila.

La próxima acción es rediseñar la forma temporal completa del descenso, no
solo su penúltima muestra, manteniendo continuidad y elevación máxima. Debe
compararse primero en pruebas cartesianas y luego en Gazebo antes de congelar
otra versión.

### Preparación de Thonny y comunicación con Raspberry (19 de agosto de 2026)

Se documentaron `Raspberry/INSTALACION_THONNY.md` y
`Raspberry/PROTOCOLO_COMUNICACION_RASPBERRY.md`. El canal principal será
Ethernet + SSH; ROS 2/DDS usará `ROS_DOMAIN_ID=42` y USB-serial de 3,3 V queda
como respaldo. La instalación de Thonny y la verificación de red, SSH, reloj,
I2C y arquitectura `aarch64` se realizarán después del primer arranque de la
Raspberry. No se conectan ni energizan servos en esta fase.

### Curva continua de descenso por eje (20 de agosto de 2026)

Se reemplazó el tratamiento aislado de la referencia `landing` por una ley
continua de potencia desde el ápice hasta `touchdown`. Los parámetros
`crawl_front_landing_height_ratio` y `crawl_rear_landing_height_ratio`
conservan su significado observable: altura normalizada al 75 % de la
oscilación. Un valor menor adelanta todo el descenso y uno mayor sostiene la
elevación; el ascenso hasta el ápice no cambia para no degradar los despegues.

Con las 24 referencias vigentes y el valor nominal `0.7071067811865476`, las
seis alturas discretas por pata son idénticas a las de la versión anterior
(diferencia máxima numérica de aproximadamente `1.23e-16`). Por tanto, este
cambio todavía no constituye una nueva línea base ni demuestra una mejora de
contactos. Se añadieron dos pruebas para la rama descendente completa y la
independencia del ascenso: pasan 39 pruebas y `nova_gait_controller` compila.

Próxima acción exacta: seleccionar una pequeña matriz de curvas delanteras y
traseras que respete continuidad articular, compararla primero en coordenadas
cartesianas y después en Gazebo. Solo tras medir retardos de aterrizaje sin
degradar los despegues se congelarán parámetros y se grabará una bolsa formal.

### Primer arranque y acceso remoto de la Raspberry Pi 4 (20 de agosto de 2026)

Se confirmó que la placa es una Raspberry Pi 4 Model B, no una Pi 3. Arrancó
correctamente con Ubuntu 22.04.5 LTS Desktop ARM64 (`aarch64`). La dirección
actual por Wi-Fi es `192.168.0.101`; el computador principal y la Raspberry
quedaron en la misma red privada.

El servidor SSH no estaba instalado inicialmente. Se instaló
`openssh-server`, se habilitó con `systemctl enable --now ssh` y se verificó
el acceso remoto desde el computador principal mediante
`ssh pavilion@192.168.0.101`. No se conectaron ni energizaron servos.

La ventana de actualización a Ubuntu 24.04 se canceló deliberadamente para
conservar Jammy y compatibilidad con ROS 2 Humble. El repositorio ROS 2 se
agregó después de corregir un comando de terminal partido; queda pendiente
confirmar con una prueba completa `talker/listener` que DDS se descubre por
Wi-Fi. La salida de `ros2 run demo_nodes_cpp talker` inicialmente indicó que
faltaba `ros-humble-demo-nodes-cpp`, por lo que ese paquete debe instalarse en
la Raspberry y en el computador antes de la prueba final.

Próxima acción de hardware/software: instalar o verificar
`ros-humble-demo-nodes-cpp` en ambos equipos, ejecutar `talker/listener` con
`ROS_DOMAIN_ID=42` y `ROS_LOCALHOST_ONLY=0`, y guardar la evidencia. Después se
clonará y compilará el paquete del proyecto en la Raspberry, todavía sin
actuadores.

### Corrección de compilación en workspace clonado de Raspberry (20 de agosto de 2026)

La primera compilación en la Raspberry falló porque `nova_sm3_description` tenía
`worlds` en `install(DIRECTORY ...)`, pero era una carpeta vacía que Git no
conserva al clonar. El lanzamiento vigente usa el mundo integrado
`empty.sdf`, por lo que se eliminó `worlds` de la lista de instalación. No se
instalaron dependencias adicionales ni se ejecutó ningún launch, controlador o
componente del PCA9685.

La corrección debe publicarse y luego actualizarse en la Raspberry con
`git pull --ff-only`; después se repetirá la compilación de
`nova_sm3_description` y `nova_gait_controller`.

La verificación quedó completada en la Raspberry el 20 de agosto de 2026:
actualizó correctamente al commit `d1e3525`, compiló
`nova_sm3_description` y `nova_gait_controller` sin errores y `ros2 pkg list`
reconoció ambos paquetes. No se ejecutó ningún launch, controlador,
trayectoria, nodo de hardware ni componente del PCA9685.

Próxima acción segura: comprobar desde la Raspberry los nodos de diagnóstico
y parámetros de entorno ROS 2, y preparar el workspace para comunicación con
el PC. La validación de I2C, PWM deshabilitado y hardware continúa pendiente.

La comprobación posterior confirmó que el overlay
`/home/pavilion/nova-spot-micro-tesis/install/setup.bash` existe y carga
correctamente `nova_gait_controller` y `nova_sm3_description`. No se ejecutó
ningún launch, controlador, trayectoria, comando I2C/PWM ni componente físico.

Siguiente acción: documentar el estado de reloj y red, y preparar la prueba de
I2C/PCA9685 solo después de cerrar el esquema eléctrico y las condiciones de
salida deshabilitada.

### Impacto social incorporado en la tesis (20 de agosto de 2026)

Se añadió en `tesis_overleaf/Chapters/4 Justificación.tex` una formulación
breve y prudente del fin social: como proyección, el robot cuadrúpedo podrá
apoyar la inspección remota de zonas peligrosas y reducir la exposición de las
personas a riesgos físicos. El texto aclara que se trata de una línea futura y
que esta tesis establece la locomoción y el control necesarios, sin afirmar una
aplicación desplegada. La fuente compiló en una salida de prueba de 32 páginas;
no se sobrescribió el PDF histórico de la tesis.

La redacción se integró posteriormente en el párrafo final de la justificación
para conservar una argumentación más amplia: investigación universitaria,
formación, avance tecnológico y, como desenlace social futuro, inspección
remota y desplazamiento controlado en lugares peligrosos para reducir la
exposición de las personas a riesgos físicos. La fuente volvió a compilar en
una salida de prueba de 30 páginas.

### PCA9685 detectado por I²C sin potencia de servos (20 de agosto de 2026)

Con los servos desconectados, `V+` sin alimentación y sin LM2596 energizado, la
Raspberry instaló `i2c-tools` y detectó en `i2c-1` las direcciones `0x40` y
`0x70`. `0x40` confirma la presencia del PCA9685; `0x70` corresponde a su
dirección general de llamada. No se ejecutaron launch, PWM, controladores ni
comandos de movimiento.

Este resultado valida el enlace lógico Raspberry--PCA9685, pero no valida aún
la potencia de servos, el LM2596, OE, PWM instrumental ni ningún actuador.
Próxima acción: documentar la prueba de salida deshabilitada y revisar la
fuente, fusible, parada física y tensión medida antes de alimentar `V+`.

### Cierre de sesión: preparación de primera prueba de un servo (20 de agosto de 2026)

La Raspberry Pi 4 y el PCA9685 permanecen comunicados por I²C en `0x40`. La
fuente externa entrega 8 V al LM2596 y el LM2596 entrega aproximadamente 5 V al
rail `V+` del PCA9685. Los servos todavía no están conectados y no se ha
ejecutado PWM, launch, controlador ni trayectoria.

La primera prueba física queda programada para la siguiente sesión con un solo
MG996R en `CH0`, sin carga mecánica y con los demás canales vacíos. Antes de
habilitar `OE` se deben confirmar con multímetro `VCC` de 3,3 V, `V+` de 5,0 V,
`OE` alto, tierra común, fusible/limitación de corriente y parada física
accesible. No se autoriza todavía la prueba de los doce servos ni la ejecución
de marchas.

### Diagrama de cableado Raspberry Pi 4–PCA9685–LM2596 (20 de agosto de 2026)

Se creó el diagrama legible en PDF y SVG
(`Raspberry/DIAGRAMA_CABLEADO_PI4_PCA9685_LM2596.*`). Separa la lógica de 3,3 V
de la Raspberry (VCC, SDA, SCL y GND), la potencia externa de servos (V+ y GND
desde el LM2596) y los canales PWM. Incluye OE en estado deshabilitado,
advertencia contra alimentar servos desde la Raspberry y ajuste del LM2596 con
multímetro antes de conectar carga.

El diagrama es una guía de cableado, no una autorización para energizar. Falta
confirmar con fotografías la variante concreta de la placa PCA9685, el jumper
VCC–V+ y la fuente de entrada del LM2596 antes de conectar cualquier servo.

La fotografía recibida el 20 de agosto confirmó la serigrafía de la placa
PCA9685 V1.2.4.6: header superior de izquierda a derecha `V+`, `VCC`, `SDA`,
`SCL`, `OE`, `GND`; header inferior en orden inverso. El PDF/SVG se actualizó
para mostrar explícitamente `Pin físico 1 → VCC`, `Pin físico 3 → SDA`,
`Pin físico 5 → SCL` y `Pin físico 6 → GND`, manteniendo `V+` y servos sin
conectar durante la fase de prueba.

### Comunicación ROS 2 por Wi-Fi validada (20 de agosto de 2026)

Con el `talker` ejecutándose en la Raspberry Pi 4, el computador principal
ejecutó el `listener` con `ROS_DOMAIN_ID=42` y `ROS_LOCALHOST_ONLY=0`. Se
recibieron consecutivamente los mensajes `Hello World: 378` a `Hello World:
385` durante aproximadamente 8 s. La comunicación DDS por Wi-Fi queda
confirmada; no se conectaron ni energizaron servos.

Siguiente acción: detener los nodos de demostración, clonar el repositorio en
la Raspberry y compilar los paquetes ROS 2 del proyecto sin ejecutar todavía
trayectorias ni nodos de hardware.

### Prueba progresiva Arduino Mega 2560–PCA9685 (24 de agosto de 2026)

En la Raspberry Pi 4 se instaló Arduino IDE 1.8.19 ARM64 y las librerías
`Adafruit PWM Servo Driver Library` y `Adafruit BusIO`. El Arduino Mega 2560 R3
quedó reconocido en `/dev/ttyACM0`, con acceso serial del usuario `pavilion`
mediante `dialout`. El escáner del Mega detectó correctamente el PCA9685 en
`0x40` después de identificar y corregir la inversión física de SDA y SCL.

Se comprobó el movimiento de servos MG996R de forma individual y progresiva.
El sketch vigente mueve simultáneamente `CH5`--`CH10` a 60 Hz, con un barrido
conservador de 1300 a 1700 microsegundos y paso de 5 microsegundos cada 20 ms;
los demás canales quedan en `FULL_OFF`. Los servos usan alimentación externa de
5--6 V y comparten tierra con PCA9685 y Mega; no se alimentan desde el pin de
5 V del Arduino.

La prueba demuestra comunicación I2C y movimiento multicanal, pero todavía no
autoriza posturas ni marchas. La próxima acción es identificar cada articulación
y canal, medir centro, mínimos, máximos y sentido de cada servo, verificar la
fuente bajo carga e instalar parada física por OE con resistencia pull-up. El
detalle reproducible quedó en `Raspberry/AVANCES_PCA9685_2026-08-24.md`.

### Criba cartesiana de curvas de descenso (24 de agosto de 2026)

Se añadió `Experimentos/evaluar_curvas_descenso.py` y se evaluó una matriz de
nueve contrastes más el control nominal sin ejecutar ROS 2 ni Gazebo. Se
mantuvieron congelados 24 muestras, paso de 0,018 m, elevación de 0,014 m,
cadencia de 0,18 s, transferencia lateral de 0,004 m y longitudinal de 0,008 m.

Los seis contrastes que combinan relaciones delanteras 0,20, 0,35 o 0,50 con
relaciones traseras 0,75 u 0,80 son alcanzables, periódicos y conservan un
salto articular menor de 0,20 rad. Los tres casos con 0,85 detrás se descartaron
porque alcanzan 0,203263 rad. La trayectoria nominal mide 0,170014 rad, lo que
confirma que el umbral provisional de 0,05 rad escrito en el protocolo tampoco
lo cumple el control y debe revisarse con los directores.

Los resultados están en
`Experimentos/curvas_descenso_cartesianas_20260824`. Pasan 39 pruebas. La
próxima exploración en Gazebo comparará el nominal con 0,20/0,75, 0,20/0,80 y
0,50/0,75 (delantera/trasera), suficientes para separar el efecto de adelantar
el descenso delantero y sostener el trasero. No se han modificado todavía los
parámetros nominales ni se reclama una mejora física.

### Exploración Gazebo de curvas de descenso (27 de agosto de 2026)

Se compararon nominal, 0,20/0,75, 0,20/0,80 y 0,50/0,75 durante 10--13 ciclos
válidos por condición, con fase, contactos, métricas, órdenes y supervisor. No
hubo activaciones de seguridad. Las coincidencias simultáneas fueron 20,949 %,
23,855 %, 23,721 % y 21,728 %, respectivamente. Los despegues no se degradaron.

`0,20/0,75` queda como candidato provisional porque redujo los aterrizajes
delanteros a 0,436/0,460 s tarde, pero los traseros permanecieron unos 0,32 s
antes. La ventaja sobre 0,20/0,80 fue solo 0,134 puntos porcentuales; por ello
no se congeló una nueva línea base ni se modificó `gaits.yaml`. Informe y CSV:
`Experimentos/exploracion_curvas_descenso_gazebo_20260827`.

### Liberación temprana trasera descartada (31 de agosto de 2026)

Al revisar las transiciones de 0,20/0,75 se observó que RL y RR recuperaban
contacto apenas 0,07--0,08 s después del despegue medido, todavía durante el
ascenso. Se añadió `crawl_rear_liftoff_height_ratio`, que controla la altura
trasera al 25 % de la oscilación sin cambiar el cero ni los 14 mm máximos. El
valor nominal mantiene exactamente el perfil anterior.

La criba `Experimentos/liberacion_trasera_cartesiana_20260831` aceptó hasta
0,80 con salto máximo de 0,189604 rad; 0,85 y superiores excedieron 0,20 rad.
El ensayo válido con 0,20/0,75/0,80 completó 15 ciclos, ciclo medio de 4,32 s,
cero eventos del supervisor y 23,644 % de coincidencia. Los aterrizajes RL/RR
fueron -0,305/-0,309 s: una mejora de solo unos 0,016 s, con coincidencia menor
que el 23,855 % de 0,20/0,75. El candidato queda rechazado y `gaits.yaml`
permanece nominal. La tentativa previa sin fases está marcada como inválida.

También se crearon `Documentacion/FICHA_CARACTERIZACION_FISICA.md` y
`Documentacion/FICHA_APROBACION_PROTOCOLO.md`. Estas tareas vencidas continúan
abiertas porque requieren mediciones reales y decisiones del profesor.

La caracterización física no puede cerrarse todavía porque el robot está
incompleto: falta imprimir y montar la tapa izquierda de fémur
`SM3_Cover_LeftFemur.stl`, tomada del repositorio público de archivos Nova-SM3
de `cguweb-com/Arduino-Projects`. Hasta entonces se aplazan las mediciones y
fotografías definitivas; esto no habilita calibración, postura ni marcha física.

### Taller 2: transición al documento final (31 de agosto de 2026)

Se resolvió el Taller 2 de Proyecto de Grado II mediante una matriz de 14
páginas que audita problema, justificación, cinco objetivos específicos,
alcance, marco y metodología. Relaciona cada objetivo con evidencia disponible,
faltantes, métricas y estado; desarrolla una prueba crítica reproducible para
la marcha nominal y proyecta resultados, conclusiones y acciones inmediatas.

La guía original, la fuente LaTeX, el README y el PDF final están en
`ProyectoII_Clases/31_08_2026`. El documento clasifica OE1--OE3 como parciales y
OE4--OE5 como aún no demostrables; no afirma que RL o el robot físico estén
terminados.

### Sustitución de dos servos y refuerzo de acoples (31 de agosto de 2026)

Se informó la sustitución de dos servomotores por limitaciones físicas y el
refuerzo de los acoples del cuadrúpedo para reducir holguras en las patas. Estas
intervenciones quedan registradas como avance mecánico, no como validación: aún
faltan identificación de articulaciones/canales, referencias de componentes,
fotografías, comparación de holgura, calibración individual y pruebas bajo
carga. Los dos servos nuevos no deben heredar calibraciones anteriores.

La tapa `SM3_Cover_LeftFemur.stl` sigue en impresión. Hasta montar e
inspeccionar el conjunto continúan bloqueadas las mediciones geométricas
definitivas, la actualización URDF/MJCF y las marchas físicas. Detalle:
`Raspberry/INTERVENCION_MECANICA_2026-08-31.md`.

### IMU, contacto robusto, margen y supervisor ampliado (31 de agosto de 2026)

El contacto de Gazebo publica ahora observación cruda y estado filtrado. Una
pérdida debe persistir 0,12 s y un recontacto 0,03 s; esto permite estudiar sin
ocultar las pausas cercanas al timeout de 0,10 s. Se añadió una IMU de 100 Hz en
`/nova/imu` y un mundo propio que carga el sistema IMU de Gazebo.

`stability_monitor` calcula en línea puntos nominales de pie, polígono de
soporte y margen estático en `/nova/stability`; declara explícitamente que el
modelo no está identificado. El supervisor valida trayectorias no finitas o
fuera de límites y ya recibe timeout, discrepancia de contactos y margen. Estas
tres últimas paradas continúan desactivadas hasta pruebas provocadas; no existe
rearme automático.

Pasaron 47 pruebas. Gazebo produjo mensajes reales de IMU, contacto y margen, y
unos tres ciclos cortos terminaron en `stand` sin eventos del supervisor.
Documento: `Documentacion/ESTABILIDAD_IMU_SUPERVISOR_GAZEBO.md`.

### Propuesta de instrumentación física para realimentación (31 de agosto de 2026)

Se definió preliminarmente una arquitectura para observar el comportamiento
real del cuadrúpedo: doce AS5600, dos multiplexores I2C TCA9548A, la BNO055 ya
contemplada, cuatro contactos de pie y un monitor de potencia INA228. Los
sensores ToF y la medición de temperatura quedan para etapas posteriores. Esta
selección busca medir ángulo y error articular, movimiento corporal, contacto,
consumo y fallos mecánicos, y después alimentar una capa correctiva de
aprendizaje por refuerzo con variables físicas sincronizadas.

La arquitectura es una propuesta técnica: no se han confirmado las variantes
de las tarjetas, comprado componentes, fabricado soportes, conectado el bus ni
realizado calibraciones. Antes de extenderla a las doce articulaciones se hará
un prototipo con un solo AS5600 sobre el eje real de salida y luego una pata
completa. Deben validarse alineación del imán, niveles de 3,3 V, `pull-up`,
ruido de servos, latencia y frecuencia del barrido secuencial. Las futuras
acciones aprendidas permanecerán limitadas a correcciones pequeñas de la
marcha nominal, nunca PWM directo. Documento completo:
`Documentacion/PROPUESTA_INSTRUMENTACION_FISICA_2026-08-31.md`.

### Modelo matemático incorporado al documento final (1 de septiembre de 2026)

Se migró al documento de tesis el modelo matemático que ya estaba implementado
y verificado en el proyecto. El nuevo capítulo 7 presenta las hipótesis y la
convención REP-103, transformaciones homogéneas, cinemática directa e inversa,
jacobiano, singularidades, dinámica nominal, envolvente del MG996R, contacto
unilateral, fricción, centro de masa y margen estático. También relaciona cada
componente con su implementación y evidencia de verificación.

La suite completa conserva 50 pruebas aprobadas. La revisión visual confirmó
que las siete páginas nuevas, sus ecuaciones y la tabla de trazabilidad no se
salen de los márgenes. El PDF preliminar quedó en 54 páginas, con SHA-256
`439b23c88dfb47395971494e6d05746e3a2218edcc68db397e79174ebaa89d94`.

Este avance eleva OE1 a parcial avanzado en modelado y verificación
computacional. No lo cierra: el modelo permanece nominal hasta medir geometría,
masas, límites, holguras y respuesta de los actuadores del ejemplar físico, y
contrastar esas mediciones con URDF, MJCF y ecuaciones.

### Paquete de caracterización física preparado (1 de septiembre de 2026)

Se preparó `Documentacion/PROTOCOLO_CARACTERIZACION_FISICA.md` para medir el
ejemplar de forma trazable y segura. El procedimiento separa la inspección sin
energizar de la calibración posterior, condicionada a aprobar alimentación y
parada física por OE. Define mediciones entre ejes, tres repeticiones, control
por resolución instrumental, evidencia fotográfica y criterio de aceptación.

Se crearon `Documentacion/caracterizacion_fisica_geometria.csv` con 21
magnitudes y `Documentacion/caracterizacion_fisica_masas.csv` con seis
conjuntos. Sus referencias nominales provienen del URDF y del modelo vigente;
las columnas medidas permanecen vacías deliberadamente. La ficha física añadió
la confirmación por trazado de CH0--CH11 y la identificación de los dos servos
sustituidos. Los CSV se comprobaron estructuralmente junto con la hoja existente
de doce servos. La suite actual completa terminó con 68 pruebas aprobadas.

La metodología de caracterización quedó incorporada en el capítulo 9 de la
tesis. El PDF conserva 54 páginas, fue revisado visualmente y tiene SHA-256
`0ec8efe9f18d3a4fcfd8837118f6c1d349a6940adb75c489d512a494a7a4b59e`.
Este avance prepara la medición, pero no genera resultados físicos ni cierra
OE1.

### Seguridad, sensibilidad y contrato RL sin hardware (1 de septiembre de 2026)

El supervisor pasó a rechazar poses no finitas y se extrajeron funciones puras
para comprobar datos vencidos, discrepancias de contacto y márgenes negativos o
no finitos. Las pruebas provocadas unitarias quedaron documentadas; las tres
paradas informativas siguen desactivadas hasta ensayos integrados en Gazebo.

La criba reproducible `Experimentos/analizar_sensibilidad_nominal.py` evaluó 14
combinaciones. Cambiar las masas ±10 % modificó el par máximo cerca de ±9 % y
cambiar la fricción articular ±50 % lo modificó cerca de ±4,7 %. También se
implementó el contrato de una corrección RL residual: ±0,08 rad, cambio máximo
de 0,02 rad por paso, límites articulares y terminaciones seguras. La suite
completa alcanzó 82 pruebas. No existe todavía una política entrenada y, por
tanto, no procede la comparación nominal--RL. El PDF actualizado quedó en 56
páginas con SHA-256
`e86068c2d10b61bc964c20b514c8eabfd16004ba5a177373597c3af8799cf8a5`.

### Cierre de gateo, repetición 1 de 5 (1 de septiembre de 2026)

Se ejecutó una instancia nueva de Gazebo y se grabaron 29 ciclos completos de
gateo nominal. La cadencia media fue 4,319985 s, el avance 0,023658 m/ciclo y no
hubo activaciones del supervisor. La prueba reprodujo la limitación conocida:
RL y RR solo perdieron contacto hasta 0,080615/0,088292 s, por debajo de 0,12 s.
La bolsa local contiene 101.370 mensajes; informe, CSV, gráficas y registro están
en las carpetas `cierre_gateo_r1_20260901`. Cuenta como repetición 1 de 5.

La repetición 2 se intentó el mismo día, pero quedó inválida: el comando se
publicó antes de la activación completa del controlador, la bolsa registró cero
fases y una sola trayectoria. Se conserva con `ENSAYO_INVALIDO.md` y no se
incorpora a métricas. El procedimiento se ajustó para verificar nodos y
suscriptores antes de iniciar cada repetición.

Se repitió el intento como `cierre_gateo_r2b_20260901`; aunque hubo fases y
trayectorias, la bolsa registró cero órdenes `/nova/gait_command`, por lo que
no pudo delimitarse la ventana y se marcó inválido. El procedimiento se ajustó
para verificar explícitamente los suscriptores del grabador antes de publicar.

El tercer intento se ejecutó con una instancia única y dos suscriptores
confirmados en `/nova/gait_command` (grabador y controlador). Fue válido: 50
ciclos de gateo, 4,319977 s/ciclo, 0,023899 m/ciclo, cero activaciones y
141.531 mensajes. Se capturaron tres `gateo` y una `stand`; la bolsa y sus
análisis están en `cierre_gateo_r3_20260901`. Cuenta como repetición 2 válida de
5. Las pérdidas traseras siguieron por debajo de 0,12 s.

La repetición `cierre_gateo_r6_20260901` fue válida: se capturaron tres
`gateo` y dos `stand`, con 36 ciclos completos, cadencia 4,320000 s/ciclo,
avance 0,023850 m/ciclo, 129.717 mensajes y cero activaciones del supervisor.
Cuenta como repetición 4 válida de 5; los análisis y el registro quedaron
versionados y las pérdidas traseras siguieron por debajo de 0,12 s.

Con `cierre_gateo_r7_20260901` se completó la quinta repetición válida: 29
ciclos, 4,320002 s/ciclo, 0,023824 m/ciclo, 101.130 mensajes, cuatro órdenes
capturadas y cero activaciones. La campaña consolidó 191 ciclos de régimen
permanente de `r1`, `r3`, `r4`, `r6` y `r7`: avance medio 0,023955 m/ciclo,
desviación 0,000621 m, velocidad 0,005545 m/s, roll máximo 2,074196° y pitch
máximo 4,099865°. La línea base nominal de gateo queda cerrada en simulación;
las pérdidas traseras continúan sin demostrar vuelo y la validación física
permanece pendiente. El PDF quedó en 57 páginas con SHA-256
`6f80671deb2f7b67e7d8f8c3cef1f3479f58591b78f92f82b27365b27252a648`.

Se inició la línea base de marcha paso con `cierre_paso_r1_20260901`. La
repetición fue válida para movimiento: 21 ciclos, 5,760859 s/ciclo, 0,021663
m/ciclo, 101.648 mensajes, tres `paso`, dos `stand` y cero activaciones. Roll y
pitch máximos medios: 1,280799° y 2,485997°. El analizador de contactos aún
requiere aceptar marcadores `paso`; no se reportan contactos de esta marcha
hasta adaptar esa herramienta.

Se adaptó `Experimentos/analizar_contactos_rosbag.py` para reconocer los modos
`paso/step` y usar 32 muestras por ciclo, manteniendo `gateo/crawl` con 24. La
regresión sobre gateo r7 pasó y la bolsa `cierre_paso_r1_20260901` produjo 21
ciclos con coincidencia simultánea cruda/filtrada de 39,067/34,787 %. El
análisis de contactos de paso quedó versionado y ya puede utilizarse en las
siguientes repeticiones.

Se ejecutó `Experimentos/evaluar_velocidades_nominales.py` con factores 1,0×,
1,25× y 1,5×. Las referencias de gateo y paso permanecieron alcanzables; la
velocidad articular máxima llegó a 1,525 y 0,609 rad/s, respectivamente, sin
cambiar el salto articular. La criba es cinemática y no demuestra estabilidad
dinámica; los factores mayores quedan preparados para pruebas posteriores en
Gazebo. La explicación del alcance de la velocidad nominal se incorporó al
capítulo de resultados de la tesis.

### Ensayos de umbral de velocidad en Gazebo (1,25×, 1,5× y 2,0×)

Se implementó el parámetro reproducible `speed_factor` en el controlador y en
`demo.launch.py`; la geometría permaneció fija y solo se escaló el periodo de
fase. Los tres ensayos de gateo fueron válidos y quedaron en
`Experimentos/rosbag2/velocidad_gateo_{125,150,200}_20260901`, con sus CSV,
gráficas e informes en `Experimentos/resultados_gateo_*`.

Resultados: 1,25× produjo 26 ciclos, 3,456 s/ciclo, 0,023286 m/ciclo y
0,006738 m/s; 1,5× produjo 28 ciclos, 2,880 s/ciclo, 0,022174 m/ciclo y
0,007699 m/s; 2,0× produjo 34 ciclos, 2,158 s/ciclo, 0,022160 m/ciclo y
0,010266 m/s. No hubo activaciones del supervisor. La coincidencia simultánea
filtrada de las cuatro patas cayó a 9,91 %, 6,75 % y 1,10 %, y el salto
articular máximo medio fue 0,021762, 0,023257 y 0,025527 rad, respectivamente.
La evidencia sugiere 1,25× como candidato rápido conservador; 1,5× queda para
validación adicional y 2,0× como condición de estrés, no recomendada para
operación nominal. Los informes no constituyen validación física.

### Segunda repetición nominal de marcha paso (1 de septiembre de 2026)

Se cerró la segunda repetición independiente de `paso` en Gazebo. La bolsa
`Experimentos/rosbag2/cierre_paso_r2_20260901` contiene 22 ciclos válidos, con
período medio 5,760001 s, avance 0,021670 m/ciclo, velocidad 0,003762 m/s,
roll máximo 1,280899°, pitch máximo 2,486195°, salto articular máximo medio
0,008411 rad y cero activaciones del supervisor. La coincidencia simultánea
filtrada fue 34,631 %. Los CSV, gráficas e informes están en
`Experimentos/resultados_paso_r2_20260901`; junto con `cierre_paso_r1` permite
comparar dos repeticiones, sin confundir ciclos con réplicas independientes.
Se ejecutó además el primer ensayo de velocidad incrementada de marcha paso,
`velocidad_paso_125_20260901`. Fue válido: 25 ciclos, 4,607986 s/ciclo,
0,021302 m/ciclo, 0,004623 m/s, roll máximo 1,259694°, pitch máximo 2,456898°,
salto articular máximo medio 0,009755 rad y cero activaciones. La coincidencia
simultánea filtrada fue 31,999 %. Sus análisis están en
`Experimentos/resultados_paso_125_20260901`. La postura se conserva, pero la
coordinación disminuye moderadamente frente a nominal; queda pendiente
contrastar con 1,5×.
Se completó el escalón de marcha paso a 1,5× (`velocidad_paso_150_20260901`):
26 ciclos válidos, 3,840720 s/ciclo, 0,020921 m/ciclo, 0,005448 m/s, roll
máximo 1,233465°, pitch máximo 2,416679°, salto articular máximo medio
0,010987 rad y cero activaciones. La coincidencia filtrada fue 29,110 %. Los
informes están en `Experimentos/resultados_paso_150_20260901`; 1,25× conserva
mejor compromiso entre rapidez y coordinación.
Se demostró en integración la parada preventiva del supervisor ante una
trayectoria inválida. Tres mensajes con `bad_joint` fueron rechazados por el
controlador; el supervisor registró `nombres_articulares_invalidos` y
`articulacion_desconocida`, publicó la parada y el controlador pasó a `stand`.
El informe reproducible quedó en
`Experimentos/prueba_supervisor_referencia_invalida_20260901`. Las paradas por
datos vencidos, contacto y margen continúan pendientes.
Se intentó provocar una parada por margen de estabilidad habilitando
`enable_stability_stop` en el lanzamiento y publicando un margen negativo. El
intento quedó no concluyente: el monitor nominal publica continuamente en el
mismo tópico y sobrescribe el estímulo antes de que pueda atribuirse una
activación al mensaje provocado. No se incorpora como resultado; el siguiente
protocolo deberá aislar el diagnóstico o usar un tópico de prueba dedicado.
Se aisló el tópico de estabilidad mediante `stability_topic` y se añadió
`startup_grace_period` configurable para repetir la prueba provocada. Aun con
el tópico aislado y gracia cero, el estímulo publicado no generó una activación
observable del watchdog; se conserva como intento no concluyente y no como
resultado. La parada por referencia inválida sigue siendo la única parada
integrada demostrada. El siguiente diagnóstico deberá instrumentar directamente
el callback o usar un nodo de prueba dedicado con reloj controlado.
Se cerró la criba cartesiana de liberación trasera en
`Experimentos/liberacion_trasera_cartesiana_20260901`. Las relaciones 0,707,
0,75 y 0,80 cumplieron el límite de salto articular (<0,20 rad), mientras
0,85--1,00 lo excedieron y fueron descartadas. Es una selección cinemática,
no una demostración de despegue; los tres candidatos deben compararse en
Gazebo contra la configuración nominal.
Se validó en Gazebo el candidato de liberación trasera 0,80
(`liberacion_gateo_080_20260901`): 18 ciclos, 4,320025 s/ciclo, 0,023597
m/ciclo, 0,005462 m/s, salto articular máximo medio 0,020331 rad y cero
activaciones. La coincidencia filtrada fue 13,458 %, superior a la referencia
nominal comparable, pero no demuestra vuelo trasero sostenido. El candidato
0,75 queda pendiente.
Se validó el candidato 0,75 en Gazebo (`liberacion_gateo_075_20260901`): 18
ciclos, 4,319997 s/ciclo, 0,023685 m/ciclo, 0,005483 m/s, salto articular
máximo medio 0,019653 rad, cero activaciones y coincidencia filtrada 13,404 %.
El resultado es prácticamente igual a 0,80 (13,458 %); se conserva 0,80 por
su mayor margen cinemático y no se demuestra vuelo trasero sostenido.
Se generó `Experimentos/comparacion_contactos_liberacion_20260901.md`, que
compara nominal r7, 0,75 y 0,80 con la misma herramienta. Los retardos
delanteros permanecen alrededor de 0,26 s/0,54 s y las traseras no aportan
pares de despegue válidos; la limitación de contacto trasero sigue abierta.
También se fijó `Experimentos/PROTOCOLO_PPO_RESIDUAL.md`; no existe todavía una
política PPO entrenada ni comparación nominal--PPO.
Se consolidó la matriz de estado de los cinco puntos de la ruta en
`Experimentos/CIERRE_RUTA_5_PUNTOS_20260901.md`. La comparación de contactos y
la selección provisional de 0,80 están completadas; el supervisor aún requiere
un nodo de prueba aislado para margen/contacto/datos, PPO está preparado pero no
entrenado y la caracterización física depende de acceso y mediciones del robot.
Se construyó `safety_test_node`, un nodo ROS 2 aislado para probar margen,
contacto y vencimiento de datos sin competir con los publicadores nominales.
El protocolo y comandos reproducibles quedaron en
`Experimentos/PROTOCOLO_NODO_PRUEBAS_SEGURIDAD.md`. La compilación y las 84
pruebas automáticas pasan; todavía falta ejecutar cada escenario con el
supervisor y conservar sus JSON como evidencia integrada.
Se añadió al generador la escala `crawl_rear_swing_height_scale` (nominal 1,0)
para buscar despegue trasero y se validó la configuración 0,80/1,25 con 85
pruebas automáticas. El primer ensayo Gazebo de esa trayectoria quedó inválido
porque la bolsa no capturó órdenes `gateo`; se conserva con
`ENSAYO_INVALIDO.md` y no se incorporan métricas. Debe repetirse verificando
suscriptores antes de publicar.
El segundo intento de la trayectoria 0,80/1,25 también quedó inválido: aunque
el controlador ejecutó tres órdenes `gateo` y pasó a `stand`, la bolsa no
conservó el marcador `stand` posterior. Se mantiene sin métricas y se ajustará
el protocolo de cierre verificando el suscriptor del grabador antes de publicar.
La repetición válida `liberacion_gateo_080_altura125_r3_20260901` capturó tres
`gateo` y cinco `stand`: 18 ciclos, 4,319999 s/ciclo, 0,022662 m/ciclo,
0,005246 m/s, coincidencia filtrada 13,639 %, roll 2,627563°, pitch 5,216466°
y salto articular 0,025376 rad. La escala trasera 1,25 no logró separación
concluyente y empeoró la postura; se descarta como configuración recomendada.
Se implementó `crawl_preload_shift_scale` y se ensayó 0,80/1,5 en Gazebo
(`preload_gateo_150_20260901`). Fue válido: 18 ciclos, 4,319985 s/ciclo,
0,023192 m/ciclo, 0,005369 m/s, coincidencia filtrada 14,527 %, roll 2,096164°,
pitch 4,167473° y salto articular 0,019615 rad. La precarga mejoró la
coordinación sin degradar la postura frente a elevar la pata; queda como mejor
candidato de trabajo, sin demostrar aún vuelo trasero sostenido.
El ensayo `preload_gateo_200_20260901` cumplió los criterios de aceptación
definidos: 18 ciclos, 4,320007 s/ciclo, 0,021662 m/ciclo, 0,005014 m/s,
coincidencia filtrada 19,356 %, cero activaciones y vuelos traseros filtrados
en los 18 episodios, con duraciones máximas RL/RR de 0,312/0,320 s (umbral
0,12 s). Roll y pitch (2,156779°/4,261714°) aumentaron menos del 10 % frente a
la línea base. La precarga 2,0 queda como candidato satisfactorio en
simulación, pendiente de repetición independiente y validación física.
La repetición independiente `preload_gateo_200_r2_20260901` fue válida y
confirmó el candidato: 18 ciclos, 4,320014 s/ciclo, 0,021639 m/ciclo,
0,005009 m/s, coincidencia filtrada 19,738 %, vuelos traseros en 18/18
episodios (máximos RL/RR 0,311/0,348 s), roll 2,153787°, pitch 4,261194°,
salto 0,019684 rad y cero activaciones. La configuración queda confirmada en
simulación; la validación física se mantiene pendiente.
Se ejecutó la criba de perturbaciones deterministas de masa, amortiguamiento y
fricción articular (`Experimentos/perturbaciones_nominales_20260902`). Cubrió
14 escenarios; la mayor variación del par máximo fue -8,997 % en paso con masa
-10 %. Se dejó además el protocolo `PROTOCOLO_PERTURBACIONES_GAZEBO.md` para
fricción de suelo, empujes, ruido y retardos. Estas últimas perturbaciones aún
no se ejecutan porque falta un inyector Gazebo reproducible; no se presentan
como estabilidad demostrada.

### Corrección de la referencia nominal y cierre del barrido PPO (2 de septiembre de 2026)

Se reconciliaron los avances PPO que aún no figuraban en esta memoria. Se
entrenaron cinco políticas residuales con semillas 11, 23, 37, 53 y 71, se
conectaron a observaciones de articulaciones, IMU, altura y contactos, y se
evaluaron dinámicamente en Gazebo. La política no se acepta para transferencia:
las escalas positivas ensayadas degradaron avance, velocidad o postura.

El valor nominal publicado inicialmente (0,027761 m/ciclo) estaba contaminado
por `campana_ppo_gazebo_20260902/nominal_03`. Ese ensayo generó siete segmentos
de unos 2,88 s para una marcha paso de 5,76 s y discontinuidades de hasta
±0,318 m; quedó reclasificado como inválido. Con los otros cuatro ensayos, la
referencia corregida es 0,021935 m/ciclo y 0,003808 m/s. La escala 0,00 obtuvo
0,021878 m/ciclo y 0,003798 m/s, diferencias de solo -0,258 % y -0,259 %; por
tanto, reproduce el nominal dentro de la variación y no evidencia un fallo del
bypass.

`Experimentos/comparar_escala_ppo.py` valida ahora la duración de ciclo antes
de construir la referencia. El diagnóstico completo está en
`Experimentos/DIAGNOSTICO_REFERENCIA_PPO_ESCALA_CERO_20260902.md`. Ninguna
escala positiva queda aceptada y PPO no debe pasar al prototipo. La siguiente
acción técnica es repetir una campaña verdaderamente emparejada de cinco
ensayos por condición y 20 ciclos, con auditoría previa de instancia única,
solo después de redefinir o reentrenar la política; antes tiene prioridad la
caracterización y seguridad física pendientes.

La tesis preliminar se recompiló tras corregir las cifras y el carácter
descriptivo no emparejado de la comparación. El PDF tiene 65 páginas y SHA-256
`79d00a6f77a315d5bdea3bfc76151098abc9eb1a984290dd852af89c6d706102`.

### Gráficas cinemáticas completadas (2 de septiembre de 2026)

Se corrigió y amplió `Experimentos/generar_graficas_cinematica.py`. La versión
anterior asignaba erróneamente 5,76 s al ciclo de gateo y su CSV solo conservaba
esa marcha. El generador usa ahora 4,32 s para gateo y 5,76 s para paso,
registra las 12 velocidades articulares de ambas marchas e incluye el cierre
cíclico.

La exploración uniforme contiene 52.111 configuraciones dentro de los límites
del URDF. El 11,600 % cumple el umbral exploratorio
`sigma_min < 0,005 m/rad` y el 5,889 % tiene `kappa > 100`; la postura nominal
queda en `sigma_min=0,038037 m/rad` y `kappa=6,647045`. Las velocidades máximas
de referencia son 0,944520 rad/s para gateo y 0,372327 rad/s para paso. Estos
resultados no incluyen autocolisión ni sustituyen límites físicos calibrados.
Figuras, CSV e informe regenerable están en
`Documento_TESIS/Figures/Resultados`.

La suite completa conserva 86 pruebas aprobadas. La tesis recompilada mantiene
65 páginas y SHA-256
`83aa51c737ac1b7deb5cf6c0958a64abbb36faf710a96a608a32edecb2305d85`.
El modelo matemático mantiene 39 páginas y SHA-256
`815747309da532d4c01ef9ccb96a8eaf3c4adb3570974a799f080d846839f5e1`.

### Modelo digital configurable y perfiles emparejados (2 de septiembre de 2026)

Se creó `src/nova_sm3_description/config/digital_twin_profiles.yaml` como
fuente única para variar masa, inercia, amortiguamiento, fricción articular y
del suelo, holgura, retardos, tensión y corriente. El estado explícito sigue
siendo `provisional_not_identified`.

`Experimentos/generar_perfiles_gemelo.py` genera un URDF Gazebo, mundo SDF,
MJCF y manifiesto con hashes. Los perfiles `nominal`,
`realistic_provisional` y `low_mass_low_friction` pasaron la auditoría de masa,
amortiguamiento, fricción y esfuerzo común. El perfil realista provisional usa
masa 1,10, inercia 1,15, fricción de suelo 0,675, holgura de un grado,
retardos de 20/50 ms y 5,5 V con 1,0 A por servo; su par queda limitado a
0,683808 N m.

Se añadió `actuator_model_node` para aplicar holgura, retardo y límite de
velocidad en ambas rutas. Gazebo carga perfiles con
`profile_gazebo.launch.py` y MuJoCo acepta ahora una ruta MJCF configurable.
Pasan 89 pruebas y ambos paquetes compilan. El perfil realista provisional se
cargó en Gazebo con sus doce articulaciones y dos controladores activos; el
MJCF correspondiente cargó directamente en MuJoCo con 12 actuadores y siete
sensores. Falta ejecutar campañas iguales y
exponer pose/contactos equivalentes desde MuJoCo; por ello aún no se declara un
gemelo digital identificado ni una comparación dinámica completa. Documento:
`Documentacion/GEMELO_DIGITAL_CONFIGURABLE.md`.

La tesis se recompiló con 66 páginas y SHA-256
`038c3fb25f2a5542cd7f249e5263dd01b1f3f0bd389bf60ed89f2f9d3852aba1`.

### Ficha suministrada de los doce MG996R-360 (2 de septiembre de 2026)

Se archivó `Documentacion/Fuentes/MG996R-360_AG_Electronica.pdf`, SHA-256
`9cbb94b33d2b84a52fad1c8379f98d6034231150f4b8f29b6a0fcd1054addd5d`.
Confirma 4,8--6,6 V, 9,4/11 kgf cm a 4,8/6,0 V, 0,19/0,15 s por 60 grados,
55 g, engranajes metálicos, doble rodamiento y banda muerta PWM de 1 us. El
modelo interpola ahora entre los dos puntos declarados de par y velocidad.

La ficha contradice su rango: título y tabla indican 360 grados, pero el texto
dice «su giro es 60°» y no define si el pulso controla posición o velocidad.
Tampoco declara corriente. No se modifican los límites revolutos del URDF y la
corriente sigue provisional hasta probar una unidad desacoplada y después
identificar las doce. Auditoría:
`Documentacion/CARACTERISTICAS_MG996R_360_SUMINISTRADAS.md`.

Tras incorporar estos datos, la tesis se recompiló con 66 páginas y SHA-256
`521e4ec0d1aae34b65f27fca3f8825b8005578759d3721a91a1de909acdacd3b`.

### Pruebas automáticas de seguridad (2 de septiembre de 2026)

Se amplió el supervisor para detectar discontinuidades mayores que 0,35 rad
tanto dentro de una trayectoria como entre mensajes consecutivos. La suite
comprueba además límites coherentes de las doce articulaciones en URDF, MJCF y
supervisor; tiempos monótonos; referencias finitas; pérdida de contactos
esperados; margen; telemetría vencida; altura y límites de roll/pitch.

Pasan 80 pruebas Python. `.github/workflows/pruebas-automaticas.yml` compila
los paquetes `nova_sm3_description` y `nova_gait_controller` y ejecuta la suite
en cada `push` y `pull_request`. La protección de rama debe configurarse en
GitHub si se desea impedir formalmente una integración cuando falle el flujo.
Estas verificaciones deterministas no sustituyen las pruebas dinámicas
integradas ni físicas. Documento:
`Documentacion/PRUEBAS_AUTOMATICAS_SEGURIDAD.md`.

La tesis recompilada conserva 66 páginas y tiene SHA-256
`ffa7760971c75c08c8b81feac1fb17246292868c74e1303b76e11f5c37992029`.

### Pruebas dinámicas provocadas del supervisor (2 de septiembre de 2026)

Se corrigió el cierre de `safety_test_node` y se amplió a nueve escenarios ROS
2 aislados: margen negativo, pérdida de contacto, datos vencidos, altura baja y
alta, roll, pitch, límite articular y discontinuidad. Todos recibieron
`triggered=true`, el motivo exacto esperado y la orden `stand`. La evidencia
JSON y los logs están en
`Experimentos/pruebas_dinamicas_supervisor_20260902`; la suite determinista
continúa con 80 pruebas aprobadas.

La campaña completa y su validador quedaron automatizados en
`Experimentos/ejecutar_pruebas_dinamicas_supervisor.sh` y GitHub Actions. Esto
cierra las pruebas integradas provocadas pendientes, pero no demuestra corte
eléctrico ni respuesta mecánica y no habilita las tres paradas por defecto. Aún
se deben definir el rearme y medir falsos positivos en ejecuciones largas.

La siguiente fase es física y comienza sin energía. El inventario F0--F4 quedó
en `Raspberry/PLAN_VALIDACION_FISICA_DESPUES_SIMULACION_2026-09-02.md`: ensamble
y caracterización, seguridad eléctrica/OE, calibración individual, integración
progresiva e instrumentación. No se autoriza PPO ni marcha física antes de
superar esas puertas.

La tesis se recompiló con 67 páginas y SHA-256
`7ba0d066f679ae60d482a9ddb494fd8c2299c4ee5f06d11b3aa2200cf6e3bb3d`.

### Documentación integral de resultados y anexos (2 de septiembre de 2026)

Se actualizó `Documento_TESIS/MATRIZ_OBJETIVO_EVIDENCIA.md` para reflejar que
las cinco semillas PPO sí fueron entrenadas y evaluadas, pero ninguna política
quedó aceptada; OE4 se clasifica como ejecutado sin mejora y OE5 como parcial
no concluyente. Se corrigió la discusión que todavía describía el entrenamiento
como pendiente.

El PDF incorporó una tabla de síntesis de resultados y alcance, un segundo
diagrama que separa la plataforma computacional comprobada de las puertas
físicas pendientes, y el Apéndice A con matriz objetivo--evidencia, protocolos,
comandos mínimos, reglas de integridad, automatización y transición F0--F4. El
índice visual y el README se sincronizaron con las figuras PPO y el estado real.

La inspección visual confirmó que la tabla, ambos diagramas y la primera página
del anexo permanecen dentro de márgenes. La compilación terminó sin referencias
indefinidas ni desbordamientos nuevos; el PDF tiene 74 páginas y SHA-256
`61a95ac84f91217d8ced474c4ce68215b1af4f8eb96240771dfc54d5241d55e5`.

### Equivalencia Gazebo--MuJoCo completada (2 de septiembre de 2026)

`nova_mujoco_observations` publica a 100 Hz pose corporal, IMU y cuatro
contactos con el contrato ROS 2 usado en Gazebo. El keyframe `stand` y ganancias
provisionales 40/4 permiten reinicios reproducibles; la tentativa anterior se
conserva marcada como inválida.

`equivalencia_paso_mujoco_r2_20260902` contiene 11 ciclos completos y cero
eventos del supervisor. Frente a `cierre_paso_r1_20260901`, Gazebo avanzó
0,022025 m/ciclo y MuJoCo 0,001157; los errores RMS fueron 0,008412 y 0,014768
rad. MuJoCo mantuvo cuatro apoyos y obtuvo 0 % de coincidencia con el plan. Se
cerró equivalencia de interfaz y campaña, no equivalencia dinámica. Véase
`Documentacion/EQUIVALENCIA_GAZEBO_MUJOCO_2026-09-02.md`. La denominación sigue
siendo **modelo digital configurable** hasta la identificación física.

La tesis recompilada tiene 73 páginas y SHA-256
`72f850b248a1ca340fae302d06ad2cadd77b9ee7aefa0f278c59c1a81398e477`.

### Depuración de la campaña MuJoCo 5x20 (3 de septiembre de 2026)

Se auditó la campaña incompleta `paso_5x20_r2_20260902`. Sus repeticiones 1 y
2 contienen 21 ciclos completos, pero `paso_r3` registró 691.518 mensajes y
cero órdenes en `/nova/gait_command`; quedó marcado como inválido y no puede
incorporarse al resumen. Reiniciar el mundo con los nodos activos también hizo
retroceder `/clock` y generó avisos persistentes en `robot_state_publisher`.

`Experimentos/ejecutar_campana_mujoco.sh` inicia ahora una instancia MuJoCo
aislada por ensayo, espera señales explícitas de controlador y grabador listos,
publica marcadores redundantes, impide sobrescribir bolsas y aplica un apagado
acotado. La validación `validacion_aislamiento_r4_20260903` capturó seis
marcadores, 96 referencias y tres ciclos completos sin retrocesos de reloj. La
validación adicional `validacion_cierre_20260903` confirmó el cierre automático
con 32 referencias y error RMS articular de 0,010531 rad. Compilaron los dos
paquetes y pasaron 98 pruebas.

Las pruebas cortas solo validan la automatización y no son resultados de la
tesis. La próxima acción es ejecutar una campaña nueva y limpia de cinco
ensayos independientes de 20 ciclos; no completar la campaña antigua mezclando
repeticiones producidas con procedimientos de reinicio distintos.

La acción quedó completada el 3 de septiembre con
`Experimentos/campanas_mujoco/paso_5x20_aislada_r3_20260903`. Después de
detectar y eliminar tres grupos de procesos huérfanos, el ejecutor pasó a crear
y cerrar un grupo completo por ensayo. Una prueba 2x2 confirmó cero procesos
remanentes y cero retrocesos de reloj antes de iniciar la campaña definitiva.

Los cinco ensayos definitivos contienen 21 ciclos y 672 referencias cada uno;
el análisis comparable conserva el ciclo 1 como transitorio y usa los ciclos
2--20. No hubo activaciones del supervisor. El avance medio fue 0,002701937
m/ciclo, roll máximo 0,646314 grados, pitch máximo 1,787264 grados y error RMS
articular 0,010531 rad. El CV entre ensayos del avance fue 0,020555 %. La
coincidencia de contactos fue 0 %, por lo que se confirma reproducibilidad de
la interfaz y seguimiento, pero no equivalencia dinámica ni marcha física útil
en MuJoCo. El registro incluye hashes de las cinco bolsas.

### Ajuste y campañas complementarias MuJoCo (3 de septiembre de 2026)

Se añadió transferencia longitudinal, altura de paso y ganancias/fricción
ajustables. La campaña `Experimentos/campanas_mujoco/paso_ajustado_5x20_20260903`
(transferencia 15 mm, altura 12 mm, kp/kv 80/8, fricción 0,9) obtuvo 9,867
mm/ciclo, 36,58 % de contacto, roll 1,51°, pitch 3,17° y RMS 0,00595 rad.
Mejora el nominal (2,702 mm/ciclo y 0 %), pero sigue lejos de Gazebo (~22 mm/ciclo).

Se ejecutó además `gateo_nominal_5x20_20260903` (6,304 mm/ciclo; 67,46 % de
contacto) y empujes de 1, 2 y 3 N. Estos verifican el registro del inyector,
pero no demuestran respuesta diferenciada del supervisor; ruido y retardos aún
no están integrados. Los perfiles con esfuerzo provisional no sostuvieron la
marcha: falta calibración con mediciones físicas. Detalle en
`Documentacion/MUJOCO_CIERRE_2026-09-03.md`.

### Validación inicial del hardware real y sobrecarga (4 de septiembre de 2026)

Se confirmó el mapa físico de canales y se verificó movimiento de los doce
servos mediante PWM reducido. La postura neutra a 1500 µs conservó el
cuadrúpedo estable y una transferencia mínima produjo movimiento de las patas.
Durante las pruebas posteriores se observó una sobrecarga de corriente, por lo
que se apagó ordenadamente la Raspberry y se dejó la fuente de servos apagada.

La siguiente reanudación debe comenzar con la verificación eléctrica del
PCA9685 sin carga, medición de VCC/V+, comprobación I²C en 0x40, diagnóstico de
CH1 y medición de corriente por servo/grupos pequeños. No ejecutar caminatas
hasta cerrar esa lista.

### Primera entrega de avances — 7 de septiembre de 2026

Se revisaron la memoria histórica, el seguimiento, los objetivos, la matriz de
 evidencia y las fuentes del documento final frente a la guía suministrada
`Primera entrega de avances - Proyecto de grado II.pdf`. Se preparó
`ProyectoII_Clases/07_09_2026` con presentación editable de seis diapositivas,
PDF, generador Python y guía de exposición de aproximadamente 8:30 minutos.

Los porcentajes propuestos (OE1 50 %, OE2 50 %, OE3 75 %, OE4 50 %, OE5 25 %)
usan cuatro hitos de 25 % por objetivo y no acreditan hitos parciales. La rúbrica
y el compromiso son propuestas para revisión del grupo, no aprobación docente.
La exposición distingue el entrenamiento PPO del éxito de la política y
conserva el bloqueo físico por sobrecarga del 4 de septiembre.

Verificación: PDF exportado con seis páginas y revisión visual de todas las
 diapositivas, con corrección de desbordamientos; cifras cotejadas con informes
existentes. No se ejecutaron ensayos nuevos. El PDF de tesis consultado tiene
73 páginas. Se detectaron conclusiones desactualizadas sobre entrenamiento PPO,
un resumen antiguo del alcance MuJoCo y resultados del 3–4 de septiembre aún
pendientes de incorporar. Las correcciones quedaron enumeradas en la guía;
no se modificó la tesis ni el control del robot en esta tarea.

Siguiente acción: revisar con el grupo los porcentajes y el compromiso, ensayar
la exposición y sincronizar las secciones documentales identificadas. La próxima
acción física conserva la verificación PCA9685 sin carga y el diagnóstico de
CH1/consumo antes de cualquier marcha. La presentación se conserva localmente;
la publicación en el repositorio queda pendiente.

### Fotografías del prototipo incorporadas — 7 de septiembre de 2026

A petición del usuario se archivaron cinco JPEG originales en
`Github/evidencias/2026-09-07`, con descripciones visibles y hashes SHA-256.
La fecha indica incorporación, no captura. Se integraron a la bitácora visual,
el progreso semanal y un enlace destacado del panel. Documentan ensamble,
electrónica, articulación y pieza impresa; aportan contexto a OE1/OE2/OE3 sin
cerrar mediciones ni modificar porcentajes o el bloqueo por sobrecarga.

Se actualizó el generador y la guía de exposición. Las cinco imágenes aparecen
en las diapositivas 1 y 3 de `Primera_entrega_avances_con_fotos.pptx` y su PDF.
Se conservó el PowerPoint anterior porque se detectó abierto mediante su archivo
de bloqueo. Verificación: seis diapositivas, cinco imágenes originales
incorporadas, revisión visual de páginas modificadas, copias idénticas y rutas
HTML de imágenes existentes. No se modificó hardware ni se ejecutaron ensayos.
Siguiente acción: usar la versión con fotos para ensayar; publicación remota
pendiente. La incorporación a la tesis final sigue como tarea documental de
cierre, sin atribuir validación experimental a las fotografías.

### Captura Gazebo para la exposición — 7 de septiembre de 2026

Se obtuvo una captura nativa del modelo Nova en Gazebo, usando el lanzamiento
local en dominio ROS 94 y partición Ignition exclusiva. Archivo y procedencia:
`Github/evidencias/2026-09-07/gazebo_nova.png` y README con SHA-256. Es una vista
ilustrativa actual, no un ensayo ni evidencia de las cifras históricas.
Se incorporó a la diapositiva 3 en `Primera_entrega_avances_gazebo.pptx` y PDF;
se conservaron las cinco fotografías y las versiones anteriores. PDF de seis
páginas y página modificada revisados visualmente. Se detuvo el lanzamiento al
terminar. Siguiente acción: ensayar con esta versión; publicación remota pendiente.

### Presentación en lenguaje sencillo — 7 de septiembre de 2026

Por solicitud del usuario se simplificaron las seis diapositivas: se explican
los simuladores y se reemplaza jerga de PPO, seguridad y planificación por
frases directas. Se conservaron cinco fotos, captura Gazebo, porcentajes y
alcance de resultados. El avance de 23,955 mm/ciclo se expresa como unos 2,4 cm;
las cifras exactas y la rúbrica siguen en la guía técnica. Versión vigente:
`ProyectoII_Clases/07_09_2026/Primera_entrega_avances_sencilla.pptx` y PDF.
Se añadió `GUION_SENCILLO.md` y se actualizaron las notas del orador y el
generador. Verificación: seis páginas inspeccionadas, seis imágenes y notas;
sin nuevos ensayos ni cambios de cumplimiento técnico. Siguiente acción:
ensayar la exposición y ajustar su duración. Publicación remota pendiente.

### Diapositiva adicional de objetivos — 7 de septiembre de 2026

El usuario autorizó explícitamente ampliar la presentación a siete diapositivas.
Se insertó en la posición 3 una tabla con los cinco objetivos resumidos, estado
parcial, porcentajes estimados (50/50/75/50/25 %) y requisitos pendientes.
Ningún objetivo se presenta como cerrado. Resultados pasa a la posición 4.
Versión vigente: `Primera_entrega_avances_7_diapositivas.pptx` y PDF, dentro de
`ProyectoII_Clases/07_09_2026`. Se actualizaron fuente, guía y guion; se verificó
la numeración y se inspeccionó visualmente la página nueva. Siguiente acción:
ensayar la versión de siete páginas. Sin cambios técnicos ni ensayos nuevos.

### Contraste de dimensiones con el sitio oficial — 7 de septiembre de 2026

Se consultó novaspotmicro.com y el código enlazado desde su lista de archivos.
`Documentacion/CONTRASTE_FUENTES_OFICIALES_NOVA_2026-09-07.md` recoge fuentes y
contraste: 90/105/132 mm por segmentos y 180/120 mm entre pivotes coinciden con
el modelo local. La masa aproximada de seis libras corresponde a unos 2,72 kg.
El enlace rotulado v5.2b conduce a código v5.0; se dejó explícita esa diferencia.
Los límites publicados son valores PWM para motores distintos de nuestros
MG996R; no se trasladan a radianes ni al robot sin calibración. No se modificaron
modelo, mediciones vacías ni cumplimiento de OE1. Verificación documental y
conversiones de unidades; sin ensayo físico. Siguiente acción: medir el ejemplar
y contrastar masas, dimensiones y límites individuales con las referencias.

### Objetivos originales sincronizados — 7 de septiembre de 2026

Se sustituyó literalmente el objetivo general y los cuatro específicos tanto
en `Documento_TESIS/Chapters/3 Objetivos.tex` como en la fuente equivalente de
`tesis_overleaf`. Se reorganizaron matriz viva, anexo, alcance, metodología,
referencia de modelado, conclusiones y plan documental para eliminar el antiguo
OE5. Las tres pruebas de OE4 quedaron explícitas; PPO entrenado no se presenta
como estabilidad garantizada.

La presentación conserva siete diapositivas, fotos y captura Gazebo. Versión:
`Primera_entrega_avances_objetivos_corregidos.pptx` y PDF. Incluye objetivo
general literal, resumen de avance y cuatro objetivos completos. La rúbrica
propuesta se rehízo: 50 % por objetivo, con entregables y pendientes distintos;
no se cambiaron resultados experimentales. Guía y notas quedaron sincronizadas.

Verificación: cuatro ítems idénticos en las dos fuentes, siete diapositivas,
compilación del documento final sin citas/referencias indefinidas y revisión
visual de objetivos, tabla de anexo y diapositivas modificadas. Persisten avisos
de ancho en rutas/bibliografía ajenos a la sustitución de objetivos. El PDF final
preliminar tiene 72 páginas. SHA-256: `54a151bd4cf1a40a0888e89cba8255bd963f5b8cd7ad568820631d3ab1147f33`.
La compilación auxiliar del anteproyecto en `build_objetivos` encontró un problema
BibTeX de esa plantilla; no se reemplazó su PDF histórico. Su capítulo de objetivos
sí quedó sincronizado. Los PowerPoint antiguos abiertos/modificados por el usuario
se preservaron. Siguiente acción: usar la presentación corregida y continuar el
cierre de los cuatro objetivos; publicación remota pendiente.

### Cierre de actualización documental — 7 de septiembre de 2026

Se sincronizaron también el panel `Github/index.html`, la ruta de trabajo, el
README y el progreso semanal con los cuatro objetivos vigentes. El panel ahora
reporta 50 % documental por objetivo, 72 páginas preliminares y cinco semillas
PPO sin mejora aceptada. Se dejaron visibles como pendientes la caracterización
física, la sobrecarga y las tres pruebas de OE4. No se añadieron resultados
experimentales nuevos.

### Propuesta de métricas y criterios para simulación — 7 de septiembre de 2026

Se dejó preparada para revisión de los directores la ficha de aprobación del
protocolo. La propuesta fija como métrica primaria el porcentaje de ciclos
válidos sin fallo, caída ni intervención; registro objetivo de 100 Hz, mínimo
50 Hz y reporte de huecos mayores de 0,10 s; límites de roll/pitch, seguimiento
articular, margen, contactos y repetibilidad; y una mejora mínima de cinco
puntos porcentuales para aceptar ventaja de PPO. Los valores están escritos en
`Documentacion/PROTOCOLO_EXPERIMENTAL_BORRADOR.md` y
`Documentacion/FICHA_APROBACION_PROTOCOLO.md`, pero requieren firma antes de la
campaña final.

### Estado del cierre experimental — 7 de septiembre de 2026

La propuesta de métricas, frecuencia y criterios numéricos quedó consolidada en
el protocolo y la ficha de aprobación. En `Seguimiento/Seguimiento.md` se
marcaron como completadas las definiciones técnicas y se dejó explícito que el
visto bueno de los directores sigue pendiente. También se resolvió la redacción
del nivel de modelo: nominal computable, coherente entre código, URDF/Gazebo y
MJCF/MuJoCo, sin declararlo gemelo digital identificado.

La prioridad no es cumplir una lista rígida de umbrales, sino demostrar los
objetivos con retroalimentación sensórica: posición articular, IMU, contactos y
telemetría eléctrica cuando estén disponibles. Las métricas numéricas quedan
como guías de análisis y se ajustarán con los directores según las señales
reales.

Siguiente paso: entregar la ficha para firma; una vez confirmada, congelar la
matriz experimental y ejecutar las tres pruebas de OE4 en simulación usando la
retroalimentación disponible.

Se añadió a `Seguimiento/Seguimiento.md` el punto de diseño sensórico para RL y
transferencia sim--real. Incluye estado articular, IMU, contactos de los cuatro
pies, salud eléctrica, comandos/fase, sincronización temporal y un contrato de
datos común entre simulación y hardware. El cierre exige registrar esas señales
sincronizadas durante una postura y una marcha manual antes de entrenar o
transferir una política.

### Reconexión a la Raspberry para pruebas físicas — 15 de septiembre de 2026

La IP histórica `192.168.0.101` no pertenece a la red actual del computador,
que está en `10.217.224.0/24`. Se localizó la Raspberry Pi 4 como
`cuadrupedo-pi` en `10.217.224.198` y se accedió por `ssh pavilion@10.217.224.198`.
La placa reportó Ubuntu 22.04.5 LTS ARM64, workspace
`/home/pavilion/nova-spot-micro-tesis` en el commit `3900edd`, PCA9685 detectado
en `0x40` y llamada general `0x70`, sin nodos ROS ni procesos de control activos.

La configuración remota conserva `hardware_ready: false`; las doce
articulaciones están sin calibrar, no hay dispositivos `/dev/ttyACM*` o
`/dev/ttyUSB*` y `pigpiod` está inactivo. Esta conexión solo verificó estado y
no ejecutó PWM, controladores ni movimiento. La siguiente acción física sigue
siendo cerrar F0--F1 y documentar mediciones antes de energizar un servo.

### Pruebas físicas iniciales de las doce articulaciones — 15 de septiembre de 2026

Durante la revisión del workspace remoto se encontró y leyó
`Raspberry/AVANCES_PRUEBA_COXAS_2026-09-15.md`. El registro informa pruebas
manuales con el robot elevado y alimentación externa del PCA9685: coxas en
`CH0--CH3`, fémures en `CH4--CH7` y tibias en `CH8--CH11`, con recorridos
reducidos y retorno al centro. Las doce articulaciones respondieron.

Se confirmó inversión de sentido en las tres articulaciones de la pata
delantera derecha: `CH0`, `CH4` y `CH8`, correspondientes a
`front_right_coxa_joint`, `front_right_femur_joint` y `front_right_tibia_joint`.
El informe no contiene calibración de centro, límites, velocidad, corriente o
torque; por tanto, demuestra respuesta manual y correspondencia preliminar de
canales, pero no autoriza postura, marcha ROS 2 ni transferencia al suelo.

La evidencia se incorporó localmente como
`Raspberry/AVANCES_PRUEBA_COXAS_2026-09-15.md`. En la Raspberry se observaron
además commits de trabajo recientes en el reflog, pero su referencia `main`
apunta a un objeto Git corrupto; queda pendiente reparar o resincronizar ese
workspace sin perder los cambios físicos registrados.

### Esquema visual de conexiones físicas — 15 de septiembre de 2026

Se incorporó la imagen entregada como
`Raspberry/documentacion/ESQUEMA_CONEXIONES_FISICAS_2026-09-15.jpeg` en el
repositorio local y como `Raspberry/ESQUEMA_CONEXIONES_FISICAS_2026-09-15.jpeg`
en la Raspberry. El SHA-256 de la imagen original y de ambas copias es
`d95ac074483b94d3ea6d44efa418563393787610b46c6a0e9ff226fceeb60f36`.

La imagen confirma la numeración desde la vista frontal: Pata 1 delantera
derecha, Pata 2 delantera izquierda, Pata 3 trasera derecha y Pata 4 trasera
izquierda. También confirma el mapa físico `CH0--CH3` para coxas, `CH4--CH7`
para fémures y `CH8--CH11` para tibias. Se corrigió la tabla local de
`Raspberry/CONEXIONES.md`, que conservaba un orden histórico incompatible con
la configuración remota y las pruebas del 15 de septiembre.

### Configuración remota alineada con la identificación física — 15 de septiembre de 2026

Se sincronizó en `/home/pavilion/nova-spot-micro-tesis/Raspberry/configuracion/servos.yaml`
el mapa confirmado por la imagen y las pruebas: `CH0--CH3` coxas, `CH4--CH7`
fémures y `CH8--CH11` tibias. La inversión observada en la pata delantera
derecha quedó en `CH0`, `CH4` y `CH8` (`direction: -1`). Todos los servos
conservan `calibrated: false`, `hardware_ready: false` y límites provisionales;
no se habilitó PWM ni se inició una caminata. La sincronización fue verificada
por hash y se confirmó que no había procesos ROS/control activos.

### Intento controlado de prueba en CH0 y pérdida de I²C — 15 de septiembre de 2026

Con autorización explícita se intentó una prueba limitada únicamente en `CH0`,
usando `OE` físico en GPIO 17, `FULL_OFF` para los demás canales, recorrido
1450--1550 us y retorno al centro. El controlador falló durante la primera
escritura de apagado global con `OSError: [Errno 121] Remote I/O error`; no
llegó a armar PWM ni a mover el servo.

La comprobación posterior mostró que `i2cdetect -y 1` ya no detecta `0x40` ni
`0x70` y `i2cget` también falla. No hay procesos ROS/control activos. La prueba
queda detenida hasta revisar físicamente VCC, GND, SDA, SCL, alimentación del
PCA9685 y continuidad del bus; no se debe reintentar PWM mientras la dirección
`0x40` no reaparezca de forma estable.

### Prueba limitada de CH0 ejecutada tras recuperar I²C — 15 de septiembre de 2026

Después de la reconexión física, `i2cdetect -y 1` volvió a mostrar `0x40` y
`0x70`, y el registro `0x00` del PCA9685 respondió `0x11`. Se ejecutó la prueba
autorizada únicamente en `CH0`, con `OE` en GPIO 17, canales `CH1--CH15` en
`FULL_OFF` y secuencia `1500 -> 1550 -> 1450 -> 1500 us`. El comando terminó
con código 0, retornó el canal al centro y deshabilitó el PWM de todos los
canales. Esta evidencia confirma comunicación y ejecución del comando; la
respuesta mecánica observada por el operador debe registrarse por separado.

La observación presencial posterior informó que `CH0` no produjo movimiento.
Se mantiene bloqueado cualquier aumento de recorrido o prueba multicanal hasta
medir la alimentación `V+` del servo, comprobar `OE` durante la habilitación,
revisar señal/tierra del conector y confirmar que el servo conectado corresponde
al canal probado.

Se repitió la prueba aislada de `CH0` sin control software de `OE`, manteniendo
`CH1--CH15` apagados y el recorrido `1500 -> 1550 -> 1450 -> 1500 us`; terminó
con código 0, pero tampoco hubo movimiento. La comunicación I²C y las
escrituras al PCA9685 no bastan para demostrar PWM físico en el pin de salida.
La siguiente acción debe ser medir la señal PWM de `CH0` con instrumento o
intercambiar el servo por uno conocido, sin ejecutar una caminata ni aumentar
el recorrido.

La prueba se repitió con el mismo rango del script de Thonny de la Raspberry,
`1350 -> 1650 -> 1350 -> 1500 us`, usando pasos de 5 us y solo `CH0` activo.
El operador confirmó movimiento y el proceso terminó con código 0, centrando
el servo y apagando todos los canales. Se concluye que el recorrido anterior
de +/-50 us era insuficiente para provocar una respuesta mecánica observable.
El centro, los límites y la velocidad de `CH0` siguen sin calibración formal.

### Movimiento de la Pata 1 — 15 de septiembre de 2026

Se ejecutó una prueba física limitada de la Pata 1 usando `CH0` (coxa), `CH4`
(fémur) y `CH8` (tibia), con recorrido `1350--1650 us`, retorno al centro y
los demás canales apagados. El operador observó que la pata se movió hacia
arriba. El resultado demuestra respuesta mecánica conjunta de esa pata en el
mapa confirmado, pero no constituye calibración angular ni una marcha; esas
medidas requieren la realimentación prevista con AS5600 y TCA9548A.

### Programa de posición de referencia visual — 15 de septiembre de 2026

Se creó `Raspberry/codigo/posicionar_pata_referencia.py`. Permite seleccionar
una pata, precarga sus tres canales en `1500 us`, apaga los demás, solicita
confirmación textual, mantiene la referencia durante ocho segundos y deshabilita
el PWM al salir. La posición es provisional para tomar fotografías y revisar el
montaje; no representa el cero calibrado ni una postura de marcha. La
calibración final se realizará con AS5600 y TCA9548A.

### Visor 3D local para postura inicial — 15 de septiembre de 2026

Se creó `Experimentos/visor_pose_inicial_3d.py` para revisar desde el PC la
postura inicial sin conectarse a ROS, SSH ni PWM. El visor usa la cinemática
nominal existente, muestra las cuatro patas, permite ajustar coxa, fémur y
tibia de la pata seleccionada, reiniciar la postura nominal y guardar una
captura PNG para contrastarla con el montaje físico. La prueba gráfica en
backend no interactivo terminó correctamente; los ángulos mostrados son
referencias del modelo, no medidas de AS5600.

El visor se amplió con botones `Pata 1`--`Pata 4` para cambiar de articulación
seleccionada sin cerrar la ventana. Cada pata conserva sus valores de coxa,
fémur y tibia, y la pata activa se resalta en la escena. La función fue
verificada generando una figura con la postura ampliada de Pata 1.

Se envió desde el PC a la Raspberry la referencia provisional ajustada en el
visor 3D para la Pata 1: `(q_coxa, q_femur, q_tibia) = (0.02, 0.03, -0.03)` rad,
convertida de forma abierta a `CH0=1494 us`, `CH4=1490 us` y `CH8=1509 us`.
Los demás canales permanecieron apagados, la referencia se mantuvo durante
tres segundos y el PWM se deshabilitó al finalizar. La comparación con la
postura física queda pendiente de la fotografía del operador; estos pulsos no
son calibración definitiva.

La Pata 1 fue colocada manualmente por el operador para hacer coincidir el
prototipo con el visor 3D. La captura `Experimentos/pose_inicial_3d.png` quedó
como referencia visual con valores aproximados `q_coxa=0.03 rad`,
`q_femur=0.02 rad` y `q_tibia=-0.01 rad`. Estos valores describen la postura
observada en el modelo, no una medición de los servos; no se enviaron como PWM
ni se marcaron como calibración. La conversión confiable quedará pendiente de
AS5600 y TCA9548A.

Para la Pata 2, el operador ajustó manualmente la postura y observó que la
coxa quedó más metida. La referencia visual guardada muestra aproximadamente
`q_coxa=-0.60 rad`, `q_femur=-0.10 rad` y `q_tibia=-0.01 rad`; la coxa llegó al
límite inferior provisional del visor. Este registro describe una observación
del montaje, no una calibración de servo ni una autorización para ampliar los
límites físicos sin sensores.

Se amplió el rango visual de coxa en `Experimentos/visor_pose_inicial_3d.py`
hasta `-1.00 rad` para representar la postura de la Pata 2, que alcanzaba el
límite provisional de `-0.60 rad`. La prueba gráfica con `q_coxa=-0.90 rad`
terminó correctamente. La ampliación es solo exploratoria y no modifica los
límites físicos, el URDF ni la configuración PWM.

En una segunda referencia visual, el operador ajustó manualmente la Pata 1 a
`q_coxa=-0.47 rad`, `q_femur=-1.20 rad` y `q_tibia=-2.20 rad`. El visor 3D se
amplió hasta `q_tibia=-3.00 rad` solo para exploración visual; no se modificó el
límite físico/modelado ni se enviaron esos valores como PWM.

### Corrección de longitud física de la coxa — 15 de septiembre de 2026

El operador reportó, con evidencia visual del montaje, que el segmento entre
la coxa y el fémur es demasiado largo y midió `1.5 in`, equivalente a
`0.0381 m`. Se actualizó `COXA_LENGTH` en la cinemática, `coxa_length` en el
URDF y la geometría equivalente de los cuatro eslabones de coxa en el MJCF.
Las posiciones de las caderas respecto al cuerpo (`±0.09 m` longitudinal y
`±0.06 m` lateral) se conservaron porque no representan la longitud del
segmento de coxa.

El visor 3D usa `COXA_LENGTH`, por lo que la modificación se refleja también
en sus referencias geométricas. La medida queda como ajuste físico inicial,
pendiente de confirmación en las cuatro patas y de validación con AS5600; no
se modificaron límites PWM ni se ejecutó ningún movimiento en la Raspberry.

El visor 3D quedó confirmado como consumidor directo de las constantes nuevas
y ahora muestra en la ventana la escala medida directamente en pulgadas: coxa
`1.50 in`, fémur `4.25 in` y tibia `5.35 in`.

La medición complementaria del operador estableció inicialmente `4.5 in`
(`0.1143 m`) para
el fémur y, inicialmente, `5.5 in` (`0.1397 m`) para el tramo tibia-piso. Se actualizaron
también `FEMUR_LENGTH` y `TIBIA_LENGTH` en la cinemática y sus equivalentes en
URDF/MJCF. Estas longitudes son referencias geométricas medidas, no límites de
ángulo ni parámetros de calibración de servos.

Corrección posterior: la medida del tramo coxa-fémur quedó establecida en
`4.25 in` (`0.10795 m`). Se corrigió `FEMUR_LENGTH` y la geometría dependiente
en el visor, URDF y MJCF; posteriormente la tibia se corrigió a `5.35 in`
(`0.13589 m`).

Corrección posterior: el tramo tibia-piso mide `5.35 in` (`0.13589 m`). Se
actualizó `TIBIA_LENGTH` y la geometría correspondiente en el visor, URDF y
MJCF.

### Confirmación de prueba de las cuatro coxas y lección operativa — 15 de septiembre de 2026

El operador confirmó que las cuatro coxas respondieron correctamente en la
Raspberry. La falla observada desde esta sesión no correspondía a los servos:
se intentó preparar un segundo control mientras Thonny mantenía abierto
`prueba_coxas_thonny.py`, y además el nombre `cuadrupedo-pi` resolvió a una IP
no operativa (`10.58.164.198`) mientras la IP accesible era `10.217.224.198`.

Regla para las siguientes pruebas: verificar primero procesos activos, usar la
IP SSH accesible, trabajar con un único controlador del PCA9685, confirmar
`0x40` en I²C y ejecutar una sola secuencia acotada. No se debe iniciar un
segundo script de servos ni atribuir una falta de movimiento al hardware sin
separar estos factores. La prueba de coxas queda documentada como exitosa;
queda pendiente repetir Pata 1 con su postura angular inicial bajo este
procedimiento único.

Se ejecutó posteriormente la prueba controlada de la Pata 1 con `CH0` (coxa),
`CH4` (fémur) y `CH8` (tibia), usando la referencia indicada por el operador
`q=(0.04, 0.0, 0.0) rad`. Cada canal se recorrió individualmente entre
`1350` y `1650 us`, con los demás canales apagados; la secuencia terminó con
código 0, retorno al centro y PWM deshabilitado. La respuesta mecánica y el
sentido observado por el operador quedan pendientes de registrar por canal.

### Cierre de sesión de pruebas físicas — 15 de septiembre de 2026

El operador indicó que cerraría la sesión. Estado guardado: Raspberry
accesible en `10.217.224.198`, PCA9685 detectado en `0x40`, Thonny detenido y
prueba de Pata 1 finalizada sin error. Se probaron individualmente `CH0`, `CH4`
y `CH8` con recorrido `1350--1650 us`; los tres canales regresaron al centro y
el controlador apagó el PWM. Falta registrar la observación física del sentido
y reacción de coxa, fémur y tibia. La próxima sesión debe comenzar revisando
ese registro antes de enviar otra orden.

### Entrenamiento PPO en MuJoCo y Gazebo con geometría medida — 24 de septiembre de 2026

Se centralizaron las dimensiones geométricas usadas por la cinemática, el visor
3D y los entrenadores: separación de caderas `0,180 x 0,120 m`, cuerpo
`0,230 x 0,120 x 0,075 m`, coxa `0,0381 m` (1,50 in), fémur `0,10795 m`
(4,25 in) y tibia `0,13589 m` (5,35 in). También se corrigió el comentario del
URDF que todavía describía el fémur como `0,1143 m`; no se modificaron límites
PWM ni calibraciones físicas.

Se creó `Experimentos/entrenar_ppo_mujoco.py`, un entorno Gymnasium que carga
`src/nova_sm3_description/mujoco/nova_sm3.xml`, genera el gateo nominal con la
misma cinemática y entrena PPO residual con 27 observaciones y 12 acciones
articulares acotadas. La semilla 11 completó 20.480 pasos efectivos de PPO
(20.000 solicitados, redondeados al rollout de 1.024) en
`Experimentos/entrenamiento_ppo_mujoco_20260924/crawl_semilla_11`.

Se creó `Experimentos/entrenar_ppo_gazebo.py` y se amplió
`ppo_residual_node` para recibir acciones externas en `/nova/rl_action`. La
semilla 11 completó 1.024 pasos de interacción real con Gazebo, esperando cada
fase publicada por `/nova/gait_phase`, en
`Experimentos/entrenamiento_ppo_gazebo_20260924/crawl_semilla_11`.
La política de Gazebo quedó guardada en formato Stable-Baselines3 y la de
MuJoCo en el mismo formato; ambas son políticas de simulación independientes.

Validación de preparación: `check_env` de MuJoCo pasó, la suite ROS 2 terminó
con 99 pruebas aprobadas y ambos paquetes compilaron. La evaluación exploratoria
de cinco episodios en MuJoCo dio, para nominal frente a PPO, avance medio
`0,469464` frente a `0,573312 m` y máxima inclinación media `0,00976` frente a
`0,01549 rad`; esto no constituye criterio de aceptación porque la política
aumentó la inclinación y todavía requiere evaluación emparejada. El
entrenamiento Gazebo terminó sin error ni procesos remanentes, pero aún falta
su evaluación separada y una campaña de cinco semillas.

Las dependencias de entrenamiento se instalaron de forma aislada en
`/tmp/nova_rl_deps` con versiones CPU de PyTorch, Gymnasium, Stable-Baselines3
y MuJoCo. No se ejecutó ningún nodo de hardware, PWM, SSH ni conexión con la
Raspberry. La próxima acción es evaluar ambas políticas contra sus nominales en
los dos simuladores, repetir con las semillas aprobadas y conservar solo las
políticas que mejoren la métrica primaria sin degradar seguridad o postura.

### Campaña PPO completa de gateo y paso — 24 de septiembre de 2026

Se añadió `Experimentos/campana_ppo_completa.py` para ejecutar de forma
reproducible las dos caminatas con las semillas `11, 23, 37, 53, 71`, guardar
metadatos y evaluar MuJoCo contra la marcha nominal. La campaña final quedó en
`Experimentos/reentrenamiento_ppo_completo_20260924/`: 10 políticas MuJoCo de
50.176 pasos efectivos cada una y 10 políticas Gazebo de 1.024 pasos efectivos
cada una.

La evaluación MuJoCo de cinco episodios por condición produjo estos promedios:
gateo nominal/PPO `0,4917/0,4598 m` de avance y `0,00993/0,02390 rad` de
inclinación máxima; paso nominal/PPO `0,0155/0,1534 m` y
`0,01392/0,02406 rad`. Se conservan como candidatas offline gateo semilla 53
y paso semilla 71, pero ninguna se acepta para hardware.

Durante la primera corrida de Gazebo se detectó que la acción externa era
limitada pero no se sumaba a la trayectoria nominal. Se corrigió
`ppo_residual_node.py`, se detuvo esa corrida y se regeneraron las 10 políticas
de Gazebo; la primera tanda invalidada no se usa. El informe completo está en
`Experimentos/reentrenamiento_ppo_completo_20260924/INFORME.md`. Gazebo queda
como campaña de interacción/robustez, no como convergencia final, porque
1.024 pasos no bastan para aceptar PPO.

La suite continúa en `99 passed`, el paquete ROS recompila y no quedaron
procesos de simulación ni conexiones a la Raspberry. Antes de usar PPO en
hardware aún faltan calibración, alimentación, seguridad y una campaña Gazebo
con mayor presupuesto.

El registro cronológico consolidado de toda la auditoría, corrección,
campañas, reentrenamiento largo, validaciones y rutas de parámetros está en
`Experimentos/reentrenamiento_ppo_largo_20260924/PROCESO_COMPLETO.md`.

La evaluación Gazebo quedó además en `gazebo_evaluation.csv`, con una prueba
nominal y una PPO por cada una de las 10 políticas. Los promedios nominal/PPO
fueron: gateo retorno `108,54/94,93`, avance `-0,0164/-0,0942 m` e inclinación
`0,03881/0,04459 rad`; paso retorno `139,28/110,49`, avance
`-0,0662/-0,0638 m` e inclinación `0,01440/0,01316 rad`. Con una sola prueba
por política y solo 1.024 pasos de entrenamiento, Gazebo queda como diagnóstico
y no como política aceptada.
### Revisión de Raspberry, PCA9685 e instrumentación — 7 de septiembre de 2026

Se actualizó la sección 8 de `Seguimiento/Seguimiento.md` con la evidencia
disponible: microSD identificada y grabada, Ubuntu 22.04.5 ARM64 con SSH,
workspace ROS 2 compilado, Wi-Fi/DDS con `ROS_DOMAIN_ID=42` y PCA9685 detectado
en `0x40`. El barrido Arduino/Mega de `CH5`--`CH10` demuestra movimiento limitado,
pero no sustituye una interfaz `ros2_control` calibrada ni una prueba PWM con
instrumento. AS5600/TCA9548A, BNO055, contactos físicos e INA228 permanecen sin
prototipo conectado; la arquitectura de realimentación es conceptual. La
sobrecarga mantiene bloqueadas las posturas y marchas hasta cerrar alimentación,
OE, calibración y vigilancia de comunicaciones.

### Adaptación larga de las candidatas PPO en Gazebo — 24 de septiembre de 2026

A petición del operador se continuó el entrenamiento desde las políticas
MuJoCo seleccionadas: gateo semilla 53 y paso semilla 71. Ambas completaron
20.480 pasos efectivos en Gazebo, con checkpoints cada 2.048 pasos, y se
guardaron en `Experimentos/reentrenamiento_ppo_largo_20260924/gazebo/`.

La validación de tres episodios por condición dio gateo nominal/PPO largo
`0,1143/0,1276 m` de avance y `0,06659/0,06421 rad` de inclinación máxima;
paso nominal/PPO largo `0,0933/0,0312 m` y `0,04462/0,04639 rad`. El gateo
queda como candidato offline; paso no se acepta aún porque pierde avance. Los
archivos `policy.zip`, `metadata.json` y las trazas contienen los parámetros
finales. No se transfirió ninguna política al hardware.

### Actualización del estado guardado — 24 de septiembre de 2026

Se verificó que el proceso completo permanece guardado en
`Experimentos/reentrenamiento_ppo_largo_20260924/PROCESO_COMPLETO.md`, junto
con las políticas finales, metadatos, checkpoints, trazas y evaluaciones. El
repositorio conserva cambios locales documentados de simulación, geometría,
control PPO, documentación y pruebas físicas; no se descartó ningún cambio
previo. El estado experimental no cambia: gateo semilla 53 es el único
candidato offline favorable, paso semilla 71 requiere otra iteración, y las
políticas siguen bloqueadas para uso en hardware.

### Preparación de lectura AS5600 por TCA9548A — 28 de septiembre de 2026

Se añadió `Raspberry/codigo/leer_as5600_tca.py`, un lector de diagnóstico para
I2C-1 que selecciona los dos TCA9548A en `0x70` y `0x71` y lee el registro
`RAW_ANGLE` de los AS5600 en `0x36`. El programa no importa el controlador
PCA9685, no cambia OE y no emite PWM; por tanto no mueve los servos. Conserva
marca temporal, valor crudo y grados absolutos, pero no declara todavía ángulos
articulares: faltan cero mecánico, sentido, límites, holgura y calibración.

La guía `Raspberry/CONEXIONES.md` especifica que PCA9685 y ambos TCA comparten
SDA en GPIO2/pin físico 3 y SCL en GPIO3/pin físico 5, con GND común y lógica
de 3,3 V. No se debe aplicar 5 V a SDA/SCL. El mapa entregado por Arduino
confirma once articulaciones y deja ambigua la entrada `0x71`, canal 3: el
sketch repetía «fémur 2» y no identificaba «coxa 2». El lector la deja pendiente
en vez de inferirla. La sintaxis Python y el diff se verificaron localmente;
no se ejecutó acceso I2C ni se movió hardware. Commit público: `986ea2d`.

Siguiente acción: con potencia de servos desconectada y OE alto, escanear I2C,
realizar una lectura única y confirmar físicamente el sensor 12 antes de
publicar posiciones medidas en ROS 2.

### Primera lectura real de AS5600 — 28 de septiembre de 2026

La Raspberry se localizó por SSH como `cuadrupedo-pi.local` (`192.168.0.101`).
I2C-1 confirmó `0x40` (PCA9685), `0x70` y `0x71` (TCA); no había procesos de
PWM, Thonny ni otro controlador activo. Se transfirió el lector de solo lectura
por SSH porque el repositorio local de la Raspberry contiene el objeto Git
corrupto `3900edd` y no puede actualizarse con Git. El barrido único no tocó
OE/PWM ni movió servos.

Respondieron nueve rutas AS5600 y fallaron con error I2C 121 las rutas `0x70`
canales 6--7 y `0x71` canal 2. La entrada `0x71` canal 3 respondió, pero sigue
sin asociación articular confirmada. La evidencia exacta, valores crudos y
siguientes comprobaciones se conservan en
`Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`. El resultado valida comunicación
parcial de sensores, no calibración ni integración ROS 2.

Corrección de mapa aportada por el operador el 28 de septiembre: los canales
`0x70` 6--7 y `0x71` 2 están intencionalmente vacíos; los doce AS5600 están en
`0x70` 0--5 y en `0x71` 0, 1, 3, 4, 5 y 6. Se asocian respectivamente con las
patas 4, 3, 1 y 2 según la tabla trazable del informe de lectura. Se actualizó
el lector para ese mapa y queda pendiente repetir el barrido completo, aún sin
declarar calibración angular, postura o marcha física.

El barrido completo posterior respondió en las doce rutas del mapa confirmado:
los seis sensores de `0x70` (canales 0--5) y los seis de `0x71` (0, 1, 3--6).
Los valores y su correspondencia están en
`Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`. Esto cierra únicamente la
comunicación básica de los doce encoders; persisten estabilidad, cero, sentido,
rango, holgura y validación de seguridad antes de postura o marcha.

Caracterización manual posterior: se guardaron veinte muestras en el extremo
horario seguro de coxa 3 (`0x70`/5) y coxa 4 (`0x70`/2). Coxa 3 promedió
36,290° con rango 16,435°; el operador indicó que no puede ajustarse en esta
sesión, por lo que se conserva exclusivamente como referencia visual inestable
y queda prohibida para control cerrado. Coxa 4 promedió 216,562° sin variación
observada. Datos en
`Raspberry/configuracion/as5600_caracterizacion_provisional.yaml` y en el
informe de lectura; no constituyen calibración completa ni autorización de
postura/marcha.

Se registraron además veinte muestras en el extremo horario seguro de los cuatro
fémures: P1 232,831° (rango 0,176°), P2 299,795° (0,000°), P3 47,039°
(0,088°) y P4 291,797° (0,000°). Las cuatro señales permanecieron estables;
los datos se conservaron como referencias visuales provisionales en el YAML de
caracterización. Falta la captura antihoraria y la calibración angular antes de
control físico.

La captura pendiente de las tibias en el extremo horario respondió tras
reconectar la Raspberry en `172.18.81.198`: P1 83,672° (rango 0,000°), P2
83,232° (0,000°), P3 300,968° (8,877°) y P4 75,472° (0,088°). P3 se marca
inestable y solo visual; las demás se conservan como referencias provisionales.
Los doce resultados parciales están en el YAML y el informe AS5600. Aún faltan
extremos antihorarios, conversión a radianes, márgenes y pruebas de seguridad.

Se capturaron los extremos antihorarios de las coxas: P1 112,373° (rango
1,142°), P2 146,162° (9,580°), P3 183,863° (0,615°) y P4 192,484° (0,088°).
P2 continúa inestable y P1 requiere verificación; P3 y P4 fueron estables en
esta captura. Se conservaron separados de los extremos horarios en la sección
`counterclockwise_measurements` del YAML; sigue prohibido usarlos para control
cerrado o marcha hasta completar la calibración y las puertas de seguridad.

Se completó también la captura antihoraria de las tibias con veinte muestras:
P1 203,379° (rango 0,000°), P2 249,811° (0,088°), P3 37,446° (5,713°) y P4
303,047° (0,000°). P3 queda inestable y solo visual; las otras tres señales
fueron estables. Los resultados se añadieron a `counterclockwise_measurements`
del YAML y al informe de sensores. La caracterización de ambos sentidos está
registrada, pero falta convertir a límites angulares calibrados, aplicar margen
de tope y validar parada/control antes de cualquier caminata.

Se verificó que la clave SSH anunciada por la nueva IP `172.18.81.198` coincidía
con la identidad conocida de `cuadrupedo-pi.local`; se reconectó usando ese
alias, sin aceptar claves nuevas. Los extremos antihorarios de fémur fueron
estables en veinte muestras: P1 132,460° (rango 0,176°), P2 288,809° (0,000°),
P3 98,126° (0,176°) y P4 66,006° (0,000°). Se guardaron en el YAML como
referencias visuales provisionales. Siguen pendientes los extremos antihorarios
de tibia, la conversión/calibración y las puertas de seguridad.

## Cierre de sesión de caracterización AS5600 — 28 de septiembre de 2026

La captura antihoraria de tibias también quedó completada: P1 203,379° (rango
0,000°), P2 249,811° (0,088°), P3 37,446° (5,713°) y P4 303,047° (0,000°).
Con el mapa físico corregido por el operador respondieron las doce rutas
ocupadas. El informe consolidado está en
`Raspberry/RESUMEN_CARACTERIZACION_AS5600_2026-09-28.md`; la cronología y
detalle por captura, en `Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`, y las
estadísticas por articulación/condición, en
`Raspberry/configuracion/as5600_caracterizacion_provisional.yaml`.

Se conservaron medias, mínimos, máximos y rangos de ventanas de veinte
muestras. Coxa 2, coxa 3 y tibia 3 tienen capturas variables; la referencia
inicial de coxa 1 tampoco fue repetible. Son grados absolutos del imán, no
ángulos calibrados del modelo. No se envió PWM ni se hizo una caminata durante
esta caracterización. Antes de realimentación o marcha faltan cero/sentido por
articulación, tratamiento del cruce 0°/360°, repetibilidad en movimiento,
márgenes respecto a topes y resolución de señales variables, además de las
puertas eléctricas y de parada segura.

### Cierre del dataset de grados absolutos AS5600 — 29 de septiembre de 2026

Por solicitud del operador, las veinte muestras por articulación y sentido
quedan finalizadas como dataset de ángulos absolutos del imán. Se actualizaron
el estado y alcance en `Raspberry/configuracion/as5600_caracterizacion_provisional.yaml`
y `Raspberry/RESUMEN_CARACTERIZACION_AS5600_2026-09-28.md`; se preservan los
rangos amplios y las señales inestables. “Finalizado” no significa cero,
sentido o límites articulares calibrados, y no habilita PWM ni caminata. El
barrido único posterior del 29 de septiembre se mantiene separado de las
ventanas de veinte muestras.

El operador fijó además intervalos finales de referencia magnética para las
doce articulaciones y ambos sentidos. Se registraron en el YAML bajo
`operator_fixed_reference_ranges_deg` y en el resumen tabular. Son referencias
absolutas del imán, no límites mecánicos ni posiciones articulares en radianes;
se preservan intactas las estadísticas empíricas originales.

### Pruebas físicas, visor 3D y preparación de calibración — 29 de septiembre de 2026

El archivo `Experimentos/visor_pose_inicial_3d.py` amplió el deslizador de
tibia hasta `+1.00 rad`, solo en la visualización. Se abrió con Pata 4; después
el operador compartió una postura de Pata 3: coxa `0.10`, fémur `-0.42` y
tibia `-0.88 rad`. Esos radianes no se enviaron al robot porque no existe
conversión calibrada a PWM.

Se hizo un barrido AS5600 de solo lectura en la Raspberry; respondieron las
doce rutas. Ángulos RAW de imán de esa captura (grados; no mezclados con las
ventanas de 20 muestras ni convertidos a radianes):

| Pata | Coxa | Fémur | Tibia |
|---:|---:|---:|---:|
| 1 | 286.172 | 179.824 | 140.010 |
| 2 | 118.477 | 261.299 | 9.668 |
| 3 | 137.900 | 194.414 | 335.039 |
| 4 | 148.887 | 317.725 | 354.814 |

El operador informó haber hecho la preparación indicada para calibrar Pata 1,
pero no se han recibido los resultados de los pulsos, la clasificación del
servo (posicional o giro continuo) ni la respuesta de la tibia 1. Por tanto,
ningún servo queda marcado como calibrado. Mapa de Pata 1: PCA CH0/AS5600
`0x71`/3 coxa; CH4/`0x71`/1 fémur; CH8/`0x71`/0 tibia. Las señales de coxa 1
y fémur 1 han dado campo magnético débil. La señal de tibia 1 fue válida, pero
una prueba previa `1500→1505→1500 µs` dio movimiento no repetible; revisar su
acople antes de inferir una escala.

Tras adaptar `Raspberry/codigo/thonny_marcha_nova.py` al preset de avance
Nova `march_forward`, se ejecutaron por SSH cuatro invocaciones de un ciclo;
cada registro terminó con código 0 y apagado de PWM, aunque varias lecturas
AS5600 dieron error I²C 121. Los registros de fases prueban que el script
emitió órdenes, no que alcanzara una posición calibrada. El operador informó
en una prueba anterior movimiento sin topar, sin medición repetible de la
postura. Se comprobó después en la Pi `hardware_ready: false`, cero servos
marcados calibrados y `nova-hardware.service` inactivo. El script directo de
Thonny llama a `arm()`/`set_pulse_us()` sin consultar esa configuración; no
volver a ejecutarlo hasta cerrar calibración y protección. Se registra que esa
ruta directa se usó en las invocaciones anteriores.

La ficha de `MG996R-360` anuncia 360 grados, pero su descripción suministrada
también habla de giro de 60° y no define relación PWM--posición; el modo real
de control todavía debe identificarse con un servo aislado y sin carga.
Siguiente acción: registrar exactamente ese resultado y las mediciones de
tibia 1 antes de modificar `calibracion_servos.csv` o habilitar hardware.

## Campaña MuJoCo step transferida desde JULI — 28 de septiembre de 2026

Se verificó por huella SSH y se conectó al equipo `JULI` como `juli`. La campaña
`Experimentos/campana_distribuida_step_s23_20260928` se copió sin eliminar ni
modificar el original. La evidencia tiene 80 políticas, 80 semillas completas
y 160 filas de evaluación; todas las sumas SHA-256 incluidas coinciden. El
paquete (333 archivos versionados contando código) quedó en la rama
`resultados/mujoco-step-80-semillas-20260928`, commit `106ee5a`, con autor
configurado `davidediaz <davidediaz@users.noreply.github.com>`. La rama sigue
local y aún no se ha publicado en GitHub. Ninguna política está aprobada para
transferencia física.

El análisis reproducible quedó en
`Experimentos/campana_distribuida_step_s23_20260928/INFORME_ANALISIS_80_SEMILLAS.md`.
La diferencia media pareada PPO−nominal es +2,903 m de avance (78/80 semillas
mejoran) y +34,18 de retorno (76/80), pero también +0,03342 rad en inclinación
reportada (80/80 empeoran). No hay política que mejore avance sin aumentar
inclinación. La evaluación reutiliza cinco episodios sin aleatorización de
dominio; requiere validación más amplia. `hardware_transfer=false` sigue vigente.

Para avanzar se preparó una campaña de desarrollo separada,
`Experimentos/campana_step_estabilidad_w32_20260928`: PPO desde cero con peso de
actitud 32 (base 8), cinco semillas predefinidas 11/23/37/53/71, 200.000 pasos
por semilla y evaluación de desarrollo de 20 ciclos con semillas 601–605. Las
semillas finales 101/202/303/404/505 quedan reservadas. Se amplió el informe
MuJoCo para recoger roll/pitch RMS y máximos, altura, contactos, deriva lateral,
seguimiento y saltos articulares. Los umbrales de la ficha de aprobación siguen
sin firma: la campaña es desarrollo, no certificación ni transferencia física.

La primera tanda w32 terminó las cinco semillas, pero no se acepta: la evaluación
mostró excursión lateral media 6,886 m y error articular máximo medio 0,1461 rad.
Además, una auditoría detectó que el entorno antiguo recorría nueve ciclos por
ciclo declarado (índice de fase avanzaba cada 20 ms, aunque cada muestra debía
durar nueve pasos). Por ello las 80 semillas anteriores y w32 son exploratorias,
no evidencia válida a la cadencia prevista. Se corrigió el entorno para
interpolar cada muestra durante nueve pasos: el nominal ahora completa cinco
ciclos en 1.440 pasos, 5,76 s por ciclo, y su salto de referencia tras el arranque
es 0,0081 rad. Siguiente campaña aislada `campana_step_estabilidad_xy_w32_20260928`:
actitud 32, posición lateral/rumbo 8 cada uno, observación de 30 dimensiones,
semillas 11/23/37/53/71; evalúa desarrollo 701–705 a 20 ciclos. No usará las
semillas finales reservadas.

La campaña lateral/rumbo terminó el 28 de septiembre sin errores: cinco PPO de
200.000 pasos y cinco episodios de evaluación de desarrollo por política, cada
uno de 20 ciclos. Informe y artefactos:
`Experimentos/campana_step_estabilidad_xy_w32_20260928/INFORME_RESULTADOS.md`.
Las políticas mantienen inclinación RMS y altura dentro de los objetivos
numéricos provisionales, pero no se selecciona ninguna: tres de cinco avanzan
menos que el nominal; excursión lateral máxima media 0,0826 m frente a 0,0040 m
nominal; deriva lateral final media 0,0360 m; contacto medio 0,8355. El error
articular máximo medio 0,0738 rad y RMS medio 0,0138 rad empeoran frente al
nominal, pero cumplen los límites de ficha de 0,15 rad máximo y 0,05 rad RMS.
Las semillas finales 101/202/303/404/505 permanecen sin usar.
La ficha de aprobación sigue sin firma, por lo que la marcha no está aprobada y
no se debe transferir PPO al robot. Próximo paso: corregir/validar control
nominal lateral y seguimiento articular antes de otra optimización PPO.

Corrección de referencia step: la trayectoria anterior de 32 puntos/0,18 s
tenía un salto articular de waypoint máximo de 0,07277 rad. Se cambió a 48
puntos/0,12 s, conservando 5,76 s por ciclo; el salto nominal calculado pasa a
0,04911 rad. Pasaron las 15 pruebas cinemáticas y la respuesta dinámica
nominal a 20 ciclos en MuJoCo antes de iniciar la siguiente campaña.

### Referencia step de 48 waypoints y PPO lateral — 29 de septiembre de 2026

La referencia se corrigió de 32 puntos/0,18 s a 48/0,12 s, manteniendo ciclo
5,76 s. El salto de waypoint bajó de 0,072772 a 0,049115 rad; pasaron las 15
pruebas de cinemática. En MuJoCo, la línea base de 20 ciclos tuvo 0,08415 m de
avance, 0,00415 m de excursión lateral, error articular RMS 0,01170 rad y
máximo 0,03795 rad; no hubo caída.

La campaña nueva `Experimentos/campana_step_estabilidad_xy48_w32_l64_20260929`
entrenó cinco PPO (11/23/37/53/71, 200.000 pasos c/u; actitud32/lateral64/
rumbo32). Resultado aleatorizado emparejado: avance medio PPO 0,04219 m vs
0,08414 nominal; excursión lateral máxima 0,06486 m vs 0,00417 m. Solo 1/5
políticas supera el avance nominal. El error articular máximo medio 0,06210 rad
y RMS 0,01297 rad sí están bajo los límites de ficha 0,15/0,05 rad. Escala de
residual 0,25 reduce desviación, pero aún da 0,07301 m de avance y 0,02438 m de
excursión lateral, peor que nominal. No se selecciona PPO; semillas finales
101/202/303/404/505 siguen reservadas.

La matriz sin aleatorización repitió un estado idéntico. En la evaluación
emparejada con fricción/amortiguamiento aleatorizados, el avance nominal varió
0,08348–0,08467 m y la excursión lateral 0,00386–0,00417 m. Las filas nominales
del CSV agregado coinciden porque todas las políticas comparten las mismas
cinco condiciones; no se perturbó pose inicial. Faltan perturbaciones
iniciales representativas, margen estático y protocolo formal firmado. La marcha no está
formalmente aprobada ni se autoriza transferencia física. Informe:
`Experimentos/campana_step_estabilidad_xy48_w32_l64_20260929/INFORME_RESULTADOS.md`.

Se solicitó apagar la Raspberry Pi. Se verificó que `172.18.81.198` presenta el
hostname `cuadrupedo-pi` y responde por la identidad SSH conocida. `sync` se
completó, pero el apagado remoto no: la cuenta requiere contraseña para `sudo`
y systemd requiere autorización interactiva. El operador debe ejecutar
`sudo poweroff` localmente o `ssh -t pavilion@172.18.81.198 'sudo poweroff'`
desde una terminal propia y escribir allí la contraseña. La alimentación
independiente de los servos debe permanecer desconectada.

### Raspberry Pi: conexión SSH vigente — 29 de septiembre de 2026

La Raspberry volvió a la red y se conectó satisfactoriamente como
`cuadrupedo-pi` en `10.139.240.198`; comprobación remota: hostname y uptime
(39 minutos al momento de la conexión). La clave ED25519 presentada coincide
con la huella SSH ya registrada para `cuadrupedo-pi`:
`SHA256:mTERAysLSgm2Xlw36tOoV0uv5gC3vj7Xoycel2xe16M`.
Se actualizó `/home/pavilion/.ssh/config`, alias `cuadrupedo-pi`, para usar
esta IP; la conexión normal es `ssh cuadrupedo-pi`. La IP previa
`172.18.81.198` ya no es válida en la red actual. La IP parece asignada por
DHCP y podría cambiar; si vuelve a fallar, consultar `hostname -I` en la Pi o
reservar esta dirección en el router. No se enviaron órdenes de movimiento.

### Prueba mínima de tibia 1 y diagnóstico de sensores — 29 de septiembre de 2026

Por autorización expresa se probó únicamente tibia 1, PCA CH8 y AS5600
`0x71`/canal 0: `1500 → 1505 → 1500 µs`. El sensor partió en 144,756°, marcó
150,645° a 1505 µs (+5,889°) y 161,455° al volver a 1500 µs (+16,699°). Una
lectura posterior con PWM deshabilitado llegó a 170,947°, pese a que el estado
magnético fue válido. No se continuó con otra articulación ni con una marcha.

Veinte barridos pasivos encontraron seis sensores magnéticamente válidos, pero
coxa 2 tuvo 27,070° de dispersión pese a `MD=1`; solo cinco señales fueron
estables dentro de 2° y magnéticamente válidas. Las restantes incluyen tres
estados de imán débil y tres sin detección. El detalle y la tabla completa están
en `Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

Después de la prueba se forzó OE BCM17 en HIGH y se verificaron individualmente
los dieciséis canales en `FULL_OFF`; no se confió en el registro de apagado
global porque su lectura no confirmó el bit. Se encontró que el driver local
liberaba OE al cerrar y no fijaba `FULL_OFF` individual por canal. Se corrigió
`Raspberry/codigo/pca9685_seguro.py`, se añadieron cuatro pruebas unitarias y
pasaron también `py_compile`. Luego se instaló en la Pi con respaldo del driver
previo; SHA-256 desplegado `a92e47aa75139f42b04cead746112818cddb6e1cdc35abdb22ef747eca8321e1`.
En la Pi pasó `compile()` y se verificó OE BCM17 alto, 16/16 canales
individualmente `FULL_OFF` y servicio de hardware inactivo. Se continúa solo
con análisis pasivo; no se manda otra orden PWM mientras el retorno no sea
repetible y la inestabilidad de sensores no esté resuelta.

Reverificación tras indicar el operador que no movió el robot: quince barridos
pasivos sin PWM repitieron señales variables (tibia 3 26,191°, coxa 3 28,389°,
coxa 1 58,359° y coxa 2 27,070° de rango circular; algunas con estado magnético
inválido). No se atribuye una causa única; se deben revisar alineación/fijación
de imanes y sensores, cableado/alimentación y holgura o caída mecánica sin par.
La razón directa de que no haya movimiento quedó verificada: OE BCM17 HIGH,
16/16 canales PCA `FULL_OFF`, `hardware_ready: false`, 0/12 calibrados y
servicio `nova-hardware.service` inactivo. Ningún PWM se ejecuta. Detalle en
`Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

Al continuar, se hicieron 60 barridos pasivos adicionales: las 12 rutas I²C
respondieron 60/60. Seis sensores mantuvieron estado magnético OK, pero coxa 2
dispersó 34,805° pese a MD=1; solo cinco señales fueron simultáneamente válidas
y estables dentro de 2°. La falla no es el bus I²C: las salidas permanecen
inhibidas intencionalmente y el feedback magnético/mecánico de siete ejes no es
usable. Resultado completo en `Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

Durante una posterior ventana en que el operador dijo enviar pulsos, se hizo
otra lectura estrictamente pasiva de fémur 1 (60 muestras): 167,607–167,783° y
`0x13` en todas (`MD=0`, `ML=1`, imán débil). No se envió PWM ni se pudo
correlacionar el ángulo RAW con pulsos cuyos valores no fueron capturados. No
cuenta como movimiento confirmado ni calibración; detalle en el diagnóstico.

### Continuación de movimiento en MuJoCo headless — 29 de septiembre de 2026

Como continuación sin tocar la realimentación física, se inició MuJoCo headless
en `ROS_DOMAIN_ID=73` aislado de la Pi. Se verificaron los nodos de simulación,
`gait_controller`, `joint_trajectory_controller`, métricas y supervisor. El
gateo nominal corrió durante 6,71 s (parámetros congelados: 24 muestras, ciclo
4,32 s, paso 18 mm y elevación 14 mm) y recibió `stop`; la simulación quedó en
reposo. Una muestra de métricas posterior al stop dio x=0,004767 m,
y=-0,000105 m, altura=0,234259 m; es una instantánea posterior, no métricas
agregadas del ciclo. No se envió PWM ni se comunicó con la Raspberry. El proceso
MuJoCo permanece abierto en reposo para inspección.

### Reanudación de pruebas AS5600 desde Arduino Uno; Raspberry no alcanzable — 7 de octubre de 2026

Se retomó el diagnóstico desde el Uno, que ya compila y ejecuta Blink. El escaneo
exhaustivo previo cubrió direcciones I²C 0x08–0x77 en los canales disponibles de
ambos TCA9548A y detectó doce AS5600 en `0x70` canales 0–5 y `0x71` canales 0, 1,
3, 4, 5 y 6. En el sketch de 12 sensores, el operador identificó FEMUR 2 en
`0x71`/canal 6 y se observó una lectura de 226,14°; las lecturas iniciales de
aproximadamente nueve iteraciones variaron como máximo ~0,09° por sensor. Esto
es una observación preliminar, no la caracterización de 100 muestras ni una
calibración.

Queda una discrepancia de asignación por resolver antes de alterar el mapa
oficial: `Raspberry/CONEXIONES.md` asigna FEMUR 2 a `0x71`/canal 5 y COXA 2 al
canal 6, mientras el sketch del Uno y la identificación física comunicada por
el operador intercambian esas dos etiquetas. La presencia de `0x36` en ambas
rutas no basta por sí sola para identificar cuál articulación es cada sensor.

Se intentó reconectar por el alias SSH conocido `cuadrupedo-pi` y la dirección
registrada `10.139.240.198`, desde el host `10.200.8.231/20`. SSH agotó el tiempo
de conexión y tampoco se encontró la Pi por mDNS. No se ejecutó ningún comando
remoto ni se obtuvieron nuevas lecturas de la Raspberry. El último estado
documentado de seguridad permanece: OE BCM17 alto, 16/16 canales PCA9685 en
`FULL_OFF`, `hardware_ready: false`, 0/12 servos calibrados y servicio inactivo.
En esta sesión no se envió PWM ni se movieron servos.

Para continuar, encender/conectar la Raspberry a una red alcanzable y confirmar
cuando esté disponible. Revalidar la identidad SSH conocida, leer estado de
seguridad sin alterarlo y usar únicamente el lector pasivo de AS5600. Comparar
especialmente `0x71`/canales 5 y 6; reconciliar FEMUR 2/COXA 2 con seguimiento
físico y lecturas repetibles antes de corregir `Raspberry/CONEXIONES.md`. No
habilitar PWM ni declarar estabilidad con la observación preliminar del Uno.

### Captura de referencias por postura, 100 muestras — 7 de octubre de 2026

El operador aportó estadísticas de 100 lecturas por articulación para fémures
(adelante/atrás), coxas (arriba/abajo) y tibias (adelante/atrás). Aclaró que
servos/patas 1 y 2 son delanteros. Los datos completos quedan en
`Raspberry/configuracion/as5600_caracterizacion_provisional.yaml`, bajo
`operator_posture_samples_2026_10_07`, y resumidos en
`Raspberry/RESUMEN_CARACTERIZACION_AS5600_2026-09-28.md`. Son ángulos absolutos
del imán, no límites de servo/PWM ni topes mecánicos calibrados. Destaca fémur 3
variable (15,820° de rango comunicado en postura adelante) y coxa 3 con 0,791°
en ambos estados. La captura se conserva separada del dataset previo de 20
muestras; no modifica la autorización de control, que continúa desactivada.

### Registro de transferencia a Raspberry — comprobado el 7 y asentado el 14 de octubre de 2026

Se recuperó la conexión SSH al hostname `cuadrupedo-pi.local`, IP observada
`10.150.110.198`; la clave SSH conocida fue aceptada y se actualizó el alias
local `cuadrupedo-pi` para resolver el hostname mDNS, ya que la IP anterior
rechazaba conexiones. Se verificó la conexión por alias, hostname e IP. Esto no
implica una prueba nueva de sensores ni de actuadores.

Para compartir los datos de estabilidad y las referencias angulares se creó
`Nuevo.md` y se copió, sin reemplazar archivos, a la raíz del checkout de la
Raspberry (`/home/pavilion/nova-spot-micro-tesis/Nuevo.md`). También se copiaron
`Raspberry/AVANCES_2026-10-07.md` y una copia fechada del dataset a
`Raspberry/configuracion/as5600_caracterizacion_2026-10-07.yaml`. Los hashes
SHA-256 remoto/local coincidieron: `Nuevo.md`
`38f0a0e371a3727552ef151f7f3fc519dec31f0c60444fb492e62c76ab6326d1`, informe
`4366ec67fc809f7023ef153b6e8cfe7e557c3dd097aea59d0c0cbff74755fbf2`, y YAML
`4de8926f13b71189d923aa40a8db0fbdd5ff2ec46cfeac693ca31c057cf40bfc`. El YAML
se pudo leer en la Pi y contiene 24 combinaciones articulación/postura, con 100
muestras por combinación.

Se transfirió además el archivo exacto `/home/pavilion/CODIGO/CODIGO.ino` a
`Raspberry/codigo/arduino_uno_12_as5600_estabilidad_2026-10-07.ino`; SHA-256
`52902c829c52cede932ee94a60b3c8c34e3f6d7f9fbe0d90d4ffc88bdfbc9f14`, igual en
origen y destino. El sketch usa `Wire`, TCA `0x70`/`0x71` y AS5600 `0x36`; toma
100 muestras de los 12 sensores, calcula mínimo/máximo/promedio/variación y no
contiene control PWM de servos. No se compiló ni ejecutó en la Pi; para correrlo
debe cargarse en un Arduino Uno conectado al equipo que lo programe.

Permanece una discrepancia importante: ese sketch asigna COXA 2 a `0x71`/canal
5 y FEMUR 2 a canal 6; `Raspberry/CONEXIONES.md` los asigna al revés. No cambiar
el mapa ni usar los nombres del sketch como identificación física definitiva
hasta comparar de forma pasiva canales 5/6 y confirmar el sensor correspondiente.
Las lecturas de postura son grados absolutos del imán, no topes certificados ni
límites PWM.

La verificación de `git status` en la Pi no fue posible porque su checkout tiene
un objeto suelto vacío/corrupto (`3900eddc17c8b0cff441a4884673fa3fa2762299`).
Por eso se copiaron archivos nuevos sin pisar los existentes, pero no se hizo
commit en la Pi. En este computador se preservan los cambios preexistentes; no
se agruparon en un commit para evitar incluir trabajo ajeno a esta actualización.
Siguiente paso técnico: revalidar estado seguro y obtener lecturas pasivas de
`0x71` canales 5/6 con identificación física confirmada; no enviar PWM.

### Pruebas con el Uno/PCA9685 y secuencia parcial tipo paso — 15 de octubre de 2026

El Uno está conectado como `/dev/ttyACM0`; el entorno aislado inicialmente
ocultaba el puerto. Se preparó y verificó en flash una orden `z` para tibia 3
(CH10), 100°→102°→100°→98°→100°. Sesión 77: C11 quedó entre 313–322 cuentas
en este tramo local; no se cruzó 104°. Sesión 78 terminó con las salidas en
`OFF`. Los datos completos están en
`CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite` y el análisis en
`CODIGO/datos_aprendizaje/INFORME_IDENTIFICACION_2026-10-15.md`.

A petición del operador se añadió y ejecutó una secuencia exploratoria `y`,
dos alternancias diagonales de ±2° sobre cozas 2–4 y fémures 1–4 (PCA CH1–CH7).
Coxa 1 (CH0) se omitió por su bloqueo de calibración; tibias 1–4 (CH8–CH11) y
CH12 permanecieron apagados. Sesión 79 almacenó 101 tramas y terminó `OFF`.
No se trata de locomoción apoyada ni de ejecutar PPO: al congelar tibias se
altera cualquier política de 12 articulaciones y las patas no pueden completar
el ciclo de levantar/apoyar. Las evaluaciones PPO guardadas no seleccionaron
una política física; no transferir a marcha en suelo. El robot se trató como
suspendido durante esta demostración breve.


### Intento de pruebas desde el Uno — 16 de octubre de 2026

El Uno tenía grabado otro sketch, "Lectura de servos y feedback". No hay fuente local; transmite a 9600 baudios y al arrancar manda PWM a CH0 = 150°, CH4 = 40° y CH8 = 55°. Se respaldó su flash y se volvió a grabar `movimiento_suspendido_11_servos`, que arranca en OFF. Tras la grabación verificada, el Uno se desconectó del USB (14:11:46) y no reapareció. No se ejecutó ninguna prueba de movimiento. Detalle: `CODIGO/datos_aprendizaje/INFORME_IDENTIFICACION_2026-10-16_sesion_claude.md`.

### Verificación posterior de MUX y telemetría — 16 de octubre de 2026

En una comprobación posterior, el Uno volvió a aparecer como `/dev/ttyACM0`
(Arduino Uno R3). Se capturaron 71 tramas `DATA` válidas, todas en estado
`OFF`, sin enviar orden de movimiento. La comunicación USB/serial está activa;
sin embargo, las lecturas ADC de C0–C15 quedaron entre 0 y 1 cuentas en todas
las muestras. Por tanto, en esta captura no se reciben señales analógicas
útiles de los potenciómetros a través del MUX. La causa aún no está aislada
(posibles alimentación de servos/MUX, tierra común, SIG/EN o cableado). No se
movió ningún servo. Datos: sesión 87 de
`CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite`; análisis en
`CODIGO/datos_aprendizaje/INFORME_IDENTIFICACION_2026-10-15.md`.

### Diagnóstico I²C y caminata en el aire desde el Uno — tarde del 16 de octubre de 2026

- En el bus I²C del Uno solo responde el PCA9685 (`0x40`). `0x70` era su dirección All Call (se desactivó el bit ALLCALL como prueba). Ningún TCA9548A ni AS5600 llega al Uno.
- El multiplexor analógico 16CH va cableado con S0=D7, S1=D6, S2=D5, S3=D4, SIG=A0 y EN=GND (diagrama del operador). El firmware `movimiento_suspendido_11_servos` se actualizó a esos pines. Los potenciómetros no dan señal individual válida desde la sesión 83 (sospecha: falta su alimentación de 5 V).
- Nueva orden `b`: gateo en el aire, en lazo abierto, orden FL→RR→FR→RL. Se ejecutó en las sesiones 85 (fémures ±6°), 88 (±10°/tibias 8°) y 89 (±15°/tibias 14°), todas terminadas en `OFF`. El operador confirmó que se movió bien. Coxa 1 y CH8 siguen sin PWM. No está validada para el suelo.
- Detalle: `CODIGO/datos_aprendizaje/INFORME_IDENTIFICACION_2026-10-16_sesion_claude.md`.
- Tibias reconectadas (16 de octubre, confirmación visual del operador): T1 = CH8 (C8 poco fiable), T2 = CH12 (C9), T3 = CH9 (C11), T4 = CH11 (C10); CH10 vacío. Selectores del MUX analógico verificados en D8–D11. Firmware actualizado.
- Caminata `b` estable (16 de octubre, sesión 135): gateo de 10 ciclos, fémures ±15°, tibias 14° (T4 invertida, 56–70°), 0,5 s por fase. Coxas fijas en su equilibrio C1=150°, C2=45°, C3=55°, C4=150°, con corrección realimentada filtrada en las coxas 2–4 (±6°, una corrección cada 200 ms). Termina con las coxas sostenidas. El operador confirmó que la coxa 2 mejoró muchísimo. Respaldo: `CODIGO/movimiento_suspendido_11_servos/caminata_estable_20261016.hex`.

### PPO entrenado con datos reales del robot — 16 de octubre de 2026
Con las caminatas `b` registradas por los sensores del MUX se identificó el actuador real: 100 ms de retardo; ganancia 0,88–0,98 en F2, F4 y T2; T4 casi sin movimiento; T1 sin PWM. Se creó `Experimentos/entrenamiento_real_20261016/entrenar_ppo_real.py`: la marcha nominal es la caminata `b` real, con coxas fijas y una observación limitada a lo medible por el Uno. Se entrenaron cinco semillas (11, 23, 37, 53 y 71) de 150 000 pasos. Todas superan el avance nominal (0,173 m). La semilla 11 mejora a la vez avance (0,299 m), deriva (0,046 m frente a 0,111 m) e inclinación (0,097 rad frente a 0,128 rad). Es un resultado de simulación, evaluado con las semillas de desarrollo 801–805; no se ha transferido al robot. Detalle en el `INFORME.md` de esa carpeta.
- Primera ejecución en el robot real (robot suspendido): modo `@` del firmware y programa `ejecutar_politica_robot.py`. Nominal y PPO semilla 11 completaron 4 ciclos; F2, F4 y T2 siguieron la orden con r ≥ 0,98 y error ≤ 0,6°. Periodo real ~29 ms (entrenamiento con 20 ms). Pendiente valorar avance y estabilidad apoyado, porque no hay IMU.
- Tarde del 16 de octubre: identificación por escalones y senoides (zona muerta ~0,5–1°, retardo de 65–85 ms, buen seguimiento hasta 1 Hz; T4 sí se mueve; sensor de T3 inservible). Con el actuador v3 corregido, la caminata nominal simulada camina casi recta (deriva 0,010 m) y el PPO solo cambia rectitud por velocidad (semilla 71: 0,284 m de avance, 0,052 m de deriva). Detalle en `Experimentos/entrenamiento_real_20261016/INFORME.md`.
- Noche del 16 de octubre: el barrido de la caminata base eligió fémur 15°, tibia 10° y fase de 0,5 s, más estable. El PPO v4 orientado a estabilidad (semilla 37) redujo en simulación la deriva un 54 % y la inclinación un 31 % respecto a esa base. Ambas se ejecutaron en el robot suspendido con error ≤ 0,7°.
- Firmware del Uno: topes absolutos por canal en escribirServo() a partir de los límites medidos por el operador (margen de 10°; límite trasero de T2 = 100°).
- Barrido de rango ±40° con sensores: relación ADC-ángulo lineal (≈2,5 cuentas/°, error RMS 0,4–1,1°), histéresis de 0,6–1,5°; F2 y F4 se saturan por encima de ~135° y T4 por encima de ~105°. Topes del firmware ajustados y modelo de actuador v4 guardado.
- PPO v5 (actuador v4) no mejora la base. En evaluación cruzada, PPO v4 semilla 37 se mantiene robusta (−28 % de inclinación, misma deriva) y queda como política elegida. En el robot ejecuta el 99–100 % de la corrección en los fémures y el 71 % en T2.

### Migración del control a la Raspberry Pi — 18 de octubre de 2026
El PC y la Pi estaban en routers distintos con el mismo SSID (`F_DIAZ_D_5G`): la Pi en 192.168.0.100, detrás del segundo router. Con el PC conectado por cable a ese router (192.168.0.126), SSH funcionó. La clave de host se verificó (ED25519 `SHA256:mTERAysLSgm2Xlw36tOoV0uv5gC3vj7Xoycel2xe16M`) y el alias `cuadrupedo-pi` apunta ahora a 192.168.0.100.

Estado de la Pi: Ubuntu 22.04.5 aarch64, 4 núcleos, 7,6 GB de RAM, Thonny 3.3.14, smbus y RPi.GPIO instalados. Sin torch ni SB3. Bus I²C vacío: el PCA9685 todavía está conectado al Uno. El repositorio antiguo `~/nova-spot-micro-tesis` sigue corrupto y se conserva como respaldo.

Se copió el proyecto a `~/Cuadrupedo` en la Pi (351 MB, historial de Git sano hasta 67c48e3, sin el venv ni los datos pesados). Se creó `Raspberry/thonny/`: `robot_nova.py` (lógica del firmware del Uno en Python), `caminata_thonny.py` (menú para Thonny) y la política PPO v4 semilla 37 exportada a NumPy. Probado en modo simulado en el PC y en la Pi; la corrección PPO coincide con la del PC (diferencia ≤ 0,5° por redondeo).

Pendiente para usar la Pi sin Arduino:
- cablear el PCA9685 a la Pi;
- añadir un ADC I²C (ADS1115) para los potenciómetros, porque la Pi no tiene entradas analógicas. Sin él no hay realimentación ni política PPO.
- 18 de octubre: se reunieron en `~/Cuadrupedo` (Pi y PC) todos los avances. Incluye los archivos que solo estaban en la Pi: sketches de Arduino, scripts de Thonny, datos AS5600 del 7 de octubre, mapas PWM y de conexiones, fotos y registros de ensayos de agosto, más los pendientes locales de septiembre y octubre.
- 18 de octubre: se eliminó `~/nova-spot-micro-tesis` de la Pi y solo queda `~/Cuadrupedo`. Respaldo completo en `Raspberry/respaldo_nova-spot-micro-tesis_20261018.tar.gz`. Las 12 versiones editadas en la Pi el 7 de octubre, más recientes que las de Cuadrupedo, están en `Raspberry/versiones_pi_20261007/`, pendientes de revisar.
- 18 de octubre: el operador autorizó desde la pantalla de la Pi: (1) se borró `~/nova-spot-micro-tesis`, de modo que solo queda `~/Cuadrupedo`; (2) `sudo` sin contraseña para `pavilion` (`/etc/sudoers.d/90-pavilion-nopasswd`, validado con visudo). Para revertirlo, borrar ese archivo.
- 18 de octubre: conexión fácil del PC a la Pi. `ssh cuadrupedo-pi` usa el ProxyCommand `~/.local/bin/conectar-cuadrupedo-pi` (copia en `scripts/`): prueba el nombre mDNS `cuadrupedo-pi.local` (funciona en la misma subred, ~0,5 s), luego la última IP conocida, luego un túnel en localhost:2222 y, por último, escanea las redes /24 del PC (~7 s). Solo acepta la huella ED25519 de la Pi. El túnel inverso Pi→PC (para cuando el PC está en el router principal) quedó pendiente de autorización.

### Diagnóstico y configuración de la Raspberry — 18 de octubre de 2026
**Diagnóstico.** Hay bajo voltaje en los 6 arranques registrados (`throttled=0x50000`: hubo bajo voltaje y reducción de frecuencia). El 17 de octubre a las 12:52 hubo dos arranques fallidos seguidos, que terminaron justo después de un aviso de bajo voltaje. Es la causa probable de que la Pi no arrancara y hubiera que reinsertar la SD. La SD (genérica "SD32G", 2019) está limpia, sin errores ext4, pero no se revisaba desde 2024. Un arranque normal tarda 30 s y la temperatura es de 49 °C.

**Configuración aplicada** (respaldos en `/root/respaldo_config_20261018`):
- `fsck` forzado en el próximo arranque y cada 20 arranques (`tune2fs -c 20`);
- registros del sistema limitados a 100 MB (`/etc/systemd/journald.conf.d/50-limite-sd.conf`; de 577 MB pasaron a 113 MB);
- `arm_boost=1` desactivado en `config.txt` para bajar el consumo pico;
- actualizaciones automáticas desactivadas;
- `pavilion` añadido a los grupos `i2c` y `video` (ya tenía I²C y GPIO por `dialout`);
- aviso de bajo voltaje al iniciar sesión (`/etc/profile.d/aviso_voltaje_cuadrupedo.sh`).

**Pendiente (hardware):** fuente oficial de 5,1 V / 3 A con cable USB-C corto, alimentación separada de los servos y SD de marca nueva (A1/A2). Los cambios de `config.txt` y el `fsck` se aplican en el próximo reinicio.
- 18 de octubre, 20:34: reinicio controlado. La Pi volvió en ~50 s con SSH por clave, sin pedir nada. El fsck se ejecutó (contador de montajes a 1, estado clean), arm_boost quedó desactivado y hay inicio de sesión automático de pavilion en el escritorio (`/etc/gdm3/custom.conf`, respaldo en `/root/respaldo_config_20261018`).
- 19 de octubre: tibias en CH8–CH11 (T1 reparada), equilibrio de las coxas 159/45/54/112 y selectores del MUX en D4–D7 (D4 = bit de menor peso). La caminata base de 10 ciclos sigue bien: F2 C5 r = −0,99, F4 C6 r = −0,98, T2 C9 r = −0,89; coxas a ~1° de su equilibrio.
- 19 de octubre: prueba de cámara para medir el cuerpo del robot. La webcam del PC (HP Wide Vision HD, /dev/video1) captura MJPEG 1280×720 a 30 fps; se ve el cuadrúpedo, pero con contraluz de la ventana y pequeño en la imagen. Se generó `Experimentos/camaras/marcadores_y_tablero_camara.pdf`: 6 marcadores ArUco DICT_4X4_50 de 50 mm (ID 0–3 para el cuerpo, 4–5 para el suelo) y un tablero de calibración 9×6 con cuadros de 25 mm. Plan: dos portátiles fijos (lateral y frontal), calibración y medición de roll, pitch, avance y deriva sincronizadas con las caminatas.
- Programas de cámara en `Experimentos/camaras/` (19 de octubre): `calibrar_camara.py` (tablero 9×6, toma automática de fotos en posiciones distintas), `grabar_caminata.py` (graba con ffmpeg 1280×720 a 30 fps mientras `ejecutar_politica_robot.py` camina; guarda las horas de inicio de los dos para sincronizar) y `analizar_video.py` (pose ArUco por fotograma, referencia de suelo con ID 4/5; roll y pitch RMS/máximos, avance y desvío por ciclo). Probado: grabación real (111 fotogramas en ~3,7 s) y video sintético con roll conocido de ±10° y avance de 0,020 m → avance 0,020 m exacto y roll RMS 7,7° (esperado 7,1°; ~1–3° de error sin calibrar).
- Segundo portátil para cámara (19 de octubre): Ubuntu 22.04, usuario yireth, conectado por Ethernet directo (este PC 10.0.0.1 en el perfil «Directo-PC2», el otro 10.0.0.2 en «Directo-PC1»). Alias SSH `pc2-camara` con clave ~/.ssh/pc2_camara_ed25519; huella ED25519 SHA256:SILtuBVidNAFBW4z6ac9n4QNyanxS5H++25tk6eepm8. Cámara HP Wide Vision HD en /dev/video0; captura 1280×720 probada. `grabar_caminata.py` graba con las dos cámaras (la remota por SSH, parada con «q»; prueba de 3,5 s → 92 fotogramas) y guarda el desfase de reloj (+0,067 s) para sincronizar.
- 19 de octubre: dos cámaras laterales (este PC /dev/video1 y pc2-camara /dev/video0). Primera grabación simultánea con caminata base de 4 ciclos (`Experimentos/camaras/grabaciones/prueba_dos_camaras`): 765 y 757 fotogramas, desfase de reloj +0,085 s. Marcadores de articulaciones de 25 mm (ID 10–19) en `marcadores_articulaciones_25mm.pdf`, pendientes de pegar. Resumen de todo el proceso del 16 al 19 de octubre en `Seguimiento/PROCESO_COMPLETO_2026-10-16_a_2026-10-19.md`; sketches del Uno copiados a `Arduino/sketches_uno_20261019/` y datos/informes a `Experimentos/entrenamiento_real_20261016/datos_uno/`.

### Dos marchas con PPO v10, diagnóstico y repetibilidad — tarde-noche del 19 de octubre de 2026
- Equilibrio de coxas vigente: 159/45/61/82 (coxa 4 colocada a mano por el operador; coxa 3 en 61: a 65-72 la pata 3 choca con la pata 1, detectable con `entrenamiento_real_20261016/choque_pata3.py`).
- Firmware: modo @ con todos los sensores (C0, C8, ENC_T1/T2 y respaldos ENC_F1/F4), I²C 400 kHz, compensación del desplazamiento común con C0. Ejecutor con respaldo de sensores (principal -> encoder -> orden retrasada 87 ms) y `caminata.config.json` por caminata.
- Marcha «paso» (continua, apoyo 75 %, ciclo 2,0 s, coxas fijas) además del gateo `b`. Políticas elegidas tras evaluar todas las copias en caminatas simuladas de 3 min (`seleccionar_copias.py`): gateo `ppo_v10_robot/gateo_semilla_11_300k`, paso `ppo_v10_robot/paso_semilla_71_2300k`.
- Cámaras: sincronía por primer fotograma (-copyts), `diagnostico_caminata.py`, `identificar_pata_camara.py`, `catalogo_caminatas.py` (catalogo.csv, ciclos.csv) y `analizar_repetibilidad.py`.
- Protocolo de repetibilidad sesión 20261019 PAUSADO a las 20:38 a petición del operador: hechas gateo_base r1, gateo_ppo r1-r2, paso_base r1-r2 (r1 sin cámara 2), paso_ppo r1-r2. Faltan gateo_base r2 y la ronda 3 completa. Para continuar (salta lo ya hecho):
  `cd Experimentos/camaras && python3 protocolo_repetibilidad.py --sesion 20261019 --repeticiones 3 --duracion-s 180 --pausa-s 30 --condicion gateo_base:gateo: --condicion gateo_ppo:gateo:ppo_v10_robot/gateo_semilla_11_300k/policy.zip --condicion paso_base:paso: --condicion paso_ppo:paso:ppo_v10_robot/paso_semilla_71_2300k/policy.zip`
  (o una sesión nueva con otro --sesion para repetibilidad entre días). Después: `python3 catalogo_caminatas.py && python3 analizar_repetibilidad.py --sesion 20261019`.
- Pendientes de hardware: encoder de la tibia 1 (TCA 0x70/0) intermitente; encoder de respaldo del fémur 4 (0x71/5) sin señal; cable Ethernet de la cámara 2 flojo; pegar marcadores ArUco 10-19.

### 20 de octubre de 2026 (mañana): 4 cámaras, ubicación por patas y bloqueo del bus I²C
- Cámaras (todas sincronizadas en grabar_caminata.py): HP de este PC /dev/video1 (frente), Logitech C170 /dev/video3 (lado izquierdo, `extra_logitech/`), celular DroidCam /dev/video0 (esquina delantera derecha, ~7,6 fps y 600 ms de retardo por Wi-Fi, `extra_celular/`), HP del portátil 2 (lado derecho, `remota/`). Ubicación deducida con `ubicar_camaras.py` (fémur senoidal y correlación píxel a píxel): `grabaciones/ubicacion_20261020_084658/`. La parte trasera del robot es la de la carcasa amarilla con ranura.
- Protocolo de repetibilidad: válidas r1 y r2 de las 4 condiciones (gateo_base_r2 marcada sospechosa). La ronda 3 falló (`*_r3_fallo_i2c`): el bus I²C del Uno quedó con SDA (A4) pegada a 0; 16 pulsos de recuperación no la liberan (`CODIGO/recuperar_i2c`) -> fallo físico (chip I²C sin VCC o SDA a GND). Firmware con `Wire.setWireTimeout(3000, true)`: ya no se cuelga si el bus se bloquea.
- Para seguir: revisar alimentación y SDA de PCA9685/TCA 0x70/0x71/AS5600, comprobar con `CODIGO/prueba_lineas_i2c` (SDA debe volver a 1 en ~10 µs), regrabar el firmware principal y repetir la ronda 3 (y gateo_base r2) con el comando del protocolo (salta las caminatas válidas).
- 20-oct 09:13-10:35: bus I²C con SDA a 0,10 V (tirada fuerte a GND, `CODIGO/diagnostico_bus_detalle`); se liberó al reajustar cables. Faltan los AS5600 de las tibias 1 y 2 (0x70/0 y 0x70/3; T2 volvió luego), sospechosos de cortocircuitar SDA con el movimiento. Después, saltos de cientos de cuentas en todos los potenciómetros solo con servos activos -> tierra común servos/Uno degradada; el operador la reforzó (desplazamiento común de 478 a 18-40 cuentas).
- Protocolo de repetibilidad sesión 20261019 COMPLETO (12 caminatas válidas; fallidas y sospechosas renombradas). Efecto día: hoy coxas ≈1,0-1,4° frente a ≈0,5° ayer en todas las condiciones; dentro del mismo día muy repetible (gateo base r2/r3: 1,24/1,22° patas). Comparar base/PPO dentro de un mismo día; para repetibilidad entre días, nueva sesión completa con el montaje estable.
- Cámaras: `vista_camaras.py` (ventana 2×2 en directo para encuadrar, tecla q). El celular por Wi-Fi baja a 1-7 fps al grabar: mejor por USB.
- 20-oct 10:40-13:42: sesión de repetibilidad 20261020 completa con 4 cámaras (las grabadas sin cámara 2 quedaron como `_3cam`). Tras cada caminata: diagnóstico, salud, `analizar_video_patas.py` (máscaras de patas por regresión píxel-orden, r y CV de amplitud por ciclo, movimiento no explicado) y `comprimir_videos.py` (MJPEG -> H.264, ~12x). Repetibilidad dentro del día: CV 3,7-10,7 % (gateo PPO 3,7 %, paso base 3,9 %, gateo base 8,0 %, paso PPO 10,7 %). El portátil 2 tenía un ffmpeg colgado desde el disco lleno (35,8 GB); `grabar_caminata.py` ahora lo cierra antes de grabar.
- 20-oct tarde: paso v11 (recompensa con suavidad 0,3 y coxas 1,0; `ppo_v10_robot/ppo_v11_paso_semilla_71_4900k`) frente a paso base en el robot, 3 rep. con 4 cámaras (sesión 20261020v11): base error 1,62-1,64° y coxas 1,47-1,50° (CV 2,4 %); v11 1,71-1,80° y 1,51-1,63° (CV 3,5 %). La v11 mejora a la v10 pero no supera a la base en el robot.
- El operador ve el paso igual al gateo (ambos de 4 tiempos, una pata en el aire; con coxas fijas el paso es un gateo continuo). Nueva marcha «trote» (pares diagonales FL+RR / FR+RL, factor de apoyo 0,5, ciclo 1,0 s, fémur ±12°, tibia 12°; `--marcha trote`). Probada en el robot (`trote_base_prueba_1min`): fémures r 0,92-0,985 y error ~3°, coxas 1,8-2,3°. Video del trote analizado por pares diagonales. PPO del trote entrenando en `ppo_trote/` (8 semillas, recompensa v11).
- Celular (LG-M700): depuración USB autorizada, `adb shell svc power stayon true`; el hub USB VIA desconecta el teléfono; en 1080p no pasa de ~4-15 fps (bajar resolución en la app DroidCam).
- 20-oct 17:00: geometría medida por el operador -> `src/nova_sm3_description/mujoco/nova_sm3_real.xml` (fémur 108 mm, tibia 135 + 20 mm de pie = 155 mm, coxa 35 mm, caderas 190 × 77 mm, cuerpo de 265 mm; robot completo 265 × 228 × 280 mm; el modelo da 228 mm de ancho y ~274 mm de alto). `entrenar_ppo_real.py` usa ya este modelo (el original `nova_sm3.xml` queda como referencia). Pendiente: ángulos reales con los servos en su base (fémur respecto a la vertical, ángulo de rodilla, coxa) y escala de los servos. El trote se reentrena con el modelo real (`ppo_trote/`; el anterior en `descartados_20261019/ppo_trote_modelo_antiguo`).

### 20 de octubre de 2026 (tarde-noche): trote, geometría real, postura abierta y calibración por pata
- **Marchas:** gateo `b` y **trote** (pares diagonales FL+RR / FR+RL, ciclo 1,0 s, fémur ±12°, tibia 12°; `--marcha trote`). El «paso» se abandonó (con coxas fijas era un gateo continuo).
- **Geometría real:** `src/nova_sm3_description/mujoco/nova_sm3_real.xml` (fémur 108, tibia 155 hasta la punta, coxa 35, caderas 190 × 77 mm, cuerpo 265 mm). Lo usa `entrenar_ppo_real.py`.
- **Postura abierta** (`--apertura`, °): las patas de un mismo lado se juntaban bajo el centro. Con la geometría real, apertura 8° (gateo) y 5° (trote) suben el hueco mínimo entre pies de 69-93 a 133 mm y reducen la inclinación en simulación. Probado en el robot sin choques (`gateo_apertura8_1min`, `trote_apertura5_1min`).
- **Calibración por pata** (`entrenamiento_real_20261016/calibracion_postura.json`, aplicada por `ejecutar_politica_robot.py`): el operador ve con la tablet que el lado derecho (1-3) y el izquierdo (2-4) no quedan igual que en la simulación. Valor actual, ajustado a ojo: 1 +1°, 2 −3°, 3 −1°, 4 +3° (+ = pie hacia delante). `postura_calibracion.py` mantiene la postura y relee el archivo; `calibrar_postura_auto.py` (oscilación + cámaras laterales) NO fue fiable sin marcadores.
- **Siguiente paso recomendado:** pegar los marcadores ArUco 10-19 (`camaras/marcadores_articulaciones_25mm.pdf`: lado izq. 10 cuerpo, 11 F2, 12 T2, 13 F4, 14 T4; lado der. 15 cuerpo, 16 F1, 17 T1, 18 F3, 19 T3) y calibrar con `analizar_articulaciones.py`.
- **Entrenamientos en curso al cerrar (21:10):** `ppo_v13_gateo_abierto` (apertura 8) y `ppo_trote_abierto` (apertura 5), 5 semillas cada uno, 3 M pasos. Mañana: `seleccionar_copias.py --marcha gateo --carpeta ppo_v13_gateo_abierto` y `--marcha trote --carpeta ppo_trote_abierto`; luego `protocolo_repetibilidad.py --sesion 20261021 ... --condicion gateo_base:gateo::--apertura 8 --condicion trote_base:trote::--apertura 5 --condicion gateo_ppo:gateo:<elegida> --condicion trote_ppo:trote:<elegida>`.
- **Sesión 20261020real** (postura antigua, sin apertura): válidas gateo_base r1, trote_base r1-r2, gateo_v12 r1, trote_ppo r1 (el trote PPO sacude menos las coxas que la base). Interrumpida para cambiar la postura.
- **Cámaras:** 5 (HP PC, Logitech, celular por USB/adb con `svc power stayon`, portátil 2, tablet). Tablet: DroidCam en 192.168.0.105:4747 vía `camaras/tablet_puente.sh` -> /dev/video10 (v4l2loopback cargado con `pkexec modprobe v4l2loopback devices=1 video_nr=10 card_label=Tablet exclusive_caps=1` y `pkexec chmod 666 /dev/video10`; se pierde al reiniciar). `vista_camaras.py` (ventana 2×2; se cierra con q o la X). Protocolo: umbral de salud 0,8 para el trote. El cable Ethernet del portátil 2 se suelta a menudo.
- **Ampliación de semillas, 20-oct 21:50–22:07:** se programaron cinco semillas nuevas por marcha en `ppo_v13_gateo_abierto` (73, 89, 107, 127, 149) y `ppo_trote_abierto` (107, 127, 149, 173, 197), para aumentar de 5 a 10 semillas por marcha. Luego, a petición del operador, se añadió otra tanda de cinco por marcha: gateo (163, 181, 199, 223, 251) y trote (211, 229, 257, 277, 293), objetivo 15 por marcha. Todas están configuradas a 3 M pasos; gateo apertura 8°, trote apertura 5° con ciclo 1 s y amplitudes de fémur/tibia de 12°, penalizaciones v11 (`w-suavidad=0.3`, `w-coxas=1.0`). Se usa `.venv-mujoco/bin/python` y el modelo `nova_sm3_real.xml`; el intento inicial con el Python del sistema falló por no tener MuJoCo instalado y no modificó el entorno global. A las 22:07 las primeras cinco semillas nuevas de gateo iban por ~0,85–0,91 M pasos y las cinco de la segunda tanda acababan de iniciar (~0,005–0,006 M); las diez semillas nuevas de trote quedaron en cola en los procesos de entrenamiento. Las 10 semillas originales (5 por marcha) siguen incompletas, entre ~1,3 y 1,8 M pasos; no hay políticas finales aún. No seleccionar semillas hasta completar y evaluar.
- **Estado comprobado 20-oct 22:15:** las cinco semillas nuevas de gateo de la primera tanda (73, 89, 107, 127, 149) siguen activas y van por 1,27–1,36 M/3 M; las cinco de la segunda (163, 181, 199, 223, 251), por 0,40–0,41 M/3 M. Las cinco semillas originales de gateo están pausadas en 1,30–1,83 M (última traza 21:12); las cinco originales de trote, pausadas en 1,30–1,68 M (última traza 21:12). Aún no se han creado las carpetas de las 10 semillas nuevas de trote: están en cola hasta que termine su tanda de gateo. Ninguna tiene `policy.zip` final todavía.
- **Tablet S10 FE configurada por USB, 20-oct 22:53:** ADB autorizado y modelo identificado como SM-X520 (`gts10fewifixx`); `com.dev47apps.obsdroidcam` instalada y abierta. Se activó `svc power stayon true`. Se creó `/dev/video10` con `v4l2loopback` (separado del `/dev/video0` del celular) y el cliente `droidcam-cli -dev=/dev/video10 -size=1280x720 -nocontrols adb 4747` está activo. FFmpeg leyó 10 fotogramas a 1280×720/30 fps y el análisis de señal dio luminancia media 101,7 (imagen no negra). `Experimentos/camaras/camaras_extra.json` ahora asigna `tablet` a `/dev/video10` en YUV420P; prueba sintáctica JSON correcta. El nodo virtual y el cliente no sobreviven reinicio; para futuras sesiones hay que cargar `v4l2loopback` de nuevo y arrancar el cliente. La antigua `tablet_puente.sh` sigue como ruta Wi-Fi alternativa, pero ya no es la entrada elegida en `camaras_extra.json`.
- **Visor 2×2 abierto, 20-oct 22:57:** `vista_camaras.py` ahora muestra las cuatro cámaras locales: HP integrada `/dev/video1`, General Webcam `/dev/video3`, Logitech C170 `/dev/video5` y tablet `/dev/video10`; el celular `/dev/video0` queda fuera del mosaico. Se corrigió salida inmediata: esta compilación GTK devuelve `-1` en `WND_PROP_VISIBLE`, no debe interpretarse como ventana cerrada; se añadió cierre ordenado de lectores. El proceso está activo; cerrar con `q` o `Esc` para liberar las cámaras.

### Cierre de sesión y estado de entrenamientos — 20 de octubre de 2026
- A petición del operador se detuvieron temporalmente el visor `vista_camaras.py` y el cliente `droidcam-cli` de la tablet. Se verificó que ambos procesos terminaron. Esto libera las capturas en el PC; no apaga ni desconecta físicamente las cámaras, y para reanudar la tablet hay que volver a iniciar DroidCam/cliente y el visor.
- **Gateo PPO v13 con postura abierta:** campaña `Experimentos/entrenamiento_real_20261016/ppo_v13_gateo_abierto`. Diez semillas (73, 89, 107, 127, 149, 163, 181, 199, 223, 251) completaron 3.000.320 pasos cada una. Evaluaciones guardadas para cinco semillas (801–805), en `semilla_*/evaluacion.csv`. En la condición PPO ninguna de las cinco pruebas por semilla registró caída. Resultados PPO medios por semilla: avance 0,132–0,469 m; deriva lateral 0,008–0,178 m; inclinación máxima 0,122–0,316 rad. Mejor avance: semilla 149 (0,469 m); mejor retorno: semilla 127 (46,2). No se ha ejecutado aún selección final de política; desempeño no constituye aceptación ni transferencia.
- **Trote PPO con postura abierta:** campaña `Experimentos/entrenamiento_real_20261016/ppo_trote_abierto`, 15 semillas (19, 31, 37, 47, 89, 107, 127, 149, 173, 197, 211, 229, 257, 277, 293). No había procesos de entrenamiento activos al cerrar. Las trazas quedaron incompletas: las semillas 107/127/149/173/197 están en 2,267–2,478 M pasos; el resto en 1,298–1,684 M de 3 M. No hay campaña completa/evaluación final para seleccionar.
- Al revisar `ps` no se encontraron procesos PPO/MuJoCo activos. Próxima acción al reanudar: comprobar trazas y procesos; completar las 15 semillas de trote hasta 3 M; después evaluar/seleccionar ambas campañas (`seleccionar_copias.py`) antes de iniciar repetibilidad física. Mantener `hardware_transfer=false`; no transferir una política solo por estos resultados de simulación.

### 21 de octubre de 2026: 5 cámaras, calibración de postura, ciclo de mejora en el robot
- **Cámaras (5):** HP local, Logitech y General (USB 2.0 directo, rutas /dev/v4l/by-id), portátil 2 (pc2-camara, 10.0.0.2) y PC Windows «David-Diaz» (pc-windows, 10.0.0.3 fija por netsh, graba H.264 en su disco y se trae; reloj −0,5 s medido por caminata). `vista_camaras.py` (cuadre 3+2, robot quieto) y `vista_vivo.py` (en vivo durante las caminatas, imágenes en `camaras/vivo/`). Identificación de patas por colores (`analizar_colores_patas.py`; fémur rojo, tibia verde, pie amarillo, suela roja vista desde abajo) y prueba de identificación (`grabar_caminata.py --ejecutor identificar_patas_robot.py`).
- **Errores corregidos:** tibias izquierdas con el signo invertido (SIGNO_TIBIA {1:-1,2:1,3:-1,4:1}); el ejecutor respeta los topes del firmware (T2 ≤ 90°, T4 ≤ 105°); postura base por pata con fémur y tibia (`calibracion_postura.json`, `calibrar_postura_colores.py`); sensores recalibrados para la postura nueva (la cámara confirmó ganancia del motor ≈ 1). Tibia 3: potenciómetro C11 sin señal (el servo sí se mueve) -> `sin_sensor`, se estima con la orden. Tibia 1: ENC_T1 sin lecturas en todas las caminatas.
- **Temporización:** los trotes «degradados» de las 19:34 y 19:51 eran el PC sobrecargado (448-714 pasos > 40 ms). Ahora el bucle de control usa los núcleos 0-1, la red PPO 1 hilo, análisis a prioridad mínima: 0 pasos tardíos con el PC entrenando.
- **Ciclo de mejora** (`camaras/ciclo_mejora.py`, estado en `ciclo_mejora.json`): prueba en el robot, puntuación con sensores, el robot enseña a la simulación (`actualizar_modelo_real.py` -> `actuadores_ciclo<N>.json`: retardo 99 ms, holgura ~0,4°, brecha robot-modelo 1,8°) y reentrenamiento. Puntuación (° medios, menor = mejor):
  vuelta 1: gateo base 1,87 / PPO v14 1,52; trote base 1,69 / PPO 307 1,67.
  vuelta 2: gateo base 1,49 / v14 1,26 / ciclo1-401 1,31; trote base 2,36 / PPO 307 1,92.
  vuelta 3 (incompleta, solo gateo): base 1,66 (1 rep) / v14 1,63 / **ciclo2-401 (entrenada con el modelo medido) 1,24** (1 rep válida).
- **Al final del día el robot se degradó:** el Arduino se reinició en un trote (22:22, probable caída de tensión) y los fémures 2-4 bajaron a r ≈ 0,88-0,93 sin carga de CPU. Revisar alimentación (Arduino separado de la fuente de servos, masas unidas) antes de seguir con trote. Portátil 2 sin red desde ~20:24 (suspendido o sin batería; hay un vigilante que le quita la suspensión al volver).
- **Siguiente:** `cd Experimentos/camaras && python3 ciclo_mejora.py --vueltas 2` (retoma con las candidatas de `ciclo_mejora.json`; la mejor de gateo es `ppo_v10_robot/ppo_ciclo2_gateo_semilla_401_2400k`).

### 22 de octubre de 2026: tesis actualizada y error de semillas
- Tesis (`Documento_TESIS`, 112 páginas): PPO a detalle en el marco teórico, capítulos nuevos «Plataforma física, instrumentación y adquisición» (9a) y «Entrenamiento de las políticas PPO para el robot físico» (9b), resultados en el robot suspendido, figuras `ppo_curvas_semillas.png` y `ppo_ciclo_robot.png` (`generar_figuras_ppo_fisico.py`), y resumen, alcance, metodología, discusión, conclusiones, trabajo futuro y anexos actualizados. Arquitectura presentada con la Raspberry Pi 4; el Uno solo como «interfaz de E/S auxiliar» en los ensayos de octubre. `compilar.sh` hace pdflatex + biber + pdflatex ×2 (latexmk elegía bibtex).
- **Error encontrado:** al continuar un entrenamiento (`--continuar`), `PPO.load` restauraba la semilla guardada en la política e ignoraba `--seed`; las 4 semillas (401, 409, 419, 421) de `ppo_ciclo1_*` y `ppo_ciclo2_*` dieron ejecuciones idénticas (una sola ejecución en la práctica). Corregido en `entrenar_ppo_real.py` (`model.set_random_seed(a.seed)` tras cargar) y verificado. Las campañas v11, v12, v14 y v15 continuaban políticas distintas y no se ven afectadas.

### 26 y 27 de octubre de 2026 — sensores, paso v16 y v17

- Revisión articulación por articulación (`revisar_sensores.py`, modo `$` del firmware con 16 canales del
  MUX y 16 encoders; escaneo I²C con `^`). Tibia 1: servo intermitente (pasado de CH8 a CH12), potenciómetro
  M7 en 0, encoder vivo en 0x70/0. Encoder del fémur 2 en 0x70/4 (campo ENC_T1). Conexiones flojas: en cada
  manipulación fallaban sensores distintos (fémures 2-4, encoders 0x71/4-5); el bus I²C se cortó dos veces.
- Paso v16: elegida semilla 563 a 1,6 M (simulación: deriva 0,021 m frente a 0,391 m nominal, avance −12 %).
  Paso v17 (4 semillas continuando la 563): ninguna la supera (mejor 2,50 frente a 2,45).
- Robot (sesión `paso_v16d`, protección de salud desactivada a pedido del operador): 3 repeticiones válidas
  por condición; la ronda 4 se cortó a los 3 s por falta de memoria (análisis de video con 5 procesos;
  limitado a 2 el 27-oct). v16 r3 inválida (coxas 80°, saltos del MUX). En las articulaciones con sensor
  fiable (fémures 1 y 3, tibias 2 y 4) la v16 no mejora a la nominal (diferencias de ±0,4°).
- Siguiente acción: asegurar conexiones (masa y 5 V del MUX, conectores con traba) y repetir el paso v16.

### 27 de octubre de 2026 — postura de trabajo nueva y repositorio para la Raspberry

**Postura y movimiento aprobados por el operador (base de trabajo desde ahora):**

| Articulación | Apoyo (servo) | Recorrido al dar el paso | Cambio |
|---|---|---|---|
| Coxa 3 | 64° | fija | antes 61° (se veía caída) |
| Tibia 1 | 40° | 40 → 20° (ganancia 2,0) | tope mínimo 25 → 18 |
| Tibia 2 | 166° (BASE) | 166 → 180° (ganancia 1,4) | antes apoyo 76° y movimiento contrario |
| Tibia 3 | 82° | 82 → 66° (ganancia 1,6) | más recorrido |
| Tibia 4 | 144° (BASE) | 144 → 162° (ganancia 1,8) | antes apoyo 91° y movimiento contrario |

- Las tibias 2 y 4 se mueven en sentido de servo opuesto al de la 1 y la 3 (`SIGNO_TIBIA = {1: −1, 2: +1, 3: −1, 4: +1}`);
  su apoyo es ahora su BASE en firmware y ejecutor (`BASE = [159, 45, 64, 82, 110, 100, 100, 100, 100, 166, 100, 144]`),
  con offsets de tibia 0. `ganancia_tibia` en `calibracion_postura.json` amplía el movimiento de cada tibia; la lectura de
  sensores se divide por la misma ganancia, así la política PPO ve el ángulo del modelo.
- Topes nuevos: tibia 2 (CH9) 155-180, tibia 4 (CH14) 130-175, tibia 1 (CH12) desde 18.
- Se llegó a esta postura con `sostener_tibias.py` (tibias sostenidas en ángulos pedidos, cambio en vivo) y caminatas de
  60 s de gateo, trote y paso grabadas con 5 cámaras (`grabaciones/*_tibiasrec_1112`, `gateo_postura_final*`).
- **Consecuencia:** todas las caminatas del robot anteriores al 27-oct tenían las tibias 2 y 4 en otra postura y moviéndose
  al revés; además gateo v14 y trote v15 se ejecutaban sin la apertura de fémures (metadata dañada por
  `seleccionar_copias.py`, corregido y reparado). Las comparaciones PPO/nominal anteriores deben repetirse.

**Otros cambios del día:**
- Firmware: IMU BNO055 (0x28; 7 campos tras ENC_F4 en la respuesta R), modo `$` (16 canales MUX + 16 encoders), `^` (escaneo I²C).
- `grabar_caminata.py`: `--solo-camaras` y `--remoto-pi` (caminata en la Raspberry por SSH, registro traído y sincronizado).
- `analizar_video_patas.py` limitado a 2 procesos (la noche anterior dejó al PC sin memoria).
- Repositorio nuevo `~/Documentos/nova_caminata_pi` (git propio): caminar.py, analizar.py, marchas idénticas al
  entrenamiento, políticas gateo v14, trote v15 y paso v16 en NumPy, CLAUDE.md para Claude en la Pi. Pendiente de copiar
  a la Raspberry (no aparecía en la red).

### 27 de octubre de 2026 (noche) — galope, carrera y viabilidad

- Marchas nuevas: galope transverso (apoyo 0,40, ciclo 0,8 s, fémur 16°, tibia 14°; coxas traseras se abren 4° al
  levantar, delanteras fijas: con la coxa 2 moviéndose cedía y la 4 a 8° rebotaba; con una delantera fija y la otra
  moviéndose el galope retrocedía en simulación) y carrera (pares diagonales con apoyo 0,45, ciclo 0,8 s).
- Firmware: modo `+` (coxas con órdenes) con corrección de caída por peso calculada con la pata apoyada.
- `evaluar_viabilidad.py`: % de 20 episodios (semillas 1001-1020, aleatorización de dominio y actuador) en que la
  política no cae, avanza ≥ 90 % de la nominal, se desvía menos que ella o < 0,5 m e inclina < 15°.
- Mejores políticas por viabilidad (copias en `ppo_v10_robot/`):

| Marcha | Política | Viabilidad | Avance / nominal | Deriva / nominal |
|---|---|---|---|---|
| Gateo | v22 s3101 2,7 M | 100 % | 1,04 / 0,99 m | 0,03 / 0,05 m |
| Trote | v15 s307 0,1 M (v22 s3203 0,2 M) | 100 % | 1,94 / 1,90 m (1,86) | 0,06 / 0,09 m (0,04) |
| Paso | v22 s3013 0,1 M (peso de avance 20) | 100 % | 1,24 / 1,25 m | 0,04 / 0,12 m |
| Carrera | v22 s3307 1,2 M | 100 % | 1,93 / 1,76 m | 0,08 / 0,08 m |
| Galope | v21 s827 0,1 M | 90 % | 1,94 / 1,90 m | 0,33 / 0,34 m |

- En el robot (27-oct, 19:39) el bus I²C volvió a cortarse: pendiente reconectar para probar estas políticas.

### 27-oct, 23:50 — pausa de la cola v24 (apagado del PC)

Terminadas: gateo y paso (4/4 semillas), trote 2/4. Pendientes desde su última copia: carrera 4301 y 4303 (2,6 M de
2,7 M), 4307 y 4309 (1,3 M de 3 M), trote 4207 (1,5 M) y 4209 (1,4 M de 3 M); galope sin empezar. Retomar con
`Experimentos/entrenamiento_real_20261016/reanudar_v24.sh` (continúa, selecciona y mide la viabilidad de las 5 marchas).
Bus I²C del robot cortado desde las 19:39: reconectar SDA, SCL, 5 V y GND antes de las pruebas físicas.

## 28-oct-2026 (tarde) — pruebas en el robot suspendido, coxa 2 y calibración de la tibia 2

- Cola v24 retomada 14:10, terminó 15:11. Viabilidad 100 %: paso v24 s4109 200k, trote v24 s4209 200k, carrera v24 s4309 200k (copiadas a ppo_v10_robot/). Gateo v24/v25/v26 ≤55 % (avanza <90 % de la nominal). Galope: la marcha base fémur 16/tibia 14 se caía 20/20 con las ganancias de tibia; barrido_nominal.py → fémur 18, tibia 7 (2,1 m sin caídas). Galope v25 65 %, v26 (w-avance 30) 85 %.
- Bus I²C colgado por el encoder del fémur 2 (TCA 0x70 canal 4): desconectado, el bus queda estable.
- Coxa 2: se caía hacia adentro al caminar; su potenciómetro C1 no sigue la coxa (fijo en ~646), así que el firmware no la corregía. Ajustada en vivo con el operador (sostener_coxas.py, modo +): base 48 → 42 en firmware y ejecutar_politica_robot.py. Firmware cargado con avrdude del sistema (arduino-cli snap no abre el puerto). Ya no se cae.
- Tibia 2 (ENC_T2): k −0,5921 → −1,15 (regresión encoder–orden en 3 caminatas, r≈0,97); el valor viejo duplicaba la amplitud medida. comparar_sim_real.py --calibracion-actual.
- Parecido sim–real (60 s, coxa 2 a 42, calibración nueva): paso 83 %, trote 70 % (fémur trasero derecho C9 con r=0,25 en esa toma), carrera 69 %. Forma r≈0,99; robot 60–130 ms atrasado; en carrera los fémures se mueven 1,2–1,8× más que en la simulación.
- Servicio apagar-cuadrupedo instalado (systemd, envía «x» al apagar).

### 28-oct-2026 (noche) — gateo y galope, presentación

- Gateo v27 (wav 40, continúa v26 6007/6001): **100 % viable** con la semilla 7013 a 4,1 M (avance 0,99 m frente a 1,03 m; deriva 0,03 frente a 0,14). El PC se apagó a las 16:50 y 17:02 con el gateo en 4,1–4,2 M de 4,5 M; se evaluaron las copias guardadas (reanudar_v27.sh) y se copió metadata.json desde v26 6007.
- Galope: v26 85 %, v27 90 % (7403 a 150 k), v28 90 % (8417 a 175 k; 8 semillas cortas desde v27). Techo del 90 % con esta marcha base; siguiente paso sería ajustar ciclo o desfases, no entrenar más igual.
- Copias para el robot en ppo_v10_robot/: paso v24 4109 200k, trote v24 4209 200k, carrera v24 4309 200k (100 %), gateo v27 7013 4100k (100 %), galope v28 8417 175k (90 %).
- Revisión completa de sensores (revisar_sensores.py --completo): encoder fémur 2 (0x70/4) vuelve a funcionar; potenciómetro de la tibia 3 responde en M12 (el firmware no lo transmite aún); coxa 2 (C1) no sigue la coxa.
- COMO_FUNCIONA_LA_RED.md: explicación de la red, estados, acciones, recompensa, GAE y PPO.
- Presentación completa (46 diapositivas) en Documentacion/presentacion_20261028/ y como artifact.
- Pendiente: probar gateo y galope en el robot; caminatas en el piso con IMU y cámaras diagonales.

### 29-oct-2026 — explicaciones, gráficas de entrenamiento y presentaciones

- Notas del orador de la presentación completa (https://claude.ai/artifact/RZ5pm312XNrX46RKTqrzYb) con la explicación de cada ecuación; parámetros de la red corregidos a ≈ 12 100 (actor ≈ 6 400).
- entrenar_ppo_real.py --registrar-perdidas: guarda progress.csv (pérdidas de PPO por actualización) y monitor.csv (recompensa de cada episodio).
- Campaña v30: las 5 marchas desde cero, 1 M de pasos, con registro (paso s4109, trote s4207, carrera s4309, gateo s4009, galope s6403). Paso, gateo y carrera convergen; trote casi; galope no converge en 1 M (varianza explicada ≈ 0).
- graficas_recompensa_perdida.py: recompensa por episodio (cruda + tendencia) y 8 paneles de pérdidas por marcha, más recompensa de las 5 marchas. Copiadas a Documento_TESIS/Figures/Resultados (ppo_recompensa_<marcha>_episodios.png, ppo_perdidas_<marcha>.png); aún no están en el texto de la tesis.
- Presentación resumida en línea de tiempo, 29 diapositivas, ecuaciones sin explicar y una sola tabla de resultados: https://claude.ai/artifact/HfRaeqjedTApv4aB1gmPgd (copia en Documentacion/presentacion_charla_20261029/).
- El documento de tesis (PDF del 22-oct) sigue sin los resultados del 26 al 29-oct. Pendiente: actualizarlo; probar gateo y galope en el robot; caminatas en el piso; exportar las políticas nuevas a NumPy para la Raspberry.

### 3-nov-2026 — videos de las caminatas movidos al disco externo

Para liberar espacio se comprimieron a H.264 los videos MJPEG (comprimir_videos.py: 199 comprimidos; 4 de extra_general conservados en MJPEG por un desfase de ≈0,15 s en el primer fotograma) y las 217 caminatas con video se copiaron a `Vidios tesis` en el disco externo USB2 (rsync, verificación por suma de comprobación sin diferencias). Los 407 `video.mkv` se borraron del PC; los datos (csv, json, análisis) siguen también en `Experimentos/camaras/grabaciones`. Disco del PC: de 28 a 96 GB libres. Para reanalizar un video hay que conectar el disco; las caminatas nuevas se siguen grabando en el PC.

### 3-nov-2026 — convergencia por marcha en el informe

Campaña v31 (cola_v31.sh): las 5 marchas desde cero con registro de cada término de la recompensa (terminos.csv), 3 M de pasos y galope 5 M, una semilla por marcha. graficas_convergencia.py: recompensa y castigo frente a pasos y épocas, épocas frente a pasos y castigos por término. Convergencia de la recompensa: gateo 0,60 M (2937 épocas), paso 0,73 M (3560), carrera 0,83 M (4044), trote 1,39 M (6758), galope 2,05 M (10 020). El avance por episodio baja durante el entrenamiento en todas. Añadida la sección 13.5 a la tesis (capítulo de políticas PPO), con 2 tablas y 5 figuras. El resto del documento sigue sin los resultados del 26 al 29-oct (viabilidad, carrera y galope en el capítulo de resultados, parecido simulación-robot).

### 3-nov-2026 — tesis actualizada con los resultados del 26-oct al 3-nov

Cap. 12: mapa de articulaciones (coxa 2 a 42, coxa 3 a 64, tibia 1 en CH12, bases y topes de tibias 2 y 4), modos + $ ^ del firmware, fallos nuevos. Cap. 13: tabla de marchas (5), ganancias de tibia, campañas v17–v31 (tabla nueva), viabilidad (ecuación), sensores al 28-oct. Cap. 14: postura del 27-oct, viabilidad, parecido sim–real por articulación, mejores políticas, pendientes y alcance. Cap. 15–17, resumen y anexo actualizados. generar_inventario_resultados.py separa carrera y galope. Inferencias nuevas señaladas en el texto: copias elegidas con las mismas 20 semillas (optimista) y copias vecinas muy distintas (s7001 v27: 30/100/60 %). No actualizada: MATRIZ_OBJETIVO_EVIDENCIA.md.

### 5-nov-2026 — gateo y galope en el robot suspendido; convergencia a ±2 %

- graficas_convergencia.py con banda ±2 % (antes ±5 %, marcaba la línea cuando la curva aún subía): gateo 0,89 M, paso 0,95, carrera 1,23, trote 2,06; galope no converge en 5 M. Tesis 13.5 actualizada (commit dc7dad8).
- robot05_gateo_v27_7013_60s_1811 y robot05_galope_v28_8417_60s_1813: inválidas, ningún sensor sigue la orden (r≈0, coxas 23–51°); probablemente servos sin fuerza en ese momento. revisar_sensores.py --completo (18:17) sí respondió: fémures M5/M6/M8/M9 r≈0,98, tibia 2 E70_3, tibia 3 M12; coxas y tibia 4 sin lectura.
- Repetidas: gateo v27 r2_1822 parecido 76 % (90 % sin tibia 4; fémures r 0,94–0,99, coxas ≈1,7°); galope v28 r2_1825 parecido 66 % (fémur 2 deriva −13,9°, fémur 4 r 0,80 con ciclos negativos, desplazamiento común 60 cuentas; tibias 1,2–1,8× la simulación). pc2-camara se cayó de la red durante el galope: su video quedó en remota_incompleta.
- Tibia 4 (C10) ya no sigue a su servo (r≈0,1 en caminata y sin lectura en la revisión).
- Python con MuJoCo: ../../.venv-mujoco/bin/python (comparar_sim_real.py y revisar_sensores.py lo necesitan).

### 5-nov-2026 (tarde) — modelo de servos ajustado por marcha (v32) y tope de la tibia 1

- ajustar_ganancia_marcha.py: ganancia por articulación = amplitud robot/sim de las tomas de 60 s (r ≥ 0,8) → actuadores_<marcha>_articulacion.json. En tomas no usadas para el ajuste el parecido subió: paso 78/80 → 91/88, trote 61/79 → 69/87, carrera 66 → 76 % (la ganancia única por marcha no mejoraba). comparar_sim_real.py y evaluar_viabilidad.py aceptan --actuador.
- v32 (cola_v32.sh + viabilidad_v32.sh): 4 semillas por marcha continuando las elegidas con el modelo ajustado. Con este modelo, la marcha nominal empeora mucho en simulación (carrera cae 19/20, galope retrocede). Viabilidad: paso 9109 300k 100 %, gateo 9009 4,6 M 100 %, carrera 9301 500k 95 %, trote 9209 650k 60 %, galope 9407 475k 60 %; las de partida con el modelo nuevo: paso y gateo 100 %, trote 5 %, carrera y galope 0 %. Copias en ppo_v10_robot/ppo_v32_*.
- Robot suspendido (parecido sin tibia 4, cuyo potenciómetro C10 ya no sigue): trote 70 → 80, carrera 71 → 83, galope 69 → 82 (r2_1936; la primera toma se cortó a 45 s por desconexión USB), paso 85 → 81, gateo 90 → 84. Elegidas para el robot: paso v24, gateo v27, trote/carrera/galope v32. En el galope los potenciómetros de los fémures 2 y 4 se alteran (deriva 13°).
- Tibia 1: se mueve (probar_tibia1.py). Tope mínimo 18 → 12 en firmware (copia .antes_tope_t1_20261105) y ejecutar_politica_robot.py; en el trote va ahora de 42 a 15°.
- v33 (cola_v33.sh) en el PC 2 (pc2-camara, ~/Cuadrupedo_entreno, venv copiado): las 5 marchas desde cero con el modelo ajustado y registro, para las gráficas de convergencia (graficas_convergencia.py --campana v33).

### 5-nov-2026 (noche) — convergencia con el modelo ajustado (v33, PC 2), videos de evidencia, visor MuJoCo

- v33 en el PC 2 (5 marchas desde cero, modelo de servos ajustado, semilla 9900). Convergencia ±2 %: trote 1,28 M, carrera 0,35 M pero degenerada (cae en el 100 % de los episodios al final, 47 pasos: con recompensa por paso negativa, caer pronto da más retorno), paso no converge (sigue subiendo a 3 M), gateo y galope tampoco con ±2 % (planos a la vista desde ~1,5 y ~2 M). Con el modelo ajustado la marcha nominal de carrera cae; de ahí el fracaso desde cero (la v32, que continúa una política buena, no lo sufre).
- graficas_convergencia.py: --campana/--semilla; media móvil sin repetir el último episodio en los bordes (v31 no cambia). Gráficas para la presentación en Documentacion/graficas_convergencia_20261105 (v31 y v33) y en el Escritorio.
- Caminatas de evidencia (19:45-19:57, 60 s, 5 cámaras): gateo v27, paso v24, trote/carrera/galope v32; videos 2×2 en ~/Escritorio/Videos_evidencia_5nov (video_evidencia.py); datos en grabaciones/evidencia_*_1945.
- ver_politica_mujoco.py: política en MuJoCo, ventana (ffplay) o video, piso o colgado. Etiqueta politicas-elegidas-20261105 en GitHub con README, SHA256SUMS, verificar.sh, requirements.txt y firmware.

### Para continuar el 6-nov-2026

- Gráficas de convergencia con fecha y hora: ~/Escritorio/Graficas_convergencia_2026-11-05_2027 (también en el Escritorio del PC 2) y Documentacion/graficas_convergencia_20261105. Se regeneran con `python3 graficas_convergencia.py [--campana v33 --salida graficas/convergencia_v33]` a partir de los terminos.csv/progress.csv de ppo_v31_* y ppo_v33_* (ya en el repositorio).
- Decisión pendiente del operador sobre la v33: (1) usar en la presentación las v31 y la v33 solo como diapositiva extra (recomendado), o (2) quitar la línea de la carrera v33 y marcarla como degenerada. Motivo: con ±2 % del recorrido la línea de la carrera v33 queda en 0,35 M y la curva aún sube hasta ~0,5 M (empezó en −2800 por las caídas); ninguna regla única (1 %, ruido final, codo, 95 % de la mejora) acierta en todas las marchas.
- Políticas elegidas para el robot (etiqueta politicas-elegidas-20261105): gateo v27 7013 4,1 M, paso v24 4109 0,2 M, trote v32 9209 650k, carrera v32 9301 500k, galope v32 9407 475k.
- Pendientes: probar el visor de Gazebo en el PC 2 (si se decide), cables de los potenciómetros de los fémures 2 y 4 y de la tibia 4, cámara General (0 fotogramas), subir videos a YouTube (los sube el operador) y poner los enlaces en la tesis, ventiladores del PC 2 a automático.
- Copias de seguridad de ppo_v32_* y ppo_v33_* en el PC 2 (~/Cuadrupedo_entreno/Experimentos/entrenamiento_real_20261016).
