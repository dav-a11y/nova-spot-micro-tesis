#!/usr/bin/env bash
# Cola v32 (5-nov): reentrenar las 5 políticas elegidas con el modelo del actuador ajustado por marcha
# (ajustar_ganancia_marcha.py --modo articulacion: ganancia por articulación = amplitud robot/sim medida en el robot
# suspendido; en tomas no usadas para el ajuste subió el parecido de 78-80→88-91 % en paso, 61-79→69-87 % en trote,
# 66→76 % en carrera). 4 semillas por marcha que continúan la política elegida; luego viabilidad de todas las copias
# (con el modelo nuevo) y de las políticas de partida como referencia.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
R=ppo_v10_robot
C="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --registrar-perdidas"
declare -A ARGS=(
 [paso]="--marcha paso --ciclo-paso 2.0 --femur 15 --tibia 10 --apertura 8 --w-avance 20 --w-lateral 20"
 [trote]="--marcha trote --ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20"
 [carrera]="--marcha carrera --ciclo-trote 0.8 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20"
 [gateo]="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 40 --w-lateral 20"
 [galope]="--marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 30 --w-lateral 30")
declare -A PARTIDA=([paso]=ppo_v24_paso_semilla_4109_200k [trote]=ppo_v24_trote_semilla_4209_200k
 [carrera]=ppo_v24_carrera_semilla_4309_200k [gateo]=ppo_v27_gateo_semilla_7013_4100k [galope]=ppo_v28_galope_semilla_8417_175k)
declare -A SEM=([paso]="9101 9103 9107 9109" [trote]="9201 9203 9207 9209" [carrera]="9301 9303 9307 9309"
 [gateo]="9001 9003 9007 9009" [galope]="9401 9403 9407 9409")
for m in paso trote carrera gateo galope; do
  if [ $m = galope ]; then T=300000; G=25000; else T=500000; G=50000; fi
  for s in ${SEM[$m]}; do
    OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $C ${ARGS[$m]} --actuador actuadores_${m}_articulacion.json \
      --guardar-cada $G --seed $s --timesteps $T --continuar $R/${PARTIDA[$m]}/policy.zip --output ppo_v32_$m \
      > log_ppo_v32_${m}_$s.txt 2>&1 &
    sleep 3
  done
done
wait
echo ENTRENADO > cola_v32.fin
for m in paso trote carrera gateo galope; do
  P=""; for f in ppo_v32_$m/semilla_*/intermedias/policy_*_steps.zip ppo_v32_$m/semilla_*/policy.zip; do [ -f "$f" ] && P="$P --politica $f"; done
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I evaluar_viabilidad.py --politica $R/${PARTIDA[$m]}/policy.zip $P --actuador actuadores_${m}_articulacion.json --top 40 --procesos 10 > viabilidad_todas_ppo_v32_$m.txt 2>&1
done
echo FIN >> cola_v32.fin
# v33: las 5 marchas DESDE CERO con el modelo ajustado y registro de cada término (como la v31), para las gráficas de
# convergencia; una semilla por marcha, 3 M de pasos (galope 5 M).
for m in paso trote carrera gateo galope; do
  if [ $m = galope ]; then T=5000000; else T=3000000; fi
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $C ${ARGS[$m]} --actuador actuadores_${m}_articulacion.json \
    --guardar-cada 100000 --seed 9900 --timesteps $T --output ppo_v33_$m > log_ppo_v33_$m.txt 2>&1 &
  sleep 3
done
wait
echo FIN_V33 >> cola_v32.fin
