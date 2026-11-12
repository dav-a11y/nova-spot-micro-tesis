#!/bin/bash
# 11-nov: lanza una caminata en el robot grabando las 4 cámaras (mosaico) al mismo tiempo.
# Uso: caminata_con_camaras.sh <nombre> [argumentos de ejecutar_politica_robot.py]
#   ej.: caminata_con_camaras.sh pace_v34_9517 --politica ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k/policy.zip --duracion-s 20
# Deja en grabaciones/<nombre>_<fecha>/: camaras.mkv, caminata.csv (+ .config.json, .inicio.txt).
# Al terminar vuelve a abrir el mosaico solo para ver.
set -u
espera() { timeout "$1" tail -f /dev/null; true; }   # pausa (sin sleep)
AQUI=$(cd "$(dirname "$0")" && pwd)
RAIZ=$(cd "$AQUI/../.." && pwd)
NOMBRE=$1; shift
DIR="$AQUI/grabaciones/${NOMBRE}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DIR"

pkill -f ver_4_camaras_ffmpeg; pkill -x ffplay; espera 1.5      # libera las cámaras
"$AQUI/ver_4_camaras.sh" "$DIR/camaras.mkv" 2>"$DIR/camaras.log" &
for i in $(seq 1 40); do [ -s "$DIR/camaras.mkv" ] && break; espera 0.25; done
[ -s "$DIR/camaras.mkv" ] || { echo "ERROR: las cámaras no arrancaron (ver $DIR/camaras.log)"; cat "$DIR/camaras.log"; exit 1; }
espera 2; date +%s.%N > "$DIR/camaras.inicio_aprox.txt"
echo "Grabando cámaras en $DIR"

cd "$RAIZ/Experimentos/entrenamiento_real_20261016"
"$RAIZ/.venv-mujoco/bin/python" ejecutar_politica_robot.py "$@" --salida "$DIR/caminata.csv"
RC=$?

espera 2
pkill -INT -f ver_4_camaras_ffmpeg; espera 2; pkill -x ffplay
echo "Video: $DIR/camaras.mkv"
setsid "$AQUI/ver_4_camaras.sh" >/dev/null 2>&1 < /dev/null &   # mosaico para seguir viendo
exit $RC
