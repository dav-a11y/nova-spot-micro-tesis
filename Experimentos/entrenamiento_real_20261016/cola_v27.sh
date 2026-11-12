#!/usr/bin/env bash
# Cola v27 (28-oct, 16:40). Gateo: v26 mejoraba al final (3,3 M: 55 %) → seguir 6001/6007 1,2 M más y 2 semillas
# nuevas desde 6007. Galope: el mejor v26 fue 6403 a 150 k (85 %) → 4 semillas nuevas cortas (300 k) y 2 que
# siguen desde esa copia. Luego viabilidad de TODAS las copias intermedias → viabilidad_todas_ppo_v27_*.txt.
cd "$(dirname "$0")"
PY=../../.venv-mujoco/bin/python
COMUN="--completo --aleatorizar --lr 1e-4 --target-kl 0.03 --n-steps 2048 --actuador actuadores_ciclo2.json --dt 0.03 \
--w-actitud 30 --w-giro 10 --w-giro-ciclo 5 --w-suavidad 0.3 --w-coxas 1.0 --guardar-cada 50000"
GALOPE="--marcha galope --ciclo-trote 0.8 --femur 18 --tibia 7 --apertura 5 --coxa 8 --ciclos-episodio 12 --w-avance 30 --w-lateral 30"
GATEO="--marcha gateo --femur 15 --tibia 10 --apertura 8 --w-avance 40 --w-lateral 20"
lanzar() { OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I entrenar_ppo_real.py $COMUN "$@" & sleep 5; }
lanzar $GATEO --seed 7001 --timesteps 1200000 --continuar ppo_v26_gateo/semilla_6001/policy.zip --output ppo_v27_gateo > log_ppo_v27_gateo_7001.txt 2>&1
lanzar $GATEO --seed 7007 --timesteps 1200000 --continuar ppo_v26_gateo/semilla_6007/policy.zip --output ppo_v27_gateo > log_ppo_v27_gateo_7007.txt 2>&1
lanzar $GATEO --seed 7011 --timesteps 1200000 --continuar ppo_v26_gateo/semilla_6007/policy.zip --output ppo_v27_gateo > log_ppo_v27_gateo_7011.txt 2>&1
lanzar $GATEO --seed 7013 --timesteps 1200000 --continuar ppo_v26_gateo/semilla_6007/policy.zip --output ppo_v27_gateo > log_ppo_v27_gateo_7013.txt 2>&1
for s in 7401 7403 7407 7409; do
  lanzar $GALOPE --seed $s --timesteps 300000 --output ppo_v27_galope > log_ppo_v27_galope_$s.txt 2>&1
done
for s in 7411 7413; do
  lanzar $GALOPE --seed $s --timesteps 300000 --continuar ppo_v26_galope/semilla_6403/intermedias/policy_150000_steps.zip \
    --output ppo_v27_galope > log_ppo_v27_galope_$s.txt 2>&1
done
wait
for c in galope gateo; do
  P=""; for f in ppo_v27_$c/semilla_*/intermedias/policy_*_steps.zip; do P="$P --politica $f"; done
  OMP_NUM_THREADS=1 nice -n 5 taskset -c 2-11 $PY -I evaluar_viabilidad.py $P --procesos 10 > viabilidad_todas_ppo_v27_$c.txt 2>&1
done
echo FIN > viabilidad_todas_v27.fin
