"""Resume the step campaign to 80 seeds, checkpointing each evaluation."""
import csv
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import campana_ppo_completa as campaign

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Experimentos/campana_distribuida_step_s23_20260928'
SEEDS = [23, *range(1001, 1080)]


def save_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def main():
    os.chdir(ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    lock = (OUT / 'expansion.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest_path = OUT / 'campaign_manifest.json'
    backup = OUT / 'campaign_manifest.original.json'
    if not backup.exists():
        backup.write_bytes(manifest_path.read_bytes())
    manifest = json.loads(manifest_path.read_text())
    manifest.update(seeds=SEEDS, expanded_at=datetime.now(timezone.utc).isoformat())
    save_json(manifest_path, manifest)
    csv_path = OUT / 'mujoco_evaluation.csv'
    rows = list(csv.DictReader(csv_path.open())) if csv_path.exists() else []
    completed = []
    status_path = OUT / 'expansion_status.json'

    def status(state, seed=None, error=None):
        save_json(status_path, dict(state=state, current_seed=seed,
                  completed_seeds=completed, target_seeds=SEEDS,
                  updated_at=datetime.now(timezone.utc).isoformat(), error=error))

    seed = None
    try:
        for seed in SEEDS:
            status('running', seed)
            folder = OUT / 'mujoco' / f'step_semilla_{seed}'
            artifacts = [folder / name for name in
                         ('policy.zip', 'metadata.json', 'training_trace.jsonl')]
            if not all(path.exists() and path.stat().st_size for path in artifacts):
                # A failed attempt is kept for inspection before retrying.
                if folder.exists():
                    folder.rename(folder.with_name(folder.name + '.partial.' +
                                  datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')))
                print(f'Training seed {seed}', flush=True)
                with (OUT / f'training_seed_{seed}.log').open('a') as log:
                    subprocess.run([sys.executable, '-u',
                        str(ROOT / 'Experimentos/entrenar_ppo_mujoco.py'),
                        '--gait', 'step', '--seed', str(seed),
                        '--timesteps', '200000', '--episode-cycles', '5',
                        '--output', str(OUT / 'mujoco')],
                        stdout=log, stderr=subprocess.STDOUT, check=True)
            metadata = json.loads(artifacts[1].read_text())
            assert metadata['seed'] == seed and metadata['gait'] == 'step'
            assert metadata['timesteps'] == 200000
            existing = [row for row in rows if int(row['seed']) == seed
                        and row['gait'] == 'step']
            if len(existing) != 2 or {r['condition'] for r in existing} != {'nominal', 'ppo'}:
                evaluated = campaign.evaluate_mujoco(
                    OUT, 5, seeds=[seed], gaits=['step'], write_csv=False)
                assert len(evaluated) == 2
                rows = [row for row in rows if not
                        (int(row['seed']) == seed and row['gait'] == 'step')]
                rows.extend(evaluated)
                temporary = csv_path.with_suffix('.tmp')
                campaign._write_csv(temporary, rows)
                temporary.replace(csv_path)
            completed.append(seed)
            status('running', seed)
            print(f'Completed {len(completed)}/80: seed {seed}', flush=True)
        status('complete')
    except BaseException as exc:
        status('failed', seed, repr(exc))
        raise


if __name__ == '__main__':
    main()
