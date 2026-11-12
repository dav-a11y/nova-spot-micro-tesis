# Cómo funciona la red neuronal del cuadrúpedo (PPO residual)

Fuente: `entrenar_ppo_real.py`, `entrenar_ppo_mujoco.py`, `actuadores_ciclo2.json` (28-oct-2026).

## 0. La idea general

El robot ya tiene una **marcha base** (un movimiento repetitivo de patas, como un metrónomo). La red
neuronal **mira** cómo están las patas y **suma pequeñas correcciones** a esa marcha para que avance más y se
desvíe menos. Aprende esas correcciones **probando millones de veces en un simulador** (MuJoCo).

## 1. Tipo de aprendizaje

### 1.1 ¿Pura o residual? → Residual

| Tipo | Qué hace la red | Problema o ventaja |
|---|---|---|
| Pura | Calcula el ángulo completo de cada servo desde cero | Al principio se mueve al azar y se cae; tarda mucho en aprender |
| **Residual (la nuestra)** | Solo calcula una **corrección** que se suma a la marcha base | Camina desde el primer intento; la red solo mejora lo que ya funciona |

**orden al servo = marcha base(fase) + corrección de la red**

- La marcha base la programamos nosotros (`generar_marcha`): amplitud de fémur y tibia, duración del ciclo y
  orden de las patas para gateo, paso, trote, carrera y galope.
- La corrección la calcula la red.

### 1.2 ¿Multiagente? → No, un solo agente centralizado

Una sola red ve las 4 patas y decide las correcciones de todas al mismo tiempo, porque para no caerse hay que
coordinar las patas entre sí.

## 2. La red neuronal

Son dos redes:

| | Actor (decide) | Crítico (evalúa) |
|---|---|---|
| Para qué sirve | Decide la corrección de cada articulación | Estima cuánta recompensa espera a futuro, V(s) |
| Entrada | 22 datos del estado | Los mismos 22 datos |
| Capa oculta 1 | 64 neuronas, tanh | 64 neuronas, tanh |
| Capa oculta 2 | 64 neuronas, tanh | 64 neuronas, tanh |
| Salida | 12 correcciones | 1 valor |

- tanh comprime cada valor entre −1 y 1.
- En el robot solo se usa el actor; el crítico solo sirve para entrenar.
- Origen: red por defecto (`MlpPolicy`) de Stable-Baselines3 2.3.2, con unos 12 100 parámetros (actor ≈ 6 400, crítico ≈ 5 700).

## 3. Espacio de estados (22 números)

| Qué es | Cuántos | De dónde sale |
|---|---|---|
| Ángulo de fémures y tibias respecto a la postura de pie | 8 | Robot: potenciómetros y encoders. Simulación: el simulador, con ruido y sesgo de ±1° |
| Fase de la marcha (seno y coseno) | 2 | Reloj de la marcha base; seno y coseno porque el ciclo se repite |
| Corrección del paso anterior | 12 | La propia red |

No ve las coxas (están fijas) ni la IMU: la política es **propioceptiva**. La inclinación solo se usa en la
recompensa, en la simulación.

## 4. Acciones: continuas

| Pregunta | Respuesta | De dónde sale |
|---|---|---|
| ¿Continuas o discretas? | Continuas | Los ángulos del servo son continuos |
| ¿Cuántas? | 12, entre −1 y +1 | Entorno base |
| Corrección máxima | ±0,08 rad = ±4,6° | Elegido: mejora la marcha sin deformarla |
| Cambio máximo por paso | 1,15° | Elegido para que el servo alcance a seguir la orden |
| Coxas | Enmascaradas (0): actúa sobre 8 articulaciones | Las coxas van fijas |

Modelo del servo real, medido en el robot (`actuadores_ciclo2.json`):

1. Límite de 3° por orden, igual que el firmware.
2. Ganancia por articulación (escalones y senoides; a 2 Hz llega al 74–92 % de lo pedido).
3. Zona muerta de 0,42°.
4. Retardo de 30 a 120 ms (típico 99 ms), medido en 10 caminatas reales.

Al entrenar, la acción se sortea de una gaussiana (exploración). En el robot se usa la media (determinista).

## 5. Función de recompensa (cada paso)

| Término | Qué significa | Peso |
|---|---|---|
| +1 | Seguir de pie | 1 |
| + avance | Metros avanzados | 10 (gateo, trote, carrera); 20 (paso); 30 (galope); 40 (último gateo) |
| − inclinación | roll² + pitch² | 30 |
| − altura | (altura − 0,235 m)² | 25 |
| − separarse de la marcha base | ‖q − q_base‖² | 0,25 |
| − corrección grande | ‖corrección‖² | 0,04 |
| − desvío lateral | y² | 20 (30 en galope) |
| − giro | rumbo² | 10 |
| − giro por ciclo | giro de cada ciclo² | 5 |
| − brusquedad | cambio de la corrección² | 0,3 |
| − coxas desviadas | error de las coxas² | 1,0 |

Fin del episodio:
- Caída: altura < 0,12 m o > 0,40 m, o inclinación > 34°.
- Tiempo cumplido: 1 s de rampa + ciclos de marcha, entre 10 y 16 s según la marcha.

## 6. Cada cuánto actúa y cada cuánto aprende

| Ritmo | Valor | De dónde sale |
|---|---|---|
| La red decide | Cada 30 ms (33 Hz) | Ritmo real placa–PC, medido (~29 ms) |
| La física se calcula | Cada 2 ms (15 por decisión) | Paso de tiempo de MuJoCo |
| La red aprende | Cada 2048 decisiones (~61 s simulados) | Valor por defecto de PPO |

En cada actualización:
- revisa las 2048 experiencias 10 veces, en grupos de 256;
- tasa de aprendizaje 0,0001;
- se frena si la política cambia demasiado (KL > 0,03).

Entrenamiento total: de 150 000 a 4,5 millones de decisiones según la marcha.

## 7. Función de ventaja (GAE)

La ventaja dice si una acción fue mejor o peor de lo esperado en esa situación.

- Sorpresa de cada paso: δ = r + γ·V(s′) − V(s).
- La ventaja suma esas sorpresas hacia adelante, cada vez con menos peso.

| Parámetro | Valor | Significado |
|---|---|---|
| γ | 0,99 | Mira ~100 pasos (~3 s) al futuro |
| λ | 0,95 | Equilibrio entre la recompensa real y la estimación del crítico |

## 8. Tipo de algoritmo: basado en política (PPO)

| Familia | Cómo aprende | Ejemplo |
|---|---|---|
| Basado en valor | Aprende cuánto vale cada acción | DQN |
| **Basado en política** | Aprende directamente la regla de decisión | REINFORCE, **PPO** |
| Actor-crítico | Política + valor | A2C, **PPO**, SAC |

PPO es basado en política y actor-crítico. Además:
- **On-policy:** aprende solo de lo que hizo la versión actual de la red.
- **Sin modelo:** no aprende la física, solo qué hacer.
- **Recorte de 0,2:** la política no cambia más de un 20 % por actualización.

Referencia: Schulman et al., 2017; implementación de Stable-Baselines3.

## 9. Aleatorización de dominio (al empezar cada intento)

| Qué se varía | Cuánto | De dónde sale |
|---|---|---|
| Retardo del servo | 30–120 ms | Rango medido en caminatas reales |
| Ganancia de cada servo | ±5 % | Variación estimada entre servos |
| Sesgo de cada sensor | ±1° | Error típico de calibración |

## Resumen

Se entrenó una política **residual** con **PPO** (basado en política, actor-crítico, on-policy, sin modelo,
Stable-Baselines3). Un **único agente centralizado** corrige a **33 Hz** una marcha base periódica en
12 articulaciones (8 efectivas), con **acciones continuas** limitadas a ±4,6°. La observación es
**propioceptiva** (22 dimensiones: ángulos de fémures y tibias, fase y acción anterior), sin IMU. Actor y
crítico son MLP independientes de 64-64 neuronas con tanh. La ventaja se estima con **GAE** (γ = 0,99,
λ = 0,95). La recompensa premia el avance y castiga inclinación, desvío, giro y correcciones bruscas. El
entrenamiento se hizo en **MuJoCo** con un modelo del servo identificado en el robot (retardo, ganancia y zona
muerta) y con aleatorización de dominio.
