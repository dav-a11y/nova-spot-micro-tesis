#!/usr/bin/env python3
"""Prueba breve y registrada de un único servo: fémur 1, CH4.

La referencia de 1500 us es provisional, no un cero angular calibrado. Solo
activa CH4; todos los demás canales permanecen en FULL_OFF. El recorrido de
prueba es 1500 -> 1510 -> 1500 us y las salidas se apagan al terminar.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

from leer_as5600_tca import AS5600_ADDRESS, RAW_ANGLE_REGISTER
from pca9685_seguro import PCA9685Seguro


PCA_CHANNEL = 4
TCA_ADDRESS = 0x71
TCA_CHANNEL = 1
SENSOR_LABEL = "femur 1"


def read_sensor(reader):
    reader.select_channel(TCA_ADDRESS, TCA_CHANNEL)
    try:
        status = reader.bus.read_byte_data(AS5600_ADDRESS, 0x0B)
        data = reader.bus.read_i2c_block_data(
            AS5600_ADDRESS, RAW_ANGLE_REGISTER, 2)
        if len(data) != 2:
            raise OSError(f"AS5600 devolvió {len(data)} bytes")
        raw = ((int(data[0]) << 8) | int(data[1])) & 0x0FFF
        return raw, raw * 360.0 / 4096.0, status
    finally:
        reader.disable_tca(TCA_ADDRESS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True,
                        help="ruta de salida CSV")
    parser.add_argument("--hold", type=float, default=1.0,
                        help="segundos por nivel PWM (0.2..2.0)")
    parser.add_argument("--sample-period", type=float, default=0.1,
                        help="periodo de lectura, en segundos")
    args = parser.parse_args()
    if not 0.2 <= args.hold <= 2.0:
        parser.error("--hold debe estar entre 0.2 y 2.0 s")
    if not 0.05 <= args.sample_period <= 0.5:
        parser.error("--sample-period debe estar entre 0.05 y 0.5 s")

    from leer_as5600_tca import AS5600Reader

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    reader = AS5600Reader(1)
    controller = None
    try:
        baseline = read_sensor(reader)
        print(f"Fémur 1 CH4; AS5600 0x71/ch1; baseline="
              f"{baseline[1]:.3f} deg; MD={(baseline[2] >> 5) & 1}; "
              f"ML={(baseline[2] >> 4) & 1}; MH={(baseline[2] >> 3) & 1}",
              file=sys.stderr, flush=True)
        if input("Robot suspendido, parada a mano. Escriba MOVER: ").strip() != "MOVER":
            print("Cancelado sin habilitar PWM.", file=sys.stderr)
            return 0

        controller = PCA9685Seguro(
            bus_number=1, address=0x40, frequency_hz=50, oe_bcm_gpio=17)
        for channel in range(16):
            controller.prepare_channel_off(channel)
        controller.prepare_pulse_us(PCA_CHANNEL, 1500)

        phases = (("referencia", 1500), ("paso_mas_10us", 1510),
                  ("retorno_referencia", 1500))
        with args.csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(("timestamp_ns", "articulacion", "canal_pca",
                             "tca", "canal_tca", "fase", "pulso_us",
                             "raw", "angulo_absoluto_deg", "status_hex",
                             "magnet_detected", "magnet_low", "magnet_high"))
            controller.arm()
            for phase, pulse in phases:
                controller.set_pulse_us(PCA_CHANNEL, pulse)
                deadline = time.monotonic() + args.hold
                while time.monotonic() < deadline:
                    timestamp_ns = time.time_ns()
                    raw, angle, status = read_sensor(reader)
                    writer.writerow((timestamp_ns, SENSOR_LABEL, PCA_CHANNEL,
                                     "0x71", TCA_CHANNEL, phase, pulse, raw,
                                     f"{angle:.4f}", f"0x{status:02X}",
                                     (status >> 5) & 1, (status >> 4) & 1,
                                     (status >> 3) & 1))
                    output.flush()
                    print(f"{phase} {pulse} us: {angle:.3f} deg "
                          f"(raw {raw}, status 0x{status:02X})",
                          file=sys.stderr, flush=True)
                    time.sleep(args.sample_period)
            print("Secuencia terminada; apagando PWM.", file=sys.stderr)
    finally:
        if controller is not None:
            controller.close()
        reader.close()
        print("Limpieza completada.", file=sys.stderr, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
