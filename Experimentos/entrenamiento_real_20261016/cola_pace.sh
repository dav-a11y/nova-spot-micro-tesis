#!/bin/bash
# 6-nov-2026 (operador): marcha nueva «pace» (ambladura pura: FL+RL y luego FR+RR, coxas ±8° en contrafase
# por lado), aprobada en MuJoCo con la marcha base: ciclo 0,45 s, fémur 12°, tibia 12°, apertura 5°.
# Mismo PPO y recompensa que v32/v33 (pesos del trote) y el modelo de servos del trote ajustado por articulación.
# 4 semillas desde cero (3 M) y 4 que continúan el trote v32 elegido (1 M). Episodios de 27 ciclos (~12 s,
# como los 12 ciclos de 1 s del trote). Después, viabilidad de todas las copias intermedias.
# --w-coxas 0.1 (no 1.0): con las coxas en movimiento a 0,45 s y el retardo del servo, la coxa va siempre detrás de
# la orden y con 1.0 ese castigo (−7500 por episodio, la política no controla las coxas) hacía preferible caerse.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
R=ppo_v10_robot
C="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 0.1 --registrar-perdidas \
--marcha pace --ciclo-trote 0.45 --femur 12 --tibia 12 --apertura 5 --coxa 8 --ciclos-episodio 27 \
--w-avance 10 --w-lateral 20 --actuador actuadores_trote_articulacion.json"
for s in 9501 9503 9505 9507; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $C --seed $s --timesteps 3000000 \
    --guardar-cada 100000 --output ppo_v34_pace > log_ppo_v34_pace_$s.txt 2>&1 &
  sleep 3
done
for s in 9511 9513 9515 9517; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $C --seed $s --timesteps 1000000 \
    --guardar-cada 50000 --continuar $R/ppo_v32_trote_semilla_9209_650k/policy.zip --output ppo_v34_pace_desde_trote \
    > log_ppo_v34_pace_desde_trote_$s.txt 2>&1 &
  sleep 3
done
wait
echo ENTRENADO > cola_pace.fin
P=""
for f in ppo_v34_pace*/semilla_*/intermedias/policy_*_steps.zip ppo_v34_pace*/semilla_*/policy.zip; do
  [ -f "$f" ] && P="$P --politica $f"
done
OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I evaluar_viabilidad.py $P --actuador actuadores_trote_articulacion.json \
  --procesos 10 > viabilidad_todas_ppo_v34_pace.txt 2>&1
echo FIN >> cola_pace.fin
