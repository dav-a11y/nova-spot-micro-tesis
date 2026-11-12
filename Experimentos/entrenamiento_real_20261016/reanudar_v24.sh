#!/usr/bin/env bash
# Retoma la cola v24 detenida el 27-oct a las 23:50 (apagado del PC). Las semillas sin policy.zip siguen
# desde su última copia intermedia con los pasos que les faltan; el galope (sin copias) empieza de nuevo.
# Después selecciona y mide la viabilidad de las 5 marchas (resumen en resumen_cola.txt).
# Uso: ./reanudar_v24.sh   (en segundo plano: setsid nohup ./reanudar_v24.sh > reanudar_v24.log 2>&1 &)
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
MAX=10
COMUN="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0"
R=ppo_v10_robot
declare -A ARGS=(
  [ppo_v24_gateo]="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 10 --w-lateral 20"
  [ppo_v24_paso]="--marcha paso --ciclo-paso 2.0 --femur 15 --tibia 10 --apertura 8 --w-avance 20 --w-lateral 20"
  [ppo_v24_trote]="--marcha trote --ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20"
  [ppo_v24_carrera]="--marcha carrera --ciclo-trote 0.8 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20"
  [ppo_v24_galope]="--marcha galope --ciclo-trote 0.8 --femur 16 --tibia 14 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 10 --w-lateral 30"
)
# semilla:campaña:pasos totales al terminar
PENDIENTES="4301:ppo_v24_carrera:2700000 4303:ppo_v24_carrera:2700000 4307:ppo_v24_carrera:3000000 4309:ppo_v24_carrera:3000000
4207:ppo_v24_trote:3000000 4209:ppo_v24_trote:3000000"

esperar_hueco() { while [ "$(pgrep -fc 'entrenar_ppo_real.py')" -ge "$MAX" ]; do sleep 30; done; }

for p in $PENDIENTES; do
  IFS=: read -r s c total <<< "$p"
  d=$c/semilla_$s
  copia=$(ls $d/intermedias/policy_*_steps.zip | sort -V | tail -1)
  hecho=$(basename "$copia" | grep -o '[0-9]*')
  cp $d/training_trace.csv $d/training_trace_parte1.csv
  esperar_hueco
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN ${ARGS[$c]} --seed $s \
    --timesteps $((total - hecho)) --continuar $copia --output $c > log_${c}_${s}_parte2.txt 2>&1 &
  sleep 5
done
rm -rf ppo_v24_galope
for s in 4401 4403; do
  esperar_hueco
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN ${ARGS[ppo_v24_galope]} --seed $s \
    --timesteps 1500000 --continuar $R/ppo_v21_galope_semilla_827_100k/policy.zip --output ppo_v24_galope > log_ppo_v24_galope_$s.txt 2>&1 &
  sleep 5
done
for s in 4407 4409; do
  esperar_hueco
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN ${ARGS[ppo_v24_galope]} --seed $s \
    --timesteps 3000000 --output ppo_v24_galope > log_ppo_v24_galope_$s.txt 2>&1 &
  sleep 5
done

for c in ppo_v24_gateo ppo_v24_paso ppo_v24_trote ppo_v24_carrera ppo_v24_galope; do
  marcha=$(echo ${ARGS[$c]} | awk '{print $2}')
  until [ "$(ls $c/semilla_*/policy.zip 2>/dev/null | wc -l)" -ge 4 ]; do sleep 60; done
  OMP_NUM_THREADS=1 nice -n 5 $PY -I seleccionar_copias.py --marcha $marcha --carpeta $c --procesos 8 --semillas 2 > seleccion_$c.txt 2>&1
  OMP_NUM_THREADS=1 nice -n 5 $PY -I evaluar_viabilidad.py --carpeta $c --top 5 --procesos 8 > viabilidad_$c.txt 2>&1
  { echo "== $c ($(date +%H:%M))"; grep -E "^base" seleccion_$c.txt; cat viabilidad_$c.txt; } >> resumen_cola.txt
done
echo "FIN $(date +%H:%M)" >> resumen_cola.txt
