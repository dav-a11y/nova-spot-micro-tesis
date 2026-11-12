#!/usr/bin/env bash
# Verifica que los archivos son exactamente los del 6-nov-2026 y repite en simulación la viabilidad del pace v34.
# Uso (desde cualquier carpeta, con el entorno de requirements.txt activo o PY=<python> exportado):
#   Experimentos/entrenamiento_real_20261016/politica_pace_20261106/verificar.sh [--rapido]
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../../.." && pwd)"
PY="${PY:-python3}"
# Ruta relativa de PY (p. ej. .venv-mujoco/bin/python) respecto a la carpeta desde la que se llama.
[[ "$PY" == */* ]] && PY="$(cd "$(dirname "$PY")" && pwd)/$(basename "$PY")"
cd "$RAIZ"
echo "== Sumas de comprobación"
sha256sum -c "$AQUI/SHA256SUMS"
EP=60; [ "${1:-}" = "--rapido" ] && EP=4
cd Experimentos/entrenamiento_real_20261016
echo "== Viabilidad en simulación ($EP episodios, semillas 1001+); con 60 debe salir 100 %"
"$PY" -I evaluar_viabilidad.py --politica ppo_v10_robot/ppo_v34_pace_semilla_9517_1600k/policy.zip \
  --actuador actuadores_trote_articulacion.json --episodios $EP
