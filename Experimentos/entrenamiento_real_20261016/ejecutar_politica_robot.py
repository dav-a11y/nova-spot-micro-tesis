#!/usr/bin/env python3
"""Ejecuta la caminata `b` en el robot real desde el PC, opcionalmente con la
corrección PPO entrenada en entrenar_ppo_real.py.

Requiere el firmware movimiento_suspendido_11_servos con el modo `@`. Cada 20 ms
el PC envía los 12 ángulos de servo; el Uno aplica límites (fémur ±20°,
tibia ±18°, 3° por línea), mantiene las coxas en equilibrio, deja la tibia 1
sin PWM y responde con los sensores de SENSORES (19-oct: todas las patas).
Abrir el puerto reinicia el Uno, que arranca con todo en OFF.

Uso:  python ejecutar_politica_robot.py --ciclos 6 [--politica ppo/semilla_11/policy.zip]
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import termios
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
from entrenar_ppo_real import STAND, JOINTS  # noqa: E402

# Índices del firmware: 0-3 coxas (patas 1..4), 4-7 fémures, 8-11 tibias.
# Patas: 1=FR, 2=FL, 3=RR, 4=RL. Base y signos de la caminata `b` del firmware.
BASE = [159, 42, 64, 82, 110, 100, 100, 100, 100, 166, 100, 144]  # 19-oct: equilibrio nuevo de coxas; 28-oct: coxa 2 48 -> 42
SIGNO_FEMUR = {1: -1, 2: 1, 3: -1, 4: 1}
# 21-oct: las tibias izquierdas (2 y 4) giran al revés que las derechas: medido con las cintas de
# de colores (al pedir «doblar» se estiraban). Antes las cuatro tenían −1.
SIGNO_TIBIA = {1: -1, 2: 1, 3: -1, 4: 1}
# 27-oct: sentido de cada servo de coxa para abrir la pata hacia afuera (+q del modelo); medido con probar_coxas.py.
SIGNO_COXA = {1: -1, 2: 1, 3: 1, 4: -1}   # medido 27-oct con la cámara frontal (prueba_coxas_20261027)   # 27-oct (operador): tibias 2 y 4 con el movimiento invertido; apoyo 174°/144° en calibracion_postura.json
PATA = {1: "front_right", 2: "front_left", 3: "rear_right", 4: "rear_left"}
CUENTAS_POR_GRADO = 2.45
# Campos de la respuesta R del modo @ (19-oct, v6), en orden.
SENSORES = ["C5", "C6", "C9", "C1", "C3", "C2", "C10", "C11", "ENC_T2",
             "C0", "C8", "ENC_T1", "ENC_F1", "ENC_F4",
             # 27-oct: IMU BNO055 (guiñada, roll, pitch en 1/16°; aceleración lineal en cm/s²; calibración);
             # -1 si no hay IMU o el firmware es anterior.
             "IMU_H", "IMU_R", "IMU_P", "IMU_AX", "IMU_AY", "IMU_AZ", "IMU_CAL"]
CALIBRACION = HERE / "sensores_robot.json"
_cal_postura = HERE / "calibracion_postura.json"
CAL_POSTURA = (__import__("json").loads(_cal_postura.read_text()).get("femur_offset_deg", {})
               if _cal_postura.exists() else {})
# 21-oct: corrección también de las tibias (+ = doblar más la rodilla), medida con las cintas de colores.
CAL_TIBIA = (__import__("json").loads(_cal_postura.read_text()).get("tibia_offset_deg", {})
             if _cal_postura.exists() else {})
RETARDO_PASOS = 3            # 87 ms de retardo de los servos a 30 ms por paso
SIGNO = {"femur": SIGNO_FEMUR, "tibia": SIGNO_TIBIA}
NUM_PATA = {v: k for k, v in PATA.items()}
DT = 0.02  # se reemplaza por control_dt del metadata.json de la política


# 21-oct: topes del firmware (movimiento_suspendido_11_servos.ino, TOPE_MIN/TOPE_MAX por canal PCA),
# en el orden de índices del firmware (0-3 coxas, 4-7 fémures, 8-11 tibias: CH8, CH9, CH10, CH14).
# El firmware recorta igual; aquí se recorta para que el registro refleje la orden que se aplica.
# 27-oct: topes de las tibias 2 (155-180) y 4 (130-175) alrededor de su apoyo nuevo; coxa 3 en 64 (antes 61).
TOPE_MIN = [105, 10, 25, 60, 30, 45, 40, 25, 12, 155, 11, 130]   # 27-oct: tibia 1 hasta 18; 5-nov: hasta 12 (operador)
TOPE_MAX = [170, 85, 90, 105, 140, 135, 160, 135, 160, 180, 160, 175]


def a_grados_servo(q):
    """Ángulos del modelo (rad, orden JOINTS) -> 12 grados de servo del firmware."""
    out = list(BASE)
    for pata in (1, 2, 3, 4):
        # 27-oct: coxas del galope (en las demás marchas q coxa = STAND[0] y queda la base).
        jc = JOINTS.index(f"{PATA[pata]}_coxa_joint")
        out[pata - 1] = round(BASE[pata - 1] + SIGNO_COXA[pata] * np.rad2deg(q[jc] - STAND[0]))
        jf = JOINTS.index(f"{PATA[pata]}_femur_joint")
        jt = JOINTS.index(f"{PATA[pata]}_tibia_joint")
        o = -(q[jf] - STAND[1])          # fémur adelante (rad)
        lift = -(q[jt] - STAND[2])       # elevación de tibia (rad)
        # 20-oct: corrección del punto neutro de cada fémur (calibracion_postura.json, + = adelante).
        o_cal = np.rad2deg(o) + CAL_POSTURA.get(str(pata), 0.0)
        out[3 + pata] = round(BASE[3 + pata] + SIGNO_FEMUR[pata] * o_cal)
        # 27-oct: la ganancia de cada tibia ya va en la marcha (entrenar_ppo_real.ganancia_tibia).
        out[7 + pata] = round(BASE[7 + pata] + SIGNO_TIBIA[pata] * (np.rad2deg(lift) + CAL_TIBIA.get(str(pata), 0.0)))
    return [int(min(max(v, lo), hi)) for v, lo, hi in zip(out, TOPE_MIN, TOPE_MAX)]


def delta_modelo(nombre, valores, ref, cal):
    """Cambio del ángulo del modelo (grados) de una articulación según su sensor.

    cal[nombre] = {"campo": C8/ENC_T1..., "k": unidades de sensor por grado de servo}.
    Potenciómetro: k en cuentas/°; encoder: k en °encoder/°servo.
    """
    c = cal[nombre]
    v, r0 = valores.get(c["campo"], -1), ref.get(c["campo"], -1)
    if (v < 0 or r0 < 0 or not lectura_valida(c["campo"], v)) and "respaldo" in c \
            and ref.get(c["respaldo"]["campo"], -1) >= 0 and valores.get(c["respaldo"]["campo"], -1) >= 0:
        c = c["respaldo"]                             # 19-oct: sensor de respaldo (encoder)
        v, r0 = valores[c["campo"]], ref[c["campo"]]
    if v < 0 or r0 < 0:
        return None                                   # sin sensor: el llamador estima con la orden
    d = v - r0
    if c["campo"].startswith("ENC"):
        d = (d * 360.0 / 4096.0 + 180.0) % 360.0 - 180.0
    elif cal.get("compensar_con"):
        # 19-oct: los potenciómetros se desplazan juntos con la corriente de los servos;
        # la coxa 1 (C0) está quieta y solo ve ese desplazamiento.
        d -= valores[cal["compensar_con"]] - ref[cal["compensar_con"]]
    d_servo = d / c["k"]
    pata = NUM_PATA[nombre.rsplit("_", 2)[0]]
    tipo = "femur" if "femur" in nombre else "tibia"
    return -d_servo / SIGNO[tipo][pata]           # fémur: adelante = q menor; tibia: elevar = q menor


def lectura_valida(campo, v):
    """Un potenciómetro fuera de 30-950 cuentas está desconectado o en cortocircuito."""
    return v >= 0 if campo.startswith("ENC") else 30 <= v <= 950


def abrir(puerto):
    fd = os.open(puerto, os.O_RDWR | os.O_NOCTTY)
    a = termios.tcgetattr(fd)
    a[4] = a[5] = termios.B115200
    a[0] = a[1] = a[3] = 0
    a[2] |= termios.CLOCAL | termios.CREAD
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


class Lector:
    def __init__(self, fd):
        self.fd, self.buf = fd, b""

    def linea(self, timeout=1.0):
        fin = time.time() + timeout
        while time.time() < fin:
            if b"\n" in self.buf:
                l, self.buf = self.buf.split(b"\n", 1)
                return l.decode(errors="replace").strip()
            self.buf += os.read(self.fd, 256)
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--puerto", default="/dev/ttyACM0")
    p.add_argument("--ciclos", type=int, default=6)
    p.add_argument("--duracion-s", type=float, help="camina este tiempo (termina el ciclo en curso); ignora --ciclos")
    p.add_argument("--politica", type=Path)
    p.add_argument("--salida", type=Path)
    p.add_argument("--dt", type=float)
    p.add_argument("--femur", type=float)
    p.add_argument("--tibia", type=float)
    p.add_argument("--fase", type=float)
    p.add_argument("--marcha", choices=("gateo", "paso", "trote", "galope", "carrera"))
    p.add_argument("--ciclo-trote", type=float)
    p.add_argument("--apertura", type=float, help="apertura delante-detrás de los fémures (°)")
    p.add_argument("--coxa", type=float, help="galope y carrera: apertura de la coxa al levantar la pata (°)")
    p.add_argument("--ciclo-paso", type=float)
    a = p.parse_args()
    global DT
    modelo = None
    sensadas = ["front_left_femur_joint", "rear_left_femur_joint", "front_left_tibia_joint"]
    sin_residual = {"front_left_coxa_joint", "front_right_coxa_joint", "rear_left_coxa_joint",
                    "rear_right_coxa_joint", "front_right_tibia_joint"}
    if a.politica:
        from stable_baselines3 import PPO
        # 21-oct: la red en un solo hilo (con varios competía con cámaras y análisis y el bucle de 33 ms llegaba tarde).
        import torch
        torch.set_num_threads(1)
        modelo = PPO.load(a.politica, device="cpu")
        meta = a.politica.with_name("metadata.json")
        if meta.exists():
            import json
            md = json.loads(meta.read_text())
            DT = float(md.get("control_dt", DT))
            m = md.get("marcha", {})
            E.FEMUR_AMP_DEG = m.get("femur_deg", E.FEMUR_AMP_DEG)
            E.TIBIA_AMP_DEG = m.get("tibia_deg", E.TIBIA_AMP_DEG)
            E.FASE_MOV_S = m.get("fase_s", E.FASE_MOV_S)
            E.MARCHA = m.get("tipo", E.MARCHA)
            E.PASO_CICLO_S = m.get("ciclo_paso_s", E.PASO_CICLO_S)
            E.TROTE_CICLO_S = m.get("ciclo_trote_s", E.TROTE_CICLO_S)
            E.APERTURA_DEG = m.get("apertura_deg", E.APERTURA_DEG)
            E.COXA_AMP_DEG = m.get("coxa_deg", E.COXA_AMP_DEG)
            sensadas = [o for o in md.get("observacion", sensadas) if o.endswith("_joint")]
            sin_residual = set(md.get("sin_residual", sin_residual))
    if a.dt:
        DT = a.dt
    if a.femur: E.FEMUR_AMP_DEG = a.femur
    if a.tibia: E.TIBIA_AMP_DEG = a.tibia
    if a.fase: E.FASE_MOV_S = a.fase
    if a.marcha: E.MARCHA = a.marcha
    if a.ciclo_paso: E.PASO_CICLO_S = a.ciclo_paso
    if a.ciclo_trote: E.TROTE_CICLO_S = a.ciclo_trote
    if a.apertura is not None: E.APERTURA_DEG = a.apertura
    if a.coxa is not None: E.COXA_AMP_DEG = a.coxa
    print(f"Periodo de control: {DT*1000:.0f} ms | {E.MARCHA} fémur {E.FEMUR_AMP_DEG}° tibia {E.TIBIA_AMP_DEG}° fase {E.FASE_MOV_S} s")
    nominal = E.generar_marcha(DT)
    stand = np.tile(STAND, 4).astype(float)
    mascara = np.array([0.0 if j in sin_residual else 1.0 for j in JOINTS])
    import json
    cal = json.loads(CALIBRACION.read_text())

    fd = abrir(a.puerto)
    lec = Lector(fd)
    time.sleep(2.0)                      # reinicio del Uno al abrir el puerto
    os.read(fd, 4096)
    # 27-oct: con coxas en movimiento se usa el modo '+' del firmware (aplica las órdenes de las coxas).
    os.write(fd, b"+" if E.COXA_AMP_DEG > 0 else b"@")
    while True:
        l = lec.linea(timeout=8.0)
        if l is None:
            sys.exit("El Uno no respondió STREAM_LISTO")
        if l.startswith("STREAM_LISTO"):
            break
    # Referencias ADC en la postura base (servo en BASE).
    os.write(fd, ("S," + ",".join(map(str, BASE)) + "\n").encode())
    r = lec.linea().split(",")
    ref = {n: int(x) for n, x in zip(SENSORES, r[2:])}
    # 19-oct: si el sensor de una articulación observada no responde, se estima con su
    # orden retrasada 87 ms (los servos siguen la orden con r > 0,99 y ~1° de error).
    # 21-oct: «sin_sensor» en sensores_robot.json = sensor que da lecturas pero no sigue la articulación
    # (tibia 3, C11 fijo): también se estima con la orden retrasada.
    estimadas = [n for n in sensadas if cal[n].get("sin_sensor") or ref.get(cal[n]["campo"], -1) < 0
                 and ref.get(cal[n].get("respaldo", {}).get("campo"), -1) < 0]
    for n in estimadas:
        print(f"AVISO: el sensor {cal[n]['campo']} de {n} no responde; se usa la orden retrasada como estimación.")
    historial_ordenes = []
    estimaciones = {}

    salida = a.salida or HERE / f"robot_{'ppo' if modelo else 'nominal'}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    f = salida.open("w", newline="")
    w = csv.writer(f)
    w.writerow(["t", "paso", "fase", *[f"orden_{i}" for i in range(12)], *[f"nominal_{i}" for i in range(12)],
                *SENSORES, *[f"residual_{j}" for j in JOINTS]])
    residual_prev = np.zeros(12)
    rampa = round(1.0 / DT)
    total = rampa + (10_000 if a.duracion_s else a.ciclos) * len(nominal)
    obs_q = np.zeros(len(sensadas))
    ultimo_valido = {n: v for n, v in ref.items() if v >= 0}
    perdidas_seguidas = {}
    t0 = time.time()
    # 19-oct: hora real de inicio, para sincronizar con el video de las cámaras.
    salida.with_suffix('.inicio.txt').write_text(f"{t0:.6f}\n")
    # 19-oct: configuración completa de la caminata, para análisis de estabilidad y repetibilidad.
    import json, hashlib
    firmware = Path.home() / "CODIGO/movimiento_suspendido_11_servos/movimiento_suspendido_11_servos.ino"
    salida.with_suffix('.config.json').write_text(json.dumps(dict(
        fecha=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t0)), argumentos=sys.argv[1:],
        marcha=E.MARCHA, ciclo_paso_s=E.PASO_CICLO_S if E.MARCHA == "paso" else None,
        femur_deg=E.FEMUR_AMP_DEG, tibia_deg=E.TIBIA_AMP_DEG, fase_s=E.FASE_MOV_S, dt=DT,
        politica=str(a.politica) if a.politica else None, observacion=list(sensadas) if modelo else None,
        base_servos=BASE, referencias_sensores=ref, calibracion_sensores=cal,
        firmware_sha1=hashlib.sha1(firmware.read_bytes()).hexdigest() if firmware.exists() else None),
        indent=2, ensure_ascii=False))
    try:
        for k in range(total):
            if k < rampa:
                q_nom = stand + (k + 1) / rampa * (nominal[0] - stand)
                fase = 0.0
            else:
                i = (k - rampa) % len(nominal)
                q_nom, fase = nominal[i], i / len(nominal)
            residual = np.zeros(12)
            if modelo is not None and k >= rampa:
                obs = np.r_[obs_q, np.sin(2 * np.pi * fase), np.cos(2 * np.pi * fase),
                            residual_prev / 0.08].astype(np.float32)
                accion = modelo.predict(obs, deterministic=True)[0] * mascara
                objetivo = np.clip(accion, -1, 1) * 0.08
                residual = (residual_prev + np.clip(objetivo - residual_prev, -0.02, 0.02)) * mascara
            residual_prev = residual
            if a.duracion_s and k >= rampa and (k - rampa) % len(nominal) == 0 and k > rampa \
                    and time.time() - t0 >= a.duracion_s:
                break                         # ciclo completo y tiempo cumplido
            grados = a_grados_servo(q_nom + residual)
            grados_nom = a_grados_servo(q_nom)
            os.write(fd, ("S," + ",".join(map(str, grados)) + "\n").encode())
            resp = lec.linea(timeout=0.3)
            if not resp or not resp.startswith("R,"):
                print("Respuesta perdida en el paso", k, resp)
                break
            valores = {n: int(x) for n, x in zip(SENSORES, resp.split(",")[2:])}
            v = [valores.get(n, -1) for n in SENSORES]
            # 19-oct: lectura perdida (-1) -> último valor válido durante 5 pasos como máximo;
            # después el sensor se da por caído y se usa el respaldo o la orden retrasada.
            for n_s, x in valores.items():
                if x >= 0:
                    ultimo_valido[n_s], perdidas_seguidas[n_s] = x, 0
                else:
                    perdidas_seguidas[n_s] = perdidas_seguidas.get(n_s, 0) + 1
                    if n_s in ultimo_valido and perdidas_seguidas[n_s] <= 5:
                        valores[n_s] = ultimo_valido[n_s]
            # Sensor -> grados de servo -> ángulo del modelo (escalas en sensores_robot.json).
            historial_ordenes.append(q_nom + residual)
            q_retrasada = historial_ordenes[max(0, len(historial_ordenes) - 1 - RETARDO_PASOS)]
            # Sensor principal -> respaldo -> orden retrasada 87 ms (estimación).
            medidas = []
            for n in sensadas:
                d = None if n in estimadas else delta_modelo(n, valores, ref, cal)
                if d is None:
                    d = np.rad2deg(q_retrasada[JOINTS.index(n)] - stand[JOINTS.index(n)])
                    estimaciones[n] = estimaciones.get(n, 0) + 1
                medidas.append(d)
            obs_q = np.deg2rad(medidas)
            w.writerow([round(time.time() - t0, 3), k, round(fase, 4), *grados, *grados_nom, *v,
                        *np.round(residual, 4)])
            espera = t0 + (k + 1) * DT - time.time()
            if espera > 0:
                time.sleep(espera)
    finally:
        os.write(fd, b"X\n")
        time.sleep(0.2)
        f.close()
        os.close(fd)
    if estimaciones:
        print("Pasos estimados con la orden por falta de sensor:", estimaciones)
    print("Registro:", salida, "| pasos:", k + 1, "| duración:", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
