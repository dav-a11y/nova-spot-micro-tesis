#!/usr/bin/env bash
# 28-oct 17:20: el PC se apagó (16:50 y 17:02) con el galope v27 terminado y el gateo v27 en 4,1-4,2 M de 4,5 M.
# Mide la viabilidad de todas las copias intermedias que hay (galope primero) → viabilidad_todas_ppo_v27_*.txt.
cd "$(dirname "$0")"
for c in galope gateo; do
  P=""; for f in ppo_v27_$c/semilla_*/intermedias/policy_*_steps.zip; do P="$P --politica $f"; done
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 ../../.venv-mujoco/bin/python -I evaluar_viabilidad.py $P --procesos 10 > viabilidad_todas_ppo_v27_$c.txt 2>&1
done
echo FIN > viabilidad_todas_v27.fin
