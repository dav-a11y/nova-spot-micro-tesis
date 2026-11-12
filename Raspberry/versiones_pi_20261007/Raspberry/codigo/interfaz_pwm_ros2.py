"""Prototipo de trayectoria posicional; incompatible con servos continuos.

Arranca siempre desarmado. Solo acepta habilitación si `hardware_ready` es true
y las doce articulaciones están marcadas como calibradas. Un watchdog apaga OE
si dejan de llegar referencias.
"""

from pathlib import Path
from time import monotonic

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from trajectory_msgs.msg import JointTrajectory
import yaml

from pca9685_seguro import PCA9685Seguro


CONFIG = Path(__file__).parents[1] / "configuracion" / "servos.yaml"


class InterfazPWM(Node):
    def __init__(self):
        super().__init__("nova_pca9685_hardware")
        self.config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        self.servos = self.config["servos"]
        self.driver = PCA9685Seguro(
            self.config["i2c_bus"], self.config["pca9685_address"],
            self.config["pwm_frequency_hz"], self.config["oe_bcm_gpio"])
        self.last_reference = monotonic()
        self.enabled = False
        self.create_subscription(
            JointTrajectory, "/joint_trajectory_controller/joint_trajectory",
            self.trajectory_callback, 10)
        self.create_subscription(
            Bool, "/nova/hardware/enable", self.enable_callback, 10)
        self.create_timer(0.05, self.watchdog)
        self.get_logger().warning("PWM iniciado DESHABILITADO; OE permanece alto")

    def calibration_complete(self):
        if self.config.get("actuator_type") != "positional":
            return False
        limits = self.config.get("motion_limits", {})
        measured_limits = (
            len(limits) == 12
            and all(item.get("max_velocity_rad_s") is not None
                    and float(item["max_velocity_rad_s"]) > 0.0
                    and item.get("torque_limit_nm") is not None
                    and float(item["torque_limit_nm"]) > 0.0
                    for item in limits.values()))
        return (bool(self.config.get("hardware_ready", False))
                and len(self.servos) == 12
                and all(item.get("calibrated", False)
                        for item in self.servos.values())
                and (measured_limits or not self.config.get(
                    "require_measured_motion_limits", True)))

    def enable_callback(self, message):
        if not message.data:
            self.disable("orden de deshabilitación")
            return
        if not self.calibration_complete():
            self.disable("calibración incompleta; habilitación rechazada")
            return
        self.driver.arm()
        self.enabled = True
        self.last_reference = monotonic()
        self.get_logger().warning("PWM HABILITADO")

    def trajectory_callback(self, message):
        if not self.enabled or not message.points:
            return
        positions = message.points[-1].positions
        if len(message.joint_names) != len(positions):
            self.disable("trayectoria inválida")
            return
        try:
            for joint, angle in zip(message.joint_names, positions):
                calibration = self.servos[joint]
                pulse = self.driver.angle_to_pulse(angle, calibration)
                self.driver.set_pulse_us(calibration["channel"], pulse)
        except (KeyError, ValueError, RuntimeError) as error:
            self.disable(f"referencia rechazada: {error}")
            return
        self.last_reference = monotonic()

    def watchdog(self):
        if (self.enabled and monotonic() - self.last_reference
                > float(self.config["watchdog_timeout_s"])):
            self.disable("watchdog: se perdieron referencias")

    def disable(self, reason):
        self.driver.all_off()
        self.enabled = False
        self.get_logger().warning(f"PWM DESHABILITADO: {reason}")

    def destroy_node(self):
        self.driver.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = InterfazPWM()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
