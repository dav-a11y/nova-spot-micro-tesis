#!/usr/bin/env bash
# Cola v28 (28-oct, 17:45): último empujón al galope (v27: 90 % con 7403 a 150 k). 8 semillas cortas (200 k,
# copias cada 25 k) que siguen desde las dos mejores copias v27; viabilidad de todas las copias.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
COMUN="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --guardar-cada 25000"
GALOPE="--marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 30 --w-lateral 30"
for s in 8401 8403 8405 8407; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN $GALOPE --seed $s --timesteps 200000 \
    --continuar ppo_v27_galope/semilla_7403/intermedias/policy_150000_steps.zip --output ppo_v28_galope > log_ppo_v28_galope_$s.txt 2>&1 &
  sleep 5
done
for s in 8411 8413 8415 8417; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN $GALOPE --seed $s --timesteps 200000 \
    --continuar ppo_v27_galope/semilla_7407/intermedias/policy_150000_steps.zip --output ppo_v28_galope > log_ppo_v28_galope_$s.txt 2>&1 &
  sleep 5
done
wait
P=""; for f in ppo_v28_galope/semilla_*/intermedias/policy_*_steps.zip; do P="$P --politica $f"; done
OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I evaluar_viabilidad.py $P --procesos 10 > viabilidad_todas_ppo_v28_galope.txt 2>&1
echo FIN > viabilidad_todas_v28.fin
