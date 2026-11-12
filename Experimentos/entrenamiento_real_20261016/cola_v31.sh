#!/usr/bin/env bash
# Cola v31 (3-nov): las 5 marchas desde cero con registro de pérdidas y de cada término de la recompensa
# (terminos.csv), para medir en qué paso y época converge cada una. 3 M de pasos; galope 5 M (a 1 M no convergía).
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
C="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --guardar-cada 100000 --registrar-perdidas"
lanzar() { n=$1; s=$2; t=$3; shift 3; OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $C "$@" --seed $s --timesteps $t \
  --output ppo_v31_$n > log_ppo_v31_${n}_$s.txt 2>&1 & sleep 3; }
lanzar paso 4109 3000000 --marcha paso --ciclo-paso 2.0 --femur 15 --tibia 10 --apertura 8 --w-avance 20 --w-lateral 20
lanzar trote 4207 3000000 --marcha trote --ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20
lanzar carrera 4309 3000000 --marcha carrera --ciclo-trote 0.8 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20
lanzar gateo 4009 3000000 --marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 40 --w-lateral 20
lanzar galope 6403 5000000 --marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 30 --w-lateral 30
wait
echo FIN > cola_v31.fin
