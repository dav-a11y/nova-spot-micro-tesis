#!/usr/bin/env bash
# 28-oct: viabilidad de TODAS las copias intermedias de v26 (gateo y galope); la selección solo miraba 8.
cd "$(dirname "$0")"
for c in galope gateo; do
  P=""; for f in ppo_v26_$c/semilla_*/intermedias/policy_*_steps.zip; do P="$P --politica $f"; done
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 ../../.venv-mujoco/bin/python -I evaluar_viabilidad.py $P --procesos 10 > viabilidad_todas_ppo_v26_$c.txt 2>&1
done
echo FIN > viabilidad_todas_v26.fin
