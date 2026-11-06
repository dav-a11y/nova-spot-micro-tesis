#!/usr/bin/env bash
# 5-nov: la v33 pasó al PC 2 (cola_v33.sh); aquí solo se espera a que terminen los entrenamientos v32 y se mide
# la viabilidad de todas sus copias y de las políticas de partida, con el modelo de servos ajustado de cada marcha.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
R=ppo_v10_robot
declare -A PARTIDA=([paso]=ppo_v24_paso_semilla_4109_200k [trote]=ppo_v24_trote_semilla_4209_200k
 [carrera]=ppo_v24_carrera_semilla_4309_200k [gateo]=ppo_v27_gateo_semilla_7013_4100k [galope]=ppo_v28_galope_semilla_8417_175k)
while pgrep -f "entrenar_ppo_rea[l].py.*ppo_v3[2]" >/dev/null; do sleep 30; done
echo ENTRENADO > cola_v32.fin
for m in paso trote carrera gateo galope; do
  P=""; for f in ppo_v32_$m/semilla_*/intermedias/policy_*_steps.zip ppo_v32_$m/semilla_*/policy.zip; do [ -f "$f" ] && P="$P --politica $f"; done
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I evaluar_viabilidad.py --politica $R/${PARTIDA[$m]}/policy.zip $P \
    --actuador actuadores_${m}_articulacion.json --top 40 --procesos 10 > viabilidad_todas_ppo_v32_$m.txt 2>&1
done
echo FIN >> cola_v32.fin
