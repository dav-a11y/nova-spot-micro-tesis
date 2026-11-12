from copy import deepcopy
import json
import math

import rclpy
from builtin_interfaces.msg import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from .kinematics import (
    cartesian_crawl, cartesian_step_walk, crawl_sample_profile,
)


JOINTS = [
    'front_left_coxa_joint', 'front_left_femur_joint', 'front_left_tibia_joint',
    'front_right_coxa_joint', 'front_right_femur_joint', 'front_right_tibia_joint',
    'rear_left_coxa_joint', 'rear_left_femur_joint', 'rear_left_tibia_joint',
    'rear_right_coxa_joint', 'rear_right_femur_joint', 'rear_right_tibia_joint',
]

# Each tuple is (coxa, femur, tibia). Negative tibia angles flex the knee.
# A small coxa opening gives the provisional model a wider support polygon.
STAND = (0.10, 0.42, -0.84)
LIFT_FORWARD = (0.10, 0.34, -0.96)
PLACE_FORWARD = (0.10, 0.40, -0.86)
STANCE_MIDDLE = STAND
STANCE_BACK = (0.10, 0.44, -0.82)

# Quasi-static weight transfer.  Increasing coxa flexion on one side moves the
# trunk toward the opposite supporting side before a foot is lifted.
LEFT_LOADED = (0.03, 0.42, -0.84)
LEFT_UNLOADED = (0.17, 0.42, -0.84)
RIGHT_LOADED = (0.03, 0.42, -0.84)
RIGHT_UNLOADED = (0.17, 0.42, -0.84)


def pose(fl=STAND, fr=STAND, rl=STAND, rr=STAND):
    """Flatten four leg targets into the controller joint order."""
    return [*fl, *fr, *rl, *rr]


# Bounding gallop: rear pair compresses and extends, then the front pair catches.
REAR_COMPRESS = (0.0, 0.02, -1.35)
REAR_EXTEND = (0.0, 0.67, -0.46)
FRONT_REACH = (0.0, -0.20, -1.00)
FRONT_CATCH = (0.0, 0.48, -0.72)
GALLOP = [
    pose(fl=FRONT_CATCH, fr=FRONT_CATCH, rl=REAR_COMPRESS, rr=REAR_COMPRESS),
    pose(fl=FRONT_REACH, fr=FRONT_REACH, rl=REAR_EXTEND, rr=REAR_EXTEND),
    pose(fl=FRONT_REACH, fr=FRONT_REACH, rl=STANCE_MIDDLE, rr=STANCE_MIDDLE),
    pose(fl=FRONT_CATCH, fr=FRONT_CATCH, rl=FRONT_REACH, rr=FRONT_REACH),
    pose(fl=STANCE_MIDDLE, fr=STANCE_MIDDLE, rl=REAR_COMPRESS, rr=REAR_COMPRESS),
]


def advance_phase_deadline(previous_deadline, duration):
    """Advance from the planned deadline so callback jitter cannot accumulate."""
    return previous_deadline + rclpy.duration.Duration(seconds=duration)


def scaled_phase_duration(duration, speed_factor):
    """Return the phase duration after applying a positive speed factor."""
    duration = float(duration)
    speed_factor = float(speed_factor)
    if not math.isfinite(speed_factor) or speed_factor <= 0.0:
        raise ValueError('speed_factor debe ser finito y mayor que cero')
    return duration / speed_factor


def gait_mode_allowed(mode, enable_experimental_gallop=False):
    """Keep gallop behind an explicit simulation-only opt-in."""
    return mode != 'gallop' or bool(enable_experimental_gallop)


def expected_contact_state(mode, phase, samples, cycle_index):
    """Return the planned swing/contact state for a published gait sample."""
    legs = ('fl', 'fr', 'rl', 'rr')
    if mode not in ('crawl', 'step') or samples <= 0:
        return {
            'mode': mode, 'sample_index': phase, 'samples_per_cycle': samples,
            'cycle_index': cycle_index, 'planned_leg': None, 'swing_leg': None,
            'gait_subphase': None,
            'expected_contacts': [], 'contact_plan_available': False,
        }
    order = ('fl', 'rr', 'fr', 'rl')
    quarter = min(3, (phase * 4) // samples)
    planned_leg = order[quarter]
    if mode == 'crawl':
        samples_per_leg = samples // 4
        _, _, subphase, expects_contact = crawl_sample_profile(
            phase % samples_per_leg, samples_per_leg)
        swing_leg = None if expects_contact else planned_leg
    else:
        subphase = 'swing'
        expects_contact = False
        swing_leg = planned_leg
    return {
        'mode': mode, 'sample_index': phase, 'samples_per_cycle': samples,
        'cycle_index': cycle_index, 'planned_leg': planned_leg,
        'swing_leg': swing_leg, 'gait_subphase': subphase,
        'expected_contacts': list(legs) if expects_contact else
        [leg for leg in legs if leg != swing_leg],
        'contact_plan_available': True,
    }


class DiscreteGaitController(Node):
    """Finite-state gait sequencer that publishes one joint target per phase."""

    def __init__(self):
        super().__init__('gait_controller')
        self.declare_parameter('initial_gait', 'stand')
        self.declare_parameter('crawl_phase_duration', 0.42)
        self.declare_parameter('crawl_samples', 24)
        self.declare_parameter('crawl_step_length', 0.018)
        self.declare_parameter('crawl_step_height', 0.014)
        self.declare_parameter('crawl_lateral_shift', 0.004)
        self.declare_parameter('crawl_fore_aft_shift', 0.008)
        self.declare_parameter('crawl_front_landing_height_ratio', 2 ** -0.5)
        self.declare_parameter('crawl_rear_landing_height_ratio', 2 ** -0.5)
        self.declare_parameter('crawl_rear_liftoff_height_ratio', 2 ** -0.5)
        self.declare_parameter('crawl_rear_swing_height_scale', 1.0)
        self.declare_parameter('crawl_preload_shift_scale', 1.0)
        self.declare_parameter('step_phase_duration', 0.12)
        self.declare_parameter('step_samples', 48)
        self.declare_parameter('step_length', 0.016)
        self.declare_parameter('step_height', 0.008)
        self.declare_parameter('step_weight_shift', 0.004)
        self.declare_parameter('step_fore_aft_shift', 0.0)
        self.declare_parameter('gallop_phase_duration', 0.20)
        self.declare_parameter('speed_factor', 1.0)
        self.declare_parameter('enable_experimental_gallop', False)
        self.declare_parameter('transition_ratio', 0.80)
        self.declare_parameter('command_topic', '/nova/gait_command')
        self.declare_parameter('phase_topic', '/nova/gait_phase')
        self.declare_parameter(
            'trajectory_topic', '/joint_trajectory_controller/joint_trajectory')

        command_topic = self.get_parameter('command_topic').value
        trajectory_topic = self.get_parameter('trajectory_topic').value
        self.publisher = self.create_publisher(JointTrajectory, trajectory_topic, 10)
        self.subscription = self.create_subscription(
            String, command_topic, self.command_callback, 10)
        self.phase_publisher = self.create_publisher(
            String, self.get_parameter('phase_topic').value, 10)

        self.mode = 'stand'
        self.crawl_states = []
        self.step_states = []
        self.phase = 0
        self.cycle_index = 0
        self.next_phase_at = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.update)
        self.set_mode(str(self.get_parameter('initial_gait').value).lower())
        self.get_logger().info(
            'Control discreto listo. Comandos: stand, gateo/crawl, paso/step, '
            f'galope/gallop, stop. Factor de velocidad: '
            f'{float(self.get_parameter("speed_factor").value):.2f}x.')

    def command_callback(self, msg):
        aliases = {'gateo': 'crawl', 'paso': 'step', 'galope': 'gallop', 'parar': 'stop'}
        requested = aliases.get(msg.data.strip().lower(), msg.data.strip().lower())
        self.set_mode(requested)

    def set_mode(self, requested):
        if requested not in ('stand', 'crawl', 'step', 'gallop', 'stop'):
            self.get_logger().warning(f'Marcha desconocida: {requested}')
            return
        if not gait_mode_allowed(
                requested,
                self.get_parameter('enable_experimental_gallop').value):
            self.get_logger().warning(
                'Galope rechazado: experimento opcional deshabilitado. '
                'Solo habilitar explícitamente en simulación.')
            return
        if requested == 'crawl':
            try:
                self.crawl_states = self.build_crawl()
            except ValueError as error:
                self.get_logger().error(f'Gateo rechazado: {error}')
                self.mode = 'stand'
                self.publish_target(pose(), 0.8)
                return
        if requested == 'step':
            try:
                self.step_states = self.build_step_walk()
            except ValueError as error:
                self.get_logger().error(f'Marcha paso rechazada: {error}')
                self.mode = 'stand'
                self.publish_target(pose(), 0.8)
                return
        self.mode = requested
        self.phase = 0
        self.cycle_index = 0
        self.next_phase_at = self.get_clock().now()
        self.get_logger().info(f'Estado -> {self.mode}')
        if requested in ('stand', 'stop'):
            self.publish_target(pose(), 0.8)

    def build_crawl(self):
        samples = int(self.get_parameter('crawl_samples').value)
        step_length = float(self.get_parameter('crawl_step_length').value)
        step_height = float(self.get_parameter('crawl_step_height').value)
        lateral_shift = float(self.get_parameter('crawl_lateral_shift').value)
        fore_aft_shift = float(self.get_parameter('crawl_fore_aft_shift').value)
        front_landing = float(
            self.get_parameter('crawl_front_landing_height_ratio').value)
        rear_landing = float(
            self.get_parameter('crawl_rear_landing_height_ratio').value)
        rear_liftoff = float(
            self.get_parameter('crawl_rear_liftoff_height_ratio').value)
        rear_height_scale = float(
            self.get_parameter('crawl_rear_swing_height_scale').value)
        preload_scale = float(
            self.get_parameter('crawl_preload_shift_scale').value)
        duration = float(self.get_parameter('crawl_phase_duration').value)
        if samples < 16 or samples > 80 or samples % 4:
            raise ValueError('crawl_samples debe ser múltiplo de 4 entre 16 y 80')
        if not 0.002 <= step_length <= 0.040:
            raise ValueError('crawl_step_length debe estar entre 0,002 y 0,040 m')
        if not 0.004 <= step_height <= 0.030:
            raise ValueError('crawl_step_height debe estar entre 0,004 y 0,030 m')
        if not 0.08 <= duration <= 1.0:
            raise ValueError('crawl_phase_duration debe estar entre 0,08 y 1,0 s')
        states = cartesian_crawl(
            STAND, samples=samples, step_length=step_length,
            step_height=step_height, lateral_shift=lateral_shift,
            fore_aft_shift=fore_aft_shift,
            front_landing_height_ratio=front_landing,
            rear_landing_height_ratio=rear_landing,
            rear_liftoff_height_ratio=rear_liftoff,
            rear_swing_height_scale=rear_height_scale,
            preload_shift_scale=preload_scale)
        self.get_logger().info(
            f'Gateo cartesiano: {samples} muestras, paso={step_length:.3f} m, '
            f'elevación={step_height:.3f} m, transferencia lateral='
            f'{lateral_shift:.3f} m, longitudinal={fore_aft_shift:.3f} m, '
            f'aterrizaje delantero={front_landing:.2f}, '
            f'trasero={rear_landing:.2f}, '
            f'despegue trasero={rear_liftoff:.2f}, '
            f'escala trasera={rear_height_scale:.2f}, '
            f'escala precarga={preload_scale:.2f}, '
            f'ciclo={samples * scaled_phase_duration(duration, self.get_parameter("speed_factor").value):.2f} s')
        return states

    def build_step_walk(self):
        samples = int(self.get_parameter('step_samples').value)
        step_length = float(self.get_parameter('step_length').value)
        step_height = float(self.get_parameter('step_height').value)
        weight_shift = float(self.get_parameter('step_weight_shift').value)
        fore_aft_shift = float(self.get_parameter('step_fore_aft_shift').value)
        duration = float(self.get_parameter('step_phase_duration').value)
        if not 0.08 <= duration <= 1.0:
            raise ValueError('step_phase_duration debe estar entre 0,08 y 1,0 s')
        states = cartesian_step_walk(
            STAND, samples=samples, step_length=step_length,
            step_height=step_height, weight_shift=weight_shift,
            fore_aft_shift=fore_aft_shift)
        self.get_logger().info(
            f'Marcha paso cartesiana: {samples} muestras, paso={step_length:.3f} m, '
            f'elevación={step_height:.3f} m, transferencia={weight_shift:.3f} m, '
            f'transferencia longitudinal={fore_aft_shift:.3f} m, '
            f'ciclo={samples * scaled_phase_duration(duration, self.get_parameter("speed_factor").value):.2f} s')
        return states

    def update(self):
        if self.mode in ('stand', 'stop') or self.get_clock().now() < self.next_phase_at:
            return

        if self.mode == 'crawl':
            states = self.crawl_states
            duration = scaled_phase_duration(
                self.get_parameter('crawl_phase_duration').value,
                self.get_parameter('speed_factor').value)
        elif self.mode == 'step':
            states = self.step_states
            duration = scaled_phase_duration(
                self.get_parameter('step_phase_duration').value,
                self.get_parameter('speed_factor').value)
        else:
            states = GALLOP
            duration = scaled_phase_duration(
                self.get_parameter('gallop_phase_duration').value,
                self.get_parameter('speed_factor').value)

        current_phase = self.phase
        self.publish_target(states[current_phase], duration)
        phase_state = expected_contact_state(
            self.mode, current_phase, len(states), self.cycle_index)
        self.phase_publisher.publish(String(
            data=json.dumps(phase_state, separators=(',', ':'))))
        self.phase = (current_phase + 1) % len(states)
        if self.phase == 0:
            self.cycle_index += 1
        self.next_phase_at = advance_phase_deadline(self.next_phase_at, duration)

    def publish_target(self, positions, phase_duration):
        ratio = float(self.get_parameter('transition_ratio').value)
        seconds = max(0.05, phase_duration * ratio)
        whole = int(seconds)
        point = JointTrajectoryPoint()
        point.positions = deepcopy(positions)
        point.velocities = [0.0] * len(JOINTS)
        point.time_from_start = Duration(
            sec=whole, nanosec=int((seconds - whole) * 1_000_000_000))
        trajectory = JointTrajectory()
        trajectory.joint_names = JOINTS
        trajectory.points = [point]
        self.publisher.publish(trajectory)


def main(args=None):
    rclpy.init(args=args)
    node = DiscreteGaitController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
