#!/usr/bin/env python3
"""Evalúa registros pasivos JSONL del lector AS5600.

No abre I2C, no importa PCA9685 y no emite PWM. Clasifica cada señal como
candidata *solo* para el siguiente paso de calibración si, durante una ventana
pasiva, todas las lecturas son válidas magnéticamente y su dispersión circular
no excede el umbral. No calcula ángulos articulares ni autoriza movimiento.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def circular_span_deg(angles: list[float]) -> float:
    """Menor arco circular que contiene los ángulos, en grados."""
    if len(angles) < 2:
        return 0.0
    values = sorted(float(angle) % 360.0 for angle in angles)
    gaps = [right - left for left, right in zip(values, values[1:])]
    gaps.append(values[0] + 360.0 - values[-1])
    return 360.0 - max(gaps)


def analyze_scans(scans: list[dict], min_samples: int, max_span_deg: float) -> list[dict]:
    """Resume una ventana de barridos del formato producido por el lector."""
    readings_by_joint: dict[str, list[dict]] = defaultdict(list)
    for scan in scans:
        for reading in scan.get("readings", []):
            joint = reading.get("joint") or reading.get("label")
            if joint:
                readings_by_joint[joint].append(reading)

    report = []
    for joint in sorted(readings_by_joint):
        readings = readings_by_joint[joint]
        successful = [item for item in readings if item.get("status") == "ok"]
        angles = [item["angle_deg"] for item in successful
                  if item.get("angle_deg") is not None]
        magnetic_valid = sum(bool(item.get("magnetically_valid")) for item in successful)
        errors = len(readings) - len(successful)
        span = circular_span_deg(angles)
        candidate = (
            len(readings) >= min_samples
            and errors == 0
            and magnetic_valid == len(readings)
            and len(angles) == len(readings)
            and span <= max_span_deg
        )
        report.append({
            "joint": joint,
            "samples": len(readings),
            "read_errors": errors,
            "magnetically_valid_samples": magnetic_valid,
            "circular_span_deg": round(span, 6),
            "candidate_for_calibration_only": candidate,
            "reason": (
                "ventana pasiva estable; requiere aún cero, sentido, límites y "
                "prueba controlada" if candidate else
                "no usar para control: faltan muestras, hay error I2C/estado magnético "
                "inválido o la dispersión supera el umbral"
            ),
        })
    return report


def load_jsonl(path: Path) -> list[dict]:
    scans = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                scans.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"JSON inválido en línea {line_number}: {error}") from error
    return scans


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="salida JSONL del lector pasivo")
    parser.add_argument("--min-samples", type=int, default=60)
    parser.add_argument("--max-span-deg", type=float, default=2.0)
    parser.add_argument("--output", type=Path, help="guarda el informe JSON")
    args = parser.parse_args()
    if args.min_samples < 1:
        parser.error("--min-samples debe ser al menos 1")
    if args.max_span_deg < 0:
        parser.error("--max-span-deg no puede ser negativo")

    report = analyze_scans(load_jsonl(args.jsonl), args.min_samples, args.max_span_deg)
    result = {
        "source": str(args.jsonl),
        "min_samples": args.min_samples,
        "max_span_deg": args.max_span_deg,
        "joints": report,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
