#!/usr/bin/env python3
"""Port Python/Thonny del preset de avance ``'f'`` de Nova SM3 v4.2.

Fuente: Nova-SM3_mega-v4.2.ino, Chris Locke (cguweb-com).
Adapta el orden de sus patas al mapa PCA9685 confirmado en este prototipo.

NOTA: el sketch de origen usa el PCA9685 a 60 Hz y posiciones en cuentas.
Este port convierte esas cuentas a microsegundos a 60 Hz y usa la calibración
local. No es un port del firmware completo; reproduce el preset ``f`` de
avance (spd=5, y_dir=10, move_steps=25, peso=1.20) como tres fases
RF+LR / RR+LF / home. La interpolación temporal es una adaptación Python.

Antes de activar PWM pide confirmación por teclado y comprueba que los
objetivos estén dentro de los servoLimit publicados por Nova v4.2. Las
lecturas AS5600 se muestran como telemetría y no bloquean el movimiento.
"""

from __future__ import annotations

import math
import sys
import time


# Parámetros del preset serial 'f' (march_forward) del Nova SM3 v4.2.
MOVE_STEPS = 25
STEP_WEIGHT_FACTOR = 1.20
Y_DIR = 10
SOURCE_SPEED = 5
PCA_FREQUENCY_HZ = 60.0
PHASE_DURATION_S = 1.5
CONTROL_PERIOD_S = 0.02

# Convierte índices y home positions del NovaSM3_mega-v4.2/NovaServos.h
# a los canales que confirmó el operador para este prototipo.
LEGS = {
    "RF": {"coxa": ("front_right_coxa_joint", 0, 352),
           "femur": ("front_right_femur_joint", 4, 280),
           "tibia": ("front_right_tibia_joint", 8, 510)},
    "LF": {"coxa": ("front_left_coxa_joint", 1, 364),
           "femur": ("front_left_femur_joint", 5, 442),
           "tibia": ("front_left_tibia_joint", 9, 225)},
    "RR": {"coxa": ("rear_right_coxa_joint", 2, 367),
           "femur": ("rear_right_femur_joint", 6, 331),
           "tibia": ("rear_right_tibia_joint", 10, 423)},
    "LR": {"coxa": ("rear_left_coxa_joint", 3, 364),
           "femur": ("rear_left_femur_joint", 7, 351),
           "tibia": ("rear_left_tibia_joint", 11, 213)},
}

# servoLimit de Nova-SM3_mega-v4.2/NovaServos.h, expresados en cuentas del
# PCA9685 original. Algunos límites aparecen invertidos para servos montados
# en espejo; se ordenan al validarlos. Son límites software de ese montaje.
SOURCE_LIMITS = {
    ("RF", "coxa"): (314, 434), ("RF", "femur"): (185, 515),
    ("RF", "tibia"): (365, 607),
    ("LF", "coxa"): (402, 282), ("LF", "femur"): (537, 207),
    ("LF", "tibia"): (370, 128),
    ("RR", "coxa"): (329, 449), ("RR", "femur"): (236, 566),
    ("RR", "tibia"): (278, 520),
    ("LR", "coxa"): (402, 282), ("LR", "femur"): (446, 116),
    ("LR", "tibia"): (358, 116),
}

SENSORS = (
    (0x70, 0, "tibia4"), (0x70, 1, "femur4"), (0x70, 2, "coxa4"),
    (0x70, 3, "tibia3"), (0x70, 4, "femur3"), (0x70, 5, "coxa3"),
    (0x71, 0, "tibia1"), (0x71, 1, "femur1"), (0x71, 3, "coxa1"),
    (0x71, 4, "tibia2"), (0x71, 5, "femur2"), (0x71, 6, "coxa2"),
)


def ticks_to_us(ticks: float) -> float:
    """Cuentas PWM del sketch a pulso equivalente, con frecuencia original 60 Hz."""
    return float(ticks) * 1_000_000.0 / (PCA_FREQUENCY_HZ * 4096.0)


def build_gait_frames():
    """Tres fases del preset Nova march_forward, en cuentas PCA originales."""
    home = {}
    for leg_name, joints in LEGS.items():
        for joint, (_config_name, _channel, ticks) in joints.items():
            home[(leg_name, joint)] = float(ticks)

    first = dict(home)
    second = dict(home)
    step = MOVE_STEPS
    weight = STEP_WEIGHT_FACTOR
    femur_delta = step * 0.700
    # step_march añade 0.015 por unidad de y_dir al factor tibia.
    tibia_delta = step * (1.300 + Y_DIR * 0.015)

    # step_march() original: RF+LR primero; signos opuestos por montaje.
    first[("RF", "femur")] -= femur_delta
    first[("RF", "tibia")] += tibia_delta
    first[("LR", "femur")] += femur_delta * weight
    first[("LR", "tibia")] -= tibia_delta * weight

    # Después RR+LF, mientras RF+LR vuelven a home.
    second[("RR", "femur")] -= femur_delta * weight
    second[("RR", "tibia")] += tibia_delta * weight
    second[("LF", "femur")] += femur_delta
    second[("LF", "tibia")] -= tibia_delta

    return (("fase 1: RF + LR", first),
            ("fase 2: RR + LF; RF + LR a home", second),
            ("fase 3: todas a home", home))


def validate_source_limits():
    """Comprueba todos los frames frente a los servoLimit del sketch Nova."""
    for phase_name, frame in build_gait_frames():
        for leg_name, leg in LEGS.items():
            for joint in leg:
                source_ticks = frame[(leg_name, joint)]
                source_min, source_max = sorted(SOURCE_LIMITS[(leg_name, joint)])
                if not source_min <= source_ticks <= source_max:
                    raise RuntimeError(
                        f"{phase_name}: {leg_name}/{joint} excede servoLimit Nova "
                        f"({source_min}..{source_max} cuentas).")


def read_sensor_snapshot():
    """Lee todos los AS5600 una vez; estado inválido se reporta, no bloquea."""
    from smbus import SMBus

    bus = SMBus(1)
    result = []
    try:
        for tca, channel, name in SENSORS:
            try:
                bus.write_byte(tca, 1 << channel)
                status = bus.read_byte_data(0x36, 0x0B)
                data = bus.read_i2c_block_data(0x36, 0x0C, 2)
                raw = ((int(data[0]) << 8) | int(data[1])) & 0x0FFF
                result.append((name, raw * 360.0 / 4096.0, status))
            except OSError as error:
                result.append((name, None, str(error)))
            finally:
                try:
                    bus.write_byte(tca, 0)
                except OSError:
                    pass
    finally:
        for tca in (0x70, 0x71):
            try:
                bus.write_byte(tca, 0)
            except OSError:
                pass
        bus.close()
    return result


def targets_to_channels(frame):
    targets = {}
    for leg_name, leg in LEGS.items():
        for joint, (_name, channel, _ticks) in leg.items():
            targets[channel] = ticks_to_us(frame[(leg_name, joint)])
    return targets


def move_interpolated(controller, start, end, seconds):
    count = max(1, math.ceil(seconds / CONTROL_PERIOD_S))
    for i in range(1, count + 1):
        fraction = i / count
        for channel, target in end.items():
            current = start[channel]
            pulse = current + (target - current) * fraction
            controller.set_pulse_us(channel, pulse)
        time.sleep(CONTROL_PERIOD_S)


def run_one_cycle():
    validate_source_limits()
    print("Límites de software Nova v4.2 cargados desde servoLimit.")
    print("El inicio ordena HOME a los 12 servos y luego ejecuta un ciclo.")
    print("Lectura inicial AS5600 (solo observación):")
    for name, angle, status in read_sensor_snapshot():
        if angle is None:
            print(f"  {name}: ERROR {status}")
        else:
            md, ml, mh = (status >> 5) & 1, (status >> 4) & 1, (status >> 3) & 1
            print(f"  {name}: {angle:.2f} deg status=0x{status:02X} MD={md} ML={ml} MH={mh}")
    if input("Robot suspendido y despejado; escribe MOVER para ejecutar un ciclo: ").strip() != "MOVER":
        print("Cancelado; sin activar el PCA9685.")
        return

    from pca9685_seguro import PCA9685Seguro

    controller = PCA9685Seguro(bus_number=1, address=0x40,
                               frequency_hz=PCA_FREQUENCY_HZ, oe_bcm_gpio=17)
    try:
        for channel in range(16):
            controller.prepare_channel_off(channel)
        controller.arm()
        frames = [(name, targets_to_channels(frame))
                  for name, frame in build_gait_frames()]
        previous = targets_to_channels(build_gait_frames()[-1][1])
        for channel, pulse in previous.items():
            controller.set_pulse_us(channel, pulse)
        time.sleep(0.5)
        for phase_name, target in frames:
            print(phase_name, flush=True)
            move_interpolated(controller, previous, target, PHASE_DURATION_S)
            for name, angle, status in read_sensor_snapshot():
                if angle is None:
                    print(f"  sensor {name}: ERROR {status}", flush=True)
                else:
                    md = (status >> 5) & 1
                    ml = (status >> 4) & 1
                    mh = (status >> 3) & 1
                    print(f"  sensor {name}: {angle:.2f} deg "
                          f"0x{status:02X} MD={md} ML={ml} MH={mh}", flush=True)
            previous = target
    finally:
        controller.close()
        print("PWM deshabilitado al terminar.", flush=True)


if __name__ == "__main__":
    try:
        run_one_cycle()
    except Exception as error:
        print("MARCHA ABORTADA:", error, file=sys.stderr, flush=True)
