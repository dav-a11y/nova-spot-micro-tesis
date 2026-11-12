#!/usr/bin/env python3
"""Train residual PPO directly in the Nova MuJoCo model.

The environment uses the same measured geometry and residual contract as the
ROS controller: 27 observations, 12 bounded joint corrections, a maximum
correction of 0.08 rad and a maximum change of 0.02 rad per control step.
This is simulation training only; it never opens the Raspberry interface.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "nova_gait_controller"))
from nova_gait_controller.kinematics import (  # noqa: E402
    BODY_HEIGHT,
    BODY_LENGTH,
    BODY_WIDTH,
    COXA_LENGTH,
    FEMUR_LENGTH,
    HIP_SPACING_X,
    HIP_SPACING_Y,
    TIBIA_LENGTH,
    cartesian_crawl,
    cartesian_step_walk,
)


JOINTS = (
    "front_left_coxa_joint", "front_left_femur_joint", "front_left_tibia_joint",
    "front_right_coxa_joint", "front_right_femur_joint", "front_right_tibia_joint",
    "rear_left_coxa_joint", "rear_left_femur_joint", "rear_left_tibia_joint",
    "rear_right_coxa_joint", "rear_right_femur_joint", "rear_right_tibia_joint",
)
IMU_GYRO = "imu_gyro"
IMU_ACCEL = "imu_accel"
CONTACTS = ("front_left_contact", "front_right_contact",
            "rear_left_contact", "rear_right_contact")
STAND = (0.10, 0.42, -0.84)


def _quat_roll_pitch(quat):
    w, x, y, z = np.asarray(quat, dtype=float)
    sin_roll = 2.0 * (w * x + y * z)
    cos_roll = 1.0 - 2.0 * (x * x + y * y)
    sin_pitch = 2.0 * (w * y - z * x)
    roll = np.arctan2(sin_roll, cos_roll)
    pitch = np.arcsin(np.clip(sin_pitch, -1.0, 1.0))
    return float(roll), float(pitch)


def _quat_yaw(quat):
    w, x, y, z = np.asarray(quat, dtype=float)
    return float(np.arctan2(2.0 * (w * z + x * y),
                            1.0 - 2.0 * (y * y + z * z)))


class NovaMujocoResidualEnv(gym.Env):
    """MuJoCo environment for residual correction of a nominal gait."""

    metadata = {"render_modes": []}

    def __init__(self, model_path, gait="crawl", episode_cycles=5,
                 control_dt=0.02, seed=11, domain_randomization=True,
                 attitude_weight=8.0, stability_observation=False,
                 lateral_weight=8.0, yaw_weight=8.0):
        super().__init__()
        self.model_path = str(model_path)
        self.gait = gait
        self.samples = 24 if gait == "crawl" else 48
        self.sample_duration = 0.18 if gait == "crawl" else 0.12
        self.episode_cycles = int(episode_cycles)
        self.control_dt = float(control_dt)
        self.sim_substeps = max(1, round(self.control_dt / 0.002))
        self.steps_per_sample = max(1, round(self.sample_duration / self.control_dt))
        self.cycle_steps = self.samples * self.steps_per_sample
        self.ramp_steps = max(1, round(1.0 / self.control_dt))
        self.rng = np.random.default_rng(seed)
        self.domain_randomization = bool(domain_randomization)
        self.attitude_weight = float(attitude_weight)
        self.stability_observation = bool(stability_observation)
        self.lateral_weight = float(lateral_weight)
        self.yaw_weight = float(yaw_weight)
        self.contact_obs_slice = slice(12, 16) if self.stability_observation else slice(9, 13)
        self.model = mujoco.MjModel.from_xml_path(self.model_path)
        self.data = mujoco.MjData(self.model)
        self.base_body = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_BODY, "base_link")
        self.qpos_ids = np.asarray([
            self.model.jnt_qposadr[mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, name)]
            for name in JOINTS
        ], dtype=int)
        self.qvel_ids = np.asarray([
            self.model.jnt_dofadr[mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_JOINT, name)]
            for name in JOINTS
        ], dtype=int)
        self.sensor_slices = {
            name: self._sensor_slice(name)
            for name in (IMU_GYRO, IMU_ACCEL, *CONTACTS)
        }
        if gait == "crawl":
            self.nominal = np.asarray(cartesian_crawl(
                STAND, samples=24, step_length=0.018, step_height=0.014,
                lateral_shift=0.004, fore_aft_shift=0.008,
                preload_shift_scale=2.0), dtype=float)
        elif gait == "step":
            self.nominal = np.asarray(cartesian_step_walk(
                STAND, samples=48, step_length=0.016, step_height=0.008,
                weight_shift=0.004), dtype=float)
        else:
            raise ValueError("gait debe ser crawl o step")
        self.max_steps = self.ramp_steps + self.episode_cycles * self.cycle_steps
        self.action_space = spaces.Box(-1.0, 1.0, shape=(12,), dtype=np.float32)
        observation_dim = 30 if self.stability_observation else 27
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(observation_dim,), dtype=np.float32)
        self.previous_residual = np.zeros(12, dtype=float)
        self.last_x = 0.0
        self.step_count = 0
        self.nominal_index = 0
        self.initial_friction = self.model.geom_friction.copy()
        self.initial_damping = self.model.dof_damping.copy()

    def _sensor_slice(self, name):
        sensor_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_SENSOR, name)
        if sensor_id < 0:
            raise ValueError(f"sensor MuJoCo inexistente: {name}")
        start = int(self.model.sensor_adr[sensor_id])
        size = int(self.model.sensor_dim[sensor_id])
        return slice(start, start + size)

    def _randomize_domain(self):
        self.model.geom_friction[:] = self.initial_friction
        self.model.dof_damping[:] = self.initial_damping
        if not self.domain_randomization:
            return
        ground = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
        if ground >= 0:
            self.model.geom_friction[ground, 0] = self.rng.uniform(0.65, 1.05)
        for dof in self.qvel_ids:
            self.model.dof_damping[dof] *= self.rng.uniform(0.85, 1.15)

    def _reset_state(self):
        key_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_KEY, "stand")
        if key_id >= 0:
            self.data.qpos[:] = self.model.key_qpos[key_id]
            self.data.qvel[:] = self.model.key_qvel[key_id]
            self.data.ctrl[:] = self.model.key_ctrl[key_id]
        else:
            self.data.qpos[:] = 0.0
            self.data.qvel[:] = 0.0
            self.data.ctrl[:] = 0.0
        mujoco.mj_forward(self.model, self.data)
        # The XML keyframe has the stand pose in qpos but zeroes in ctrl. Hold
        # the measured starting pose before beginning the commanded ramp.
        self.data.ctrl[:] = self.data.qpos[self.qpos_ids]
        self.previous_q = self.data.qpos[self.qpos_ids].copy()
        self.previous_ctrl = self.data.ctrl.copy()

    def _observation(self):
        roll, pitch = _quat_roll_pitch(self.data.xquat[self.base_body])
        height = float(self.data.xpos[self.base_body, 2])
        accel = self.data.sensordata[self.sensor_slices[IMU_ACCEL]]
        gyro = self.data.sensordata[self.sensor_slices[IMU_GYRO]]
        contacts = np.asarray([
            float(self.data.sensordata[self.sensor_slices[name]].max() > 1e-5)
            for name in CONTACTS
        ])
        body_state = [roll, pitch, height - 0.235]
        if self.stability_observation:
            yaw_error = float(np.arctan2(
                np.sin(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw),
                np.cos(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw)))
            lateral_error = float(
                self.data.xpos[self.base_body, 1] - self.initial_y)
            body_state.extend((lateral_error, np.sin(yaw_error), np.cos(yaw_error)))
        q = self.data.qpos[self.qpos_ids]
        phase = (max(0, self.step_count - self.ramp_steps) % self.cycle_steps
                 / self.cycle_steps)
        obs = np.r_[body_state, accel, gyro,
                    contacts, q, np.sin(2.0 * np.pi * phase),
                    np.cos(2.0 * np.pi * phase)]
        return np.asarray(obs, dtype=np.float32)

    def _reward(self, residual, before_x):
        obs = self._observation()
        roll, pitch, height_error = map(float, obs[:3])
        dx = float(self.data.xpos[self.base_body, 0] - before_x)
        q_error = self.data.qpos[self.qpos_ids] - self.current_nominal
        contact_bonus = float(np.sum(obs[self.contact_obs_slice])) * 0.003
        reward = float(
            1.0 + 18.0 * dx - self.attitude_weight * roll**2
            - self.attitude_weight * pitch**2
            - 25.0 * height_error**2 - 0.25 * np.dot(q_error, q_error)
            - 0.04 * np.dot(residual, residual) + contact_bonus)
        if self.stability_observation:
            yaw_error = float(np.arctan2(obs[4], obs[5]))
            lateral_error = float(obs[3])
            reward -= self.lateral_weight * lateral_error**2
            reward -= self.yaw_weight * yaw_error**2
        return reward

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._randomize_domain()
        self._reset_state()
        self.initial_y = float(self.data.xpos[self.base_body, 1])
        self.initial_yaw = _quat_yaw(self.data.xquat[self.base_body])
        self.initial_ctrl = self.data.ctrl.copy()
        self.previous_residual[:] = 0.0
        self.last_x = float(self.data.xpos[self.base_body, 0])
        self.step_count = 0
        self.nominal_index = 0
        self.current_nominal = self.nominal[0].copy()
        return self._observation(), {
            "geometry": {
                "hip_spacing_x_m": HIP_SPACING_X,
                "hip_spacing_y_m": HIP_SPACING_Y,
            "body_height_m": BODY_HEIGHT,
                "coxa_m": COXA_LENGTH,
                "femur_m": FEMUR_LENGTH,
                "tibia_m": TIBIA_LENGTH,
            }
        }

    def step(self, action):
        action = np.asarray(action, dtype=float)
        if action.shape != (12,):
            raise ValueError("la acción debe tener 12 componentes")
        target = np.clip(action, -1.0, 1.0) * 0.08
        delta = np.clip(target - self.previous_residual, -0.02, 0.02)
        residual = self.previous_residual + delta
        self.previous_residual = residual
        ramp_active = self.step_count < self.ramp_steps
        if ramp_active:
            ramp_fraction = (self.step_count + 1) / self.ramp_steps
            self.nominal_index = 0
            nominal = (self.initial_ctrl + ramp_fraction
                       * (self.nominal[0] - self.initial_ctrl))
        else:
            sample_phase = ((self.step_count - self.ramp_steps)
                            % self.cycle_steps) / self.steps_per_sample
            self.nominal_index = int(np.floor(sample_phase)) % self.samples
            fraction = sample_phase - np.floor(sample_phase)
            next_index = (self.nominal_index + 1) % self.samples
            nominal = ((1.0 - fraction) * self.nominal[self.nominal_index]
                       + fraction * self.nominal[next_index])
        self.current_nominal = nominal
        before_x = float(self.data.xpos[self.base_body, 0])
        self.data.ctrl[:] = np.clip(
            nominal + residual, self.model.actuator_ctrlrange[:, 0],
            self.model.actuator_ctrlrange[:, 1])
        for _ in range(self.sim_substeps):
            mujoco.mj_step(self.model, self.data)
        reward = self._reward(residual, before_x)
        self.step_count += 1
        obs = self._observation()
        roll, pitch = map(float, obs[:2])
        height = float(self.data.xpos[self.base_body, 2])
        q_now = self.data.qpos[self.qpos_ids].copy()
        command = self.data.ctrl.copy()
        joint_step = float(np.max(np.abs(q_now - self.previous_q)))
        tracking_error = float(np.max(np.abs(q_now - command)))
        command_step = float(np.max(np.abs(command - self.previous_ctrl)))
        self.previous_q = q_now
        self.previous_ctrl = command
        terminated = bool(
            not np.isfinite(obs).all() or height < 0.12 or height > 0.40
            or abs(roll) > 0.60 or abs(pitch) > 0.60)
        truncated = self.step_count >= self.max_steps
        self.last_x = float(self.data.xpos[self.base_body, 0])
        return obs, reward, terminated, truncated, {
            "roll": roll, "pitch": pitch, "height": height,
            "x": self.last_x, "residual_norm": float(np.linalg.norm(residual)),
            "joint_step_rad": joint_step,
            "joint_tracking_error_rad": tracking_error,
            "command_step_rad": command_step,
            "lateral_error_m": float(self.data.xpos[self.base_body, 1]
                                      - self.initial_y),
            "yaw_error_rad": float(np.arctan2(
                np.sin(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw),
                np.cos(_quat_yaw(self.data.xquat[self.base_body]) - self.initial_yaw))),
            "ramp_active": ramp_active,
        }


class MetricsCallback(BaseCallback):
    """Keep a small JSONL trace without coupling training to ROS bags."""

    def __init__(self, output, verbose=0):
        super().__init__(verbose)
        self.output = Path(output)
        self.handle = None

    def _on_training_start(self):
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.output.open("w", encoding="utf-8")

    def _on_step(self):
        if self.handle is not None and self.num_timesteps % 1000 == 0:
            rewards = [float(info["r"]) for info in self.model.ep_info_buffer
                       if "r" in info]
            self.handle.write(json.dumps({
                "timesteps": self.num_timesteps,
                "mean_reward": float(np.mean(rewards)) if rewards else None,
            }) + "\n")
            self.handle.flush()
        return True

    def _on_training_end(self):
        if self.handle is not None:
            self.handle.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gait", choices=("crawl", "step"), default="crawl")
    parser.add_argument("--timesteps", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--episode-cycles", type=int, default=5)
    parser.add_argument("--attitude-weight", type=float, default=8.0,
                        help="peso común de penalización de roll y pitch")
    parser.add_argument("--stability-observation", action="store_true",
                        help="añade deriva lateral y rumbo a la observación (30D)")
    parser.add_argument("--lateral-weight", type=float, default=8.0)
    parser.add_argument("--yaw-weight", type=float, default=8.0)
    parser.add_argument("--output", type=Path, default=ROOT /
                        "Experimentos/entrenamiento_ppo_mujoco_20260924")
    parser.add_argument("--no-domain-randomization", action="store_true")
    args = parser.parse_args()
    model_path = ROOT / "src" / "nova_sm3_description" / "mujoco" / "nova_sm3.xml"
    output = args.output / f"{args.gait}_semilla_{args.seed}"
    output.mkdir(parents=True, exist_ok=True)
    env = NovaMujocoResidualEnv(
        model_path, gait=args.gait, episode_cycles=args.episode_cycles,
        seed=args.seed, domain_randomization=not args.no_domain_randomization,
        attitude_weight=args.attitude_weight,
        stability_observation=args.stability_observation,
        lateral_weight=args.lateral_weight, yaw_weight=args.yaw_weight)
    algorithm = PPO(
        "MlpPolicy", env, seed=args.seed, verbose=1, n_steps=1024,
        batch_size=256, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95,
        clip_range=0.2,
    )
    algorithm.learn(
        total_timesteps=args.timesteps,
        callback=MetricsCallback(output / "training_trace.jsonl"),
    )
    algorithm.save(output / "policy")
    metadata = {
        "simulator": "mujoco",
        "gait": args.gait,
        "seed": args.seed,
        "timesteps": args.timesteps,
        "episode_cycles": args.episode_cycles,
        "ramp_duration_s": env.ramp_steps * env.control_dt,
        "control_dt_s": env.control_dt,
        "gait_samples": env.samples,
        "sample_duration_s": env.sample_duration,
        "steps_per_sample": env.steps_per_sample,
        "cycle_duration_s": env.cycle_steps * env.control_dt,
        "nominal_interpolation": "linear_at_control_rate",
        "dimensions_m": {
            "hip_spacing_x": HIP_SPACING_X, "hip_spacing_y": HIP_SPACING_Y,
            "body_length": BODY_LENGTH, "body_width": BODY_WIDTH,
            "body_height": BODY_HEIGHT, "coxa": COXA_LENGTH,
            "femur": FEMUR_LENGTH, "tibia": TIBIA_LENGTH,
        },
        "domain_randomization": not args.no_domain_randomization,
        "observation_dim": env.observation_space.shape[0],
        "action_dim": 12,
        "residual_limit_rad": 0.08,
        "max_action_step_rad": 0.02,
        "attitude_weight": args.attitude_weight,
        "stability_observation": args.stability_observation,
        "lateral_weight": args.lateral_weight,
        "yaw_weight": args.yaw_weight,
        "hardware_transfer": False,
    }
    (output / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Política MuJoCo guardada en {output / 'policy.zip'}")


if __name__ == "__main__":
    main()
