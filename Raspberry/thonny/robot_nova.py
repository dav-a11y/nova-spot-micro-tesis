"""Control del cuadrúpedo Nova desde la Raspberry Pi (Thonny), sin Arduino.

Reproduce en Python lo que hacía el firmware movimiento_suspendido_11_servos
del Arduino Uno (16 de octubre de 2026):
- mapa de canales del PCA9685 (coxas CH0-CH3, fémures CH4-CH7, tibias
  T1=CH8, T2=CH9, T3=CH10, T4=CH14, desde el 19-oct);
- topes absolutos por canal (límites del operador con 10° de margen y
  saturaciones medidas: F2/F4 <= 135°, T4 <= 105°);
- coxas fijas en su punto de equilibrio (159, 45, 54, 74 desde el 19-oct);
- caminata base (gateo FL -> RR -> FR -> RL) y ejecución de la política PPO
  exportada a NumPy.

Convención de ángulos: 0-180 grados de servo, 50 Hz, pulso de 498 a 2500 us
(igual que el Uno: map(ángulo, 0, 180, 102, 512) cuentas del PCA9685).
Todo movimiento pasa por mover_canal(), que aplica los topes.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "codigo"))

# ---------------------------------------------------------------- mapa
# Patas: 1 = delantera derecha (FR), 2 = delantera izquierda (FL),
#        3 = trasera derecha (RR), 4 = trasera izquierda (RL).
# 19-oct: tibias T1=CH8 (reparada), T2=CH9, T3=CH10, T4=CH14.
CANAL = {
    "coxa1": 0, "coxa2": 1, "coxa3": 2, "coxa4": 3,
    "femur1": 4, "femur2": 5, "femur3": 6, "femur4": 7,
    "tibia1": 8, "tibia2": 9, "tibia3": 10, "tibia4": 14,
}
BASE = {
    "coxa1": 159, "coxa2": 45, "coxa3": 61, "coxa4": 82,  # 19-oct: coxa 4 a mano; coxa 3 en 61 (72 y 65 chocaban con la pata 1)
    "femur1": 110, "femur2": 100, "femur3": 100, "femur4": 100,
    "tibia1": 100, "tibia2": 80, "tibia3": 100, "tibia4": 70,
}
SIN_USO = set()                 # 19-oct: la tibia 1 se reparó
COXAS = ("coxa1", "coxa2", "coxa3", "coxa4")
# Topes absolutos por canal PCA (mínimo, máximo).
TOPES = {0: (105, 170), 1: (10, 85), 2: (25, 90), 3: (60, 105),
         4: (30, 140), 5: (45, 135), 6: (40, 160), 7: (25, 135),
         8: (25, 160), 9: (25, 90), 10: (11, 160), 14: (15, 105)}
SIGNO_FEMUR = {1: -1, 2: 1, 3: -1, 4: 1}   # sentido "adelante" en grados de servo
SIGNO_TIBIA = {1: -1, 2: -1, 3: -1, 4: -1}  # sentido de elevación de la tibia
ORDEN_PATAS = (2, 3, 1, 4)


def grados_a_us(angulo):
    return 498.05 + max(0.0, min(180.0, angulo)) * (2001.95 / 180.0)


class ControladorSimulado:
    """Sustituto del PCA9685 para probar en el PC sin hardware."""

    def __init__(self):
        self.armed, self.pulsos = False, {}

    def prepare_channel_off(self, canal):
        self.pulsos.pop(canal, None)

    set_channel_off = prepare_channel_off

    def arm(self):
        self.armed = True

    def set_pulse_us(self, canal, us):
        if not self.armed:
            raise RuntimeError("PWM deshabilitado")
        self.pulsos[canal] = us

    def all_off(self):
        self.armed, self.pulsos = False, {}

    def close(self):
        self.all_off()


class RobotNova:
    def __init__(self, simulado=False):
        if simulado:
            self.pca = ControladorSimulado()
        else:
            from pca9685_seguro import PCA9685Seguro
            self.pca = PCA9685Seguro(bus_number=1, address=0x40, frequency_hz=50, oe_bcm_gpio=17)
        self.orden = {}                         # último ángulo enviado por articulación
        self.historial = []                     # (t, {articulación: ángulo}) para revisar

    # ------------------------------------------------------------ básico
    def mover(self, articulacion, angulo):
        if articulacion in SIN_USO:
            return None
        canal = CANAL[articulacion]
        lo, hi = TOPES[canal]
        angulo = int(round(max(lo, min(hi, angulo))))
        self.pca.set_pulse_us(canal, grados_a_us(angulo))
        self.orden[articulacion] = angulo
        return angulo

    def armar(self):
        for canal in range(16):
            self.pca.prepare_channel_off(canal)
        self.pca.arm()

    def sostener_coxas(self, pausa=0.3):
        """Lleva las cuatro coxas a su equilibrio, una por una."""
        for c in COXAS:
            self.mover(c, BASE[c])
            time.sleep(pausa)

    def postura_base(self, pausa=0.3):
        """Coxas primero, luego fémures y tibias en su posición estática."""
        self.sostener_coxas(pausa)
        for a in ("femur1", "femur2", "femur3", "femur4", "tibia1", "tibia2", "tibia3", "tibia4"):
            self.mover(a, BASE[a])
            time.sleep(pausa)

    def soltar_patas(self):
        """Apaga fémures y tibias, pero deja las coxas sostenidas (no se caen)."""
        for a, canal in CANAL.items():
            if a not in COXAS:
                self.pca.set_channel_off(canal)
                self.orden.pop(a, None)

    def apagar_todo(self):
        self.pca.all_off()
        self.orden.clear()

    def cerrar(self):
        self.pca.close()

    # ---------------------------------------------------------- caminata
    @staticmethod
    def marcha(femur=15.0, tibia=10.0, fase=0.5, pausa=0.15, dt=0.03):
        """Muestras de la caminata base en grados de servo (una por paso dt)."""
        mov, pau = round(fase / dt), round(pausa / dt)
        offset = {p: -femur + k * (2 * femur / 3) for k, p in enumerate(ORDEN_PATAS)}
        muestras = []
        for vuela in ORDEN_PATAS:
            inicio = dict(offset)
            for s in range(1, mov + pau + 1):
                t = min(1.0, s / mov)
                g = {}
                for p in ORDEN_PATAS:
                    if p == vuela:
                        o = inicio[p] + 2 * femur * t
                        lift = tibia * math.sin(math.pi * t)
                    else:
                        o, lift = inicio[p] - (2 * femur / 3) * t, 0.0
                    offset[p] = o
                    g[f"femur{p}"] = BASE[f"femur{p}"] + SIGNO_FEMUR[p] * o
                    g[f"tibia{p}"] = BASE[f"tibia{p}"] + SIGNO_TIBIA[p] * lift
                muestras.append(g)
        return muestras

    def caminar(self, ciclos=4, femur=15.0, tibia=10.0, fase=0.5, dt=0.03,
                politica=None, sensores=None):
        """Ejecuta la caminata base, opcionalmente con la corrección PPO."""
        muestras = self.marcha(femur, tibia, fase, dt=dt)
        corrector = CorrectorPPO(politica, sensores, dt) if politica else None
        # Rampa de 1 s desde la postura actual a la primera muestra.
        inicio = {a: self.orden.get(a, BASE[a]) for a in muestras[0]}
        pasos_rampa = round(1.0 / dt)
        t0 = time.time()
        k = 0
        for r in range(1, pasos_rampa + 1):
            for a, v in muestras[0].items():
                self.mover(a, inicio[a] + (v - inicio[a]) * r / pasos_rampa)
            k += 1
            _esperar(t0, k, dt)
        for c in range(ciclos):
            for i, g in enumerate(muestras):
                fase_ciclo = i / len(muestras)
                if corrector:
                    g = corrector.corregir(g, fase_ciclo)
                enviado = {a: self.mover(a, v) for a, v in g.items()}
                self.historial.append((round(time.time() - t0, 3), enviado))
                k += 1
                _esperar(t0, k, dt)
        # Regreso suave al centro.
        actual = dict(self.orden)
        for r in range(1, pasos_rampa + 1):
            for a in muestras[0]:
                if a in actual:
                    self.mover(a, actual[a] + (BASE[a] - actual[a]) * r / pasos_rampa)
            k += 1
            _esperar(t0, k, dt)


def _esperar(t0, k, dt):
    espera = t0 + k * dt - time.time()
    if espera > 0:
        time.sleep(espera)


class CorrectorPPO:
    """Política PPO exportada (politica_v4_semilla37.npz) ejecutada con NumPy.

    Observación (17): ángulos de fémur 2, fémur 4 y tibia 2 medidos (rad,
    respecto a la base), seno y coseno de la fase y residual previo / 0,08.
    Sin sensores no se puede ejecutar: la política depende de esa medición.
    """

    JOINTS = ("front_left_coxa_joint", "front_left_femur_joint", "front_left_tibia_joint",
              "front_right_coxa_joint", "front_right_femur_joint", "front_right_tibia_joint",
              "rear_left_coxa_joint", "rear_left_femur_joint", "rear_left_tibia_joint",
              "rear_right_coxa_joint", "rear_right_femur_joint", "rear_right_tibia_joint")
    PATA_DE = {"front_right": 1, "front_left": 2, "rear_right": 3, "rear_left": 4}
    SIN_RESIDUAL = {0, 3, 5, 6, 9}   # coxas y tibia FR

    def __init__(self, ruta, sensores, dt):
        import numpy as np
        if sensores is None:
            raise RuntimeError("La política PPO necesita los sensores de fémur 2, fémur 4 y tibia 2.")
        self.np, self.sensores = np, sensores
        d = np.load(ruta, allow_pickle=False)
        self.capas = []
        i = 0
        while f"W{i}" in d:
            self.capas.append((d[f"W{i}"], d[f"b{i}"]))
            i += 1
        self.Wa, self.ba = d["Wa"], d["ba"]
        self.residual = np.zeros(12)

    def corregir(self, g, fase):
        np = self.np
        med = self.sensores.leer_grados()            # {"femur2": Δ°, "femur4": Δ°, "tibia2": Δ°}
        obs_q = np.deg2rad([-SIGNO_FEMUR[2] * med["femur2"], -SIGNO_FEMUR[4] * med["femur4"],
                            -SIGNO_TIBIA[2] * med["tibia2"]])
        obs = np.r_[obs_q, math.sin(2 * math.pi * fase), math.cos(2 * math.pi * fase),
                    self.residual / 0.08]
        h = obs
        for W, b in self.capas:
            h = np.tanh(W @ h + b)
        accion = np.clip(self.Wa @ h + self.ba, -1, 1)
        for j in self.SIN_RESIDUAL:
            accion[j] = 0.0
        objetivo = accion * 0.08
        self.residual = self.residual + np.clip(objetivo - self.residual, -0.02, 0.02)
        g = dict(g)
        for j, nombre in enumerate(self.JOINTS):
            if j in self.SIN_RESIDUAL:
                continue
            pata = self.PATA_DE[nombre.rsplit("_", 2)[0]]
            r_deg = math.degrees(self.residual[j])
            if "femur" in nombre:     # q del modelo: fémur adelante = q menor
                g[f"femur{pata}"] += SIGNO_FEMUR[pata] * (-r_deg)
            else:                     # tibia: elevación = q menor
                g[f"tibia{pata}"] += SIGNO_TIBIA[pata] * (-r_deg)
        return g


class SensoresMuxADS1115:
    """Lectura de los potenciómetros por el multiplexor CD74HC4067 con un ADS1115.

    PENDIENTE DE CABLEAR Y PROBAR: la Raspberry no tiene entradas analógicas.
    Supone SIG del MUX -> A0 del ADS1115 (0x48), selectores S0-S3 en los GPIO
    BCM indicados y escala de ~2,5 cuentas/grado medida con el ADC del Uno
    (habrá que recalibrar con el ADS1115). Canales: F2=C5, F4=C6, T2=C9.
    """

    CANALES = {"femur2": 5, "femur4": 6, "tibia2": 9}

    def __init__(self, selectores=(5, 6, 13, 19), direccion=0x48, cuentas_por_grado=None):
        raise NotImplementedError("Conectar el ADS1115 y calibrar antes de usar la política en la Pi.")
