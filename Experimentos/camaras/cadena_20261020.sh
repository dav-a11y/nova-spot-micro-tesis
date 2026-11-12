#!/bin/bash
# 20-oct: cadena automática con el modelo de geometría real.
# 1) espera a que terminen los entrenamientos (gateo v12 y trote), 2) elige la mejor copia de
# cada uno en caminatas simuladas de 3 min, 3) prueba en el robot gateo base / gateo v12 /
# trote base / trote PPO (3 repeticiones, 4 cámaras, análisis de video tras cada caminata),
# 4) análisis de repetibilidad, catálogo y commit local.
set -u
EXP=/home/pavilion/Documentos/Cuadrupedo/Experimentos
ENT=$EXP/entrenamiento_real_20261016
CAM=$EXP/camaras
PY=/home/pavilion/Documentos/Cuadrupedo/.venv-mujoco/bin/python
LOG=$CAM/cadena_20261020.log
echo "$(date '+%H:%M') inicio de la cadena" >> $LOG

while pgrep -f '^\.\./\.\./\.venv-mujoco/bin/python -I entrenar_ppo_real' >/dev/null; do sleep 60; done
echo "$(date '+%H:%M') entrenamientos terminados" >> $LOG

cd $ENT
for par in "gateo ppo_v12_gateo" "trote ppo_trote"; do
    set -- $par
    OMP_NUM_THREADS=1 $PY -I seleccionar_copias.py --marcha $1 --carpeta $2 --procesos 10 --semillas 2 > seleccion_$2.txt 2>&1
    tail -6 seleccion_$2.txt >> $LOG
done
GATEO=$(grep -o 'ppo_v10_robot/ppo_v12_gateo_[^ ]*' seleccion_ppo_v12_gateo.txt | tail -1)
TROTE=$(grep -o 'ppo_v10_robot/ppo_trote_[^ ]*' seleccion_ppo_trote.txt | tail -1)
echo "$(date '+%H:%M') elegidas: gateo=${GATEO:-ninguna} trote=${TROTE:-ninguna}" >> $LOG

COND=(--condicion gateo_base:gateo: --condicion trote_base:trote:)
[ -n "$GATEO" ] && COND+=(--condicion gateo_v12:gateo:$GATEO/policy.zip)
[ -n "$TROTE" ] && COND+=(--condicion trote_ppo:trote:$TROTE/policy.zip)

# Celular despierto y cámaras libres antes de empezar.
adb shell svc power stayon true >/dev/null 2>&1; adb shell input keyevent KEYCODE_WAKEUP >/dev/null 2>&1
cd $CAM
python3 protocolo_repetibilidad.py --sesion 20261020real --repeticiones 3 --duracion-s 180 --pausa-s 10 "${COND[@]}" >> protocolo_20261020real.log 2>&1
echo "$(date '+%H:%M') protocolo terminado (código $?)" >> $LOG
python3 -I analizar_repetibilidad.py --sesion 20261020real >> $LOG 2>&1
cd /home/pavilion/Documentos/Cuadrupedo && git add -A && git commit -q -m "Cadena 20-oct: gateo v12 y trote con geometría real, selección y prueba en el robot (sesión 20261020real)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "$(date '+%H:%M') commit $(git log --oneline -1)" >> $LOG
echo "$(date '+%H:%M') FIN" >> $LOG
