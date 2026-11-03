#!/usr/bin/env python3
"""PPO residual en MuJoCo ajustado al robot real del 16 de octubre de 2026.

Diferencias respecto a Experimentos/entrenar_ppo_mujoco.py (que no se modifica):
- Marcha nominal = la caminata `b` que funciona en el robot (firmware
  movimiento_suspendido_11_servos): gateo FL -> RR -> FR -> RL, fémures +/-15°,
  tibias 14° de elevación en la oscilación, 0,5 s de movimiento + 0,15 s de
  pausa por fase. Coxas fijas en su punto de equilibrio.
- Actuador identificado con los sensores del MUX (actuadores_reales.json):
  retardo y ganancia por articulación; tibia 1 (FR) sin PWM (sin fuerza).
- Observación limitada a lo que el Uno puede medir: ángulos de fémur 2, fémur 4
  y tibia 2 (con ruido de 1°), fase de la marcha y residual previo.
- El residual solo actúa sobre fémures y tibias con servo útil; coxas y tibia 1
  quedan con residual cero. La recompensa usa el estado del cuerpo simulado.
Solo simulación: no abre el puerto serie ni mueve el robot.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from pathlib import Path

import mujoco
import numpy as np
import torch

torch.set_num_threads(1)   # 19-oct: varios entrenamientos en paralelo; con más hilos se estorban
from gymnasium import spaces
from stable_baselines3 import PPO

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "Experimentos"))
from entrenar_ppo_mujoco import (  # noqa: E402
    JOINTS, STAND, MetricsCallback, NovaMujocoResidualEnv, _quat_roll_pitch,
)

# 20-oct: geometría medida en el robot real (antes nova_sm3.xml, referencia publicada).
MODEL = ROOT / "src/nova_sm3_description/mujoco/nova_sm3_real.xml"
LEG_JOINT_BASE = {"FL": 0, "FR": 3, "RL": 6, "RR": 9}
ORDEN_PATAS = ("FL", "RR", "FR", "RL")
FEMUR_AMP_DEG = 15.0
TIBIA_AMP_DEG = 14.0
FASE_MOV_S, FASE_PAUSA_S = 0.5, 0.15
SENSADAS = ("front_left_femur_joint", "rear_left_femur_joint", "front_left_tibia_joint")
SIN_RESIDUAL = {"front_left_coxa_joint", "front_right_coxa_joint", "rear_left_coxa_joint",
                "rear_right_coxa_joint", "front_right_tibia_joint"}
# 19-oct (v6): observación de los 8 fémures y tibias y tibia 1 activa (--completo).
SENSADAS_COMPLETO = tuple(j for j in JOINTS if "coxa" not in j)
SIN_RESIDUAL_COMPLETO = {j for j in JOINTS if "coxa" in j}


def marcha_b(control_dt):
    """Muestras articulares (rad) de la caminata `b`, una por paso de control."""
    a = np.deg2rad(FEMUR_AMP_DEG)
    pasos_mov = round(FASE_MOV_S / control_dt)
    pasos_pausa = round(FASE_PAUSA_S / control_dt)
    offset = {pata: -a + k * (2 * a / 3) for k, pata in enumerate(ORDEN_PATAS)}
    muestras = []
    for vuela in ORDEN_PATAS:
        inicio = dict(offset)
        for s in range(1, pasos_mov + pasos_pausa + 1):
            t = min(1.0, s / pasos_mov)
            q = np.tile(STAND, 4).astype(float)
            for pata in ORDEN_PATAS:
                if pata == vuela:
                    o = inicio[pata] + 2 * a * t
                    lift = np.deg2rad(TIBIA_AMP_DEG) * np.sin(np.pi * t)
                else:
                    o, lift = inicio[pata] - (2 * a / 3) * t, 0.0
                offset[pata] = o
                b = LEG_JOINT_BASE[pata]
                q[b + 1] = STAND[1] - (o + apertura(pata))   # fémur adelante = q menor
                q[b + 2] = STAND[2] - lift * ganancia_tibia(pata)     # tibia flexiona al levantar
            muestras.append(q)
    return np.asarray(muestras)


# 19-oct: segunda marcha, «paso». Versión articular de cartesian_step_walk con las
# coxas fijas: continua, sin pausas, cada pata apoya el 75 % del ciclo (el fémur va
# hacia atrás a velocidad constante) y oscila el 25 % restante en el orden
# FL -> RR -> FR -> RL. La duración del ciclo es PASO_CICLO_S.
LIMITE_CAMBIO_RAD = np.deg2rad(3.0)
# 20-oct: «apertura» delante-detrás. Las patas de un mismo lado se acercaban bajo el centro
# del cuerpo (la 1 y la 3 llegaban a chocar): las delanteras oscilan alrededor de un punto
# adelantado APERTURA_DEG y las traseras de uno atrasado lo mismo.
APERTURA_DEG = 0.0


# 27-oct: ganancia del movimiento de cada tibia (calibracion_postura.json, «ganancia_tibia» por número de pata),
# aplicada en la marcha para que la simulación entrene el mismo movimiento que hace el robot (antes solo se
# aplicaba al convertir a grados de servo y las tibias 2 y 4 del robot se movían 1,4-2,3 veces más que en la
# simulación).
def ganancia_tibia(pata):
    cal = Path(__file__).resolve().parent / "calibracion_postura.json"
    if not hasattr(ganancia_tibia, "g"):
        ganancia_tibia.g = json.loads(cal.read_text()).get("ganancia_tibia", {}) if cal.exists() else {}
    return float(ganancia_tibia.g.get({"FR": "1", "FL": "2", "RR": "3", "RL": "4"}[pata], 1.0))


def apertura(pata):
    """Desplazamiento neutro del fémur (rad, positivo = adelante) según la pata."""
    return np.deg2rad(APERTURA_DEG) * (1.0 if pata in ("FL", "FR") else -1.0)
# 19-oct (v7): variación por episodio del actuador y de los sensores (--aleatorizar).
ALEATORIZAR = False
MARCHA = "gateo"
PASO_CICLO_S = 2.4
DESFASE_PASO = {"FL": 0.75, "RR": 0.50, "FR": 0.25, "RL": 0.00}


def marcha_paso(control_dt):
    """Muestras articulares (rad) de la marcha «paso», una por paso de control."""
    a = np.deg2rad(FEMUR_AMP_DEG)
    n = round(PASO_CICLO_S / control_dt)
    apoyo = 0.75
    muestras = []
    for k in range(n):
        ciclo = k / n
        q = np.tile(STAND, 4).astype(float)
        for pata, desfase in DESFASE_PASO.items():
            fase = (ciclo + desfase) % 1.0
            if fase < apoyo:
                o, lift = a * (1.0 - 2.0 * fase / apoyo), 0.0
            else:
                t = (fase - apoyo) / (1.0 - apoyo)
                o = a * (-1.0 + 2.0 * (1.0 - np.cos(np.pi * t)) / 2.0)
                lift = np.deg2rad(TIBIA_AMP_DEG) * np.sin(np.pi * t)
            b = LEG_JOINT_BASE[pata]
            q[b + 1] = STAND[1] - (o + apertura(pata))
            q[b + 2] = STAND[2] - lift * ganancia_tibia(pata)
        muestras.append(q)
    return np.asarray(muestras)


# 20-oct: tercera marcha, «trote», claramente distinta del gateo: las patas diagonales se
# mueven a la vez (FL+RR, luego FR+RL), dos en el aire y dos apoyadas, factor de apoyo 0,5.
TROTE_CICLO_S = 1.4
PARES_TROTE = {"FL": 0.0, "RR": 0.0, "FR": 0.5, "RL": 0.5}


def marcha_trote(control_dt):
    """Muestras articulares (rad) del trote: oscilación cosenoidal de medio ciclo por par diagonal."""
    a = np.deg2rad(FEMUR_AMP_DEG)
    n = round(TROTE_CICLO_S / control_dt)
    muestras = []
    for k in range(n):
        ciclo = k / n
        q = np.tile(STAND, 4).astype(float)
        for pata, desfase in PARES_TROTE.items():
            fase = (ciclo + desfase) % 1.0
            if fase < 0.5:                       # en el aire: avanza y levanta
                t = fase / 0.5
                o = a * (-1.0 + 2.0 * (1.0 - np.cos(np.pi * t)) / 2.0)
                lift = np.deg2rad(TIBIA_AMP_DEG) * np.sin(np.pi * t)
            else:                                # apoyada: retrocede a velocidad constante
                t = (fase - 0.5) / 0.5
                o, lift = a * (1.0 - 2.0 * t), 0.0
            b = LEG_JOINT_BASE[pata]
            q[b + 1] = STAND[1] - (o + apertura(pata))
            q[b + 2] = STAND[2] - lift * ganancia_tibia(pata)
        muestras.append(q)
    return np.asarray(muestras)


# 27-oct: galope y carrera (pedido del operador). Marchas cíclicas definidas por el desfase de cada pata y
# la fracción del ciclo que pasa apoyada; la duración del ciclo es TROTE_CICLO_S (--ciclo-trote).
# Galope transverso: las patas de cada par aterrizan casi juntas (desfase 0,1), primero las traseras.
# Carrera: trote rápido con fase aérea (pares diagonales, cada pata apoyada menos de la mitad del ciclo).
# Elegidos en simulación (27-oct, 40 ciclos, 2 semillas): galope con apoyo 0,40, ciclo 0,8 s, fémur 16° y
# tibia 14° avanza 2,18 m (deriva 0,96 m; otras secuencias y apoyos no avanzan); carrera con apoyo 0,45,
# ciclo 0,8 s, fémur 12° y tibia 12° avanza 2,92 m (deriva 0,07 m). Ninguna cae.
DESFASE_GALOPE = {"RL": 0.0, "RR": 0.1, "FR": 0.5, "FL": 0.6}
APOYO_GALOPE = 0.40
APOYO_CARRERA = 0.45
# 27-oct (operador): en el galope las coxas también se mueven: cada una se abre COXA_AMP_DEG hacia afuera
# mientras su pata está en el aire (+q = afuera en las cuatro patas del modelo) y vuelve al apoyar.
COXA_AMP_DEG = 0.0
# Ganancia de la coxa de cada pata (calibracion_postura.json, «ganancia_coxa» por número de pata 1-4): la misma
# marcha en simulación y en el robot (27-oct: coxa 2 fija y coxa 4 a la mitad, rebotaban al apoyar).
_cal = HERE / "calibracion_postura.json"
GANANCIA_COXA = json.loads(_cal.read_text()).get("ganancia_coxa", {}) if _cal.exists() else {}
NUM_PATA_LETRAS = {"FR": "1", "FL": "2", "RR": "3", "RL": "4"}


def marcha_ciclica(control_dt, desfases, apoyo):
    """Muestras articulares (rad): apoyo con el fémur hacia atrás a velocidad constante y oscilación
    cosenoidal hacia adelante con la tibia levantada (como el trote, con otra fracción de apoyo)."""
    a = np.deg2rad(FEMUR_AMP_DEG)
    n = round(TROTE_CICLO_S / control_dt)
    muestras = []
    for k in range(n):
        q = np.tile(STAND, 4).astype(float)
        for pata, desfase in desfases.items():
            fase = (k / n + desfase) % 1.0
            if fase < apoyo:
                o, lift = a * (1.0 - 2.0 * fase / apoyo), 0.0
            else:
                t = (fase - apoyo) / (1.0 - apoyo)
                o = a * (-1.0 + (1.0 - np.cos(np.pi * t)))
                lift = np.deg2rad(TIBIA_AMP_DEG) * np.sin(np.pi * t)
            b = LEG_JOINT_BASE[pata]
            q[b + 1] = STAND[1] - (o + apertura(pata))
            q[b + 2] = STAND[2] - lift * ganancia_tibia(pata)
            if fase >= apoyo:
                q[b] = STAND[0] + np.deg2rad(COXA_AMP_DEG) * GANANCIA_COXA.get(NUM_PATA_LETRAS[pata], 1.0) \
                    * np.sin(np.pi * (fase - apoyo) / (1.0 - apoyo))
        muestras.append(q)
    return np.asarray(muestras)


def generar_marcha(control_dt):
    if MARCHA == "trote":
        return marcha_trote(control_dt)
    if MARCHA == "galope":
        return marcha_ciclica(control_dt, DESFASE_GALOPE, APOYO_GALOPE)
    if MARCHA == "carrera":
        return marcha_ciclica(control_dt, PARES_TROTE, APOYO_CARRERA)
    return marcha_paso(control_dt) if MARCHA == "paso" else marcha_b(control_dt)


# 3-nov: con --registrar-perdidas, terminos.csv guarda por episodio cada término de la recompensa.
RUTA_TERMINOS = None
TERMINOS = ("vivo", "avance", "actitud", "altura", "base", "correccion", "lateral", "giro", "suavidad", "coxas",
            "giro_ciclo")


class NovaRealEnv(NovaMujocoResidualEnv):
    def __init__(self, actuador, seed=11, episode_cycles=6, domain_randomization=True,
                 sensor_noise_deg=1.0, control_dt=0.02):
        super().__init__(MODEL, gait="crawl", episode_cycles=episode_cycles,
                         control_dt=control_dt, seed=seed,
                         domain_randomization=domain_randomization)
        self.nominal = generar_marcha(self.control_dt)
        self.samples = len(self.nominal)
        self.steps_per_sample = 1
        self.cycle_steps = self.samples
        self.max_steps = self.ramp_steps + self.episode_cycles * self.cycle_steps
        self.sensor_noise = np.deg2rad(sensor_noise_deg)
        self.retardo_pasos = max(0, round(actuador["retardo_s"] / self.control_dt))
        g = actuador["ganancia"]
        self.ganancia = np.full(12, g)
        for nombre, datos in actuador["articulaciones"].items():
            # Se usa la ganancia medida también cuando la correlación es baja
            # pero el sensor es bueno (tibia 4 casi no se mueve en la caminata).
            if datos["fiable"] or nombre == "rear_left_tibia_joint":
                self.ganancia[JOINTS.index(nombre)] = datos["ganancia"]
        self.mascara = np.array([0.0 if j in SIN_RESIDUAL else 1.0 for j in JOINTS])
        self.zona_muerta = np.deg2rad(float(actuador.get("zona_muerta_grados", 0.0)))
        if actuador.get("retardo_pasos_rango"):
            self.rango_retardo = tuple(int(x) for x in actuador["retardo_pasos_rango"])
        self.idx_sensadas = [JOINTS.index(j) for j in SENSADAS]
        self.idx_coxas = [JOINTS.index(j) for j in JOINTS if "coxa" in j]
        if "front_right_tibia_joint" in SIN_RESIDUAL:
            # Tibia 1 (FR) sin PWM: actuador sin rigidez, solo amortiguamiento.
            act = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, "front_right_tibia_act")
            self.model.actuator_gainprm[act, 0] = 0.0
            self.model.actuator_biasprm[act, 1] = 0.0
        obs_dim = len(SENSADAS) + 2 + 12
        self.observation_space = spaces.Box(-np.inf, np.inf, (obs_dim,), np.float32)
        self.cola = deque()

    def _observation(self):
        q = self.data.qpos[self.qpos_ids][self.idx_sensadas]
        q = q + self.rng.normal(0.0, self.sensor_noise, size=q.shape)
        q = q + getattr(self, "sesgo_sensor", 0.0)
        fase = (max(0, self.step_count - self.ramp_steps) % self.cycle_steps) / self.cycle_steps
        return np.asarray(np.r_[q - np.asarray(STAND * 4)[self.idx_sensadas],
                                np.sin(2 * np.pi * fase), np.cos(2 * np.pi * fase),
                                self.previous_residual / 0.08], dtype=np.float32)

    def _cuerpo(self):
        roll, pitch = _quat_roll_pitch(self.data.xquat[self.base_body])
        return roll, pitch, float(self.data.xpos[self.base_body, 2])

    def _reward(self, residual, before_x):
        roll, pitch, h = self._cuerpo()
        dx = float(self.data.xpos[self.base_body, 0] - before_x)
        q_err = (self.data.qpos[self.qpos_ids] - self.current_nominal) * self.mascara
        w = getattr(self, "pesos", {})
        rec = (1.0 + w.get("avance", 18.0) * dx - w.get("actitud", 8.0) * (roll ** 2 + pitch ** 2)
               - 25.0 * (h - 0.235) ** 2 - 0.25 * q_err @ q_err - 0.04 * residual @ residual)
        if w.get("lateral") or w.get("giro"):
            from entrenar_ppo_mujoco import _quat_yaw
            lat = float(self.data.xpos[self.base_body, 1] - self.initial_y)
            yaw = float(np.arctan2(np.sin(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw),
                                   np.cos(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw)))
            rec -= w.get("lateral", 0.0) * lat ** 2 + w.get("giro", 0.0) * yaw ** 2
        if RUTA_TERMINOS:
            # 3-nov: desglose de la recompensa solo para registrarlo; no cambia el valor devuelto.
            self._t = dict(vivo=1.0, avance=w.get("avance", 18.0) * dx,
                           actitud=-w.get("actitud", 8.0) * (roll ** 2 + pitch ** 2),
                           altura=-25.0 * (h - 0.235) ** 2, base=-0.25 * float(q_err @ q_err),
                           correccion=-0.04 * float(residual @ residual))
            if w.get("lateral") or w.get("giro"):
                self._t["lateral"] = -w.get("lateral", 0.0) * lat ** 2
                self._t["giro"] = -w.get("giro", 0.0) * yaw ** 2
        return float(rec)

    def reset(self, *, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        if ALEATORIZAR:
            # Retardo de 60-120 ms, ganancia +/-5 % por servo y desfase de sensor +/-1°.
            if not hasattr(self, "ganancia_nominal"):
                self.ganancia_nominal, self.retardo_nominal = self.ganancia.copy(), self.retardo_pasos
            # 21-oct: rango de retardo medido en el robot (actualizar_modelo_real.py); si no hay, 2-4 pasos.
            lo, hi = getattr(self, "rango_retardo", (2, 4))
            self.retardo_pasos = int(self.rng.integers(lo, hi + 1))
            self.ganancia = self.ganancia_nominal * self.rng.uniform(0.95, 1.05, 12)
            self.sesgo_sensor = np.deg2rad(self.rng.uniform(-1.0, 1.0, len(self.idx_sensadas)))
        self.cola = deque([self.data.ctrl.copy()] * self.retardo_pasos)
        self.ultimo_efectivo = None
        self.orden_previa = None
        self.yaw_ciclo = None
        return self._observation(), info

    def _registrar_terminos(self, reward, terminated, truncated):
        """3-nov: suma por episodio cada premio y castigo y escribe una fila en terminos.csv."""
        if not hasattr(self, "_acum"):
            self._acum, self._ep = dict.fromkeys(TERMINOS, 0.0), 0
            self._pasos_ep, self._total_ep = 0, 0.0
        for k, v in self._t.items():
            self._acum[k] += v
        self._pasos_ep += 1
        self._total_ep += reward
        if terminated or truncated:
            nuevo = not RUTA_TERMINOS.exists()
            with RUTA_TERMINOS.open("a") as f:
                if nuevo:
                    f.write("episodio,pasos_ep,total,caida," + ",".join(TERMINOS) + "\n")
                f.write(f"{self._ep},{self._pasos_ep},{self._total_ep:.6f},{int(terminated)},"
                        + ",".join(f"{self._acum[k]:.6f}" for k in TERMINOS) + "\n")
            self._ep += 1
            self._acum = dict.fromkeys(TERMINOS, 0.0)
            self._pasos_ep, self._total_ep = 0, 0.0

    def step(self, action):
        action = np.asarray(action, dtype=float) * self.mascara
        target = np.clip(action, -1.0, 1.0) * 0.08
        delta = np.clip(target - self.previous_residual, -0.02, 0.02)
        residual = (self.previous_residual + delta) * self.mascara
        self.previous_residual = residual
        ramp = self.step_count < self.ramp_steps
        if ramp:
            f = (self.step_count + 1) / self.ramp_steps
            nominal = self.initial_ctrl + f * (self.nominal[0] - self.initial_ctrl)
        else:
            nominal = self.nominal[(self.step_count - self.ramp_steps) % self.cycle_steps]
        self.current_nominal = nominal
        orden = nominal + residual
        # 19-oct: el firmware limita el cambio de cada orden a 3° por línea.
        previa = getattr(self, "orden_previa", None)
        if previa is not None:
            orden = np.clip(orden, previa - LIMITE_CAMBIO_RAD, previa + LIMITE_CAMBIO_RAD)
        self.orden_previa = orden.copy()
        stand = np.tile(STAND, 4)
        efectivo = stand + self.ganancia * (orden - stand)
        if self.zona_muerta > 0:
            # Zona muerta del servo: no se mueve si el cambio pedido es menor.
            previo = getattr(self, "ultimo_efectivo", None)
            if previo is not None:
                efectivo = np.where(np.abs(efectivo - previo) < self.zona_muerta, previo, efectivo)
            self.ultimo_efectivo = efectivo.copy()
        self.cola.append(efectivo)
        aplicado = self.cola.popleft() if len(self.cola) > self.retardo_pasos else efectivo
        before_x = float(self.data.xpos[self.base_body, 0])
        self.data.ctrl[:] = np.clip(aplicado, self.model.actuator_ctrlrange[:, 0],
                                    self.model.actuator_ctrlrange[:, 1])
        for _ in range(self.sim_substeps):
            mujoco.mj_step(self.model, self.data)
        reward = self._reward(residual, before_x)
        # 20-oct (v11): en el robot la PPO del paso daba correcciones bruscas que los servos no
        # siguen y sacudía el cuerpo (coxas desviadas). Se penalizan el cambio del residual
        # (en unidades del cambio máximo por paso) y la desviación de las coxas (grados²).
        pesos = getattr(self, "pesos", {})
        if pesos.get("suavidad"):
            reward -= pesos["suavidad"] * float(np.sum((delta * self.mascara / 0.02) ** 2))
            if RUTA_TERMINOS:
                self._t["suavidad"] = -pesos["suavidad"] * float(np.sum((delta * self.mascara / 0.02) ** 2))
        if pesos.get("coxas"):
            err = np.degrees(self.data.qpos[self.qpos_ids][self.idx_coxas] - self.data.ctrl[self.idx_coxas])
            reward -= pesos["coxas"] * float(np.mean(err ** 2))
            if RUTA_TERMINOS:
                self._t["coxas"] = -pesos["coxas"] * float(np.mean(err ** 2))
        # 19-oct (v10): giro del cuerpo en cada ciclo completo. Sin IMU la política no ve el
        # rumbo; penalizar el giro por ciclo evita que se curve en caminatas largas.
        w_ciclo = getattr(self, "pesos", {}).get("giro_ciclo", 0.0)
        if w_ciclo and not ramp and (self.step_count - self.ramp_steps + 1) % self.cycle_steps == 0:
            from entrenar_ppo_mujoco import _quat_yaw
            yaw = _quat_yaw(self.data.xquat[self.base_body])
            previo = getattr(self, "yaw_ciclo", None)
            if previo is not None:
                giro = np.degrees(np.arctan2(np.sin(yaw - previo), np.cos(yaw - previo)))
                reward -= w_ciclo * giro ** 2
                if RUTA_TERMINOS:
                    self._t["giro_ciclo"] = -w_ciclo * giro ** 2
            self.yaw_ciclo = yaw
        self.step_count += 1
        roll, pitch, h = self._cuerpo()
        obs = self._observation()
        terminated = bool(not np.isfinite(obs).all() or h < 0.12 or h > 0.40
                          or abs(roll) > 0.60 or abs(pitch) > 0.60)
        truncated = self.step_count >= self.max_steps
        if RUTA_TERMINOS:
            self._registrar_terminos(reward, terminated, truncated)
        return obs, reward, terminated, truncated, {
            "roll": roll, "pitch": pitch, "height": h,
            "x": float(self.data.xpos[self.base_body, 0]),
            "y": float(self.data.xpos[self.base_body, 1]),
            "residual_norm": float(np.linalg.norm(residual)), "ramp_active": ramp}


def evaluar(model, actuador, semillas, deterministic=True, control_dt=0.02):
    filas = []
    for cond in ("nominal", "ppo"):
        for s in semillas:
            env = NovaRealEnv(actuador, seed=s, control_dt=control_dt)
            obs, _ = env.reset(seed=s)
            x0, y0, ret, maxinc, caida = None, None, 0.0, 0.0, False
            while True:
                act = np.zeros(12) if cond == "nominal" else model.predict(obs, deterministic=deterministic)[0]
                obs, r, term, trunc, info = env.step(act)
                if x0 is None and not info["ramp_active"]:
                    x0, y0 = info["x"], info["y"]
                ret += r
                maxinc = max(maxinc, abs(info["roll"]), abs(info["pitch"]))
                if term:
                    caida = True
                if term or trunc:
                    break
            filas.append(dict(condicion=cond, semilla_eval=s, retorno=round(ret, 2),
                              avance_m=round(info["x"] - (x0 or 0), 4),
                              deriva_lateral_m=round(abs(info["y"] - (y0 or 0)), 4),
                              inclinacion_max_rad=round(maxinc, 4), caida=caida))
    return filas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=11)
    p.add_argument("--timesteps", type=int, default=150_000)
    p.add_argument("--eval-seeds", type=int, nargs="+", default=[801, 802, 803, 804, 805])
    p.add_argument("--output", type=Path, default=HERE / "ppo")
    p.add_argument("--actuador", type=Path, default=HERE / "actuadores_reales.json")
    p.add_argument("--dt", type=float, default=0.02, help="periodo de control (s)")
    p.add_argument("--femur", type=float, default=15.0)
    p.add_argument("--tibia", type=float, default=14.0)
    p.add_argument("--fase", type=float, default=0.5)
    p.add_argument("--w-avance", type=float, default=18.0)
    p.add_argument("--w-actitud", type=float, default=8.0)
    p.add_argument("--w-lateral", type=float, default=0.0)
    p.add_argument("--w-giro", type=float, default=0.0)
    p.add_argument("--w-giro-ciclo", type=float, default=0.0, help="penalización por grado² de giro en cada ciclo")
    p.add_argument("--w-suavidad", type=float, default=0.0, help="penalización del cambio del residual (v11)")
    p.add_argument("--w-coxas", type=float, default=0.0, help="penalización de la desviación de las coxas en grados² (v11)")
    p.add_argument("--marcha", choices=("gateo", "paso", "trote", "galope", "carrera"), default="gateo")
    p.add_argument("--apertura", type=float, default=0.0, help="apertura delante-detrás de los fémures (°)")
    p.add_argument("--coxa", type=float, default=0.0, help="galope y carrera: apertura de la coxa al levantar la pata (°)")
    p.add_argument("--ciclo-trote", type=float, default=1.4, help="duración del ciclo del trote (s)")
    p.add_argument("--ciclo-paso", type=float, default=2.4, help="duración del ciclo del paso (s)")
    p.add_argument("--ciclos-episodio", type=int, default=6, help="ciclos de marcha por episodio")
    p.add_argument("--lr", type=float, default=3e-4, help="tasa de aprendizaje")
    p.add_argument("--target-kl", type=float, help="límite de cambio de la política por actualización")
    p.add_argument("--n-steps", type=int, default=1024)
    p.add_argument("--continuar", type=Path, help="policy.zip desde la que seguir entrenando")
    p.add_argument("--guardar-cada", type=int, default=100_000, help="pasos entre copias intermedias")
    p.add_argument("--registrar-perdidas", action="store_true",
                   help="29-oct: guarda en perdidas.csv las pérdidas de PPO de cada actualización")
    p.add_argument("--aleatorizar", action="store_true",
                   help="varía retardo, ganancia y desfase de sensores en cada episodio (v7)")
    p.add_argument("--completo", action="store_true",
                   help="observa los 8 fémures y tibias y corrige también la tibia 1 (v6)")
    a = p.parse_args()
    global SENSADAS, SIN_RESIDUAL, MARCHA, PASO_CICLO_S
    MARCHA, PASO_CICLO_S = a.marcha, a.ciclo_paso
    global TROTE_CICLO_S, APERTURA_DEG, COXA_AMP_DEG
    TROTE_CICLO_S, APERTURA_DEG, COXA_AMP_DEG = a.ciclo_trote, a.apertura, a.coxa
    global ALEATORIZAR
    ALEATORIZAR = a.aleatorizar
    if a.completo:
        SENSADAS, SIN_RESIDUAL = SENSADAS_COMPLETO, SIN_RESIDUAL_COMPLETO
    actuador = json.loads(a.actuador.read_text())
    global FEMUR_AMP_DEG, TIBIA_AMP_DEG, FASE_MOV_S
    FEMUR_AMP_DEG, TIBIA_AMP_DEG, FASE_MOV_S = a.femur, a.tibia, a.fase
    NovaRealEnv.pesos = dict(avance=a.w_avance, actitud=a.w_actitud, lateral=a.w_lateral, giro=a.w_giro,
                             giro_ciclo=a.w_giro_ciclo, suavidad=a.w_suavidad, coxas=a.w_coxas)
    out = a.output / f"semilla_{a.seed}"
    out.mkdir(parents=True, exist_ok=True)
    global RUTA_TERMINOS
    if a.registrar_perdidas:
        RUTA_TERMINOS = out / "terminos.csv"
    env = NovaRealEnv(actuador, seed=a.seed, control_dt=a.dt, episode_cycles=a.ciclos_episodio)
    if a.registrar_perdidas:
        # 29-oct: monitor.csv con la recompensa cruda de cada episodio (para graficar ruido y convergencia).
        from stable_baselines3.common.monitor import Monitor
        env = Monitor(env, filename=str(out / "monitor"))
    if a.continuar:
        model = PPO.load(a.continuar, env=env, device="cpu",
                         custom_objects=dict(learning_rate=a.lr, target_kl=a.target_kl))
        # 22-oct: PPO.load restaura la semilla guardada en la política y reinicia con ella el entorno y
        # la red, así que varias «semillas» que continuaban la misma política daban ejecuciones idénticas
        # (campañas ciclo1/ciclo2). Se impone la semilla pedida.
        model.set_random_seed(a.seed)
        model.seed = a.seed
    else:
        model = PPO("MlpPolicy", env, seed=a.seed, verbose=0, n_steps=a.n_steps, batch_size=256,
                    learning_rate=a.lr, target_kl=a.target_kl)
    if a.registrar_perdidas:
        # 29-oct: pérdida total, de la política, del crítico, entropía, KL y varianza explicada por actualización.
        from stable_baselines3.common.logger import configure
        model.set_logger(configure(str(out), ["csv"]))
    from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback
    copias = CheckpointCallback(save_freq=a.guardar_cada, save_path=str(out / "intermedias"), name_prefix="policy")
    model.learn(total_timesteps=a.timesteps, reset_num_timesteps=not a.continuar,
                callback=CallbackList([MetricsCallback(out / "training_trace.csv"), copias]))
    model.save(out / "policy.zip")
    RUTA_TERMINOS = None  # 3-nov: los episodios de evaluación no son entrenamiento
    filas = evaluar(model, actuador, a.eval_seeds, control_dt=a.dt)
    with (out / "evaluacion.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader(); w.writerows(filas)
    (out / "metadata.json").write_text(json.dumps(dict(
        seed=a.seed, timesteps=int(model.num_timesteps),
        continuado_desde=str(a.continuar) if a.continuar else None, ciclos_episodio=a.ciclos_episodio,
        ppo=dict(lr=a.lr, target_kl=a.target_kl, n_steps=a.n_steps), eval_seeds=a.eval_seeds, control_dt=a.dt,
        marcha=dict(tipo=a.marcha, femur_deg=a.femur, tibia_deg=a.tibia, fase_s=a.fase,
                    ciclo_paso_s=a.ciclo_paso, ciclo_trote_s=a.ciclo_trote, apertura_deg=a.apertura, coxa_deg=a.coxa), pesos=NovaRealEnv.pesos,
        actuador=actuador, hardware_transfer=False,
        observacion=list(SENSADAS) + ["sin_fase", "cos_fase", "residual_previo x12"],
        sin_residual=sorted(SIN_RESIDUAL), aleatorizar_actuador=a.aleatorizar,
        limite_cambio_grados=float(np.rad2deg(LIMITE_CAMBIO_RAD)),
        nota="Simulación ajustada al robot real del 16-oct; no transferida al robot."),
        indent=2, ensure_ascii=False))
    for cond in ("nominal", "ppo"):
        sub = [f for f in filas if f["condicion"] == cond]
        print(cond, {k: round(float(np.mean([f[k] for f in sub])), 4)
                     for k in ("retorno", "avance_m", "deriva_lateral_m", "inclinacion_max_rad")},
              "caidas", sum(f["caida"] for f in sub))


if __name__ == "__main__":
    main()
