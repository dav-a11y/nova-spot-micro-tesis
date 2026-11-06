#!/bin/bash
# 6-nov-2026: segunda parte del pace v34 que continúa el trote. La semilla 9517 (de la que salió la copia elegida,
# 1,6 M, 100 % viable en 60 episodios) y la 9521 seguían subiendo a 1 M de pasos de pace. Se continúan 2 M más
# (3 M de pace en total, como las de cero) para ver la convergencia. Mismos argumentos que cola_pace.sh; salida
# aparte (ppo_v34_pace_desde_trote_parte2) que luego se une a la primera parte para las gráficas.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
C="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 0.1 --registrar-perdidas \
--marcha pace --ciclo-trote 0.45 --femur 12 --tibia 12 --apertura 5 --coxa 8 --ciclos-episodio 27 \
--w-avance 10 --w-lateral 20 --actuador actuadores_trote_articulacion.json"
for s in 9517 9521; do
  OMP_NUM_THREADS=1 $PY -I entrenar_ppo_real.py $C --seed $s --timesteps 2000000 --guardar-cada 50000 \
    --continuar ppo_v34_pace_desde_trote/semilla_$s/policy.zip --output ppo_v34_pace_desde_trote_parte2 \
    > log_ppo_v34_pace_desde_trote_parte2_$s.txt 2>&1 &
  sleep 3
done
wait
P=""
for f in ppo_v34_pace_desde_trote_parte2/semilla_*/intermedias/policy_*_steps.zip ppo_v34_pace_desde_trote_parte2/semilla_*/policy.zip; do
  [ -f "$f" ] && P="$P --politica $f"
done
OMP_NUM_THREADS=1 $PY -I evaluar_viabilidad.py $P --actuador actuadores_trote_articulacion.json --procesos 12 \
  > viabilidad_todas_ppo_v34_pace_parte2.txt 2>&1
echo FIN > cola_pace_parte2.fin
