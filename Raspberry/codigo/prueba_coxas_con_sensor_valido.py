#!/usr/bin/env python3
"""Prueba breve de coxa 2 con AS5600 que detecta el imán correctamente.

Prueba únicamente Pata 2/CH1, secuencia 1500 -> 1510 -> 1500 us. El estado
magnético se comprueba antes y durante la prueba. Son referencias PWM, no topes
calibrados.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from leer_as5600_tca import AS5600_ADDRESS, RAW_ANGLE_REGISTER, AS5600Reader
from pca9685_seguro import PCA9685Seguro


TESTS = (
    (2, "coxa 2", 1, 0x71, 6),
)


def read_sensor(reader, tca, channel):
    reader.select_channel(tca, channel)
    try:
        status = reader.bus.read_byte_data(AS5600_ADDRESS, 0x0B)
        data = reader.bus.read_i2c_block_data(
            AS5600_ADDRESS, RAW_ANGLE_REGISTER, 2)
        if len(data) != 2:
            raise OSError(f"AS5600 devolvió {len(data)} bytes")
        raw = ((int(data[0]) << 8) | int(data[1])) & 0x0FFF
        return raw, raw * 360.0 / 4096.0, status
    finally:
        reader.disable_tca(tca)


def magnetic_ok(status):
    detected = (status >> 5) & 1
    weak = (status >> 4) & 1
    strong = (status >> 3) & 1
    return bool(detected and not weak and not strong)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--hold", type=float, default=1.0)
    parser.add_argument("--sample-period", type=float, default=0.2)
    args = parser.parse_args()
    if not 0.2 <= args.hold <= 2.0:
        parser.error("--hold debe estar entre 0.2 y 2.0 s")
    if not 0.05 <= args.sample_period <= 0.5:
        parser.error("--sample-period debe estar entre 0.05 y 0.5 s")

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    reader = AS5600Reader(1)
    controller = None
    try:
        for leg, joint, servo, tca, sensor_channel in TESTS:
            raw, angle, status = read_sensor(reader, tca, sensor_channel)
            if not magnetic_ok(status):
                print(f"ABORTADO antes de PWM: pata {leg} {joint}, "
                      f"AS5600 status 0x{status:02X} no válido",
                      file=sys.stderr, flush=True)
                return 2
            print(f"Pata {leg} {joint} CH{servo}: {angle:.3f} deg, "
                  f"AS5600 {tca:#04x}/ch{sensor_channel}, "
                  f"status=0x{status:02X} válido",
                  file=sys.stderr, flush=True)
        if input("Robot suspendido, parada a mano. Escriba MOVER: ").strip() != "MOVER":
            print("Cancelado sin habilitar PWM.", file=sys.stderr)
            return 0

        controller = PCA9685Seguro(
            bus_number=1, address=0x40, frequency_hz=50, oe_bcm_gpio=17)
        for channel in range(16):
            controller.prepare_channel_off(channel)

        phases = (("referencia", 1500), ("paso_mas_10us", 1510),
                  ("retorno_referencia", 1500))
        with args.csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(("timestamp_ns", "pata", "articulacion",
                             "canal_pca", "tca", "canal_tca", "fase",
                             "pulso_us", "raw", "angulo_absoluto_deg",
                             "status_hex", "magnet_detected", "magnet_low",
                             "magnet_high", "lectura_valida"))
            controller.arm()
            for leg, joint, servo, tca, sensor_channel in TESTS:
                for phase, pulse in phases:
                    controller.set_pulse_us(servo, pulse)
                    deadline = time.monotonic() + args.hold
                    while time.monotonic() < deadline:
                        raw, angle, status = read_sensor(reader, tca, sensor_channel)
                        md, ml, mh = (status >> 5) & 1, (status >> 4) & 1, (status >> 3) & 1
                        if not magnetic_ok(status):
                            raise RuntimeError(
                                f"Pata {leg}: estado magnético inválido 0x{status:02X}")
                        writer.writerow((time.time_ns(), leg, joint, servo,
                                         f"0x{tca:02X}", sensor_channel, phase,
                                         pulse, raw, f"{angle:.4f}",
                                         f"0x{status:02X}", md, ml, mh, 1))
                        output.flush()
                        print(f"P{leg} {joint} {phase} {pulse} us: "
                              f"{angle:.3f} deg", file=sys.stderr, flush=True)
                        time.sleep(args.sample_period)
                controller.set_channel_off(servo)
            print("Pruebas terminadas; apagando PWM.", file=sys.stderr)
    finally:
        if controller is not None:
            controller.close()
        reader.close()
        print("Limpieza completada.", file=sys.stderr, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
