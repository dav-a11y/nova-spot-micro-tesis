#!/usr/bin/env bash
# Verifica que los archivos son exactamente los del 5-nov-2026 y repite en simulación la viabilidad de las 5 políticas.
# Uso (desde cualquier carpeta, con el entorno de requirements.txt activo o PY=<python> exportado):
#   Experimentos/entrenamiento_real_20261016/politicas_elegidas_20261105/verificar.sh [--rapido]
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../../.." && pwd)"
PY="${PY:-python3}"
cd "$RAIZ"
echo "== Sumas de comprobación"
sha256sum -c "$AQUI/SHA256SUMS"
EP=20; [ "${1:-}" = "--rapido" ] && EP=4
cd Experimentos/entrenamiento_real_20261016
R=ppo_v10_robot
echo "== Viabilidad en simulación ($EP episodios, semillas 1001+)"
"$PY" -I evaluar_viabilidad.py --politica $R/ppo_v24_paso_semilla_4109_200k/policy.zip --actuador actuadores_ciclo2.json --episodios $EP
"$PY" -I evaluar_viabilidad.py --politica $R/ppo_v27_gateo_semilla_7013_4100k/policy.zip --actuador actuadores_ciclo2.json --episodios $EP
"$PY" -I evaluar_viabilidad.py --politica $R/ppo_v32_trote_semilla_9209_650k/policy.zip --actuador actuadores_trote_articulacion.json --episodios $EP
"$PY" -I evaluar_viabilidad.py --politica $R/ppo_v32_carrera_semilla_9301_500k/policy.zip --actuador actuadores_carrera_articulacion.json --episodios $EP
"$PY" -I evaluar_viabilidad.py --politica $R/ppo_v32_galope_semilla_9407_475k/policy.zip --actuador actuadores_galope_articulacion.json --episodios $EP
