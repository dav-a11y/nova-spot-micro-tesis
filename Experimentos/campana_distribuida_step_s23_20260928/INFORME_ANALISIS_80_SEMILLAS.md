# Análisis de campaña PPO MuJoCo step — 80 semillas

Fecha de análisis: 28 de septiembre de 2026. Fuente cuantitativa:
`mujoco_evaluation.csv`; configuración, logs, políticas y trazas se conservan
junto a este informe. Los resultados no habilitan transferencia a hardware.

**Auditoría temporal posterior (28 de septiembre de 2026):** la versión del
entorno identificada en la procedencia avanzaba una muestra nominal por cada
paso de control de 20 ms, pero dimensionaba el episodio para nueve pasos por
muestra. Por ello, las corridas declaradas de cinco ciclos recorrieron en
realidad 45 ciclos de referencia (0,64 s por ciclo en lugar de 5,76 s). La
estadística de este informe describe fielmente esos artefactos, pero no valida
la marcha en la temporización especificada. Se preserva la campaña sin cambios
en sus datos originales; no usarla para selección ni transferencia.

## Diseño y comprobaciones

- 80 entrenamientos PPO (`MlpPolicy`), semillas 23 y 1001–1079; 200.000 pasos
  solicitados por entrenamiento (200.704 efectivos por bloques de 1.024, según
  README y logs).
- Marcha `step`, MuJoCo, 27 observaciones y 12 acciones residuales; límite
  residual ±0,08 rad y cambio máximo 0,02 rad. El metadato indica entrenamiento
  con aleatorización de dominio; la evaluación usa `domain_randomization=False`.
- Cada condición se resume en cinco episodios con semillas fijas 100–104. Hay
  160 filas: una nominal y una PPO por semilla. Las diferencias se calculan
  pareadas por semilla, restando nominal de PPO.
- Estado `complete`; hay 80 políticas y 160 filas. Las sumas de `SHA256SUMS`
  se verificaron después de transferir los datos. Los 400 episodios de
  evaluación PPO terminaron en 1.440 pasos y ninguno tuvo terminación temprana.

## Resultado agregado

| Métrica | Nominal (media) | PPO entre 80 semillas (media ± DE) | Diferencia pareada media (IC 95% t aprox.) |
|---|---:|---:|---:|
| Retorno | 1451,299 | 1485,482 ± 16,306 | +34,183 (+30,555 a +37,811) |
| Avance neto | 0,0155 m | 2,9181 ± 0,9141 m | +2,9026 m (+2,6992 a +3,1060) |
| Inclinación máxima media por episodio | 0,01392 rad | 0,04734 ± 0,00838 rad | +0,03342 rad (+0,03156 a +0,03529) |

DE es la desviación estándar entre políticas/semillas. Los intervalos son
aproximaciones t para la media de las 80 diferencias pareadas; no son
intervalos sobre episodios ambientales independientes ni prueban generalización.
“Inclinación máxima media por episodio” es el promedio de cinco máximos por
política, no el peor máximo de todos los episodios.

El retorno aumenta en promedio 2,36% frente a la referencia. El avance pasa de
una referencia casi estacionaria a 2,92 m netos en promedio; por eso no es útil
expresar su mejora como porcentaje. El coste es consistente: la inclinación
reportada es aproximadamente 3,40 veces la nominal.

## Distribución entre semillas

- Avance neto mayor que nominal: 78/80 (97,5%); menor: 2/80 (semillas 1001 y
  1077). Rango PPO: −0,435 a 3,892 m.
- Retorno mayor que nominal: 76/80 (95%); menor: 4/80. Rango PPO: 1428,805 a
  1505,065.
- Inclinación mayor que nominal: 80/80. Rango PPO de la media de máximos:
  0,02535–0,06150 rad. Ninguna semilla supera al nominal en avance sin también
  empeorar esta métrica de inclinación.
- 76/80 políticas avanzan más de 1 m; 68/80 más de 2 m y 49/80 más de 3 m.
- No hubo terminaciones tempranas en evaluación. Esto evita confundir los
  promedios con episodios cortados, pero no demuestra estabilidad robusta.

La frontera descriptiva de Pareto (maximizar avance y minimizar inclinación
media) contiene cuatro candidatas, sin selección de ganadora:

| Semilla | Avance | Inclinación media de máximos | Retorno |
|---:|---:|---:|---:|
| 1018 | 3,613 m | 0,02535 rad | 1502,14 |
| 1079 | 3,709 m | 0,03429 rad | 1500,48 |
| 1074 | 3,764 m | 0,03602 rad | 1502,86 |
| 1014 | 3,892 m | 0,04053 rad | 1505,07 |

La frontera depende solo de avance e inclinación; no considera robustez,
contactos, energía, variación de dominio ni tolerancias mecánicas. Es una lista
para evaluación adicional, no un ranking de despliegue.

## Interpretación y decisión

El entrenamiento encuentra avance de forma bastante consistente, y la mayoría
de políticas también mejora el retorno. Sin embargo, las 80 políticas aumentan
la inclinación frente a nominal; por ese criterio ninguna domina a la referencia.
La conclusión correcta es “mejora de locomoción simulada con penalización de
actitud”, no “marcha estable aceptada”.

La variación entre semillas está medida, pero la evaluación ambiental es
estrecha: se reutilizan los mismos cinco episodios, sin aleatorización de dominio,
para todas las semillas. Los 80 entrenamientos no equivalen a 80 escenarios
ambientales independientes. Antes de seleccionar una política, evaluar con
episodios nuevos, aleatorización de masa/fricción y otros escenarios de contacto;
informar máximos y percentiles por episodio, no solo su media. Mantener
`hardware_transfer=false`; ninguna política debe conectarse al cuadrúpedo sin
pasar límites articulares, control gradual, parada segura y validación física
independiente.

## Reproducción

Las estadísticas se derivan de `mujoco_evaluation.csv`: para cada semilla se
restó nominal de PPO; medias, desviaciones estándar, proporciones y frontera
Pareto se calcularon sobre las 80 políticas. Los IC son aproximaciones t con
79 grados de libertad. Integridad de archivos:

```bash
cd Experimentos/campana_distribuida_step_s23_20260928
sha256sum -c SHA256SUMS
```
