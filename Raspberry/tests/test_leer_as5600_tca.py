import unittest

from Raspberry.codigo.leer_as5600_tca import (
    AS5600_ADDRESS,
    MAGNET_STATUS_REGISTER,
    RAW_ANGLE_REGISTER,
    AS5600Reader,
    SENSORS,
    decode_magnet_status,
)
from Raspberry.codigo.analizar_estabilidad_as5600 import (
    analyze_scans,
    circular_span_deg,
)


class FakeBus:
    def __init__(self, status=0x67, angle_bytes=(0x08, 0x00)):
        self.status = status
        self.angle_bytes = angle_bytes
        self.writes = []
        self.closed = False

    def write_byte(self, address, value):
        self.writes.append((address, value))

    def read_byte_data(self, address, register):
        self.last_status_read = (address, register)
        return self.status

    def read_i2c_block_data(self, address, register, length):
        self.last_angle_read = (address, register, length)
        return list(self.angle_bytes)

    def close(self):
        self.closed = True


class AS5600PassiveReaderTests(unittest.TestCase):
    def test_status_decoder_requires_detected_magnet_at_valid_strength(self):
        self.assertTrue(decode_magnet_status(0x67)["magnetically_valid"])
        self.assertFalse(decode_magnet_status(0x13)["magnetically_valid"])
        self.assertFalse(decode_magnet_status(0x37)["magnetically_valid"])
        self.assertFalse(decode_magnet_status(0x2F)["magnetically_valid"])

    def test_read_sensor_reports_angle_and_magnet_quality(self):
        reader = AS5600Reader.__new__(AS5600Reader)
        reader.bus = FakeBus(status=0x67, angle_bytes=(0x08, 0x00))
        result = reader.read_sensor(SENSORS[0])

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["raw"], 2048)
        self.assertEqual(result["angle_deg"], 180.0)
        self.assertEqual(result["magnet_status"], "0x67")
        self.assertTrue(result["magnetically_valid"])
        self.assertEqual(
            reader.bus.last_status_read,
            (AS5600_ADDRESS, MAGNET_STATUS_REGISTER),
        )
        self.assertEqual(
            reader.bus.last_angle_read,
            (AS5600_ADDRESS, RAW_ANGLE_REGISTER, 2),
        )
        self.assertEqual(reader.bus.writes, [(SENSORS[0].tca, 1), (SENSORS[0].tca, 0)])

    def test_read_sensor_preserves_invalid_magnet_state_without_pwm(self):
        reader = AS5600Reader.__new__(AS5600Reader)
        reader.bus = FakeBus(status=0x13)
        result = reader.read_sensor(SENSORS[1])

        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["magnet_detected"])
        self.assertTrue(result["magnet_low"])
        self.assertFalse(result["magnetically_valid"])
        # Solo se selecciona y deselecciona el TCA; no existe acceso al PCA9685.
        self.assertEqual(reader.bus.writes, [(SENSORS[1].tca, 2), (SENSORS[1].tca, 0)])


class AS5600StabilityAnalysisTests(unittest.TestCase):
    def test_circular_span_handles_zero_degree_crossing(self):
        self.assertAlmostEqual(circular_span_deg([359.5, 0.2, 0.8]), 1.3)

    def test_analysis_accepts_only_complete_stable_valid_window(self):
        scans = [
            {"readings": [
                {"joint": "stable", "status": "ok", "angle_deg": 359.8,
                 "magnetically_valid": True},
                {"joint": "weak", "status": "ok", "angle_deg": 10.0,
                 "magnetically_valid": False},
            ]},
            {"readings": [
                {"joint": "stable", "status": "ok", "angle_deg": 0.3,
                 "magnetically_valid": True},
                {"joint": "weak", "status": "ok", "angle_deg": 10.1,
                 "magnetically_valid": False},
            ]},
            {"readings": [
                {"joint": "stable", "status": "ok", "angle_deg": 0.7,
                 "magnetically_valid": True},
                {"joint": "weak", "status": "ok", "angle_deg": 10.2,
                 "magnetically_valid": False},
            ]},
        ]
        by_joint = {item["joint"]: item for item in analyze_scans(
            scans, min_samples=3, max_span_deg=2.0)}

        self.assertTrue(by_joint["stable"]["candidate_for_calibration_only"])
        self.assertAlmostEqual(by_joint["stable"]["circular_span_deg"], 0.9)
        self.assertFalse(by_joint["weak"]["candidate_for_calibration_only"])


if __name__ == "__main__":
    unittest.main()
