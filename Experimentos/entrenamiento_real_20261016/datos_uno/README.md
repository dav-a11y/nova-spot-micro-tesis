# Datos de aprendizaje físico

`datos_cuadrupedo.sqlite` conserva las posiciones declaradas, las futuras
calibraciones y las tramas reales de adquisición. Los extremos introducidos por
el operador son evidencia inicial; no son límites seguros hasta validarlos.
El estado y los resultados de la identificación física actual están en
`INFORME_IDENTIFICACION_2026-10-15.md`.

La fuente de aprendizaje para cada articulación será:

`tiempo, orden_en_grados, lectura_ADC, canal_PCA, canal_MUX, estado`.

Primero se identificará qué canal del multiplexor corresponde a cada servo y
se ajustará la relación `ADC -> ángulo real`. Solo las sesiones con esos dos
pasos cerrados se marcarán como válidas para aprendizaje de trayectorias.

Inicialización:

```bash
cd /home/pavilion/CODIGO/datos_aprendizaje
python3 base_datos_aprendizaje.py inicializar
python3 base_datos_aprendizaje.py resumen
```

Con el firmware de telemetría instalado y el Uno en `/dev/ttyACM0`, una captura
pasiva de 30 segundos es:

```bash
python3 base_datos_aprendizaje.py capturar --segundos 30 --proposito calibracion_estatica
```

Abrir el puerto reinicia el Uno; este firmware inicia con el PWM apagado. Una
sesión cruda no se marca como entrenable hasta confirmar `CH_MUX -> servo` y
validar la escala ADC de cada articulación.

Para identificar el canal MUX de cada servo con el robot suspendido, la orden
`c` mueve uno por uno los servos habilitados solamente ocho grados a cada lado
de su posición estática. Tibia 2 y tibia 4 quedan apagadas.

```bash
python3 base_datos_aprendizaje.py capturar --segundos 35 \
  --proposito mapeo_mux_individual --orden c
```

La tibia 2 no se activa: sus datos declarados (`15`, `80`, `10` grados) no
describen un intervalo válido. Los topes traseros de fémur 1 y fémur 2 se
mantienen igualmente fuera de la adquisición automática por posible roce.

La tibia 4 alcanzó un límite mecánico durante la prueba de `CH11` con la
referencia de 70 grados y una excursión de cinco grados. Hasta identificar el
sentido exacto del roce y fijar un margen, `CH11` queda apagado en las pruebas
automáticas.
