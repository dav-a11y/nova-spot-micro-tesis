#!/usr/bin/env python3
"""Development-only inference-time residual scaling ablation for step PPO."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "Experimentos"),
                str(ROOT / "src" / "nova_gait_controller")]
from campana_ppo_completa import _episode_metrics  # noqa: E402
from entrenar_ppo_mujoco import NovaMujocoResidualEnv  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402


class ScaledPolicy:
    def __init__(self, policy, scale):
        self.policy = policy
        self.scale = float(scale)

    def predict(self, observation, deterministic=True):
        action, state = self.policy.predict(
            observation, deterministic=deterministic)
        return np.asarray(action) * self.scale, state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--scales", type=float, nargs="+",
                        default=(0.0, 0.25, 0.5, 0.75, 1.0))
    args = parser.parse_args()
    output = args.output or args.campaign / "residual_scale_ablation.csv"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing result: {output}")
    model_path = ROOT / "src/nova_sm3_description/mujoco/nova_sm3.xml"
    rows = []
    for policy_seed in (11, 23, 37, 53, 71):
        policy_path = (args.campaign / "mujoco" /
                       f"step_semilla_{policy_seed}" / "policy.zip")
        policy = PPO.load(policy_path)
        for scale in args.scales:
            scaled = ScaledPolicy(policy, scale)
            env = NovaMujocoResidualEnv(
                model_path, gait="step", episode_cycles=20, seed=11,
                domain_randomization=False, attitude_weight=32.0,
                stability_observation=True, lateral_weight=64.0,
                yaw_weight=32.0)
            try:
                for eval_seed in (801, 802, 803, 804, 805):
                    metrics = _episode_metrics(env, scaled, eval_seed)
                    rows.append({
                        "policy_seed": policy_seed,
                        "residual_scale": scale,
                        "evaluation_seed": eval_seed,
                        **metrics,
                    })
            finally:
                env.close()
            print(f"done policy={policy_seed} scale={scale:g}", flush=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {output} ({len(rows)} episodes)")


if __name__ == "__main__":
    main()
