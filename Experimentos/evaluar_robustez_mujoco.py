#!/usr/bin/env python3
"""Run paired randomized-domain development evaluation for an existing campaign."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Experimentos"))
from campana_ppo_completa import evaluate_mujoco  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output-name", default="mujoco_evaluation_randomized.csv")
    args = parser.parse_args()
    output_path = args.campaign / args.output_name
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite existing evaluation: {output_path}")
    manifest = json.loads(
        (args.campaign / "campaign_manifest.json").read_text(encoding="utf-8"))
    evaluate_mujoco(
        args.campaign, 5,
        seeds=tuple(manifest["training_seeds"]), gaits=("step",),
        episode_seeds=(801, 802, 803, 804, 805), episode_cycles=20,
        environment_kwargs=manifest["environment"],
        evaluation_domain_randomization=True,
        csv_name=args.output_name)
    print(f"Randomized paired evaluation saved to {output_path}")


if __name__ == "__main__":
    main()
