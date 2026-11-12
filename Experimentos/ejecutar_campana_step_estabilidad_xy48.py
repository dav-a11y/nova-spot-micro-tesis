#!/usr/bin/env python3
"""Train/evaluate step PPO against the 48-waypoint continuous reference."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Experimentos/campana_step_estabilidad_xy48_w32_l64_20260929"
SEEDS = (11, 23, 37, 53, 71)
DEV_EVAL_SEEDS = (801, 802, 803, 804, 805)
TIMESTEPS = 200_000
ENVIRONMENT_KWARGS = {
    "attitude_weight": 32.0,
    "stability_observation": True,
    "lateral_weight": 64.0,
    "yaw_weight": 32.0,
}


def save_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_checksums() -> None:
    rows = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{digest}  {path.relative_to(OUT).as_posix()}")
    (OUT / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing campaign: {OUT}")
    OUT.mkdir(parents=True)
    (OUT / "mujoco").mkdir()
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "development_only_lateral_stability_with_smoothed_step_reference",
        "gait": "step",
        "training_seeds": SEEDS,
        "timesteps_requested": TIMESTEPS,
        "episode_cycles_training": 5,
        "ramp_duration_s": 1.0,
        "control_dt_s": 0.02,
        "gait_samples": 48,
        "sample_duration_s": 0.12,
        "steps_per_sample": 6,
        "cycle_duration_s": 5.76,
        "nominal_interpolation": "linear_at_control_rate",
        "reference_max_waypoint_jump_rad": 0.049114793385375166,
        "training_domain_randomization": True,
        "environment": ENVIRONMENT_KWARGS,
        "development_evaluation_seeds": DEV_EVAL_SEEDS,
        "evaluation_episodes": 5,
        "evaluation_cycles": 20,
        "evaluation_domain_randomization": False,
        "reserved_final_evaluation_seeds": (101, 202, 303, 404, 505),
        "provisional_targets": {
            "waypoint_jump_rad_max": 0.05,
            "roll_pitch_rms_deg_max": 5.0,
            "roll_pitch_abs_max_deg": 15.0,
            "body_height_m": [0.16, 0.32],
            "joint_tracking_error_rms_rad_max": 0.05,
            "joint_tracking_error_abs_rad_max": 0.15,
            "source": "Documentacion/FICHA_APROBACION_PROTOCOLO.md",
            "approval_status": "unsigned_provisional",
        },
        "hardware_transfer": False,
    }
    save_json(OUT / "campaign_manifest.json", manifest)
    status = {"state": "running", "completed_seeds": [], "current_seed": None}
    save_json(OUT / "campaign_status.json", status)

    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src/nova_gait_controller:" + environment.get(
        "PYTHONPATH", "")
    environment.setdefault("OMP_NUM_THREADS", "1")
    trainer = ROOT / "Experimentos/entrenar_ppo_mujoco.py"

    try:
        for seed in SEEDS:
            print(f"Training corrected step seed {seed}", flush=True)
            status["current_seed"] = seed
            save_json(OUT / "campaign_status.json", status)
            command = [
                sys.executable, "-u", str(trainer), "--gait", "step",
                "--timesteps", str(TIMESTEPS), "--seed", str(seed),
                "--episode-cycles", "5", "--attitude-weight", "32",
                "--stability-observation", "--lateral-weight", "64",
                "--yaw-weight", "32", "--output", str(OUT / "mujoco"),
            ]
            with (OUT / f"training_seed_{seed}.log").open(
                    "w", encoding="utf-8") as log:
                subprocess.run(command, cwd=ROOT, env=environment, stdout=log,
                               stderr=subprocess.STDOUT, check=True)
            metadata_path = OUT / "mujoco" / f"step_semilla_{seed}" / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            for key, value in ENVIRONMENT_KWARGS.items():
                if metadata.get(key) != value:
                    raise RuntimeError(f"Unexpected {key} for seed {seed}")
            if (metadata.get("gait_samples") != 48
                    or metadata.get("sample_duration_s") != 0.12
                    or metadata.get("steps_per_sample") != 6):
                raise RuntimeError(f"Unexpected step reference timing for seed {seed}")
            status["completed_seeds"].append(seed)
            status["current_seed"] = None
            save_json(OUT / "campaign_status.json", status)

        print(f"Evaluating 20-cycle development episodes {DEV_EVAL_SEEDS}",
              flush=True)
        sys.path.insert(0, str(ROOT / "Experimentos"))
        from campana_ppo_completa import evaluate_mujoco

        evaluate_mujoco(
            OUT, len(DEV_EVAL_SEEDS), seeds=SEEDS, gaits=("step",),
            episode_seeds=DEV_EVAL_SEEDS, episode_cycles=20,
            environment_kwargs=ENVIRONMENT_KWARGS)
        status.update(state="complete",
                      finished_at=datetime.now(timezone.utc).isoformat())
        save_json(OUT / "campaign_status.json", status)
        write_checksums()
        print(f"Campaign complete: {OUT}", flush=True)
    except Exception as error:
        status.update(state="failed", error=repr(error),
                      failed_at=datetime.now(timezone.utc).isoformat())
        save_json(OUT / "campaign_status.json", status)
        write_checksums()
        raise


if __name__ == "__main__":
    main()
