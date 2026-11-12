#!/bin/bash
# 21-oct: espera a los entrenamientos v14 (gateo apertura 8°, trote apertura 5°, geometría real),
# elige la mejor copia de cada uno y prueba en el robot con las 5 cámaras:
# gateo base / gateo v14 / trote base / trote v14, 3 repeticiones; análisis de video, colores y
# repetibilidad tras cada caminata; commit local al final.
set -u
EXP=/home/pavilion/Documentos/Cuadrupedo/Experimentos
ENT=$EXP/entrenamiento_real_20261016; CAM=$EXP/camaras
PY=/home/pavilion/Documentos/Cuadrupedo/.venv-mujoco/bin/python
LOG=$CAM/cadena_20261021.log
echo "$(date '+%H:%M') inicio" >> $LOG
while pgrep -f "output ppo_v14_" >/dev/null; do sleep 60; done
echo "$(date '+%H:%M') entrenamientos terminados" >> $LOG
cd $ENT
for par in "gateo ppo_v14_gateo" "trote ppo_v14_trote"; do
    set -- $par
    OMP_NUM_THREADS=1 $PY -I seleccionar_copias.py --marcha $1 --carpeta $2 --procesos 10 --semillas 2 > seleccion_$2.txt 2>&1
    grep -E "^base|Elegida" seleccion_$2.txt >> $LOG
done
GATEO=$(grep -o 'ppo_v10_robot/ppo_v14_gateo_[^ ]*' seleccion_ppo_v14_gateo.txt | tail -1)
TROTE=$(grep -o 'ppo_v10_robot/ppo_v14_trote_[^ ]*' seleccion_ppo_v14_trote.txt | tail -1)
echo "$(date '+%H:%M') elegidas: gateo=${GATEO:-ninguna} trote=${TROTE:-ninguna}" >> $LOG
COND=(--condicion "gateo_base:gateo::--apertura 8" --condicion "trote_base:trote::--apertura 5")
[ -n "$GATEO" ] && COND+=(--condicion "gateo_v14:gateo:$GATEO/policy.zip")
[ -n "$TROTE" ] && COND+=(--condicion "trote_v14:trote:$TROTE/policy.zip")
cd $CAM
python3 protocolo_repetibilidad.py --sesion 20261021 --repeticiones 3 --duracion-s 180 --pausa-s 10 "${COND[@]}" >> protocolo_20261021.log 2>&1
echo "$(date '+%H:%M') protocolo terminado (código $?)" >> $LOG
python3 -I analizar_repetibilidad.py --sesion 20261021 >> $LOG 2>&1
cd /home/pavilion/Documentos/Cuadrupedo && git add -A Experimentos/camaras/*.py Experimentos/camaras/*.sh Experimentos/camaras/*.log Experimentos/camaras/repetibilidad_20261021.* Experimentos/entrenamiento_real_20261016/seleccion_ppo_v14_* && git commit -q -m "Cadena 21-oct: gateo y trote v14 (postura abierta, geometría real), prueba en el robot con 5 cámaras

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "$(date '+%H:%M') commit $(git log --oneline -1)" >> $LOG
echo "$(date '+%H:%M') FIN" >> $LOG
