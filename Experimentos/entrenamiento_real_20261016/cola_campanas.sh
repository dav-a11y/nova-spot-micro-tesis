#!/usr/bin/env bash
# Cola de campañas PPO (27-oct): entrena varias semillas por marcha (hasta MAX a la vez, núcleos 2-11),
# y al terminar cada campaña la selecciona y mide su viabilidad (evaluar_viabilidad.py, 20 episodios).
# El resumen va a resumen_cola.txt. Uso: ./cola_campanas.sh   (en segundo plano)
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
MAX=10
COMUN="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0"
R=ppo_v10_robot

# nombre | marcha | argumentos de la marcha | semillas continuando:copia:pasos | semillas desde cero:pasos
# 27-oct (noche): v24, la simulación ya incluye las ganancias de las tibias (mismo movimiento que el robot).
CAMPANAS=(
"ppo_v24_gateo|gateo|--femur 15 --tibia 10 --apertura 8 --w-avance 10 --w-lateral 20|4001,4003:$R/ppo_v22_gateo_semilla_3101_2700k/policy.zip:1500000|4007,4009:3000000"
"ppo_v24_paso|paso|--ciclo-paso 2.0 --femur 15 --tibia 10 --apertura 8 --w-avance 20 --w-lateral 20|4101,4103:$R/ppo_v22_paso_semilla_3013_100k/policy.zip:1500000|4107,4109:3000000"
"ppo_v24_trote|trote|--ciclo-trote 1.0 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20|4201,4203:$R/ppo_v15_trote_semilla_307_100k/policy.zip:1500000|4207,4209:3000000"
"ppo_v24_carrera|carrera|--ciclo-trote 0.8 --femur 12 --tibia 12 --apertura 5 --ciclos-episodio 12 --w-avance 10 --w-lateral 20|4301,4303:$R/ppo_v22_carrera_semilla_3307_1200k/policy.zip:1500000|4307,4309:3000000"
"ppo_v24_galope|galope|--ciclo-trote 0.8 --femur 16 --tibia 14 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 10 --w-lateral 30|4401,4403:$R/ppo_v21_galope_semilla_827_100k/policy.zip:1500000|4407,4409:3000000"
)

esperar_hueco() { while [ "$(pgrep -fc 'entrenar_ppo_real.py')" -ge "$MAX" ]; do sleep 30; done; }

for c in "${CAMPANAS[@]}"; do
  IFS='|' read -r nombre marcha args cont nuevas <<< "$c"
  IFS=':' read -r sc copia pc <<< "$cont"
  IFS=':' read -r sn pn <<< "$nuevas"
  for s in ${sc//,/ }; do
    esperar_hueco
    OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN --marcha $marcha $args \
      --seed $s --timesteps $pc --continuar $copia --output $nombre > log_${nombre}_$s.txt 2>&1 &
    sleep 5
  done
  for s in ${sn//,/ }; do
    esperar_hueco
    OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN --marcha $marcha $args \
      --seed $s --timesteps $pn --output $nombre > log_${nombre}_$s.txt 2>&1 &
    sleep 5
  done
done

# Selección y viabilidad, una campaña cada vez (seleccion_<marcha>.csv es compartido).
for c in "${CAMPANAS[@]}"; do
  IFS='|' read -r nombre marcha _ <<< "$c"
  n=$(ls -d $nombre/semilla_* | wc -l)
  until [ "$(ls $nombre/semilla_*/policy.zip 2>/dev/null | wc -l)" -ge "$n" ]; do sleep 60; done
  OMP_NUM_THREADS=1 nice -n 5 $PY -I seleccionar_copias.py --marcha $marcha --carpeta $nombre --procesos 8 --semillas 2 \
    > seleccion_$nombre.txt 2>&1
  OMP_NUM_THREADS=1 nice -n 5 $PY -I evaluar_viabilidad.py --carpeta $nombre --top 5 --procesos 8 > viabilidad_$nombre.txt 2>&1
  { echo "== $nombre ($(date +%H:%M))"; grep -E "^base|Elegida" seleccion_$nombre.txt; cat viabilidad_$nombre.txt; } >> resumen_cola.txt
done
echo "FIN $(date +%H:%M)" >> resumen_cola.txt
