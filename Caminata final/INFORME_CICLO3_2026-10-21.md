# Análisis de grabaciones — Ciclo 3 (21/10/2026)

## Alcance y método

Se revisaron seis carpetas nuevas, con 28 videos fuente en conjunto. En las cuatro sesiones completas de marcha se verificaron los análisis existentes por cámara (`video_analisis.json`), el diagnóstico de sensores/temporización (`diagnostico.json`), el registro de órdenes (`caminata.csv`) y las etiquetas de configuración. Se completó también el análisis visual de `prueba_nucleos_2104`. La ejecución PPO1 de trote se conserva como parcial/fallida: no se considera una repetición válida.

El análisis visual estima qué movimiento de imagen acompaña las órdenes del robot; no mide directamente ángulos articulares ni demuestra causalidad mecánica. “Pata no visible” significa que esa cámara no permitió asignarla de forma fiable. El trote se evalúa por pares diagonales (P2+P3 y P1+P4), porque las órdenes no permiten separar cada pata individualmente.

## Resumen cronológico

| Inicio local | Ensayo / marcha | Integridad y datos de control | Resultado visual por cámaras |
|---|---|---|---|
| 21:04:50 | `prueba_nucleos_2104` — gateo PPO | 61,7 s; 1.881 pasos; 21 ciclos; temporización estable (p99 35 ms). Prueba técnica del sistema/cámaras, no repetición comparativa del ciclo. | HP-PC1: P1/P2 visibles (r 0,92/0,97); general y Logitech: 4/4 visibles (r 0,85–0,99; CV 1–4%). Remota: solo 40 fotogramas, insuficiente. Sin anomalías visuales marcadas. |
| 21:06:49 | `rep_ciclo3_gateo_base_r1` — gateo base | 182,8 s; 5.577 pasos; 63 ciclos. Temporización estable (p99 33 ms). | Logitech y Windows: 4/4 patas; HP-PC1/general y remota: 3/4. Correlaciones mayormente r 0,86–0,98. Anomalías visuales localizadas: ciclos 48–49 en HP-PC1 y 1–2 en general. |
| 21:15:56 | `rep_ciclo3_gateo_ppo1_r1` — gateo PPO1 | 180,0 s; 5.489 pasos; 62 ciclos; temporización del control generalmente estable. **ENC_T1 y C11 sin respuesta**; sus pasos se estimaron con órdenes retrasadas. | Ventanas: 4/4, pero con r 0,71–0,93. HP-PC1 solo 2/4 (CV hasta 22%); remota 2/4; general sin fotogramas; Logitech sin patas asignables. HP-PC1 marca anomalías en ciclos 39–62. Evidencia incompleta y no concordante entre vistas. |
| 22:05:38 | `rep_ciclo3_gateo_ppo2_r1` — gateo PPO2 | 180,3 s; 5.137 pasos; 58 ciclos. Temporización irregular: p99 52 ms, máximo 91 ms, 638 pasos >40 ms (12,4%). **ENC_T1 y C11 sin respuesta**; pasos estimados. | Windows: 4/4 y r 0,87–0,95 sin anomalías; remota: 3/4; Logitech: 3/4. HP-PC1 solo 2/4 y anomalías 48–58; remota/Logitech también marcan ciclos 47–58. General ve 4/4, pero CV alto en P3/P4 (43%/36%). Señal mixta; coincide temporalmente con carga/irregularidad. |
| 22:13:17 | `rep_ciclo3_trote_base_r1` — trote base | 181,0 s; 5.511 pasos; 166 ciclos. Temporización relativamente estable (p99 35 ms; nueve pasos >40 ms). | HP-PC1: ambos pares diagonales visibles (r 0,85–0,89); general y Logitech: ambos pares con r 0,99 y CV 2%. Retardo estimado de 400 ms en esas dos vistas. Logitech marca una anomalía aislada en ciclo 1. Remota y Windows no permiten ver los pares. |
| 22:21:03 | `rep_ciclo3_trote_ppo1_r1_fallo_222251` — intento PPO1 | **Inválida: caminata cortada a los 44,9 s**; 1.342 pasos, 40 ciclos; máximo de intervalo 195 ms. **ENC_T1 y C11 sin respuesta**, remota no disponible. | Análisis parcial: general y Logitech detectan ambos pares (r 0,97–0,99; CV 3–5%); HP-PC1 detecta solo P1+P4; Windows no ve los pares. La señal visible no convierte el intento incompleto en una repetición válida. |

## Lectura conjunta

- La marcha base de gateo presenta la evidencia visual más completa y consistente: las cuatro patas se identifican en Logitech y Windows, con correlaciones fuertes. Hay dos pequeños grupos de ciclos señalados como anomalías, que deben tratarse como candidatos a inspección y no como fallas confirmadas.
- Gateo PPO1 tiene cobertura insuficiente y desacuerdo entre cámaras. Además, faltan las lecturas de ENC_T1 y C11. No es prudente atribuir las anomalías de ciclos tardíos a un problema mecánico: podrían mezclarse pérdida de visibilidad, cambios de escena o calidad de captura.
- Gateo PPO2 sí muestra una señal importante de temporización irregular y anomalías coincidentes alrededor de los ciclos 47–58 en varias vistas; sin embargo, la cámara Windows no las reproduce y el análisis general tiene alta variabilidad en dos patas. Conviene repetir PPO2 con carga del PC controlada y sensores recuperados antes de concluir que la política causa inestabilidad.
- El trote base ofrece las dos vistas más consistentes en sus pares diagonales. La limitación es que el método no puede separar miembros dentro de cada par bajo este patrón de órdenes.
- El intento PPO1 de trote es demasiado corto y temporalmente irregular para compararlo con el trote base. Queda documentado, pero no se usa para afirmar mejora o empeoramiento.
- En los ensayos PPO1/PPO2 y el intento fallido se registran ENC_T1 y C11 sin respuesta. La orden retrasada sirve como estimación, no sustituye una lectura real del sensor.

## Archivos fuente del análisis

Cada carpeta de sesión conserva `caminata.config.json`, `caminata.csv`, `diagnostico.json`/gráfico y, cuando corresponde, `video_analisis.json`, sus gráficos por cámara, informe/log y datos de color. La prueba técnica tiene diagnóstico y análisis visual nuevos. Los videos fuente no forman parte del paquete de resultados para evitar duplicarlos.

Las sesiones y sus etiquetas de marcha se indexan en `HISTORIAL_GRABACIONES_ANALIZADAS.csv`. El análisis visual es observacional y depende de visibilidad, sincronización y calidad de las cámaras; no es una recomendación autónoma para cambiar el robot.
