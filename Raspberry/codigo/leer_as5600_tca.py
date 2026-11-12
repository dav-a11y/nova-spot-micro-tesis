#!/usr/bin/env python3
"""Lee AS5600 a través de dos TCA9548A desde la Raspberry Pi.

Este programa es exclusivamente de adquisición: solo escribe el registro de
selección de cada TCA y lee ``RAW_ANGLE`` de los AS5600. No importa el módulo
del PCA9685, no modifica OE y no genera PWM para los servos.

Antes de usar sus ángulos como posición articular deben medirse, para cada
articulación, el cero mecánico, sentido, recorrido útil y holgura. El valor
reportado aquí es el ángulo absoluto del imán (0--360 grados), no radianes ni
un ángulo calibrado del modelo Nova.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


TCA_1 = 0x70
TCA_2 = 0x71
AS5600_ADDRESS = 0x36
MAGNET_STATUS_REGISTER = 0x0B
RAW_ANGLE_REGISTER = 0x0C


@dataclass(frozen=True)
class Sensor:
    """Ubicación I2C y articulación confirmada, si existe."""

    tca: int
    channel: int
    label: str
    joint: Optional[str]


# Mapa confirmado físicamente por el operador el 28 de septiembre de 2026.
# Los canales omitidos (0x70: 6--7; 0x71: 2 y 7) no tienen AS5600 conectado.
SENSORS = (
    Sensor(TCA_1, 0, "tibia 4", "rear_left_tibia_joint"),
    Sensor(TCA_1, 1, "femur 4", "rear_left_femur_joint"),
    Sensor(TCA_1, 2, "coxa 4", "rear_left_coxa_joint"),
    Sensor(TCA_1, 3, "tibia 3", "rear_right_tibia_joint"),
    Sensor(TCA_1, 4, "femur 3", "rear_right_femur_joint"),
    Sensor(TCA_1, 5, "coxa 3", "rear_right_coxa_joint"),
    Sensor(TCA_2, 0, "tibia 1", "front_right_tibia_joint"),
    Sensor(TCA_2, 1, "femur 1", "front_right_femur_joint"),
    Sensor(TCA_2, 3, "coxa 1", "front_right_coxa_joint"),
    Sensor(TCA_2, 4, "tibia 2", "front_left_tibia_joint"),
    Sensor(TCA_2, 5, "femur 2", "front_left_femur_joint"),
    Sensor(TCA_2, 6, "coxa 2", "front_left_coxa_joint"),
)


def decode_magnet_status(status: int) -> dict:
    """Decodifica el registro STATUS del AS5600 sin inferir posición articular.

    ``MD`` indica detección de imán; ``ML`` y ``MH`` indican, respectivamente,
    campo demasiado débil o fuerte. Una lectura angular solo se marca como
    magnéticamente válida cuando MD=1, ML=0 y MH=0. Esta condición no sustituye
    la calibración mecánica ni valida la estabilidad de la señal.
    """
    status = int(status) & 0xFF
    magnet_detected = bool((status >> 5) & 1)
    magnet_low = bool((status >> 4) & 1)
    magnet_high = bool((status >> 3) & 1)
    return {
        "magnet_status": f"0x{status:02X}",
        "magnet_detected": magnet_detected,
        "magnet_low": magnet_low,
        "magnet_high": magnet_high,
        "magnetically_valid": magnet_detected and not magnet_low and not magnet_high,
    }


class AS5600Reader:
    def __init__(self, bus_number: int):
        try:
            from smbus2 import SMBus
        except ImportError:
            try:
                # Ubuntu publica esta misma API con el nombre ``smbus`` en el
                # paquete del sistema python3-smbus.
                from smbus import SMBus
            except ImportError as error:
                raise RuntimeError(
                    "Falta acceso Python a I2C. En la Raspberry: "
                    "sudo apt install python3-smbus") from error
        self.bus = SMBus(bus_number)

    def select_channel(self, tca: int, channel: int) -> None:
        if not 0 <= channel <= 7:
            raise ValueError(f"Canal TCA inválido: {channel}")
        self.bus.write_byte(tca, 1 << channel)

    def disable_tca(self, tca: int) -> None:
        self.bus.write_byte(tca, 0)

    def disable_all(self) -> None:
        for tca in (TCA_1, TCA_2):
            try:
                self.disable_tca(tca)
            except OSError:
                # No oculta la lectura que falló; solo evita sustituirla por un
                # segundo error durante la limpieza.
                pass

    def read_sensor(self, sensor: Sensor) -> dict:
        result = {
            "tca": f"0x{sensor.tca:02X}",
            "channel": sensor.channel,
            "label": sensor.label,
            "joint": sensor.joint,
            "raw": None,
            "angle_deg": None,
            "status": "error",
        }
        try:
            self.select_channel(sensor.tca, sensor.channel)
            magnet_status = self.bus.read_byte_data(
                AS5600_ADDRESS, MAGNET_STATUS_REGISTER)
            data = self.bus.read_i2c_block_data(
                AS5600_ADDRESS, RAW_ANGLE_REGISTER, 2)
            if len(data) != 2:
                raise OSError(f"AS5600 devolvió {len(data)} bytes")
            raw = ((int(data[0]) << 8) | int(data[1])) & 0x0FFF
            result.update(raw=raw, angle_deg=raw * 360.0 / 4096.0,
                          status="ok", **decode_magnet_status(magnet_status))
        except (OSError, ValueError) as error:
            result["error"] = str(error)
        finally:
            try:
                self.disable_tca(sensor.tca)
            except OSError as error:
                result.setdefault("disable_error", str(error))
        return result

    def close(self) -> None:
        self.disable_all()
        self.bus.close()


def print_scan(scan: dict) -> None:
    print(f"barrido={scan['scan']} t_ns={scan['timestamp_ns']}")
    for item in scan["readings"]:
        name = item["joint"] or item["label"]
        if item["status"] == "ok":
            quality = "válido" if item["magnetically_valid"] else "NO válido"
            print(f"  {item['tca']} ch{item['channel']}: {name}: "
                  f"raw={item['raw']:4d}, {item['angle_deg']:7.3f} deg; "
                  f"imán={item['magnet_status']} ({quality})")
        else:
            print(f"  {item['tca']} ch{item['channel']}: {name}: "
                  f"ERROR: {item.get('error', 'desconocido')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bus", type=int, default=1,
                        help="bus Linux I2C; la Raspberry usa 1 por defecto")
    parser.add_argument("--once", action="store_true",
                        help="hace exactamente un barrido y termina")
    parser.add_argument("--period", type=float, default=0.10,
                        help="periodo objetivo entre barridos en segundos")
    parser.add_argument("--jsonl", type=Path,
                        help="guarda los barridos JSON Lines en esta ruta")
    args = parser.parse_args()
    if not args.once and args.period <= 0.0:
        parser.error("--period debe ser positivo")

    reader = AS5600Reader(args.bus)
    output = (args.jsonl.open("a", encoding="utf-8") if args.jsonl else None)
    scan_index = 0
    try:
        while True:
            started = time.monotonic()
            scan_index += 1
            scan = {
                "timestamp_ns": time.time_ns(),
                "scan": scan_index,
                "bus": args.bus,
                "as5600_address": f"0x{AS5600_ADDRESS:02X}",
                "readings": [reader.read_sensor(sensor) for sensor in SENSORS],
            }
            print_scan(scan)
            if output:
                output.write(json.dumps(scan) + "\n")
                output.flush()
            if args.once:
                return 0
            time.sleep(max(0.0, args.period - (time.monotonic() - started)))
    except KeyboardInterrupt:
        print("Lectura detenida por el operador.")
        return 0
    finally:
        if output:
            output.close()
        reader.close()


if __name__ == "__main__":
    sys.exit(main())
