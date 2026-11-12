"""Contenido (imágenes) de las 7 diapositivas nuevas de la sustentación (8-nov-2026):
tras «Modelo y simulación»: cinemática, dinámica, caracterización del servo y servo en el simulador;
tras «Control PPO residual»: proceso de decisión de Markov, política PPO y función de recompensa.
Fórmulas de la tesis (cap. 9) y valores verificados en el código (entrenar_ppo_real.py, nova_sm3_real.xml,
metadata.json de v33/v34 y los policy.zip: 22 observaciones, 12 acciones, red 64-64, γ 0,99, λ 0,95, ε 0,2).
Uso: python3 diapositivas_modelo_ppo.py CARPETA_SALIDA"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 23.7, 13.4
NAVY, AZUL, MAG, TINTA, GRIS = "#002060", "#2E3192", "#A31A9A", "#262626", "#595959"
TINTE, TINTE_M, NARANJA, TINTE_N = "#ECEEF8", "#F6EAF5", "#E65100", "#FFF3E0"
plt.rcParams["font.family"] = "Liberation Sans"
plt.rcParams["mathtext.fontset"] = "stix"


def lienzo():
    fig = plt.figure(figsize=(W / 2.54, H / 2.54), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


def caja(ax, x0, y0, x1, y1, fill=TINTE, borde=AZUL, titulo=None, color_t=None, lw=1.3):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.15",
                                fc=fill, ec=borde, lw=lw, zorder=1))
    if titulo:
        ax.text(x0 + 0.3, y1 - 0.45, titulo, fontsize=13, fontweight="bold", color=color_t or borde,
                va="center", ha="left", zorder=3)


def t(ax, x, y, s, sz=11, c=TINTA, ha="left", va="center", b=False, i=False):
    ax.text(x, y, s, fontsize=sz, color=c, ha=ha, va=va, fontweight="bold" if b else "normal",
            fontstyle="italic" if i else "normal", zorder=3)


def flecha(ax, x0, y0, x1, y1, c=AZUL):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14, color=c, lw=1.6,
                                 zorder=2))


def guardar(fig, nombre):
    fig.savefig(OUT / f"{nombre}.png", dpi=300, transparent=True)
    plt.close(fig)
    print("ok", nombre)


# ---------------------------------------------------------------- 1 · Cinemática
fig, ax = lienzo()
caja(ax, 0.1, 3.0, 11.6, 13.3, titulo="Directa: ángulos → posición del pie")
eqs = [r"$a = s_i\,q_c,\qquad Q = q_f + q_t$",
       r"$x = -l_f \sin q_f - l_t \sin Q$",
       r"$z_p = -l_f \cos q_f - l_t \cos Q$",
       r"$y = s_i\, l_c \cos a - z_p \sin a$",
       r"$z = s_i\, l_c \sin a + z_p \cos a$"]
for k, e in enumerate(eqs):
    t(ax, 0.6, 11.55 - 1.45 * k, e, 17)
caja(ax, 12.1, 3.0, 23.6, 13.3, fill=TINTE_M, borde=MAG, titulo="Inversa: posición del pie → ángulos")
eqs = [r"$z_p = -\sqrt{y^2 + z^2 - l_c^2}$",
       r"$q_c = s_i\left[\mathrm{atan2}(z,y) - \mathrm{atan2}(z_p,\, s_i l_c)\right]$",
       r"$D = \dfrac{b^2 + d^2 - l_f^2 - l_t^2}{2\, l_f\, l_t},\quad b=-x,\; d=-z_p$",
       r"$q_t = -\arccos D$",
       r"$q_f = \mathrm{atan2}(b,d) - \mathrm{atan2}(l_t \sin q_t,\; l_f + l_t \cos q_t)$"]
for k, (e, dy) in enumerate(zip(eqs, (0, 0, 0.1, 0.45, 0.45))):
    t(ax, 12.6, 11.55 - 1.45 * k - dy, e, 16 if k != 4 else 14.5)
t(ax, 0.2, 2.25, r"Jacobiano:  $\dot{\mathbf{p}}_i = \mathbf{J}_i(\mathbf{q}_i)\,\dot{\mathbf{q}}_i$,"
                 r"   $\mathbf{\tau}_i = \mathbf{J}_i^{\top}\mathbf{f}_i$   ·   postura nominal con "
                 r"$\kappa = 6{,}65$ (lejos de singularidades)", 12.5, NAVY)
t(ax, 0.2, 1.2, r"$l_c,\, l_f,\, l_t = 0{,}090;\ 0{,}105;\ 0{,}132$ m   ·   $s_i = \pm 1$ según el lado   ·   "
                r"ida y vuelta directa → inversa con error $< 10^{-12}$ rad", 11.5, GRIS)
guardar(fig, "1_cinematica")

# ---------------------------------------------------------------- 2 · Dinámica
fig, ax = lienzo()
caja(ax, 0.1, 9.2, 23.6, 13.3, titulo="Ecuación de movimiento de base flotante (Lagrange)")
t(ax, 11.85, 10.85, r"$\mathbf{M}(\mathbf{q})\,\ddot{\mathbf{q}} + \mathbf{C}(\mathbf{q},\dot{\mathbf{q}})\,"
                    r"\dot{\mathbf{q}} + \mathbf{g}(\mathbf{q}) + \mathbf{\tau}_f = \mathbf{S}^{\top}"
                    r"\mathbf{\tau} + \mathbf{J}_c^{\top}\mathbf{\lambda}$", 22, ha="center")
caja(ax, 0.1, 3.0, 11.6, 8.7, fill="white", titulo="De dónde salen M y g")
t(ax, 0.5, 6.95, r"$K = \frac{1}{2}\sum_k \left[ m_k \mathbf{v}_k^{\top}\mathbf{v}_k + \mathbf{\omega}_k^{\top}"
                 r"\mathbf{R}_k \mathbf{I}_k \mathbf{R}_k^{\top}\mathbf{\omega}_k \right]$", 15)
t(ax, 0.5, 5.6, r"$U = \sum_k m_k\, g\, z_k$", 15)
t(ax, 0.5, 4.3, r"$M_{ab} = \dfrac{\partial^2 K}{\partial \dot q_a\, \partial \dot q_b},\qquad "
                r"g_a = \dfrac{\partial U}{\partial q_a}$", 15)
caja(ax, 12.1, 3.0, 23.6, 8.7, fill="white", borde=MAG, titulo="Términos")
filas = [(r"$\mathbf{M}\ddot{\mathbf{q}}$", "masa e inercia × aceleración"),
         (r"$\mathbf{C}\dot{\mathbf{q}}$", "fuerzas centrífugas y de Coriolis"),
         (r"$\mathbf{g},\ \mathbf{\tau}_f$", "gravedad y fricción articular"),
         (r"$\mathbf{S}^{\top}\mathbf{\tau}$", "pares de los 12 servos"),
         (r"$\mathbf{J}_c^{\top}\mathbf{\lambda}$", "fuerzas de contacto del piso")]
for k, (e, d) in enumerate(filas):
    y = 7.45 - 0.92 * k
    t(ax, 12.6, y, e, 15)
    t(ax, 14.6, y, d, 11.5)
t(ax, 0.2, 2.2, r"Por pata:  $\mathbf{\tau}_i = \mathbf{M}_i\ddot{\mathbf{q}}_i + \mathbf{c}_i + \mathbf{g}_i"
                r" + \mathbf{\tau}_{f,i} - \mathbf{J}_i^{\top}\mathbf{f}_i$   ·   la resuelve MuJoCo cada 2 ms",
  12.5, NAVY)
t(ax, 0.2, 1.15, "Masas, inercias y fricción nominales del modelo (URDF), sin identificar en el robot · "
                 "M simétrica y definida positiva", 11.5, GRIS)
guardar(fig, "2_dinamica")

# ---------------------------------------------------------------- 3 · Caracterización del servo
fig, ax = lienzo()
cab = ["Ensayo en el robot", "Qué se le pidió al servo", "Resultado"]
xs = [0.1, 6.0, 13.6, 23.6]
filas = [("1 · Caminatas nominales", "orden frente a sensor", "retardo ≈ 100 ms · ganancia 0,88–0,98"),
         ("2 · Escalones", "saltos de ±1, ±2, ±6 y ±12°", "zona muerta 0,5–1° · subida 130–165 ms"),
         ("2 · Senoides", "0,5, 1 y 2 Hz", "retardo 65–85 ms · a 2 Hz llega al 74–92 %"),
         ("3 · Barrido de rango", "±40° despacio", "lineal · histéresis 0,6–1,5° · topes"),
         ("4 · Ciclo de mejora", "10 caminatas de gateo y trote", "retardo 99 ms (66–99) · error 1,8°")]
y_top = 13.3
ax.add_patch(FancyBboxPatch((0.1, y_top - 1.0), 23.5, 1.0, boxstyle="round,pad=0,rounding_size=0.12",
                            fc=NAVY, ec=NAVY, zorder=1))
for k, c in enumerate(cab):
    t(ax, xs[k] + 0.3, y_top - 0.5, c, 12.5, "white", b=True)
for r, fila in enumerate(filas):
    y0 = y_top - 1.0 - 1.2 * (r + 1)
    if r % 2 == 0:
        ax.add_patch(plt.Rectangle((0.1, y0), 23.5, 1.2, fc=TINTE, ec="none", zorder=0))
    for k, c in enumerate(fila):
        t(ax, xs[k] + 0.3, y0 + 0.6, c, 12, TINTA, b=(k == 0))
caja(ax, 0.1, 0.2, 23.6, 4.9, fill=TINTE_N, borde=NARANJA, titulo="Parámetros que se llevan al simulador",
     color_t=NARANJA)
res = [("retardo", "99 ms (1 a 4 pasos de 30 ms)"), ("zona muerta", "0,42°"),
       ("ganancia", "una por articulación (medida)"), ("límite", "3° por orden (firmware)")]
for k, (a, b) in enumerate(res):
    x = 0.6 + 11.6 * (k % 2)
    y = 3.4 - 1.25 * (k // 2)
    t(ax, x, y, a, 13, NARANJA, b=True)
    t(ax, x + 3.1, y, b, 13)
t(ax, 0.6, 0.75, "La cámara confirmó que el motor recorre 1,08 veces lo ordenado.", 11, GRIS, i=True)
guardar(fig, "3_servo_caracterizacion")

# ---------------------------------------------------------------- 4 · Servo en el simulador
fig, ax = lienzo()
caja(ax, 0.1, 9.6, 23.6, 13.3, titulo="Función de transferencia del servo en MuJoCo")
t(ax, 11.85, 11.45, r"$G_j(s) = \dfrac{\Theta_j(s)}{\Theta_{ord,j}(s)} = g_j\; e^{-s T_d}\;"
                   r"\dfrac{k_p}{J_j\, s^2 + (k_v + b)\, s + k_p}$", 19, ha="center")
t(ax, 11.85, 9.95, r"$T_d = d \cdot 30$ ms,  $d \in \{1,\dots,4\}$   ·   $k_p = 40$ N·m/rad,  "
                   r"$k_v = 4$ N·m·s/rad,  $b = 0{,}08$   ·   $g_j$ medida por articulación", 11.5, GRIS,
  ha="center")
# cadena de bloques
bloques = [("Orden", r"$q_{nom} + \Delta q$"), ("Límite", r"$\pm 3°$ por orden"), ("Ganancia", r"$g_j$"),
           ("Zona muerta", r"$|\Delta| < 0{,}42°$"), ("Retardo", r"$z^{-d}$"),
           ("Servo MuJoCo", r"$k_p,\ k_v$")]
bw, gap, y0, y1 = 3.4, 0.62, 5.6, 8.5
for k, (n, e) in enumerate(bloques):
    x0 = 0.1 + k * (bw + gap)
    fill, bc = (TINTE_N, NARANJA) if k in (1, 2, 3, 4) else (TINTE, AZUL)
    caja(ax, x0, y0, x0 + bw, y1, fill=fill, borde=bc)
    t(ax, x0 + bw / 2, 7.65, n, 12.5, bc, ha="center", b=True)
    t(ax, x0 + bw / 2, 6.45, e, 13, TINTA, ha="center")
    if k:
        flecha(ax, x0 - gap + 0.02, (y0 + y1) / 2, x0 - 0.02, (y0 + y1) / 2)
t(ax, 0.1, 4.95, "No linealidades medidas en el robot (naranja), aplicadas en cada paso de control de 30 ms",
  11, NARANJA, i=True)
caja(ax, 0.1, 0.2, 23.6, 4.2, fill="white", borde=MAG, titulo="Aleatorización en cada episodio",
     color_t=MAG)
al = [("Retardo", r"$d$ sorteado entre 1 y 4 pasos", "(30 a 120 ms)"),
      ("Ganancia", r"$g_j \times \mathcal{U}(0{,}95;\ 1{,}05)$", "distinta en cada servo"),
      ("Sensores", r"sesgo $\mathcal{U}(-1°;\ 1°)$", "y ruido de 1°")]
for k, (a, b, c) in enumerate(al):
    x = 0.6 + 7.8 * k
    t(ax, x, 2.75, a, 13, MAG, b=True)
    t(ax, x, 1.75, b, 12.5)
    t(ax, x, 0.95, c, 12.5)
guardar(fig, "4_servo_simulador")

# ---------------------------------------------------------------- 5 · Markov
fig, ax = lienzo()
caja(ax, 0.1, 9.9, 23.6, 13.3, titulo="Proceso de decisión de Markov")
t(ax, 11.85, 11.75, r"$\mathrm{MDP} = (\mathcal{S},\ \mathcal{A},\ P,\ r,\ \gamma)\qquad "
                    r"a_t \sim \pi_\theta(a \mid s_t),\quad s_{t+1} \sim P(\cdot \mid s_t, a_t)$", 19, ha="center")
t(ax, 11.85, 10.55, r"$J(\theta) = \mathbb{E}_\tau\left[\sum_t \gamma^t r_t\right],\qquad "
                    r"A(s,a) = Q(s,a) - V(s)$", 17, ha="center")
cols = [("Estado  $s_t \\in \\mathbb{R}^{22}$", AZUL, TINTE,
         ["8 ángulos de fémures y tibias\n(respecto a la postura de pie)", "2 fase de la marcha (sin, cos)",
          "12 corrección del paso anterior", "Sin IMU: solo lo que\nel robot puede medir"]),
        ("Acción  $a_t \\in [-1, 1]^{12}$", MAG, TINTE_M,
         ["Corrección residual sobre\nla marcha base", r"$\Delta q = 0{,}08 \cdot \mathrm{clip}(a_t)$  (±4,6°)",
          "Cambio máximo de 1,15°\npor paso", "8 de 12 articulaciones\n(las coxas no se corrigen)"]),
        ("Transición  $P$ y descuento  $\\gamma$", NARANJA, TINTE_N,
         ["MuJoCo + modelo del servo,\ncon aleatorización", "Una decisión cada 30 ms\n(33 Hz)",
          r"$\gamma = 0{,}99$", "Horizonte ≈ 100 pasos ≈ 3 s,\nmás de un ciclo de marcha"])]
for k, (tit, c, f, lin) in enumerate(cols):
    x0 = 0.1 + k * 7.95
    caja(ax, x0, 0.2, x0 + 7.6, 9.4, fill=f, borde=c, titulo=tit)
    for j, l_ in enumerate(lin):
        ax.text(x0 + 0.35, 7.9 - 1.95 * j, l_, fontsize=12.5 if "$" not in l_ else 14, color=TINTA, ha="left",
                va="top", linespacing=1.35, zorder=3)
guardar(fig, "5_markov")

# ---------------------------------------------------------------- 6 · Política PPO
fig, ax = lienzo()
caja(ax, 0.1, 8.9, 23.6, 13.3, titulo="PPO: optimización de política proximal (actor-crítico)")
t(ax, 0.6, 11.55, r"$\pi_\theta(a \mid s) = \mathcal{N}\!\left(\mu_\theta(s),\ \mathrm{diag}(\sigma^2)\right),"
                  r"\qquad \rho_t = \dfrac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{ant}}(a_t \mid s_t)}$", 16)
t(ax, 0.6, 9.85, r"$L^{CLIP}(\theta) = \mathbb{E}_t\left[\min\left(\rho_t \hat{A}_t,\ "
                 r"\mathrm{clip}(\rho_t,\, 1-\varepsilon,\, 1+\varepsilon)\, \hat{A}_t\right)\right]$", 17)
t(ax, 15.2, 11.55, r"$\delta_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$", 14.5)
t(ax, 15.2, 9.85, r"$\hat{A}_t = \sum_l (\gamma\lambda)^l\, \delta_{t+l}$  (GAE)", 14.5)
# red
caja(ax, 0.1, 0.2, 11.6, 8.4, fill="white", titulo="Red neuronal (MLP, tanh)")
capas = [("22", "estado"), ("64", ""), ("64", ""), ("12", r"$\mu$")]
for k, (n, e) in enumerate(capas):
    x = 1.4 + k * 2.9
    caja(ax, x - 0.9, 4.3, x + 0.9, 6.6, fill=NAVY if k in (0, 3) else TINTE, borde=NAVY)
    t(ax, x, 5.45, n, 15, "white" if k in (0, 3) else NAVY, ha="center", b=True)
    t(ax, x, 3.85, e, 12, GRIS, ha="center")
    if k:
        flecha(ax, x - 2.0, 5.45, x - 0.92, 5.45, NAVY)
t(ax, 0.5, 7.4, r"Actor $\pi_\theta$:  22 → 64 → 64 → 12", 12.5, NAVY, b=True)
t(ax, 0.5, 2.65, r"Crítico $V_\phi$:  22 → 64 → 64 → 1 (solo al entrenar)", 12, TINTA)
t(ax, 0.5, 1.5, "En el robot se usa la media μ (determinista)", 11.5, GRIS, i=True)
caja(ax, 12.1, 0.2, 23.6, 8.4, fill=TINTE_M, borde=MAG, titulo="Hiperparámetros (Stable-Baselines3)")
hp = [(r"$\gamma$ = 0,99", r"$\lambda$ = 0,95"), (r"$\varepsilon$ = 0,2", "épocas = 10"),
      ("tasa de aprendizaje = 1e-4", ""), ("2 048 pasos por actualización", ""), ("lote = 256", "KL objetivo = 0,03"),
      (r"$c_1$ = 0,5 (crítico)", r"$c_2$ = 0 (entropía)")]
for k, (a, b) in enumerate(hp):
    y = 6.95 - 1.05 * k
    t(ax, 12.6, y, a, 13)
    if b:
        t(ax, 18.3, y, b, 13)
guardar(fig, "6_politica_ppo")

# ---------------------------------------------------------------- 7 · Recompensa
fig, ax = lienzo()
caja(ax, 0.1, 8.0, 23.6, 13.3, titulo="Recompensa por paso (cada 30 ms)")
t(ax, 0.5, 11.3, r"$r_t = 1 + w_{av}\,\Delta x - w_{act}(\phi^2 + \vartheta^2) - 25\,(h - 0{,}235)^2"
                 r" - 0{,}25\,\|\mathbf{e}_q\|^2 - 0{,}04\,\|\Delta\mathbf{q}\|^2$", 18)
t(ax, 1.1, 9.75, r"$-\ w_{lat}\, y^2 - w_{giro}\, \psi^2 - w_{suav} \sum_j \left(\dfrac{\Delta q_{t,j} - "
                 r"\Delta q_{t-1,j}}{0{,}02}\right)^2 - w_{cox}\, \bar{e}^{\,2}_{coxa}$", 18)
t(ax, 1.1, 8.55, r"al cerrar cada ciclo:  $-\ w_{gc}\,(\Delta\psi_{ciclo})^2$", 13, GRIS)
caja(ax, 0.1, 0.2, 9.4, 7.5, fill="white", borde=MAG, titulo="Variables", color_t=MAG)
var = [(r"$\Delta x$", "avance del cuerpo en el paso"), (r"$\phi,\ \vartheta$", "alabeo y cabeceo"),
       (r"$h$", "altura del cuerpo"), (r"$\mathbf{e}_q$", "error frente a la marcha base"),
       (r"$y,\ \psi$", "desvío lateral y giro"), (r"$\bar{e}_{coxa}$", "desviación de las coxas")]
for k, (a, b) in enumerate(var):
    y = 6.15 - 0.95 * k
    t(ax, 0.5, y, a, 14.5)
    t(ax, 2.6, y, b, 11.5)
# tabla de pesos por marcha
caja(ax, 9.9, 0.2, 23.6, 7.5, fill=TINTE, titulo="Pesos usados")
cab = ["", "Gateo", "Trote", "Galope", "Pace"]
xs = [10.3, 15.1, 17.3, 19.5, 21.7]
filas = [(r"avance $w_{av}$", "40", "10", "30", "10"), (r"actitud $w_{act}$", "30", "30", "30", "30"),
         (r"lateral $w_{lat}$", "20", "20", "30", "20"), (r"giro $w_{giro}$ / $w_{gc}$", "10 / 5", "10 / 5",
                                                         "10 / 5", "10 / 5"),
         (r"suavidad $w_{suav}$", "0,3", "0,3", "0,3", "0,3"), (r"coxas $w_{cox}$", "1", "1", "1", "0,1")]
for k, c in enumerate(cab):
    t(ax, xs[k] + (0.75 if k else 0), 6.15, c, 12, NAVY, ha="center" if k else "left", b=True)
for r, fila in enumerate(filas):
    y = 5.2 - 0.82 * r
    for k, c in enumerate(fila):
        t(ax, xs[k] + (0.75 if k else 0), y, c, 12 if k else 12.5, TINTA, ha="center" if k else "left")
guardar(fig, "7_recompensa")
