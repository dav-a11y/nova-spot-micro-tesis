#!/usr/bin/env bash
# Instala el servicio que apaga el PWM de los servos del cuadrúpedo al apagar el PC (27-oct-2026).
# Uso (como root): pkexec bash <ruta>/instalar.sh
set -e
cd "$(dirname "$0")"
install -m 755 apagar-cuadrupedo /usr/local/bin/apagar-cuadrupedo
install -m 644 apagar-cuadrupedo.service /etc/systemd/system/apagar-cuadrupedo.service
systemctl daemon-reload
systemctl enable apagar-cuadrupedo.service
systemctl is-enabled apagar-cuadrupedo.service
