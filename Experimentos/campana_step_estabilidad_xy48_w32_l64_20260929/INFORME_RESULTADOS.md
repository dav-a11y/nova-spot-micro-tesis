# Step PPO con referencia suavizada: resultado de desarrollo

Fecha: 29 de septiembre de 2026 (America/Bogota). Simulación MuJoCo solamente;
sin órdenes a Raspberry Pi, ROS, PWM ni servos.

## Cambio y validación de la referencia

La referencia anterior usaba 32 puntos a 0,18 s por punto. Su mayor salto
articular entre waypoints era 0,072772 rad, sobre la guía provisional de
0,05 rad. Se cambió la marcha step a 48 puntos de 0,12 s: mantiene el ciclo de
5,76 s, con seis pasos de control por waypoint y salto máximo calculado
0,049115 rad. El generador y la configuración de ROS comparten ahora esos
valores. Las 15 pruebas cinemáticas pasaron.

La línea base MuJoCo se ejecutó a 20 ciclos en cinco episodios. No hubo
terminaciones tempranas; el avance fue 0,08415 m, deriva lateral −0,00126 m,
excursión lateral 0,00415 m, error articular RMS 0,01170 rad y máximo 0,03795
rad. Roll/pitch RMS fueron 0,01078/0,01678 rad y la altura quedó entre
0,23259–0,23500 m.

## Entrenamiento PPO y evaluación

Cinco políticas (semillas 11, 23, 37, 53, 71), 200.000 pasos cada una,
observación lateral/rumbo, peso actitud 32, peso lateral 64 y peso de rumbo 32.
Se evaluaron en 20 ciclos, semillas de desarrollo 801–805; las semillas finales
101/202/303/404/505 siguen reservadas. La evaluación emparejada original y
otra con variación de fricción/amortiguamiento se conservan por separado en sus
CSV. Cada matriz de evaluación tiene 50 episodios; no hubo caídas.

En la evaluación sin aleatorización, los cinco episodios nominales repiten el
mismo estado determinista y no constituyen una prueba de robustez. La segunda
matriz emparejada sí aleatoriza fricción/amortiguamiento: para nominal, el
avance por episodio varió 0,08348–0,08467 m, excursión lateral
0,00386–0,00417 m y fracción de contacto 0,84342–0,85202. En el CSV agregado,
la fila nominal aparece idéntica para cada política porque todas comparten las
mismas cinco condiciones emparejadas. Aún no se varía la pose inicial ni se
demuestra repetibilidad física.

En la evaluación aleatorizada emparejada, PPO promedió 0,04219 m de avance
(−0,17056 a 0,31060 m entre políticas), frente a 0,08414 m nominales. La
excursión lateral máxima media fue 0,06486 m (0,01695–0,12887 m), frente a
0,00417 m nominales. Solo una de cinco políticas superó el avance nominal.
El error articular máximo medio fue 0,06210 rad y RMS medio 0,01297 rad; ambos
quedan debajo de los límites propuestos en la ficha (0,15 y 0,05 rad), aunque
son peores que el nominal. No se selecciona ninguna política.

## Escala de corrección en inferencia

Se evaluaron escalas 0, 0,25, 0,5, 0,75 y 1 sobre las cinco políticas, con
cinco episodios nominales por combinación (125 episodios; CSV
`residual_scale_ablation.csv`). Escala 0 reproduce la línea base. Escala 0,25
promedia 0,07301 m de avance y 0,02438 m de excursión lateral: mejora frente a
la corrección completa, pero todavía queda por debajo del avance nominal y
supera casi seis veces su excursión lateral. Ninguna escala PPO comprobada
mejora simultáneamente avance y trayectoria lateral respecto a la referencia.
Esta criba usa el mismo estado inicial determinista, por lo que sirve para
comparar escalas, no para inferir repetibilidad.

## Conclusión y límites

La referencia nominal de 48 puntos pasa los chequeos computacionales y la
línea base de seguimiento/deriva en MuJoCo. La optimización PPO lateral/rumbo y
la reducción de escala no aportan una candidata que domine esa referencia. El
resultado es negativo para selección de PPO; conservar la marcha nominal como
línea base simulada y rediseñar observación/recompensa o identificar dinámicas
antes de más entrenamiento.

La ficha de aprobación sigue sin firma y faltan margen estático, perturbaciones
iniciales representativas, las pruebas físicas supervisadas y validación por
el director. No declarar marcha aprobada ni transferir políticas al robot.
Manifiesto, estados, políticas, logs, CSV y SHA-256 están en esta carpeta.
