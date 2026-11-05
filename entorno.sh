# Uso: source entorno.sh
# Carga ROS 2 Humble y el entorno de Python del proyecto.
RAIZ_LAB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source /opt/ros/humble/setup.bash
source "$RAIZ_LAB/.venv/bin/activate"
if [ -f "$RAIZ_LAB/install/setup.bash" ]; then
  source "$RAIZ_LAB/install/setup.bash"
fi
