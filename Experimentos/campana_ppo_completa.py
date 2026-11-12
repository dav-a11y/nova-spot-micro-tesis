#!/usr/bin/env python3
"""Orquestador reproducible para el reentrenamiento PPO de las dos marchas.

La campaña separa entrenamiento y evaluación. Las políticas se entrenan con
las mismas dimensiones medidas del prototipo y el mismo contrato residual
(27 observaciones, 12 acciones, +/-0.08 rad y +/-0.02 rad por paso). La
evaluación de MuJoCo compara cada política contra la marcha nominal, sin
randomización, para evitar seleccionar una política solo por su recompensa de
entrenamiento. Gazebo se ejecuta como proceso ROS 2 independiente por corrida.

No existe ninguna ruta hacia Raspberry Pi o servos en este script.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEEDS = (11, 23, 37, 53, 71)
GAITS = ("crawl", "step")


def _run(command, env=None):
    print("+", " ".join(str(part) for part in command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def train_one(simulator, gait, seed, timesteps, episode_cycles, output):
    script = ROOT / "Experimentos" / f"entrenar_ppo_{simulator}.py"
    command = [
        sys.executable, str(script), "--gait", gait,
        "--timesteps", str(timesteps), "--seed", str(seed),
        "--episode-cycles", str(episode_cycles), "--output", str(output),
    ]
    env = os.environ.copy()
    if simulator == "mujoco":
        extra = "/tmp/nova_rl_deps:src/nova_gait_controller"
    else:
        extra = "/tmp/nova_rl_deps:"
    env["PYTHONPATH"] = extra + env.get("PYTHONPATH", "")
    _run(command, env=env)


def _episode_metrics(env, model=None, seed=100):
    obs, _ = env.reset(seed=seed)
    initial_x = float(env.data.xpos[env.base_body, 0])
    total_reward = 0.0
    max_tilt = 0.0
    rolls = []
    pitches = []
    heights = []
    lateral_positions = []
    contact_states = []
    joint_steps = []
    joint_tracking_errors = []
    joint_tracking_error_vectors = []
    command_steps = []
    terminated = False
    truncated = False
    steps = 0
    initial_y = float(env.data.xpos[env.base_body, 1])
    while not (terminated or truncated):
        if model is None:
            action = np.zeros(12, dtype=np.float32)
        else:
            action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += float(reward)
        max_tilt = max(max_tilt, abs(float(info["roll"])),
                       abs(float(info["pitch"])))
        rolls.append(float(info["roll"]))
        pitches.append(float(info["pitch"]))
        heights.append(float(info["height"]))
        lateral_positions.append(float(env.data.xpos[env.base_body, 1]))
        contact_states.append(np.asarray(obs[env.contact_obs_slice], dtype=float))
        joint_steps.append(float(info["joint_step_rad"]))
        joint_tracking_errors.append(float(info["joint_tracking_error_rad"]))
        joint_tracking_error_vectors.append(
            np.asarray(env.data.qpos[env.qpos_ids] - env.data.ctrl, dtype=float))
        command_steps.append(float(info["command_step_rad"]))
        steps += 1
    final_x = float(env.data.xpos[env.base_body, 0])
    final_y = float(env.data.xpos[env.base_body, 1])
    return {
        "return": total_reward,
        "steps": steps,
        "advance_m": final_x - initial_x,
        "max_tilt_rad": max_tilt,
        "roll_rms_rad": float(np.sqrt(np.mean(np.square(rolls)))),
        "pitch_rms_rad": float(np.sqrt(np.mean(np.square(pitches)))),
        "max_abs_roll_rad": max(abs(value) for value in rolls),
        "max_abs_pitch_rad": max(abs(value) for value in pitches),
        "min_height_m": min(heights),
        "max_height_m": max(heights),
        "foot_contact_fraction": float(np.mean(contact_states)),
        "lateral_drift_m": final_y - initial_y,
        "lateral_excursion_m": max(lateral_positions) - min(lateral_positions),
        "max_joint_step_rad": max(joint_steps),
        "max_joint_tracking_error_rad": max(joint_tracking_errors),
        "joint_tracking_error_rms_rad": float(np.sqrt(
            np.mean(np.square(joint_tracking_error_vectors)))),
        "max_command_step_rad": max(command_steps),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
    }


def evaluate_mujoco(output, eval_episodes, *, seeds=SEEDS, gaits=GAITS,
                    write_csv=True, episode_seeds=None, episode_cycles=5,
                    environment_kwargs=None,
                    evaluation_domain_randomization=False,
                    csv_name="mujoco_evaluation.csv"):
    """Evaluate every MuJoCo policy and write paired nominal comparisons."""
    sys.path.insert(0, str(ROOT / "Experimentos"))
    sys.path.insert(0, str(ROOT / "src" / "nova_gait_controller"))
    from entrenar_ppo_mujoco import NovaMujocoResidualEnv  # noqa: E402
    from stable_baselines3 import PPO  # noqa: E402

    model_path = ROOT / "src" / "nova_sm3_description" / "mujoco" / "nova_sm3.xml"
    episode_seeds = (tuple(range(100, 100 + eval_episodes))
                     if episode_seeds is None else tuple(episode_seeds))
    if len(episode_seeds) != eval_episodes:
        raise ValueError("episode_seeds debe tener eval_episodes elementos")
    environment_kwargs = {} if environment_kwargs is None else dict(environment_kwargs)
    rows = []
    for gait in gaits:
        for seed in seeds:
            policy_path = output / "mujoco" / f"{gait}_semilla_{seed}" / "policy.zip"
            if not policy_path.exists():
                continue
            model = PPO.load(policy_path)
            for condition in ("nominal", "ppo"):
                env = NovaMujocoResidualEnv(
                    model_path, gait=gait, episode_cycles=episode_cycles, seed=100,
                    domain_randomization=evaluation_domain_randomization,
                    **environment_kwargs)
                try:
                    metrics = []
                    for episode_seed in episode_seeds:
                        metrics.append(_episode_metrics(
                            env, model if condition == "ppo" else None,
                            seed=episode_seed))
                finally:
                    env.close()
                aggregate = {
                    "simulator": "mujoco", "gait": gait, "seed": seed,
                    "condition": condition, "episodes": eval_episodes,
                }
                for key in ("return", "advance_m"):
                    aggregate[key] = float(np.mean([item[key] for item in metrics]))
                for key in ("roll_rms_rad", "pitch_rms_rad",
                            "foot_contact_fraction", "lateral_drift_m"):
                    aggregate[key] = float(np.mean([item[key] for item in metrics]))
                for key in ("max_abs_roll_rad", "max_abs_pitch_rad",
                            "max_tilt_rad", "max_height_m",
                            "max_joint_step_rad",
                            "max_joint_tracking_error_rad",
                            "max_command_step_rad"):
                    aggregate[key] = float(max(item[key] for item in metrics))
                aggregate["joint_tracking_error_rms_rad"] = float(np.mean(
                    [item["joint_tracking_error_rms_rad"] for item in metrics]))
                aggregate["min_height_m"] = float(
                    min(item["min_height_m"] for item in metrics))
                aggregate["max_lateral_excursion_m"] = float(
                    max(item["lateral_excursion_m"] for item in metrics))
                aggregate["steps"] = int(np.mean([item["steps"] for item in metrics]))
                aggregate["early_terminations"] = int(
                    sum(item["terminated"] for item in metrics))
                rows.append(aggregate)
    path = output / csv_name
    if write_csv:
        _write_csv(path, rows)
    return rows


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulators", nargs="+", choices=("mujoco", "gazebo"),
                        default=("mujoco", "gazebo"))
    parser.add_argument("--gaits", nargs="+", choices=GAITS, default=GAITS)
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--mujoco-timesteps", type=int, default=50000)
    parser.add_argument("--gazebo-timesteps", type=int, default=4096)
    parser.add_argument("--episode-cycles", type=int, default=5)
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-seeds", nargs="+", type=int, default=None)
    parser.add_argument("--output", type=Path, default=ROOT /
                        "Experimentos/reentrenamiento_ppo_completo_20260924")
    parser.add_argument("--skip-training", action="store_true")
    parser.add_argument("--skip-evaluation", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = {
        "date": "2026-09-24", "simulators": args.simulators,
        "gaits": args.gaits, "seeds": args.seeds,
        "mujoco_timesteps": args.mujoco_timesteps,
        "gazebo_timesteps": args.gazebo_timesteps,
        "episode_cycles": args.episode_cycles,
        "evaluation_episodes": args.eval_episodes,
        "hardware_transfer": False,
        "dimensions_m": {
            "coxa": 0.0381, "femur": 0.10795, "tibia": 0.13589,
            "hip_spacing_x": 0.180, "hip_spacing_y": 0.120,
            "body_length": 0.230, "body_width": 0.120,
            "body_height": 0.075,
        },
    }
    (args.output / "campaign_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    if not args.skip_training:
        for simulator in args.simulators:
            timesteps = (args.mujoco_timesteps if simulator == "mujoco"
                         else args.gazebo_timesteps)
            for gait in args.gaits:
                for seed in args.seeds:
                    train_one(simulator, gait, seed, timesteps,
                              args.episode_cycles, args.output / simulator)

    if "mujoco" in args.simulators and not args.skip_evaluation:
        rows = evaluate_mujoco(
            args.output, args.eval_episodes, seeds=args.seeds,
            episode_seeds=args.eval_seeds,
            episode_cycles=args.episode_cycles)
        print(f"Evaluación MuJoCo escrita: {len(rows)} filas", flush=True)


if __name__ == "__main__":
    main()
