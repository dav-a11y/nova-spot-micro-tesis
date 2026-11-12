"""Filtro final de referencias articulares con realimentación AS5600.

Este módulo no mueve hardware: recibe las lecturas ya adquiridas y decide si
una referencia articular puede pasar. Está pensado para ejecutarse dentro de la
Raspberry antes de que la interfaz PCA9685 convierta radianes a PWM.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from time import monotonic
from typing import Mapping


class FeedbackRejected(RuntimeError):
    """Una referencia o una medición no cumple la puerta de seguridad."""


def normalize_degrees(delta_deg: float) -> float:
    """Lleva una diferencia angular a [-180, 180), incluido cruce 0/360."""
    return (float(delta_deg) + 180.0) % 360.0 - 180.0


@dataclass(frozen=True)
class FeedbackCalibration:
    encoder_zero_deg: float
    encoder_direction: int
    joint_min_rad: float
    joint_max_rad: float
    max_velocity_rad_s: float
    max_tracking_error_rad: float

    @classmethod
    def from_mapping(cls, values: Mapping) -> "FeedbackCalibration":
        required = (
            "encoder_zero_deg", "encoder_direction", "joint_min_rad",
            "joint_max_rad", "max_velocity_rad_s", "max_tracking_error_rad",
        )
        missing = [name for name in required if values.get(name) is None]
        if missing:
            raise ValueError("faltan parámetros de realimentación: " + ", ".join(missing))
        result = cls(*(float(values[name]) if name != "encoder_direction"
                       else int(values[name]) for name in required))
        if result.encoder_direction not in (-1, 1):
            raise ValueError("encoder_direction debe ser -1 o 1")
        if not result.joint_min_rad < result.joint_max_rad:
            raise ValueError("el límite mínimo debe ser menor que el máximo")
        if result.max_velocity_rad_s <= 0.0 or result.max_tracking_error_rad <= 0.0:
            raise ValueError("velocidad y error máximo deben ser positivos")
        return result

    def angle_from_encoder(self, absolute_deg: float) -> float:
        return self.encoder_direction * normalize_degrees(
            float(absolute_deg) - self.encoder_zero_deg) * pi / 180.0


class FeedbackControlFilter:
    """Limita referencias a velocidad segura y vigila seguimiento medido."""

    def __init__(self, calibrations: Mapping[str, FeedbackCalibration],
                 feedback_timeout_s: float = 0.15):
        if not calibrations:
            raise ValueError("se requiere al menos una articulación")
        if feedback_timeout_s <= 0.0:
            raise ValueError("feedback_timeout_s debe ser positivo")
        self.calibrations = dict(calibrations)
        self.feedback_timeout_s = float(feedback_timeout_s)
        self._measurements: dict[str, float] = {}
        self._measurement_time: float | None = None
        self._commanded: dict[str, float] = {}
        self._last_command_time: float | None = None

    @classmethod
    def from_config(cls, config: Mapping) -> "FeedbackControlFilter":
        entries = config.get("joint_feedback", {})
        calibrations = {
            joint: FeedbackCalibration.from_mapping(values)
            for joint, values in entries.items()
        }
        return cls(calibrations, config.get("feedback_timeout_s", 0.15))

    @staticmethod
    def config_complete(config: Mapping, expected_joints: set[str]) -> bool:
        try:
            controller = FeedbackControlFilter.from_config(config)
        except (TypeError, ValueError):
            return False
        return set(controller.calibrations) == set(expected_joints)

    def update_measurements(self, readings: list[Mapping], now: float | None = None) -> None:
        """Acepta una ventana completa de lecturas AS5600 del lector pasivo."""
        now = monotonic() if now is None else float(now)
        found: dict[str, float] = {}
        for reading in readings:
            joint = reading.get("joint")
            if joint not in self.calibrations:
                continue
            if reading.get("status") != "ok" or not reading.get("magnetically_valid"):
                raise FeedbackRejected(f"{joint}: AS5600 no válido")
            angle_deg = reading.get("angle_deg")
            if angle_deg is None or not isfinite(float(angle_deg)):
                raise FeedbackRejected(f"{joint}: ángulo AS5600 inválido")
            angle = self.calibrations[joint].angle_from_encoder(float(angle_deg))
            calibration = self.calibrations[joint]
            if not calibration.joint_min_rad <= angle <= calibration.joint_max_rad:
                raise FeedbackRejected(f"{joint}: medición fuera de límites")
            found[joint] = angle
        missing = set(self.calibrations) - set(found)
        if missing:
            raise FeedbackRejected("faltan lecturas: " + ", ".join(sorted(missing)))
        self._measurements = found
        self._measurement_time = now

    def limit_references(self, references: Mapping[str, float],
                         now: float | None = None) -> dict[str, float]:
        """Devuelve objetivos limitados; rechaza ante sensor vencido o error alto."""
        now = monotonic() if now is None else float(now)
        if self._measurement_time is None or now - self._measurement_time > self.feedback_timeout_s:
            raise FeedbackRejected("telemetría AS5600 vencida")
        if set(references) != set(self.calibrations):
            raise FeedbackRejected("la referencia no contiene exactamente las 12 articulaciones")
        dt = 0.0 if self._last_command_time is None else max(0.0, now - self._last_command_time)
        output = {}
        for joint, target in references.items():
            target = float(target)
            calibration = self.calibrations[joint]
            measured = self._measurements[joint]
            if not isfinite(target) or not calibration.joint_min_rad <= target <= calibration.joint_max_rad:
                raise FeedbackRejected(f"{joint}: referencia fuera de límites")
            previous = self._commanded.get(joint, measured)
            max_step = calibration.max_velocity_rad_s * dt
            limited = max(previous - max_step, min(previous + max_step, target))
            if abs(limited - measured) > calibration.max_tracking_error_rad:
                raise FeedbackRejected(f"{joint}: error de seguimiento excesivo")
            output[joint] = limited
        self._commanded = output
        self._last_command_time = now
        return output
