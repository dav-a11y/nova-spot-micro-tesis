#!/usr/bin/env bash
# Cola v25 (28-oct): galope con marcha base que no se cae con las ganancias de tibia (barrido_nominal.py:
# fémur 18°, tibia 7° → avanza 2,1 m sin caídas; la de v24, fémur 16° tibia 14°, caía 20/20) y gateo con
# más peso al avance (las v24 avanzaban <90 % de la nominal). Luego selección y viabilidad → resumen_v25.txt.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
COMUN="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --guardar-cada 50000"
GALOPE="--marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 15 --w-lateral 30"
GATEO="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 25 --w-lateral 20"
for s in 5401 5403 5407 5409; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN $GALOPE --seed $s --timesteps 1500000 \
    --output ppo_v25_galope > log_ppo_v25_galope_$s.txt 2>&1 &
  sleep 5
done
for s in 5001 5003 5007 5009; do
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN $GATEO --seed $s --timesteps 800000 \
    --continuar ppo_v10_robot/ppo_v22_gateo_semilla_3101_2700k/policy.zip --output ppo_v25_gateo > log_ppo_v25_gateo_$s.txt 2>&1 &
  sleep 5
done
wait
for c in ppo_v25_gateo:gateo ppo_v25_galope:galope; do
  IFS=: read -r d m <<< "$c"
  OMP_NUM_THREADS=1 nice -n 5 $PY -I seleccionar_copias.py --marcha $m --carpeta $d --procesos 10 --semillas 2 > seleccion_$d.txt 2>&1
  OMP_NUM_THREADS=1 nice -n 5 $PY -I evaluar_viabilidad.py --carpeta $d --top 8 --procesos 10 > viabilidad_$d.txt 2>&1
  { echo "== $d ($(date +%H:%M))"; grep -E "^base" seleccion_$d.txt; cat viabilidad_$d.txt; } >> resumen_v25.txt
done
echo "FIN $(date +%H:%M)" >> resumen_v25.txt
