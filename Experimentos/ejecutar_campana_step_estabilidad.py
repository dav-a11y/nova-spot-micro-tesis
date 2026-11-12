#!/usr/bin/env python3
"""Development run for a more attitude-conservative step PPO policy."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Experimentos/campana_step_estabilidad_w32_20260928"
SEEDS = (11, 23, 37, 53, 71)
DEV_EVAL_SEEDS = (601, 602, 603, 604, 605)
FROZEN_EVAL_SEEDS = (101, 202, 303, 404, 505)
TIMESTEPS = 200_000
ATTITUDE_WEIGHT = 32.0


def save_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_checksums() -> None:
    entries = []
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(f"{digest}  {path.relative_to(OUT).as_posix()}")
    (OUT / "SHA256SUMS").write_text("\n".join(entries) + "\n", encoding="utf-8")


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing campaign: {OUT}")

    OUT.mkdir(parents=True)
    (OUT / "mujoco").mkdir()
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "development_only_stability_weight_sweep_single_arm",
        "gait": "step",
        "training_seeds": SEEDS,
        "timesteps_requested": TIMESTEPS,
        "attitude_weight": ATTITUDE_WEIGHT,
        "baseline_attitude_weight": 8.0,
        "episode_cycles_training": 5,
        "training_domain_randomization": True,
        "development_evaluation_seeds": DEV_EVAL_SEEDS,
        "evaluation_episodes": 5,
        "evaluation_cycles": 20,
        "evaluation_domain_randomization": False,
        "reserved_final_evaluation_seeds": FROZEN_EVAL_SEEDS,
        "provisional_targets": {
            "roll_pitch_rms_deg_max": 5.0,
            "roll_pitch_abs_max_deg": 15.0,
            "body_height_m": [0.16, 0.32],
            "source": "Documentacion/FICHA_APROBACION_PROTOCOLO.md",
            "approval_status": "unsigned_provisional",
        },
        "hardware_transfer": False,
    }
    save_json(OUT / "campaign_manifest.json", manifest)
    status = {"state": "running", "completed_seeds": [], "current_seed": None}
    save_json(OUT / "campaign_status.json", status)

    env = os.environ.copy()
    env["PYTHONPATH"] = "src/nova_gait_controller:" + env.get("PYTHONPATH", "")
    env.setdefault("OMP_NUM_THREADS", "1")
    trainer = ROOT / "Experimentos/entrenar_ppo_mujoco.py"

    try:
        for seed in SEEDS:
            print(f"Training step seed {seed} at attitude_weight={ATTITUDE_WEIGHT}",
                  flush=True)
            status.update(current_seed=seed)
            save_json(OUT / "campaign_status.json", status)
            log_path = OUT / f"training_seed_{seed}.log"
            command = [
                sys.executable, "-u", str(trainer), "--gait", "step",
                "--timesteps", str(TIMESTEPS), "--seed", str(seed),
                "--episode-cycles", "5", "--attitude-weight",
                str(ATTITUDE_WEIGHT), "--output", str(OUT / "mujoco"),
            ]
            with log_path.open("w", encoding="utf-8") as log:
                subprocess.run(command, cwd=ROOT, env=env, stdout=log,
                               stderr=subprocess.STDOUT, check=True)
            metadata_path = OUT / "mujoco" / f"step_semilla_{seed}" / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("attitude_weight") != ATTITUDE_WEIGHT:
                raise RuntimeError(f"Unexpected reward config for seed {seed}")
            status["completed_seeds"].append(seed)
            status["current_seed"] = None
            save_json(OUT / "campaign_status.json", status)

        print("Evaluating paired 20-cycle episodes on development seeds "
              f"{DEV_EVAL_SEEDS}", flush=True)
        sys.path.insert(0, str(ROOT / "Experimentos"))
        from campana_ppo_completa import evaluate_mujoco

        evaluate_mujoco(
            OUT, len(DEV_EVAL_SEEDS), seeds=SEEDS, gaits=("step",),
            episode_seeds=DEV_EVAL_SEEDS, episode_cycles=20,
            environment_kwargs={"attitude_weight": ATTITUDE_WEIGHT})
        status.update(state="complete", finished_at=datetime.now(timezone.utc).isoformat())
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
