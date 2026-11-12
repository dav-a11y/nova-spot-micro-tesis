# Seguimiento

## Objetivos vigentes

Desde el 7 de septiembre rigen los cuatro objetivos aportados por el usuario:
hardware/software (OE1), modelado (OE2), control aprendido (OE3) y las tres pruebas
de margen estático, seguimiento articular y repetibilidad (OE4). Las referencias
históricas a cinco objetivos deben interpretarse con la matriz actualizada de
`Documento_TESIS/MATRIZ_OBJETIVO_EVIDENCIA.md`.

## Proyecto

Desarrollo y evaluación del control de locomoción del robot cuadrúpedo Nova
Spot Micro mediante una marcha nominal convencional y una política de
aprendizaje por refuerzo que aplique correcciones pequeñas, acotadas y
supervisadas.

Última actualización documental: 14 de octubre de 2026, America/Bogota.

Actualización cinemática del 2 de septiembre: se completaron las gráficas de
workspace, proximidad a singularidades y velocidades articulares. Se corrigió
el período de gateo de 5,76 a 4,32 s en el generador, se añadieron ambas marchas
y las doce articulaciones al CSV, y se documentaron umbrales y limitaciones en
`Documento_TESIS/Figures/Resultados/INFORME_GRAFICAS_CINEMATICA.md`. La postura
nominal tiene $\sigma_{\min}=0,038037$ m/rad y $\kappa=6,647$; los máximos de
referencia son 0,944520 rad/s en gateo y 0,372327 rad/s en paso. El punto queda
cerrado computacionalmente, pero los límites físicos bajo carga siguen sujetos
a calibración.

Actualización del modelo digital del 2 de septiembre: una fuente YAML genera
perfiles emparejados para Gazebo y MuJoCo, con variación de masa, inercia,
fricción, amortiguamiento, holgura, retardos, tensión y corriente. Tres perfiles
pasan la auditoría de compatibilidad. Se modeló la saturación del MG996R por
velocidad, tensión y corriente, y una capa ROS común aplica holgura y retardo.
MuJoCo publica ya pose, IMU y contactos mediante el contrato de Gazebo. La
primera comparación común de 11 ciclos cubre avance, orientación, contactos,
margen y seguimiento. No cierra un gemelo digital: falta identificación física
y repetición estadística; se conserva ``modelo digital configurable''.

Ficha de servos recibida el 2 de septiembre: confirma tensión, par, velocidad,
masa y dimensiones de los doce MG996R-360, pero contradice el rango angular y
no contiene corriente. Se incorporaron ambos puntos nominales de 4,8 y 6,0 V
al modelo. El giro continuo/posicional y las corrientes deben verificarse
físicamente antes de modificar articulaciones o dimensionar la fuente.

## Punto de partida confirmado

No se parte de cero. Ya están implementados y comprobados:

- ROS 2 Humble con los paquetes `nova_gait_controller` y
  `nova_sm3_description`.
- Modelo provisional coherente en URDF/Gazebo y MJCF/MuJoCo.
- Cinemática directa e inversa propia para las cuatro patas.
- Jacobianos, masa, Coriolis, gravedad, dinámica inversa, centro de masa,
  margen estático, modelo MG996R y contacto penalizado.
- Control de postura, parada y gateo cartesiano mediante 12 articulaciones.
- Gateo estable en Gazebo durante más de diez ciclos: avance de 0,21887 m,
  altura entre 0,22287 y 0,22428 m y desviación lateral máxima de 0,00986 m.
- Parámetros base del gateo: 24 muestras, paso de 18 mm, elevación de 14 mm,
  0,18 s por muestra y ciclo de 4,32 s.
- Nodo de métricas de pose 3D y estados articulares.
- Supervisor provisional de simulación que ordena `stand` ante altura o
  inclinación insegura; su activación provocada ya fue verificada.
- Documentación matemática y técnica del código, ROS 2 y simulación.
- Word matemático consolidado el 14 de agosto de 2026 a partir de las fórmulas
  corregidas y la guía de complementos: 22 páginas, 37 ecuaciones/gráficos
  preservados y secciones detalladas sobre workspace, singularidades, J̇,
  contacto, estabilidad, identificación, validación y sensibilidad.
- Scripts preparatorios para Raspberry Pi 4 Model B con Ubuntu 22.04 y ROS 2
  Humble.

La referencia `mike4192/spot_micro_kinematics_python` se conserva como apoyo
conceptual para cinemática, transferencia de peso y marcha cuasiestática. La
implementación del proyecto es propia y está adaptada al URDF NovaSM3.

## Lo que falta, en orden de ejecución

### 1. Registrar y analizar la línea base en Gazebo

Estado: **completado el 14 de agosto de 2026**.

- [x] Grabar con `rosbag2` al menos diez ciclos continuos de gateo sin cambiar
  paso, altura ni velocidad.
- [x] Registrar pose 3D, estados articulares, métricas, órdenes de marcha y
  activaciones del supervisor.
- [x] Automatizar el cálculo de avance por ciclo, velocidad, desviación
  lateral, altura, roll, pitch y continuidad articular.
- [x] Guardar fecha, versión del código, configuración y duración de cada
  ensayo.
- [x] Repetir el ensayo para comprobar reproducibilidad y no depender de una
  sola ejecución favorable.

Criterio de cierre: bolsa reproducible, tabla de resultados y gráficas de al
menos diez ciclos con la configuración nominal congelada.

Avance del 14 de agosto de 2026: se creó la bolsa válida
`Experimentos/rosbag2/linea_base_gateo_limpia_20260814_0925`, con 98,978769 s
continuos entre las órdenes `gateo` y `stand` (20 ciclos ejecutados completos),
83.442 mensajes y cero activaciones del supervisor. Se guardó el registro del
ensayo, parámetros congelados, tópicos, resumen preliminar y SHA-256 dentro de
la bolsa. La primera tentativa `linea_base_gateo_20260814_0918` quedó marcada
como inválida porque había nodos ROS 2 duplicados. El análisis, el CSV y las
gráficas quedaron en `Experimentos/analisis/linea_base_gateo_limpia_20260814_0925`.
La duración configurada era 4,32 s por ciclo, pero las referencias articulares
muestran 4,797996 s de media: el temporizador publicó las fases aproximadamente
cada 0,20 s. Permanece pendiente la repetición de reproducibilidad.
La auditoría `AUDITORIA_TOPICOS.md` confirma 10.232 mensajes de pose 3D, 17.372
estados articulares, 10.231 mensajes de métricas, las órdenes `gateo` y
`stand`, y cero eventos de seguridad en el tópico del supervisor.

Repetición completada el 14 de agosto de 2026: la bolsa válida
`repeticion_gateo_limpia_20260814_0956` contiene 36 ciclos completos y cero
activaciones del supervisor. Se compararon los primeros 20 ciclos de cada
ensayo; en régimen permanente (ciclos 2--20) las diferencias relativas fueron
-0,102 % en avance, -0,036 % en velocidad, 0,193 % en excursión lateral,
-0,001 % en altura, -0,000 % en roll y -0,002 % en pitch. Los hashes del código,
configuración, analizador y bolsa están en `REGISTRO_REPETICION.md`. La tentativa
`repeticion_gateo_20260814_0948` se marcó inválida porque no almacenó la orden
inicial `gateo`.

Corrección posterior: el planificador temporal dejó de acumular el retraso del
callback de 20 ms. Las 24 pruebas pasaron y una validación ligera de seis ciclos
midió 0,180003383 s por fase y 4,320106573 s por ciclo. Esta es una nueva versión
experimental; requiere su propia línea base y repetición en Gazebo, separadas de
las dos bolsas anteriores.

Nueva línea base corregida: `linea_base_cadencia_corregida_20260814_1049`, con
13 ciclos, ciclo observado medio de 4,320013 s, 32.352 mensajes y cero eventos
del supervisor. Su análisis y gráficas están en
`Experimentos/analisis/linea_base_cadencia_corregida_20260814_1049`. Falta una
repetición equivalente de esta nueva versión.

Repetición corregida completada: `repeticion_cadencia_corregida_20260814_1100`,
con 13 ciclos, 32.395 mensajes y cero eventos del supervisor. La comparación de
los ciclos 2--13 arrojó diferencias menores al 0,2 % en duración, avance,
velocidad, excursión lateral, altura, roll, pitch y continuidad articular. La
línea base de la versión corregida queda cerrada y reproducida.

### 2. Cerrar las definiciones experimentales con los directores

Estado: **propuesta técnica completa; pendiente de visto bueno de los directores**.

- [x] Redactar formalmente qué significa `paso` en esta tesis: movimiento de una
  pata o secuencia completa de cuatro patas.
- [x] Documentar el orden de apoyo/oscilación del `gateo` y qué constituye un
  ciclo completo.
- [x] Definir en borrador ensayo, ciclo válido, fallo, intervención y caída.
- [x] Aprobar y adoptar número de ensayos, ciclos por condición y semillas de
  RL.
- [x] Definir la evidencia principal: señales de retroalimentación y pruebas
  suficientes para demostrar OE1--OE4.
- [x] Proponer frecuencias por sensor: contacto/IMU a 100 Hz como objetivo y
  mínimo de 50 Hz para métricas.
- [x] Dejar métricas y umbrales numéricos como guías de análisis, subordinadas
  al cumplimiento de los objetivos y ajustables con los directores.
- [ ] Obtener la firma o confirmación escrita de los directores sobre estas
  definiciones.
- [x] Resolver documentalmente el nivel del modelo: nominal computable,
  coherente entre código, URDF/Gazebo y MJCF/MuJoCo, sin declararlo gemelo
  digital identificado.

Criterio de cierre: protocolo escrito y aprobado por los directores antes de
iniciar el experimento comparativo. La propuesta técnica ya está consolidada;
queda pendiente únicamente la confirmación externa.

Borrador técnico creado en
`Documentacion/PROTOCOLO_EXPERIMENTAL_BORRADOR.md`. Propone paso como oscilación
completa de una pata, ciclo como 24 referencias con las cuatro oscilaciones y
orden FL--RR--FR--RL. Define ensayo, transitorio, validez, fallo, intervención,
caída, datos, métricas, umbrales provisionales y alcance del modelo. Las
cantidades quedaron fijadas internamente en cinco ensayos de 20 ciclos por
condición y semillas RL `11`, `23`, `37`, `53`, `71`. La decisión está en
`Documentacion/DECISION_TAMANO_MUESTRAL_Y_SEMILLAS_RL.md`. La evidencia
principal, la retroalimentación sensórica y la redacción del nivel de modelo
están consolidadas en la ficha y el protocolo; falta la firma de los directores.

### 3. Implementar la marcha `paso`

Estado: **implementada y validada en Gazebo y MuJoCo**.

- [x] Diseñar transferencia de peso, elevación, avance, colocación y
  recuperación estable.
- [x] Contrastar la secuencia con la referencia de Mike4192 sin copiar sus
  parámetros físicos.
- [x] Generar la trayectoria en espacio cartesiano y convertirla con la IK
  propia.
- [x] Validar alcanzabilidad, límites y continuidad.
- [x] Añadir pruebas unitarias y parámetros configurables.
- [x] Validar al menos diez ciclos en Gazebo y MuJoCo.
- [x] Relegar `galope` a experimento opcional de simulación.

Criterio de cierre: paso definido, documentado y repetible sin caída en ambos
simuladores.

Implementación inicial del 14 de agosto de 2026: comando `paso/step`, 32
referencias, ciclo nominal de 5,76 s, paso de 0,016 m, elevación de 0,008 m y
transferencia lateral de 0,004 m. Pasaron 26 pruebas. Un ensayo exploratorio de
cuatro ciclos en Gazebo tuvo cero eventos de seguridad, ciclo medio de 5,759993
s, avance de 0,020730 m/ciclo, roll máximo medio de 1,275 grados y pitch máximo
medio de 2,497 grados. Diseño en `Documentacion/MARCHA_PASO_DISENO.md`.

Validación extensa completada: dos ensayos Gazebo de 12 ciclos con cero eventos
del supervisor y diferencias de medias menores al 0,4 %. MuJoCo completó 12
ciclos con duración media de 5,759999 s, error RMS articular de 0,026232 rad y
error máximo de 0,054983 rad. La pose corporal de MuJoCo aún no está expuesta,
por lo que su validación se limita a cadencia y articulaciones. Informe en
`Documentacion/MARCHA_PASO_VALIDACION.md`.

El galope quedó formalmente fuera del alcance principal y deshabilitado por
defecto mediante `enable_experimental_gallop=false`. Solo puede habilitarse de
forma explícita en simulación; no entra en las líneas base, la comparación con
RL ni las pruebas de hardware. Decisión documentada en
`Documentacion/EXPERIMENTO_GALOPE_OPCIONAL.md`.

### 4. Incorporar estabilidad y sensores en simulación

Estado: **parcial**.

- [x] Publicar fase de marcha y patas previstas en contacto.
- [x] Añadir contactos de los cuatro pies en Gazebo.
- [x] Comparar en línea contacto previsto frente a observado, inicialmente sin
  actuación automática.
- [x] Añadir pose, IMU y contactos equivalentes en MuJoCo.
- [x] Añadir o conectar una IMU simulada.
- [x] Calcular en línea el polígono de soporte y el margen de estabilidad con
  contactos y centro de masa.
- [x] Extender el supervisor con contacto inesperado, pérdida de comunicación,
  límites articulares y referencias inválidas.
- [ ] Definir mecanismo de rearme seguro del supervisor.
- [x] Ejecutar las pruebas unitarias nuevas con `python3 -m pytest`.

Criterio de cierre: métricas y supervisor reaccionan correctamente a pruebas
provocadas de altura, inclinación, contacto y pérdida de datos.

Pruebas provocadas completadas el 2 de septiembre de 2026: nueve escenarios
ROS 2 aislados validaron margen negativo, pérdida de contacto, datos vencidos,
altura baja y alta, roll, pitch, límite articular y discontinuidad. Todos
produjeron `triggered=true`, el motivo esperado y la orden `stand`. La campaña
es reproducible, se valida automáticamente y fue añadida a GitHub Actions. La
suite determinista conserva 80 pruebas aprobadas. Evidencia:
`Experimentos/pruebas_dinamicas_supervisor_20260902`. El rearme seguro y la
medición de falsos positivos antes de habilitar contacto, margen y timeout por
defecto continúan pendientes.

Integración del 31 de agosto de 2026: la IMU de Gazebo publica a 100 Hz en
`/nova/imu`; el contacto distingue estado crudo, filtrado y transición
pendiente; `stability_monitor` publica polígono y margen nominal en
`/nova/stability`. El supervisor rechaza referencias no finitas o fuera de
límites y observa timeout, contacto y margen, pero estas tres paradas permanecen
desactivadas hasta ejecutar pruebas provocadas. Pasan 47 pruebas y tres ciclos
cortos no produjeron paradas espurias. El punto del supervisor sigue parcial y
el rearme seguro continúa pendiente. Detalle en
`Documentacion/ESTABILIDAD_IMU_SUPERVISOR_GAZEBO.md`.

Avance del 14 de agosto de 2026: cuatro sensores de 100 Hz funcionan en Gazebo,
el nodo `contact_monitor` publica `/nova/foot_contacts` y
`/nova/contact_diagnostics`, y 32 pruebas pasan. Se confirmaron cuatro apoyos
válidos en `stand` y discrepancias detectadas correctamente durante `crawl` y
`step`. El monitor no detiene ni modifica la marcha. Detalles en
`Documentacion/CONTACTOS_MEDIDOS_GAZEBO.md`.

Ensayo cuantitativo completado: la bolsa
`contactos_gateo_validado_20260814_1410` contiene 76 ciclos y seis marcadores.
La coincidencia simultánea fue 32,550 %. Las patas delanteras despegaron unos
0,38 s tarde y aterrizaron unos 1,364 s tarde; las traseras no despegaron y
deslizaron. Cero eventos del supervisor. Antes de calcular un polígono de
soporte útil debe corregirse la trayectoria de gateo y repetir esta medición.

El controlador publica `/nova/gait_phase` como JSON sincronizado con cada
referencia. Incluye modo, muestra, ciclo, pata en oscilación y tres contactos
previstos para `crawl` y `step`; `gallop` declara el plan no disponible. Pasaron
29 pruebas y se verificó un mensaje ROS 2 real. Contrato documentado en
`Documentacion/FASE_Y_CONTACTOS_PREVISTOS.md`.

Iteración exploratoria del 17 de agosto de 2026: se añadió transferencia
lateral de 4 mm y longitudinal parametrizable al gateo, sin cambiar paso,
altura, muestras ni cadencia. Con 8 mm longitudinales se obtuvo el mejor valor
exploratorio (35,787 % de coincidencia simultánea, 13 ciclos), y por primera vez
hubo transiciones de las patas traseras. No obstante, sus despegues permanecen
1,17--1,19 s tarde. Pasan 35 pruebas y el paquete compila, pero el punto sigue
parcial: debe separarse la precarga de la oscilación y reflejar las subfases en
`/nova/gait_phase` antes de una nueva línea base formal.

Subfases implementadas y verificadas el 17 de agosto de 2026: cada cuarto de
gateo publica transferencia, precarga, despegue, vuelo, aterrizaje y contacto
final, con un plan de cuatro o tres apoyos coherente con la referencia. En 15
ciclos exploratorios, los cuatro despegues quedaron entre 0,133 y 0,141 s tarde;
RL y RR ya despegan en su ventana correcta. Hubo cero eventos del supervisor y
36 pruebas pasan. Falta ajustar aterrizajes: delanteras aproximadamente 0,50 s
tarde y traseras 0,33 s antes. No se ha congelado una línea base nueva.

Iteración del 18 de agosto de 2026: se hizo configurable la altura de `landing`
por eje y se ensayó el contraste continuo 0,20 delante / 0,80 detrás durante 22
ciclos completos. Los aterrizajes delanteros quedaron 0,446--0,455 s tarde y
los traseros 0,323--0,327 s antes; la mejora fue insuficiente. El contraste fue
descartado y los valores nominales volvieron al perfil sinusoidal 0,70710678.
Los despegues corregidos no se degradaron. Pasan 37 pruebas y el paquete
compila. La siguiente iteración debe modificar la curva completa de descenso,
no solamente la penúltima referencia.

Iteración del 20 de agosto de 2026: el mismo parámetro observable (altura
normalizada al 75 % de la oscilación) controla ahora una curva continua de
potencia desde el ápice hasta `touchdown`, diferenciable por eje. El ascenso
permanece inalterado. Con 24 muestras y el valor nominal, las referencias son
numéricamente iguales a las anteriores, por lo que aún no se reclama una
mejora física ni una nueva línea base. Pasan 39 pruebas y el paquete compila.
Falta comparar candidatos cartesianos y ensayarlos en Gazebo.

Criba cartesiana del 24 de agosto de 2026: se compararon nueve contrastes y el
control nominal con `Experimentos/evaluar_curvas_descenso.py`. Seis contrastes
con relación delantera 0,20--0,50 y trasera 0,75--0,80 cumplen alcanzabilidad,
periodicidad y salto articular menor de 0,20 rad; 0,85 detrás se descartó por
alcanzar 0,203263 rad. Pasan 39 pruebas. El informe está en
`Experimentos/curvas_descenso_cartesianas_20260824/INFORME_CRIBA_CARTESIANA.md`.
La siguiente exploración Gazebo usará nominal, 0,20/0,75, 0,20/0,80 y
0,50/0,75. El protocolo conserva un umbral provisional de 0,05 rad que no
cumple ni el nominal (0,170014 rad), por lo que requiere acuerdo formal.

Exploración Gazebo del 27 de agosto de 2026: se compararon esas cuatro curvas
en ventanas estrictas de 10--13 ciclos, con cero eventos del supervisor. La
coincidencia simultánea fue 20,949 % nominal, 23,855 % para 0,20/0,75,
23,721 % para 0,20/0,80 y 21,728 % para 0,50/0,75. Los despegues se mantuvieron
entre 0,132 y 0,143 s tarde. `0,20/0,75` redujo los aterrizajes delanteros a
0,436/0,460 s tarde, pero los traseros continuaron unos 0,32 s antes. Es el
candidato provisional, no una nueva línea base. Informe en
`Experimentos/exploracion_curvas_descenso_gazebo_20260827/INFORME_COMPARACION.md`.

Exploración del 31 de agosto de 2026: las transiciones mostraron que RL y RR
recuperaban contacto 0,07--0,08 s después del despegue observado, todavía en
ascenso. Se añadió una relación independiente de altura trasera al 25 % de la
oscilación. La criba aceptó como máximo 0,80 (salto 0,189604 rad); desde 0,85
se supera 0,20 rad. En Gazebo, 0,20/0,75 con ascenso 0,80 completó 15 ciclos,
pero solo desplazó los aterrizajes traseros a -0,305/-0,309 s y obtuvo 23,644 %
de coincidencia. El candidato fue rechazado y `gaits.yaml` conserva el nominal.
La próxima iteración debe revisar liberación física y semántica/debounce del
contacto; no seguir aumentando la altura temprana.

Preparación del 1 de septiembre de 2026: `/nova/contact_diagnostics` conserva
el estado observado compatible y añade explícitamente los conjuntos crudo y
filtrado. `Experimentos/analizar_contactos_rosbag.py` calcula ahora la
coincidencia de ambos sin dejar de aceptar bolsas históricas. Pasaron 49 pruebas
y la regresión sobre la bolsa válida del 31 de agosto reprodujo 23,643955 % de
coincidencia. Falta la bolsa nueva de al menos diez ciclos: sin ella todavía no
se consideran caracterizados el timeout de 0,10 s ni los debounce de 0,12/0,03
s.

Ensayo formal completado el 1 de septiembre de 2026: 24 ciclos nominales y cero
eventos del supervisor. La coincidencia cruda/filtrada fue 20,639/13,621 %. Las
pérdidas crudas RL/RR duraron en promedio 0,074645/0,073803 s, con máximos
menores de 0,09 s y ningún episodio por encima del debounce de 0,12 s. El vuelo
trasero aparente queda reclasificado como interrupción breve, no como despegue
sostenido. Evidencia en
`Documentacion/RESULTADOS_CONTACTO_CRUDO_FILTRADO_2026-09-01.md` y en la bolsa
`contactos_debounce_nominal_valido_20260901_0828`. La trayectoria nominal sigue
sin producir despegue trasero confirmado; no habilitar aún las paradas del
supervisor basadas en contacto.

### 5. Caracterizar físicamente el robot sin energizar

Estado: **bloqueado temporalmente por ensamble incompleto**.

Actualización del 31 de agosto de 2026: falta imprimir y montar la pieza
`SM3_Cover_LeftFemur.stl` de la pata izquierda. Hasta completar esa pieza no se
consideran definitivas la inspección, las fotografías ni las mediciones de la
geometría física. Fuente indicada para impresión:
`https://github.com/cguweb-com/Arduino-Projects/blob/main/Nova-SM3/STL%20Files/SM3%20Files/SM3_Cover_LeftFemur.stl`.
La ficha de caracterización está preparada, pero no debe llenarse con valores
parciales presentados como robot terminado.

Intervención mecánica informada el 31 de agosto de 2026: se sustituyeron dos
servos por limitaciones físicas y se reforzaron los acoples para reducir el
juego de las patas. El cambio mejora la preparación del ensamble, pero todavía
no está cuantificado ni calibrado. Faltan identificar las dos articulaciones y
canales, documentar los componentes anteriores/nuevos, fotografiar los
refuerzos y verificar que no introduzcan topes o rozamiento. Registro en
`Raspberry/INTERVENCION_MECANICA_2026-08-31.md`.

- [ ] Fotografiar estructura, patas, articulaciones, electrónica y cableado.
- [ ] Confirmar que las doce unidades sean MG996R y registrar fabricante o
  diferencias visibles.
- [x] Confirmar Raspberry Pi 4 Model B, PCA9685, BNO055 y demás componentes
  disponibles.
- [ ] Medir tres veces separaciones de cadera, longitudes de coxa/fémur/tibia y
  dimensiones del cuerpo.
- [ ] Medir masa total, cuerpo/electrónica y patas cuando sea posible.
- [ ] Inspeccionar holguras, topes, tornillos, rodamientos, pies y colisiones.
- [ ] Registrar toda diferencia frente al modelo provisional.

Criterio de cierre: inventario con evidencia fotográfica y mediciones
trazables. Esta fase no autoriza energizar los doce servos.

### 6. Diseñar y verificar la seguridad eléctrica

Estado: **pendiente**.

- [ ] Medir primero la corriente de un MG996R asegurado, sin carga y con límite
  de corriente.
- [ ] Seleccionar fuente de servos a partir de mediciones reales, no del
  consumo promedio ni únicamente de una hoja de datos.
- [ ] Dimensionar distribución, calibre de cable, conectores y fusible.
- [ ] Mantener alimentación lógica y potencia de servos separadas con tierra
  común controlada.
- [ ] Implementar parada física que corte o deshabilite potencia de actuadores
  sin depender de ROS 2.
- [ ] Definir el comportamiento seguro del pin `OE` del PCA9685.
- [ ] Seleccionar medición de tensión/corriente y confirmar la necesidad real
  de sensores de temperatura.

Criterio de cierre: esquema revisado, protecciones instaladas y protocolo de
emergencia probado antes de conectar simultáneamente los servos.

### 7. Calibrar los doce MG996R

Estado: **bloqueado hasta completar la seguridad eléctrica**.

Dos servos fueron sustituidos el 31 de agosto. Sus calibraciones deben partir
de cero y no pueden heredar centro, sentido ni límites de los componentes
retirados. La correspondencia articulación--canal de ambos sigue pendiente.

- [ ] Calibrar un servo a la vez con el robot asegurado.
- [ ] Registrar canal, centro PWM, sentido, pulsos mínimo/máximo y límites
  mecánicos seguros.
- [ ] Medir corriente sin carga, bajo carga controlada y temperatura.
- [ ] Crear un archivo YAML de calibración por articulación.
- [ ] Probar una pata suspendida antes de habilitar las cuatro.
- [ ] Sustituir en URDF/MJCF los límites y parámetros provisionales que puedan
  identificarse.

Criterio de cierre: doce calibraciones trazables, sin colisiones ni topes
mecánicos, revisadas antes de apoyar el robot.

### 8. Preparar Raspberry Pi 4 e interfaz PCA9685

Estado: **base Raspberry instalada y comunicación lógica validada; interfaz física,
seguridad e instrumentación pendientes**.

- [x] Identificar la unidad extraíble de 32 GB (`/dev/sda`) y grabar la imagen
  ARM64, separándola del NVMe interno.
- [x] Instalar y arrancar Ubuntu 22.04.5 ARM64 con SSH habilitado. La imagen
  instalada es Desktop, no Server; se conserva así por la evidencia existente.
- [x] Ejecutar y verificar la preparación de ROS 2 Humble: workspace compilado,
  overlay cargable y paquetes reconocidos en la Raspberry.
- [x] Confirmar Wi-Fi/SSH, `ROS_DOMAIN_ID=42`, DDS e I2C. El reloj común aún
  debe documentarse explícitamente antes de sincronizar sensores.
- [ ] Probar PCA9685 sin servos y comprobar PWM con instrumento.
- [ ] Desarrollar la interfaz física `ros2_control` usando las calibraciones
  medidas.
- [ ] Integrar BNO055, corriente/tensión, contactos y estado de parada.
- [x] Documentar una arquitectura preliminar de realimentación física con
  AS5600, multiplexores I2C, IMU, contactos y medición de potencia.
- [ ] Confirmar las variantes comerciales y actualizar presupuesto y diagrama
  eléctrico antes de comprar o conectar la instrumentación.
- [ ] Prototipar un AS5600 en una articulación y validar alineación, cero,
  sentido, límites, repetibilidad, holgura, ruido y frecuencia de adquisición.
- [ ] Probar tres AS5600 en una pata mediante TCA9548A antes de extender el bus
  a las doce articulaciones.
- [ ] Seleccionar y validar un sensor de contacto físico por pie; comparar FSR,
  microswitch y celda de carga según geometría y repetibilidad.
- [ ] Dimensionar y validar INA228, resistencia shunt, fusible y conectores para
  la corriente real de los servos.
- [ ] Añadir vigilancia por pérdida de comunicación y arranque con salidas
  deshabilitadas.

Revisión del estado: ya están demostrados la microSD identificada, Ubuntu
22.04.5 ARM64 con SSH, la compilación del workspace ROS 2, Wi-Fi/DDS con
`ROS_DOMAIN_ID=42` y la detección I²C del PCA9685 en `0x40`. También existe
una prueba Arduino/Mega que mueve `CH5`--`CH10` a 60 Hz con un barrido limitado,
pero no es todavía una interfaz `ros2_control` calibrada ni una validación de
PWM con instrumento. No hay evidencia de prototipo AS5600, TCA9548A, BNO055,
contactos físicos o INA228 conectados; la arquitectura sensórica sigue siendo
conceptual. La sobrecarga registrada obliga a mantener bloqueadas las posturas
y marchas hasta cerrar fuente, OE, calibración y vigilancia de comunicaciones.

Avance del 18 de agosto de 2026: se detectó la Raspberry como `arm64`, con
Ethernet `192.168.0.132`, Wi-Fi `192.168.0.134` y SSH activo, habilitado y
escuchando en el puerto 22. Tenía Ubuntu 24.04.4 LTS y no tenía ROS 2. Se decidió
descartar esa instalación y reinstalar Ubuntu Server 22.04 LTS ARM64 para usar
la misma distribución ROS 2 Humble del computador de Gazebo. La unidad aún no
se ha conectado al computador ni se ha sobrescrito. La próxima comprobación
obligatoria es identificar de forma inequívoca el dispositivo de almacenamiento
antes de grabar la imagen.

Avance del 19 de agosto de 2026: se identificó `/dev/sda` como la unidad USB
extraíble de 28,9 GiB de la Raspberry, separada del NVMe interno. Se verificó el
SHA-256 oficial y se grabó correctamente Ubuntu 22.04.5 Desktop ARM64 con
interfaz gráfica (9.269.411.840 bytes, salida cero y `sync` completado). Las
particiones resultantes fueron `system-boot` y `writable`. Permanecen pendientes
el primer arranque y la comprobación en la Raspberry de versión, escritorio,
red, SSH y expansión del sistema de archivos; no marcar todavía como completada
la instalación de Ubuntu.

Avance del 20 de agosto de 2026: el primer arranque confirmó una Raspberry Pi
4 Model B con Ubuntu 22.04.5 LTS Desktop ARM64 (`aarch64`). Se conectó por
Wi-Fi en `192.168.0.101`; se instaló y habilitó `openssh-server`, y el acceso
desde el computador principal fue verificado. La actualización propuesta a
Ubuntu 24.04 fue cancelada para conservar compatibilidad con ROS 2 Humble.
La comunicación ROS 2 por Wi-Fi aún no se marca como validada: falta instalar
`ros-humble-demo-nodes-cpp` donde sea necesario y demostrar `talker/listener`
con dominio 42. No se conectaron ni energizaron servos.

Validación completada el 20 de agosto de 2026: con el `talker` en la Raspberry
Pi 4 y el `listener` en el computador principal se recibieron por Wi-Fi los
mensajes `Hello World: 378`--`385` durante aproximadamente 8 s, usando
`ROS_DOMAIN_ID=42` y `ROS_LOCALHOST_ONLY=0`. DDS queda validado para esta red.
La siguiente tarea es clonar y compilar el workspace en la Raspberry; los
actuadores permanecen desconectados.

La primera compilación del workspace en la Raspberry reveló que
`nova_sm3_description/CMakeLists.txt` intentaba instalar una carpeta `worlds`
vacía que no se conserva en Git. Se corrigió el instalador para usar solo
`config`, `launch`, `mujoco`, `rviz` y `urdf`; la corrección está pendiente de
actualizarse en la Raspberry y verificarse allí. No se ejecutaron nodos ni
hardware.

Verificación completada: la Raspberry actualizó al commit `d1e3525`, compiló
los dos paquetes y reconoció `nova_gait_controller` y
`nova_sm3_description`. No se ejecutó ningún launch, controlador, trayectoria
ni componente del PCA9685.

La validación del overlay también quedó completada: existe
`/home/pavilion/nova-spot-micro-tesis/install/setup.bash` y, tras cargarlo,
ambos paquetes aparecen con código de salida 0. No hay nodos, procesos físicos,
adaptadores I2C ni PWM activos. La siguiente fase será preparar I2C/PCA9685
con seguridad eléctrica cerrada.

Prueba I²C completada el 20 de agosto de 2026: con servos y `V+` desconectados,
la Raspberry detectó `0x40` y `0x70` en `i2c-1` mediante `i2cdetect`. El enlace
lógico con el PCA9685 queda validado; la potencia, OE, PWM y actuadores siguen
pendientes y no se ejecutó ningún controlador.

Estado al cierre de sesión: el LM2596 recibe 8 V y entrega aproximadamente 5 V
al rail `V+` del PCA9685; no hay servos conectados ni PWM habilitado. La próxima
sesión comenzará con las mediciones de `VCC`, `V+`, `OE`, tierra común y
protecciones, seguida de una prueba individual con un MG996R en `CH0`, sin
carga mecánica. La marcha del robot y la conexión de los doce servos siguen
bloqueadas.

Criterio de cierre pendiente: referencias articulares convertidas a PWM con
calibraciones medidas, salidas deshabilitadas durante el arranque y
realimentación sensórica sincronizada. La comunicación Raspberry--PCA9685 está
demostrada, pero el PWM instrumental, la interfaz `ros2_control` y la
instrumentación física no están cerrados.

### 9. Transferir progresivamente la marcha nominal

Estado: **prohibido iniciar antes de cerrar caracterización, calibración y
seguridad**.

- [ ] Ejecutar software con PCA9685 deshabilitado.
- [ ] Probar un servo y luego una pata suspendida.
- [ ] Probar cuatro patas con el robot suspendido.
- [ ] Mantener postura sobre el suelo con soporte y parada accesible.
- [ ] Ejecutar transferencia de peso y un paso.
- [ ] Ejecutar un ciclo de gateo y después ciclos continuos.
- [ ] Registrar orientación, corriente, tensión, temperatura, intervención y
  desplazamiento externo.
- [ ] Validar la marcha nominal física antes de cualquier corrección aprendida.

Criterio de cierre: postura, paso y gateo nominales repetibles bajo el protocolo
aprobado y sin eventos de seguridad.

### 10. Desarrollar la capa correctiva de aprendizaje por refuerzo

Estado: **entrenamiento y validación inicial completados; política rechazada**.

- [ ] Definir observaciones disponibles tanto en simulación como en hardware.
- [ ] Definir acciones como correcciones pequeñas de referencias nominales,
  nunca PWM directo.
- [ ] Fijar saturaciones, tasa máxima de cambio y autoridad del supervisor.
- [ ] Formular recompensa, terminaciones y currículo.
- [x] Entrenar inicialmente PPO en un banco reducido con varias semillas.
- [ ] Aleatorizar masas, fricción, centro de masa, ganancias, retardos y ruido.
- [x] Validar la política en Gazebo antes de cualquier transferencia.
- [ ] Conservar configuraciones, semillas, curvas, modelos y versiones.

Criterio de cierre: mejora repetible de métricas físicas frente a la misma
marcha nominal, sin aumentar caídas, saturaciones ni intervenciones.

Actualización del 2 de septiembre: se entrenaron las semillas 11, 23, 37, 53 y
71 y se ejecutaron campañas Gazebo y un barrido de escala residual. Ninguna
escala positiva cumplió el criterio conjunto. La referencia nominal inicial
estaba sesgada por `nominal_03`, ensayo inválido con ciclos de 2,88 s. Al
excluirlo de forma trazable, el nominal quedó en 0,021935 m/ciclo y la escala
0,00 en 0,021878 m/ciclo (-0,258 %), coherentes entre sí. El hallazgo corrige
la comparación, pero no convierte ninguna política en mejora ni autoriza su
transferencia. Véase
`Experimentos/DIAGNOSTICO_REFERENCIA_PPO_ESCALA_CERO_20260902.md`.

### 11. Ejecutar la comparación experimental final

Estado: **fase final**.

Comparaciones obligatorias:

1. marcha nominal sin aprendizaje;
2. la misma marcha nominal con corrección aprendida.

Para `paso` y `gateo` se deberán registrar como mínimo los ciclos y ensayos
aprobados, con condiciones iniciales equivalentes. El análisis incluirá:

- inclinación RMS y máxima;
- avance y velocidad por ciclo;
- desviación lateral;
- variabilidad entre ciclos;
- margen de estabilidad;
- ciclos completados, fallos, caídas e intervenciones;
- corriente, tensión, temperatura y energía si la instrumentación lo permite;
- seguimiento articular solamente si existe medición física real de posición.

Criterio de cierre: conjunto de datos, análisis estadístico, comparación
nominal frente a nominal más RL y trazabilidad completa de cada ensayo.

### 12. Completar y corregir la tesis

Estado: **parcial**.

- [x] Actualizar la matriz objetivo--método--evidencia con el estado real de
  PPO, seguridad y locomoción.
- [x] Incorporar una tabla de síntesis y conservar las tablas cuantitativas de
  cada campaña aceptada.
- [x] Incorporar diagramas de arquitectura funcional y transición física
  segura.
- [x] Actualizar limitaciones y trabajo futuro sin presentar PPO o hardware
  como validados.
- [x] Crear anexos con protocolos, comandos, integridad y reproducibilidad.

- [x] Actualizar la introducción para explicar claramente la comparación con la
  capa correctiva RL.
- [ ] Incorporar los resultados técnicos ya comprobados sin presentar el
  modelo provisional como gemelo digital.
- [ ] Definir el nivel de modelado dinámico entregado y eliminar contradicciones
  de alcance.
- [ ] Corregir el presupuesto: suma directa de 1.591.800 COP frente al resumen
  de 2.029.270 COP y aclarar el precio de los 12 DS18B20.
- [ ] Eliminar o reemplazar el texto de plantilla de `AppendixA.tex` antes de
  incluir apéndices.
- [ ] Mantener una sola bibliografía mediante `\printbibliography`; no usar la
  lista manual de `Chapters/11 Referencias.tex`.
- [ ] Actualizar metodología, cronograma y trazabilidad según el protocolo
  definitivo.
- [ ] Incorporar tablas, gráficas, limitaciones y resultados de la comparación.

Criterio de cierre: PDF final compilado, objetivos trazables a resultados y
afirmaciones respaldadas por evidencia experimental.

Actualización documental del 15 de septiembre de 2026: se amplió la
introducción de `Documento_TESIS/Chapters/1 Introducción.tex` para explicar que
la comparación central es marcha nominal frente a la misma marcha con corrección
aprendida, acotada y supervisada. La redacción vincula la evaluación con margen
estático, seguimiento articular y repetibilidad, y conserva explícito que las
campañas PPO disponibles son resultados negativos que no autorizan transferencia
al prototipo físico. El PDF recompiló correctamente en
`Documento_TESIS/Documento_TESIS_PRELIMINAR.pdf` con 78 páginas. Siguiente
acción documental: incorporar resultados técnicos ya comprobados sin presentar
el modelo provisional como gemelo digital y revisar las contradicciones de
alcance del modelado dinámico.

Actualización documental del 2 de septiembre de 2026: los cinco productos
anteriores quedaron integrados en el PDF. La matriz viva corrigió OE4 como
entrenado pero no aceptado y OE5 como comparación parcial no concluyente. Se
añadieron una tabla ejecutiva de resultados, un segundo diagrama de arquitectura
y el Apéndice A con protocolos, comandos, reglas de exclusión y transición al
hardware. El PDF compiló en 74 páginas. La tesis continúa parcial porque aún
faltan resultados físicos y una comparación final emparejada, no por ausencia
de estructura documental.

## Próxima acción concreta

Actualización del 3 de septiembre de 2026: se depuró el ejecutor de campañas
MuJoCo. La tercera repetición de `paso_5x20_r2_20260902` es inválida porque no
capturó órdenes de marcha. Una validación aislada posterior registró 96
referencias, tres ciclos y seis marcadores sin retrocesos de reloj; otra prueba
confirmó el apagado acotado. Los paquetes compilaron y pasaron 98 pruebas. La
próxima campaña MuJoCo 5x20 debe comenzar en una carpeta nueva y usar una
instancia independiente por ensayo; las pruebas cortas no entran en resultados.

Campaña completada el 3 de septiembre: cinco ensayos independientes de marcha
paso en MuJoCo, cada uno con 21 ciclos completos, 672 referencias, nueve
marcadores y cero activaciones del supervisor. Para la comparación se usaron
los ciclos 2--20. El avance fue 0,002701937 m/ciclo, roll máximo 0,646314°,
pitch máximo 1,787264° y error RMS articular 0,010531 rad; el CV del avance fue
0,020555 %. La coincidencia simultánea de contactos permaneció en 0 %, así que
la campaña demuestra repetibilidad computacional, no equivalencia dinámica.
Evidencia en `Experimentos/campanas_mujoco/paso_5x20_aislada_r3_20260903`.

Las pruebas dinámicas provocadas del supervisor quedaron cerradas. La prioridad
inmediata pasa a la fase física F0, todavía sin energizar: terminar e
inspeccionar el ensamble, identificar los dos servos sustituidos, trazar
CH0--CH11, completar fotografías y medir geometría y masa. El orden completo de
puertas F0--F4 está en
`Raspberry/PLAN_VALIDACION_FISICA_DESPUES_SIMULACION_2026-09-02.md`.

Sin modificar la longitud de paso de 18 mm, la elevación máxima de 14 mm ni la
cadencia de 0,18 s por referencia:

1. revisar la correspondencia entre ausencia de mensajes, despegue real,
   recontacto breve y `touchdown`; **completado el 1 de septiembre**: los
   episodios traseros crudos duran menos de 0,09 s y no constituyen vuelo
   sostenido;
2. diseñar una corrección nueva de liberación trasera que produzca una pérdida
   filtrada sostenida sin aumentar la altura
   temprana por encima de 0,80 ni exceda 0,20 rad;
3. completar la caracterización física con
   `Documentacion/FICHA_CARACTERIZACION_FISICA.md`;
4. obtener las decisiones del profesor mediante
   `Documentacion/FICHA_APROBACION_PROTOCOLO.md`;
5. repetir en Gazebo frente a nominal y 0,20/0,75 solo después de definir una
   hipótesis nueva y verificable.
6. mientras termina la integración mecánica, confirmar las tarjetas de
   instrumentación y diseñar el prototipo de un AS5600 para una sola
   articulación, sin conectar todavía los doce sensores.

El supervisor de contactos seguirá informativo durante esta corrección. No se
debe transferir PPO ni mover el hardware hasta superar las etapas que lo
bloquean. Una nueva campaña PPO solo procede después de corregir la política y
debe usar cinco ensayos emparejados de 20 ciclos con validación automática de
cadencia e instancia única.

## Propuesta de instrumentación física del 31 de agosto de 2026

Se documentó en
`Documentacion/PROPUESTA_INSTRUMENTACION_FISICA_2026-08-31.md` una arquitectura
preliminar con doce AS5600, dos TCA9548A, BNO055, cuatro contactos de pie y un
INA228 global. El objetivo es disponer de ángulos reales, error de seguimiento,
orientación, contacto y consumo para validar el modelo y definir las futuras
observaciones de RL. ToF, celdas de carga completas y temperatura se aplazan.

Solo queda cerrada la selección conceptual; compra, montaje, cableado,
calibración y funcionamiento permanecen pendientes. El siguiente hito es un
AS5600 en una articulación y después tres en una pata, con medición explícita de
alineación, repetibilidad, holgura, ruido, latencia y frecuencia. La política
aprendida, cuando se autorice, actuará únicamente mediante correcciones
acotadas de referencias nominales y no mediante PWM directo.

## Regla de actualización

Al finalizar cada sesión, marcar únicamente tareas demostradas con evidencia,
registrar el archivo o prueba correspondiente y cambiar la próxima acción
concreta. No marcar como terminado algo que solo se haya propuesto o visto
funcionar una vez.

Cada cambio realizado por cualquiera de los integrantes debe quedar notificado
en GitHub: se debe crear un commit descriptivo y subirlo al repositorio público
`https://github.com/davidediaz/nova-spot-micro-tesis`. La notificación debe
resumir fecha, archivos modificados, motivo, pruebas o evidencia, resultado y
siguiente acción. Para cambios de código o documentación se recomienda trabajar
en una rama y abrir un Pull Request hacia `main`; no se deben dejar cambios
locales sin sincronizar ni reescribir silenciosamente el historial experimental.

## Actualización de hardware del 24 de agosto de 2026

Se verificó en la Raspberry Pi 4 el Arduino Mega 2560 R3 por `/dev/ttyACM0` y
la detección del PCA9685 en `0x40`, tras corregir SDA y SCL invertidos. Con
alimentación externa para los MG996R se avanzó desde pruebas individuales hasta
un barrido simultáneo de `CH5`--`CH10` a 60 Hz entre 1300 y 1700 microsegundos.
Los canales restantes permanecen en `FULL_OFF`.

Este resultado sustituye el estado anterior de «servos todavía no conectados»,
pero no cierra la caracterización ni habilita una marcha. Permanecen pendientes
la correspondencia canal-articulación, calibración independiente, ensayo de la
fuente bajo carga y parada física segura mediante OE con pull-up. Evidencia:
`Raspberry/AVANCES_PCA9685_2026-08-24.md`.

## Automatización de pruebas del 2 de septiembre de 2026

Se añadieron validaciones automáticas de límites articulares, continuidad entre
referencias, pérdida de contacto esperado, altura, inclinación y condiciones de
seguridad. Pasan 80 pruebas Python y el flujo de GitHub Actions compila y prueba
los paquetes en cada `push` y `pull_request`. Las pruebas integradas provocadas
en los simuladores y la validación física siguen pendientes; no deben marcarse
como completadas a partir de esta suite determinista.

## Campañas MuJoCo y ajuste de marcha del 3 de septiembre de 2026

Se completaron barridos de transferencia, altura, fricción y ganancias, una
campaña de paso 5×20 ajustada y una campaña de gateo 5×20. El ajuste seleccionado
(15 mm, 12 mm, kp/kv 80/8) alcanzó 9,867 mm/ciclo y 36,58 % de coincidencia de
contacto; gateo alcanzó 6,304 mm/ciclo y 67,46 %. Los empujes de 1–3 N quedaron
registrados, pero ruido/retardos y calibración física siguen pendientes. Ver
`Documentacion/MUJOCO_CIERRE_2026-09-03.md`.

## Estado de hardware real al 4 de septiembre de 2026

Los doce canales respondieron con fuente externa y se confirmó una postura
neutra estable. Una sobrecarga de corriente obligó a apagar la Raspberry y
mantener desconectada la fuente de servos. La próxima sesión debe verificar el
PCA9685 sin carga, resolver CH1 y medir el consumo antes de cualquier marcha.

## Preparación de primera entrega — 7 de septiembre de 2026

Se prepararon seis diapositivas en PowerPoint/PDF y una guía de 8:30 minutos en
`ProyectoII_Clases/07_09_2026`. PDF verificado visualmente. La rúbrica de avance
y el compromiso son propuestas explícitas; no cambian el cumplimiento técnico
de los objetivos. La guía incluye fuentes y respuestas a las ocho preguntas
del profesor. Pendiente: revisar con el grupo, ensayar y actualizar la tesis con
las campañas MuJoCo del 3 de septiembre, la incidencia física del 4 y las
conclusiones desactualizadas sobre PPO. No se ejecutaron pruebas de hardware.

### Evidencia fotográfica — 7 de septiembre de 2026

Se incorporaron las cinco fotografías suministradas a `Github/BITACORA.html`,
`Github/PROGRESO_SEMANAL.md` y a la presentación de seis diapositivas
`Primera_entrega_avances_con_fotos`. Originales íntegros y hashes en
`Github/evidencias/2026-09-07`. Se verificaron copias, enlaces y distribución
visual del PDF. Documentan construcción e integración, sin cambiar porcentajes
ni declarar marcha o seguridad física validadas. Captura sin fecha confirmada.

Se añadió a la exposición una captura nativa actual de Gazebo del modelo Nova,
sin generar resultados experimentales nuevos. Versión vigente:
`ProyectoII_Clases/07_09_2026/Primera_entrega_avances_gazebo.pdf` y PowerPoint.
Conserva seis diapositivas y las cinco fotografías del prototipo.

La versión vigente de exposición es `Primera_entrega_avances_sencilla` (PDF y
PowerPoint), con seis diapositivas, imágenes conservadas y `GUION_SENCILLO.md`.
Se simplificó el lenguaje sin modificar los resultados ni el estado técnico.

Por autorización del usuario, la exposición pasó a siete diapositivas con una
tabla adicional de objetivos, estado, porcentajes y faltantes en la posición 3.
Versión: `Primera_entrega_avances_7_diapositivas`. Guion y numeración actualizados;
la ampliación no modifica el cumplimiento técnico de los objetivos.

### Referencias oficiales para OE1 — 7 de septiembre de 2026

Se contrastaron cinco dimensiones nominales y la masa aproximada con fuentes
del autor. Informe: `Documentacion/CONTRASTE_FUENTES_OFICIALES_NOVA_2026-09-07.md`.
El diseño oficial usa motores diferentes; sus límites PWM no validan los
MG996R locales. La caracterización física permanece pendiente y las columnas
de mediciones se conservan vacías.

Se sincronizaron objetivos, matriz, metodología, alcance, conclusiones y presentación. PDF de tesis: 72 páginas; presentación: siete diapositivas, versión `Primera_entrega_avances_objetivos_corregidos`. Sin ensayos nuevos ni cumplimiento adicional.

### Actualización integral de seguimiento — 7 de septiembre de 2026

El panel público, la ruta operativa, el README y el progreso semanal quedaron
alineados con los cuatro objetivos oficiales. El estado se mantiene parcial:
OE1/OE2 con base nominal, OE3 con cinco PPO sin mejora aceptada y OE4 con las
tres pruebas aún por cerrar. Se priorizan mediciones físicas, diagnóstico de
sobrecarga y seguridad, además del acuerdo de alcance con los directores.
### 4. Diseñar la retroalimentación sensórica para aprendizaje por refuerzo

Estado: **pendiente de diseño y validación en el cuadrúpedo físico**.

El agente de aprendizaje no debe recibir únicamente referencias ideales del
simulador. La observación debe construirse con señales que también puedan
medirse en el robot real:

- [ ] **Estado articular:** posición de las 12 articulaciones y, si es posible,
  velocidad estimada. Los MG996R no entregan posición por PWM; se debe decidir
  entre servos con realimentación, potenciómetros, encoders u otra medición
  externa.
- [ ] **Estado corporal:** IMU con orientación, velocidad angular y aceleración,
  con reloj común para sincronizarla con las articulaciones.
- [ ] **Contacto de los pies:** cuatro sensores de contacto o fuerza para saber
  qué patas están apoyadas. La corriente del servo puede servir como diagnóstico,
  pero no debe sustituir el contacto si se necesita una señal confiable.
- [ ] **Salud del sistema:** tensión, corriente, temperatura, pérdida de
  comunicación y estado del supervisor para terminar un episodio con seguridad.
- [ ] **Comandos y fase:** velocidad o dirección solicitada, modo de marcha y
  fase del ciclo, usando las mismas unidades y convenciones en simulación y
  hardware.
- [ ] **Contrato de datos:** nombres de tópicos, unidades, marcas de tiempo,
  frecuencia efectiva, filtros, valores ausentes y límites de saturación.
- [ ] **Correspondencia simulación--hardware:** generar en Gazebo/MuJoCo las
  mismas observaciones, retardos, ruido, saturaciones y fallos que se medirán
  físicamente antes de entrenar o transferir una política.

La acción del agente debe ser una referencia articular o corrección acotada,
pasada por límites y por el supervisor; no debe comandar PWM directamente. El
criterio de cierre será una prueba de registro en la que todas las señales
seleccionadas se reciban sincronizadas durante una postura y una marcha manual,
antes de usarlas para aprendizaje por refuerzo.

## Reconexión a la Raspberry para pruebas físicas — 15 de septiembre de 2026

La IP histórica `192.168.0.101` no respondió porque el computador está ahora en
la red `10.217.224.0/24`. Se localizó la Raspberry Pi 4 como `cuadrupedo-pi` en
`10.217.224.198` y se verificó el acceso SSH con el usuario `pavilion`. La placa
reportó Ubuntu 22.04.5 LTS ARM64, workspace en el commit `3900edd`, PCA9685 en
`0x40` y `0x70`, sin procesos ROS/control activos y sin dispositivos seriales
detectados.

La configuración remota mantiene `hardware_ready: false` y las doce
articulaciones sin calibrar; no se ejecutó PWM ni movimiento. Resultado: conexión
recuperada, pero las puertas F0--F1 y la calibración individual siguen siendo
requisito previo para las pruebas físicas.

## Pruebas físicas iniciales de las doce articulaciones — 15 de septiembre de 2026

En la Raspberry se leyó `Raspberry/AVANCES_PRUEBA_COXAS_2026-09-15.md`. Con el
robot elevado y el PCA9685 alimentado externamente se probaron manualmente las
cuatro coxas (`CH0--CH3`), los cuatro fémures (`CH4--CH7`) y las cuatro tibias
(`CH8--CH11`). Las doce articulaciones respondieron y cada script retornó los
servos al centro al finalizar.

La pata delantera derecha requiere inversión de sentido en `CH0`, `CH4` y
`CH8`; el resto respondió según el mapa preliminar. Esta evidencia confirma
respuesta y correspondencia inicial de canales, no calibración: siguen vacíos
los centros, límites, velocidades, corrientes y torques medidos. Se mantiene
bloqueada la postura, la marcha ROS 2 y la prueba sobre el suelo hasta cerrar
F0--F2.

También se detectó que la referencia `main` del Git remoto apunta a un objeto
corrupto, aunque el reflog conserva commits de trabajo de la sesión. No se
intentó reparar el repositorio durante esta revisión.

## Esquema visual de conexiones físicas — 15 de septiembre de 2026

Se registró `Raspberry/documentacion/ESQUEMA_CONEXIONES_FISICAS_2026-09-15.jpeg`
como evidencia de la numeración física del cuadrúpedo y la asignación de
servos. Su SHA-256 es
`d95ac074483b94d3ea6d44efa418563393787610b46c6a0e9ff226fceeb60f36`; la misma
imagen fue copiada al workspace de la Raspberry.

La referencia confirma Pata 1 delantera derecha, Pata 2 delantera izquierda,
Pata 3 trasera derecha y Pata 4 trasera izquierda, con coxas en `CH0--CH3`,
fémures en `CH4--CH7` y tibias en `CH8--CH11`. Se corrigió la tabla local de
`Raspberry/CONEXIONES.md` para alinearla con la imagen, `servos.yaml` y los
scripts de prueba remotos. La imagen documenta conexiones y numeración, pero no
autoriza por sí sola energización, calibración ni marcha.

## Configuración remota alineada con la identificación física — 15 de septiembre de 2026

Se corrigió y sincronizó en la Raspberry `Raspberry/configuracion/servos.yaml`
para reflejar el mapa de la imagen y las pruebas físicas: coxas `CH0--CH3`,
fémures `CH4--CH7` y tibias `CH8--CH11`. La pata delantera derecha conserva la
inversión comprobada en `CH0`, `CH4` y `CH8`. Se mantuvieron `hardware_ready:
false`, `calibrated: false` y los límites provisionales. La configuración fue
verificada remotamente sin procesos de movimiento activos; la marcha continúa
bloqueada hasta completar calibración individual y validación progresiva.

## Intento controlado de prueba en CH0 y pérdida de I²C — 15 de septiembre de 2026

Se intentó iniciar la calibración limitada de `CH0` con `OE` físico, los demás
canales apagados, recorrido de 1450--1550 us y retorno al centro. La primera
escritura al PCA9685 produjo `OSError: [Errno 121] Remote I/O error`; no se armó
PWM ni se produjo movimiento.

La verificación posterior confirmó que `i2cdetect -y 1` no detecta `0x40` ni
`0x70`, y la lectura del registro del PCA9685 falla. No se reintentará la prueba
hasta revisar VCC, GND, SDA, SCL y la alimentación de la tarjeta, y confirmar
que `0x40` reaparece de manera estable.

## Prueba limitada de CH0 ejecutada tras recuperar I²C — 15 de septiembre de 2026

Con `0x40` y `0x70` nuevamente visibles y el registro `0x00` respondiendo
`0x11`, se ejecutó únicamente `CH0` con `OE` físico en GPIO 17. Los canales
restantes permanecieron en `FULL_OFF`; la secuencia fue `1500 -> 1550 -> 1450
-> 1500 us`. El proceso terminó correctamente, centró `CH0` y apagó el PWM
global. Se confirma la comunicación y la ejecución del comando, pero la
respuesta mecánica debe anotarse según la observación presencial antes de
continuar con otro canal.

La observación presencial informó que `CH0` no se movió. Se bloquean nuevos
recorridos y pruebas multicanal hasta medir `V+` en el conector del servo,
comprobar el estado de `OE` durante la habilitación, revisar señal/tierra y
confirmar la correspondencia física del servo con `CH0`.

Se repitió `CH0` sin control software de `OE`, con `CH1--CH15` apagados y
recorrido `1500 -> 1550 -> 1450 -> 1500 us`; el proceso terminó sin error, pero
el servo tampoco se movió. La comunicación I²C no demuestra por sí sola que
exista PWM físico en la salida. Antes de otra orden se debe medir `CH0` con
osciloscopio/analizador o conectar allí un servo conocido, manteniendo bloqueada
la caminata.

Se repitió la prueba con el rango del script de Thonny, `1350 -> 1650 -> 1350
-> 1500 us`, pasos de 5 us y únicamente `CH0` activo. El operador confirmó el
movimiento; el proceso terminó correctamente, centró el servo y apagó el PWM.
El rango de +/-50 us era insuficiente para observar respuesta mecánica. La
calibración formal de centro, límites y velocidad de `CH0` continúa pendiente.

## Movimiento de la Pata 1 — 15 de septiembre de 2026

Se probó la Pata 1 con `CH0` (coxa), `CH4` (fémur) y `CH8` (tibia), de forma
secuencial, con recorrido `1350--1650 us`, retorno al centro y el resto de
canales apagados. El operador observó movimiento ascendente de la pata. Esto
confirma respuesta mecánica conjunta en la asignación física actual, pero no
calibración angular ni marcha; la calibración se completará con la
realimentación de AS5600 mediante TCA9548A.

## Programa de posición de referencia visual — 15 de septiembre de 2026

Se creó `Raspberry/codigo/posicionar_pata_referencia.py`, que permite
seleccionar una pata, mantener sus tres articulaciones en `1500 us` durante
ocho segundos para tomar una fotografía y apagar el PWM automáticamente. Es
una referencia visual provisional, no una calibración angular ni una postura de
marcha; la calibración definitiva usará AS5600 y TCA9548A.

## Visor 3D local para postura inicial — 15 de septiembre de 2026

Se implementó `Experimentos/visor_pose_inicial_3d.py`. Se ejecuta en el PC sin
ROS ni conexión con actuadores, muestra la geometría nominal del cuadrúpedo,
resalta una pata y ofrece controles para coxa, fémur y tibia, reinicio y
guardado de captura PNG. La generación de la figura fue verificada
correctamente en backend no interactivo. Sirve para comparar la posición
visual del prototipo; no sustituye la realimentación de AS5600.

Se añadieron botones `Pata 1`--`Pata 4` para cambiar la pata seleccionada dentro
de la misma ventana y conservar independientemente sus tres valores articulares.
La pata activa queda resaltada y la figura de prueba se generó correctamente.

Se envió a la Raspberry la postura provisional de Pata 1 seleccionada en el
visor 3D: `(0.02, 0.03, -0.03)` rad, usando `CH0=1494 us`, `CH4=1490 us` y
`CH8=1509 us` durante tres segundos. Los demás canales quedaron apagados y el
PWM se deshabilitó al terminar. La respuesta física y el ajuste del modelo se
completarán con la fotografía del prototipo; no se considera calibración.

El operador colocó manualmente la Pata 1 para hacer coincidir el prototipo con
el visor 3D y guardó `Experimentos/pose_inicial_3d.png`. La referencia visual
actual muestra aproximadamente `q_coxa=0.03 rad`, `q_femur=0.02 rad` y
`q_tibia=-0.01 rad`. No se enviaron estos valores como PWM ni se consideran
calibración de los servos; la medición real dependerá de AS5600 y TCA9548A.

En una segunda referencia visual, el operador ajustó manualmente la Pata 1 a
`q_coxa=-0.47 rad`, `q_femur=-1.20 rad` y `q_tibia=-2.20 rad`. El control 3D de
tibia se amplió hasta `-3.00 rad` únicamente para exploración; no se cambiaron
los límites físicos del modelo ni se enviaron estos valores como PWM.

En la Pata 2 el operador observó que la coxa quedó más metida y ajustó el visor
aproximadamente a `q_coxa=-0.60 rad`, `q_femur=-0.10 rad` y `q_tibia=-0.01 rad`.
La coxa alcanzó el límite inferior provisional del modelo. Se conserva como
referencia visual, sin marcar calibración ni modificar los límites físicos.

El visor 3D amplió el rango visual de coxa hasta `-1.00 rad` para representar
la postura observada de la Pata 2. La generación de una figura con `-0.90 rad`
funcionó correctamente. El rango ampliado es exploratorio y no cambia los
límites físicos, el URDF ni la configuración PWM.

## Corrección de longitud física de la coxa — 15 de septiembre de 2026

Se recibió la observación de que el tramo entre coxa y fémur resulta largo en
el montaje y que su medida física es `1.5 in` (`0.0381 m`). Se actualizó la
longitud del segmento en `kinematics.py`, `nova_sm3.urdf.xacro` y en los cuatro
eslabones equivalentes de `nova_sm3.xml`. Se conservaron las posiciones de las
caderas del chasis, que son referencias de montaje distintas de la longitud
de la coxa. La modificación es provisional hasta medir las cuatro patas con
mayor precisión y contrastar los ángulos mediante AS5600.

La medición complementaria estableció inicialmente `4.5 in` (`0.1143 m`) para el fémur y
inicialmente `5.5 in` (`0.1397 m`) para el tramo tibia-piso. Se actualizaron las constantes
de cinemática y los modelos URDF/MJCF; los límites angulares y PWM permanecen
sin cambios.

Corrección posterior del operador: el tramo coxa-fémur mide `4.25 in`
(`0.10795 m`). Se actualizó el fémur en cinemática, visor, URDF y MJCF; la
tibia se corrigió posteriormente a `5.35 in` (`0.13589 m`).

Corrección posterior: el tramo tibia-piso mide `5.35 in` (`0.13589 m`). Se
actualizó `TIBIA_LENGTH` y la geometría correspondiente del visor, URDF y MJCF.

## Confirmación de prueba de las cuatro coxas y lección operativa — 15 de septiembre de 2026

El operador confirmó que las cuatro coxas respondieron correctamente en la
Raspberry. La incidencia de esta sesión fue de coordinación: Thonny mantenía
abierto `prueba_coxas_thonny.py` y se intentó preparar otro controlador; además,
`cuadrupedo-pi` resolvió a `10.58.164.198`, mientras la IP SSH accesible era
`10.217.224.198`. No se debe iniciar un segundo programa que controle el
PCA9685. Para la siguiente prueba se verificará proceso activo, IP accesible,
PCA9685 en `0x40` y una única secuencia acotada antes de energizar o mover la
pata. La prueba de coxas queda registrada como exitosa.

Se ejecutó la prueba controlada de la Pata 1 con `CH0` (coxa), `CH4` (fémur)
y `CH8` (tibia), usando la referencia angular provisional
`q=(0.04, 0.0, 0.0) rad`. Cada canal recorrió individualmente `1350--1650 us`,
con los demás apagados. El comando terminó correctamente, centró los canales
y deshabilitó el PWM. La reacción mecánica y el sentido de cada servo aún
deben ser reportados por observación física.

### Cierre de sesión de pruebas físicas — 15 de septiembre de 2026

Se guardó el estado de la sesión para retomarlo posteriormente. La Raspberry
quedó verificada en `10.217.224.198`, el PCA9685 respondió en `0x40`, Thonny se
detuvo y la prueba de Pata 1 terminó con `CH0`, `CH4` y `CH8` centrados y PWM
apagado. Queda pendiente anotar el sentido y la reacción mecánica observados
en cada servo antes de realizar nuevas pruebas.

## Entrenamiento PPO en ambos simuladores con geometría medida — 24 de septiembre de 2026

Se centralizaron en la cinemática las dimensiones empleadas por el visor 3D y
los entrenadores: separación de caderas `0,180 x 0,120 m`, cuerpo
`0,230 x 0,120 x 0,075 m`, coxa `0,0381 m`, fémur `0,10795 m` y tibia
`0,13589 m`. Se corrigió además el comentario inconsistente del URDF sobre el
fémur. Los límites físicos y PWM continúan provisionales.

Se implementaron dos adaptadores PPO residual con el mismo contrato de 27
observaciones y 12 correcciones articulares acotadas:

- `Experimentos/entrenar_ppo_mujoco.py` entrena directamente sobre el MJCF y
  aplica aleatorización moderada de fricción y amortiguamiento.
- `Experimentos/entrenar_ppo_gazebo.py` entrena mediante ROS 2 sobre Gazebo,
  sincronizando una acción con cada fase de `/nova/gait_phase`.

La conexión externa se añadió a `ppo_residual_node` mediante
`/nova/rl_action`; el nodo conserva límites de `0,08 rad` y cambio máximo de
`0,02 rad` por paso. Esto no modifica el camino del hardware.

La semilla 11 completó 20.480 pasos efectivos en MuJoCo y 1.024 pasos en
Gazebo. Las políticas, metadatos y trazas están en:
`Experimentos/entrenamiento_ppo_mujoco_20260924/crawl_semilla_11` y
`Experimentos/entrenamiento_ppo_gazebo_20260924/crawl_semilla_11`.

Verificación: 99 pruebas Python aprobadas, `check_env` de MuJoCo aprobado,
compilación de ambos paquetes ROS 2 aprobada y ningún proceso de simulación
remanente. La primera evaluación MuJoCo mostró más avance con PPO, pero mayor
inclinación; por tanto, no se acepta todavía la política. Falta ejecutar la
evaluación emparejada en Gazebo y MuJoCo, repetir las cinco semillas aprobadas
y documentar el criterio de selección. PPO sigue prohibido en el hardware.

## Campaña PPO completa de las dos caminatas — 24 de septiembre de 2026

Se incorporó `Experimentos/campana_ppo_completa.py` y se ejecutó la matriz de
gateo y paso para las semillas `11, 23, 37, 53, 71` en ambos simuladores. Los
resultados y trazas están en
`Experimentos/reentrenamiento_ppo_completo_20260924/INFORME.md`. MuJoCo hizo
50.176 pasos efectivos por política y Gazebo 1.024 pasos efectivos por
política.

La evaluación emparejada de MuJoCo se guardó en `mujoco_evaluation.csv` con
cinco episodios nominales y cinco PPO por política. La selección offline
conservadora actual es gateo semilla 53 y paso semilla 71; no se autoriza
transferencia al robot.

Se encontró y corrigió un defecto de integración: `/nova/rl_action` se
limitaba, pero no se aplicaba a la trayectoria nominal. La primera tanda de
Gazebo se interrumpió y se regeneró después de corregirlo. Gazebo queda
pendiente de una fase de convergencia con más pasos y evaluación nominal/PPO.

La evaluación nominal/PPO de Gazebo se completó para las 10 políticas y se
guardó en `gazebo_evaluation.csv`. Los promedios de retorno fueron `108,54`
frente a `94,93` en gateo y `139,28` frente a `110,49` en paso; por ahora no
se acepta ninguna política de Gazebo y se requiere más presupuesto de
entrenamiento y más episodios de evaluación.

## Reentrenamiento largo de gateo y paso — 24 de septiembre de 2026

Se continuó PPO en Gazebo desde las políticas MuJoCo gateo-53 y paso-71. Cada
corrida completó 20.480 pasos efectivos y dejó `policy.zip`, metadatos,
checkpoints y trazas en `Experimentos/reentrenamiento_ppo_largo_20260924/`.
La validación de tres episodios mejoró el avance del gateo (`0,1143` a
`0,1276 m`) y redujo levemente su inclinación; la política de paso redujo el
avance (`0,0933` a `0,0312 m`) y no se acepta todavía. Ningún parámetro fue
enviado a servos o Raspberry Pi.

El proceso completo quedó guardado en
`Experimentos/reentrenamiento_ppo_largo_20260924/PROCESO_COMPLETO.md`, junto
con las rutas de políticas, checkpoints, trazas, evaluaciones y restricciones
de seguridad.

### Actualización del registro — 24 de septiembre de 2026

Se confirmó la conservación local de todos los artefactos del entrenamiento y
de la documentación asociada. No se eliminaron cambios existentes ni se
transfirieron políticas a la Raspberry Pi. El estado vigente sigue siendo:
gateo semilla 53 como candidato offline; paso semilla 71 pendiente de mejorar
su avance antes de considerarlo aceptable; hardware bloqueado hasta completar
calibración, alimentación, supervisión y pruebas físicas controladas.

## Reentrenamiento PPO extendido de las dos marchas — 25 de septiembre de 2026

Se abrió la campaña independiente
`Experimentos/reentrenamiento_ppo_extendido_20260925`, sin modificar las
campañas históricas. El entorno aislado se verificó con Gymnasium 0.29.1,
Stable-Baselines3 2.3.2, PyTorch CPU 2.3.1 y MuJoCo 3.9.0.

Se reentrenaron en MuJoCo las candidatas gateo semilla 53 y paso semilla 71,
con 200.000 pasos solicitados y 200.704 efectivos por política por el rollout
de PPO de 1.024 pasos. Se conservó la geometría medida, el contrato de 27
observaciones/12 acciones residuales, `±0,08 rad`, `0,02 rad` por cambio y
`hardware_transfer=false`. Los artefactos, metadatos, trazas y evaluación están
en la carpeta de la campaña.

La evaluación emparejada de cinco episodios por marcha fue:

| Marcha | Condición | Retorno | Avance (m) | Inclinación máxima (rad) |
| --- | --- | ---: | ---: | ---: |
| Gateo | nominal | 1091,31 | 0,4917 | 0,00993 |
| Gateo | PPO extendido | 1095,71 | 1,2860 | 0,03505 |
| Paso | nominal | 1451,30 | 0,0155 | 0,01392 |
| Paso | PPO extendido | 1497,67 | 3,5561 | 0,04289 |

El aumento de avance no basta para aceptar las políticas: ambas presentan más
inclinación y requieren evaluación con más escenarios y criterio de estabilidad.
Se intentó adaptación en Gazebo con 50.000 pasos para gateo, pero la corrida se
detuvo en 500 pasos por el costo de tiempo casi real; no produjo política final.
La adaptación de paso en Gazebo queda pendiente. El intento parcial no se usa
como resultado de convergencia.

Estado: entrenamiento MuJoCo de ambas marchas completado; políticas pendientes
de aceptación; Gazebo pendiente de adaptación extendida; transferencia física
prohibida.

## Preparación de adquisición articular AS5600 — 28 de septiembre de 2026

Se preparó `Raspberry/codigo/leer_as5600_tca.py` para leer AS5600 mediante los
TCA9548A `0x70` y `0x71` por I2C-1 de la Raspberry. Es una utilidad de solo
lectura: no inicializa PCA9685, OE ni PWM. Produce valores crudos, grados
absolutos y marca temporal; todavía no representa posición articular calibrada.

El bus se comparte con PCA9685 por GPIO2/pin 3 (SDA) y GPIO3/pin 5 (SCL), con
GND común y lógica de 3,3 V. La asociación `0x71`/canal 3 se mantiene pendiente
porque el sketch recibido duplica «fémur 2» y omite «coxa 2». Falta escanear el
bus con servos desenergizados, hacer una lectura única, verificar esa
asociación y medir cero, sentido, rango, ruido y repetibilidad antes de integrar
el tópico `/nova/joint_states_measured` o habilitar movimientos.

### Primera lectura en Raspberry — 28 de septiembre de 2026

Una lectura única, sin PWM ni movimiento, confirmó `0x40`, `0x70` y `0x71` en
I2C-1. Respondieron nueve rutas AS5600; `0x70` canales 6--7 y `0x71` canal 2
fallaron con error I2C 121. `0x71` canal 3 responde pero todavía no tiene
articulación identificada. El registro, valores y protocolo siguiente están en
`Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`. La adquisición queda parcial y
no habilita PWM, postura, marcha ni observaciones para PPO.

Corrección del operador: esos tres canales sin respuesta están vacíos por
diseño. El mapa de doce sensores queda en `0x70` 0--5 y `0x71` 0, 1, 3, 4, 5 y
6, con articulaciones confirmadas en el informe de lectura. El lector se
actualizó y falta un barrido completo con dicho mapa antes de medir cero,
sentido, rango y repetibilidad.

El barrido posterior del mapa actualizado respondió en las doce rutas. Queda
confirmada la comunicación básica de todos los AS5600; no queda cerrada su
calibración ni se habilitan posturas o caminatas hasta medir estabilidad, cero,
sentido, rango y holgura.

### Cierre de caracterización pasiva AS5600 — 28 de septiembre de 2026

Se completaron capturas de referencia y de ambos extremos manuales para las
doce articulaciones, con ventanas de veinte muestras por extremo. La tabla
consolidada y las limitaciones están en
`Raspberry/RESUMEN_CARACTERIZACION_AS5600_2026-09-28.md`; las estadísticas
quedan en `Raspberry/configuracion/as5600_caracterizacion_provisional.yaml`.
Coxa 2, coxa 3 y tibia 3 muestran dispersión relevante y no se autorizan para
realimentación cerrada. Las lecturas son grados absolutos de encoder: todavía
no están calibradas contra cero, sentido y límites del modelo. No se ordenó
PWM ni marcha. Próximo paso: calibración angular con cruce circular, pruebas
repetibles de una articulación a la vez, márgenes de tope y validación de parada
segura antes de cualquier movimiento motorizado.

### Captura antihoraria de tibias — 28 de septiembre de 2026

Se tomaron veinte muestras por tibia en el extremo antihorario: P1 203,379°
(rango 0,000°), P2 249,811° (0,088°), P3 37,446° (5,713°) y P4 303,047°
(0,000°). P3 se conserva como inestable; las otras tres fueron estables durante
la toma. Los datos se guardaron en
`Raspberry/configuracion/as5600_caracterizacion_provisional.yaml` y el detalle
en `Raspberry/LECTURA_AS5600_TCA_2026-09-28.md`. Los extremos son referencias
provisionales, no límites de control; faltan márgenes y validación de seguridad.

### Campaña step de 80 semillas recibida desde JULI — 28 de septiembre de 2026

Se transfirió por SSH verificado la campaña completa MuJoCo step desde el equipo
JULI, sin alterar la fuente. Se comprobaron las 80 políticas, 160 filas de
evaluación y las sumas SHA-256. Quedó guardada en
`Experimentos/campana_distribuida_step_s23_20260928`, con el código incremental,
en la rama local `resultados/mujoco-step-80-semillas-20260928` (commit
`106ee5a`). No se ha subido aún a GitHub ni se aprueban políticas para hardware.
Las carpetas PPO locales sin seguimiento se preservaron.

El análisis está en
`Experimentos/campana_distribuida_step_s23_20260928/INFORME_ANALISIS_80_SEMILLAS.md`:
el avance medio mejora +2,903 m (78/80) y el retorno +34,18 (76/80), mientras
la inclinación reportada empeora en 80/80 semillas (+0,03342 rad de media).
Ninguna política domina la nominal en avance e inclinación. Faltan pruebas con
episodios/escenarios nuevos y aleatorización ambiental antes de elegir candidatas.

Se preparó una campaña de desarrollo con penalización de actitud cuatro veces
mayor (32 frente a 8), cinco semillas del protocolo (11, 23, 37, 53 y 71),
200.000 pasos por semilla y evaluación de 20 ciclos en semillas de desarrollo
601–605. Las semillas finales 101, 202, 303, 404 y 505 quedan reservadas. La
ficha de aprobación aún no está firmada; no se declarará marcha aprobada ni se
habilitará hardware a partir de este entrenamiento.

La tanda w32 completó cinco semillas, pero se rechazó como candidata por
excursión lateral media de 6,886 m y error articular máximo medio de 0,1461 rad.
También se corrigió un error de fase: el código antiguo recorría nueve ciclos
por cada ciclo declarado. Las 80 semillas previas y w32 quedan etiquetadas como
exploratorias, no comparables con la cadencia prevista. El nominal corregido
interpola cada muestra durante nueve pasos y completa cinco ciclos en 1.440
pasos; el salto de referencia en régimen es 0,0081 rad. Se preparó otra tanda
desde cero con observación lateral/rumbo y penalizaciones, misma quinteta de
entrenamiento y evaluación de desarrollo 701–705; las semillas finales siguen
reservadas.

### Evaluación step PPO con estabilidad lateral/rumbo — 28 de septiembre de 2026

La campaña `Experimentos/campana_step_estabilidad_xy_w32_20260928` completó
cinco políticas (200.000 pasos cada una) y su evaluación de cinco episodios por
política, de 20 ciclos corregidos. La cadencia nominal es 288 pasos/ciclo a
20 ms, precedidos por una rampa de 1 s; el episodio de 20 ciclos tiene 5.810
pasos. No hubo terminaciones tempranas. El informe reproducible es
`Experimentos/campana_step_estabilidad_xy_w32_20260928/INFORME_RESULTADOS.md`.

Resultado negativo para selección: solo dos de cinco políticas superaron el
avance nominal; la excursión lateral máxima media fue 0,0826 m frente a 0,0040
m en nominal. El error articular máximo medio 0,0738 rad (RMS 0,0138 rad) es
mayor que el nominal, pero cumple los límites de la ficha (máximo 0,15 rad,
RMS 0,05 rad). Aunque inclinación RMS y altura permanecieron dentro
de la guía numérica provisional, no se elige política ni se marca la marcha
aprobada. La ficha de aprobación sigue sin firma. No se usaron las semillas
finales 101/202/303/404/505 y no se habilitó transferencia física. Siguiente:
validar referencia nominal, trayectoria lateral y seguimiento articular antes
de una nueva optimización.

Corrección de referencia nominal step: se detectó que los 32 waypoints de la
configuración anterior tienen un salto articular máximo de 0,07277 rad, por
encima de la guía de 0,05 rad. La configuración actual propuesta aumenta a 48
waypoints y reduce el tiempo por punto a 0,12 s; conserva el ciclo de 5,76 s y
baja el salto calculado a 0,04911 rad. Se ejecutaron pruebas y evaluación
dinámica MuJoCo antes de iniciar la siguiente campaña PPO.

### Step 48 puntos y PPO lateral/rumbo — 29 de septiembre de 2026

La referencia se cambió a 48 waypoints de 0,12 s sin alterar los 5,76 s por
ciclo. Su salto máximo bajó de 0,072772 a 0,049115 rad; pasaron las 15 pruebas
cinemáticas. La referencia nominal completó cinco episodios MuJoCo de 20 ciclos
sin caída, con avance 0,08415 m, excursión lateral 0,00415 m, error articular
RMS 0,01170 rad y máximo 0,03795 rad.

La campaña `Experimentos/campana_step_estabilidad_xy48_w32_l64_20260929` entrenó
cinco políticas (200.000 pasos; actitud32/lateral64/rumbo32). En evaluación
emparejada, PPO promedió 0,04219 m de avance y 0,06486 m de excursión lateral
máxima, contra 0,08414 m y 0,00417 m nominal. Una sola política superó el avance
nominal. El error articular medio máximo/RMS 0,06210/0,01297 rad cumple las
guías de 0,15/0,05 rad, pero no compensa la trayectoria lateral. La escala
residual 0,25 tampoco dominó nominal.

La evaluación sin aleatorización repitió un estado determinista. La evaluación
emparejada con fricción/amortiguamiento aleatorizados encontró para nominal
0,08348–0,08467 m de avance y 0,00386–0,00417 m de excursión lateral. Las filas
nominales agregadas coinciden entre políticas porque comparten las cinco
condiciones emparejadas; la pose inicial aún no se perturba. Esto no prueba
repetibilidad física. Las semillas finales 101/202/303/404/505
permanecen reservadas. Resultado: no se selecciona PPO, no se transfiere a
hardware y la ficha sigue sin firma. Informe completo en
`Experimentos/campana_step_estabilidad_xy48_w32_l64_20260929/INFORME_RESULTADOS.md`.

### Conexión SSH Raspberry recuperada — 29 de septiembre de 2026

La Pi `cuadrupedo-pi` respondió en `10.139.240.198`; se validó hostname y
uptime, y la huella ED25519 coincidió con la identidad ya conocida
(`SHA256:mTERAysLSgm2Xlw36tOoV0uv5gC3vj7Xoycel2xe16M`). Se actualizó el alias
`Host cuadrupedo-pi` en `~/.ssh/config`, de modo que puede conectarse con
`ssh cuadrupedo-pi`. La IP `172.18.81.198` quedó obsoleta. Si DHCP cambia la
dirección, leer `hostname -I` localmente y actualizar `HostName`; se recomienda
reservar la IP en el router. No se enviaron órdenes a los servos.

### Apagado de Raspberry pendiente de autenticación — 28 de septiembre de 2026

Se verificó la identidad SSH de `cuadrupedo-pi` en `172.18.81.198` y se ejecutó
`sync`. El apagado remoto fue rechazado porque `sudo` y systemd requieren
autenticación interactiva. No se solicitó ni transmitió la contraseña. Para
completarlo, el operador debe ejecutar `sudo poweroff` en la Raspberry o
`ssh -t pavilion@172.18.81.198 'sudo poweroff'` desde su terminal e ingresar
allí su contraseña.

### Identificación pasiva posterior a prueba mínima — 29 de septiembre de 2026

Se ejecutó por autorización una única prueba tibia 1/CH8 de 5 µs y retorno.
El AS5600 `0x71`/canal 0 cambió 5,889° con el paso y quedó 16,699° apartado
del punto inicial tras retornar a 1500 µs; luego alcanzó 170,947° con PWM
deshabilitado. Se detuvo la prueba. Veinte barridos pasivos de los doce AS5600
mostraron seis rutas con estado MD/ML/MH válido, pero solo cinco señales
estables dentro de 2°; coxa 2 tuvo 27,070° de dispersión aun con imán detectado.
La tabla está en `Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

El cierre dejó OE BCM17 alto y los dieciséis canales individualmente en
`FULL_OFF`. Se corrigió localmente `PCA9685Seguro` para fijar el apagado por
canal y no liberar OE al cerrar. Pasaron cuatro pruebas unitarias y
`py_compile`; luego se instaló en la Pi con respaldo del archivo anterior
`pca9685_seguro.py.codex-backup-20260929`, SHA-256
`a92e47aa75139f42b04cead746112818cddb6e1cdc35abdb22ef747eca8321e1`. La Pi pasó
`compile()` y confirmó OE alto, 16/16 canales en `FULL_OFF` y servicio inactivo.
Criterio de aceptación física no cumplido: retorno articular no repetible y
sensores insuficientes; no se ejecutará otra orden a servos hasta resolver la
inestabilidad. Detalle del ensayo en
`Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

Revisión adicional solicitada indicando el operador que no movió el robot:
quince barridos sin PWM mantuvieron señales variables en tibia 3 y coxas 1/2/3;
seis rutas tuvieron estados magnéticos débiles o sin detección. Se deben revisar
alineación/fijación, cableado/alimentación y holgura mecánica; la causa exacta
no está determinada. Se verificó por SSH por qué no se mueve: OE alto, 16/16
canales `FULL_OFF`, `hardware_ready: false`, 0/12 calibrados y servicio
inactivo. Es un bloqueo deliberado de seguridad, no una orden de marcha fallida.

Se amplió la observación a 60 barridos pasivos: 12/12 rutas I²C respondieron
60/60 veces, por lo que el bus/mapeo TCA funciona. Solo 5 sensores quedaron
válidos y estables dentro de 2°; coxa 2 varió 34,805° aunque el imán fue
detectado. Resultado completo en `Raspberry/DIAGNOSTICO_AS5600_2026-09-29_POSTPRUEBA.md`.

Para avanzar sin hardware se abrió MuJoCo headless aislado en ROS domain 73 y se
ejecutó gateo nominal durante 6,71 s (24 muestras; ciclo configurado 4,32 s;
paso 18 mm; elevación 14 mm), seguido de `stop`. La simulación quedó en reposo.
Una lectura post-stop fue x=0,004767 m, y=-0,000105 m y altura=0,234259 m; no
constituye métrica agregada de la marcha. No hubo PWM ni enlace con la Raspberry.

### Diagnóstico desde Arduino Uno y reconexión pendiente de la Raspberry — 7 de octubre de 2026

El escaneo I²C realizado con Arduino Uno encontró doce AS5600 (`0x36`) en los
canales `0–5` del TCA `0x70` y `0, 1, 3, 4, 5, 6` del TCA `0x71`. El sketch de
doce sensores reportó FEMUR 2 en `0x71`/canal 6, con una lectura observada de
226,14°; unas nueve iteraciones iniciales mostraron variaciones de hasta ~0,09°.
Es evidencia preliminar, no una prueba de estabilidad de 100 muestras. Hay que
resolver una discrepancia antes de editar el mapa de conexiones: el mapa de la
Raspberry identifica `0x71`/canal 5 como FEMUR 2 y canal 6 como COXA 2, pero el
sketch/identificación física comunicada para el Uno indica lo contrario.

No se pudo iniciar la prueba con la Raspberry: `cuadrupedo-pi` en
`10.139.240.198` agotó el tiempo de conexión SSH desde la red actual y mDNS no
la descubrió. No hubo comandos remotos ni nuevas lecturas. Se conserva el último
estado seguro registrado (OE alto, PCA9685 16/16 `FULL_OFF`, sin servos
calibrados y servicio inactivo); no se envió PWM ni se movieron articulaciones.
Próximo paso: conectar y encender la Pi, verificar su identidad SSH y ejecutar
lecturas exclusivamente pasivas para comparar canales 5 y 6 y confirmar la
etiqueta física de cada sensor antes de modificar el mapa.

### Estadísticas AS5600 aportadas por postura — 7 de octubre de 2026

Se registró una captura nueva, separada de la caracterización anterior: 100
muestras por articulación en fémures adelante/atrás, coxas arriba/abajo y tibias
adelante/atrás. El operador confirmó que las patas 1 y 2 son delanteras. El
dataset detallado está en `Raspberry/configuracion/as5600_caracterizacion_provisional.yaml`
(`operator_posture_samples_2026_10_07`); las tablas están en
`Raspberry/RESUMEN_CARACTERIZACION_AS5600_2026-09-28.md`. Se mantienen unidades
de grados absolutos del imán; no son límites PWM o mecánicos. Fémur 3 muestra la
mayor variación comunicada (15,820° con fémur adelante); no se habilita control
ni se infieren límites de servo a partir de estos datos.

### Registro de transferencia de registros y sketch a Raspberry — 7–14 de octubre de 2026

La Pi volvió a ser accesible como `cuadrupedo-pi.local` (`10.150.110.198`); se
validó la identidad SSH conocida y se ajustó el alias local para resolver el
nombre mDNS. Se enviaron archivos nuevos, sin sobrescritura: `Nuevo.md`, el
resumen `Raspberry/AVANCES_2026-10-07.md`, copia fechada del YAML con las 24
combinaciones de postura (100 muestras por combinación) y el sketch
`Raspberry/codigo/arduino_uno_12_as5600_estabilidad_2026-10-07.ino`. Hashes de
origen/destino coincidieron y el YAML se pudo leer en la Pi.

El sketch es un lector de doce AS5600, no un controlador de servos: no genera
PWM, y no se ejecutó en la Raspberry. Queda sin resolver el cruce de etiquetas
FEMUR 2/COXA 2 entre canales 5 y 6 del TCA `0x71`; no modificar el mapa hasta
confirmación física. El checkout remoto tiene un objeto Git vacío/corrupto y
no se hizo commit allí. No hubo movimiento ni PWM durante esta transferencia.
