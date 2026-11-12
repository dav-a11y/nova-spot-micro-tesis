import unittest

from Raspberry.codigo.filtro_control_realimentado import (
    FeedbackCalibration,
    FeedbackControlFilter,
    FeedbackRejected,
    normalize_degrees,
)


CALIBRATION = FeedbackCalibration(
    encoder_zero_deg=0.0,
    encoder_direction=1,
    joint_min_rad=-1.0,
    joint_max_rad=1.0,
    max_velocity_rad_s=0.5,
    max_tracking_error_rad=0.2,
)


def reading(angle_deg=0.0, valid=True):
    return {"joint": "joint", "status": "ok", "angle_deg": angle_deg,
            "magnetically_valid": valid}


class FeedbackControlFilterTests(unittest.TestCase):
    def test_encoder_angle_normalizes_zero_crossing(self):
        self.assertEqual(normalize_degrees(359.0), -1.0)
        self.assertAlmostEqual(CALIBRATION.angle_from_encoder(359.0), -0.0174532925)

    def test_reference_is_limited_from_measured_initial_position(self):
        controller = FeedbackControlFilter({"joint": CALIBRATION})
        controller.update_measurements([reading()], now=10.0)
        first = controller.limit_references({"joint": 0.8}, now=10.0)
        second = controller.limit_references({"joint": 0.8}, now=10.1)
        self.assertEqual(first["joint"], 0.0)
        self.assertAlmostEqual(second["joint"], 0.05)

    def test_invalid_sensor_and_expired_feedback_are_rejected(self):
        controller = FeedbackControlFilter({"joint": CALIBRATION}, feedback_timeout_s=0.1)
        with self.assertRaises(FeedbackRejected):
            controller.update_measurements([reading(valid=False)], now=1.0)
        controller.update_measurements([reading()], now=1.0)
        with self.assertRaises(FeedbackRejected):
            controller.limit_references({"joint": 0.0}, now=1.2)

    def test_tracking_error_rejects_stuck_joint(self):
        controller = FeedbackControlFilter({"joint": CALIBRATION})
        controller.update_measurements([reading()], now=0.0)
        controller.limit_references({"joint": 0.1}, now=0.0)
        controller.update_measurements([reading()], now=1.0)
        with self.assertRaises(FeedbackRejected):
            controller.limit_references({"joint": 0.5}, now=1.0)


if __name__ == "__main__":
    unittest.main()
