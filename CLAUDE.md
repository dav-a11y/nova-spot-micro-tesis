# LabRobotica

Copia de trabajo del repositorio `dav-a11y/nova-spot-micro-tesis`, el repositorio propio del
usuario. Es una copia exacta, hecha el 5 de noviembre de 2026, del repositorio de su compañero
`davidediaz/nova-spot-micro-tesis`. Responde en español.

Aquí se trabaja con simulación y aprendizaje por refuerzo (ROS 2 Humble, MuJoCo, Gazebo) y,
más adelante, con el control del robot mediante Arduino.

## Repositorios y carpetas

- Se trabaja y se sube solo a `origin` (`dav-a11y/nova-spot-micro-tesis`).
- No modifiques el repositorio de `davidediaz` ni la carpeta local `~/Documents/Cuadrupedo`;
  solo léelos si te lo piden.
- Sube los cambios en ramas y comparte cada una mediante un Pull Request hacia `main`.
- `CONTINUIDAD.md` y `README.md` describen el historial y el uso del proyecto original.

## Entorno

Antes de ejecutar algo, carga el entorno con `source entorno.sh`.

- Ubuntu 22.04, Python 3.10, ROS 2 Humble, Gazebo Harmonic (gz-sim 8) y el puente
  `ros-humble-ros-gzharmonic`.
- `.venv` (fuera de Git) contiene las dependencias de `requirements.txt`. Para reproducir los
  entrenamientos originales, usa las versiones de
  `Experimentos/campana_distribuida_step_s23_20260928/requirements-lock.txt`
  (rama `entrenamiento/ppo-robot-real-20261016`).

Al terminar un avance importante, regístralo con fecha para que la siguiente sesión pueda
continuar desde ahí.
