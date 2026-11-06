#!/usr/bin/env bash
# 5-nov (se ejecuta en el PC 2, ~/Cuadrupedo_entreno): las 5 marchas DESDE CERO con el modelo de servos ajustado por
# marcha (actuadores_<marcha>_articulacion.json) y registro de cada término de la recompensa, como la v31, para las
# gráficas de convergencia. Una semilla por marcha, 3 M de pasos (galope 5 M).
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
C="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --dt 0.03 --w-actitud 30 --w-giro 10 \
--w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --registrar-perdidas --guardar-cada 100000 --seed 9900"
declare -A ARGS=(
 [paso]="--marcha paso --ciclo-paso 2.0 --femur 15 --tibia 10 --apertura 8 --w-avance 20 --w-lateral 20 --timesteps 3000000"
 [trote]="--marcha trote --ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20 --timesteps 3000000"
 [carrera]="--marcha carrera --ciclo-trote 0.8 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20 --timesteps 3000000"
 [gateo]="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 40 --w-lateral 20 --timesteps 3000000"
 [galope]="--marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 30 --w-lateral 30 --timesteps 5000000")
for m in paso trote carrera gateo galope; do
  OMP_NUM_THREADS=1 nice -n 5 $PY -I entrenar_ppo_real.py $C ${ARGS[$m]} --actuador actuadores_${m}_articulacion.json \
    --output ppo_v33_$m > log_ppo_v33_$m.txt 2>&1 &
  sleep 3
done
wait
echo FIN > cola_v33.fin
