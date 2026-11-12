#!/bin/bash
# 20-oct: conexión permanente con la tablet (DroidCam por Wi-Fi) publicada como webcam virtual.
# DroidCam solo admite un cliente y se bloquea si se conecta y desconecta a menudo; aquí hay
# una única conexión, que se rehace sola si se corta, y su imagen va a /dev/video10
# (v4l2loopback, «Tablet»). Grabaciones, análisis y visores leen /dev/video10 sin tocar la tablet.
# Uso: tablet_puente.sh [IP] [PUERTO]   (por defecto 192.168.0.105 4747)
IP=${1:-192.168.0.105}
PUERTO=${2:-4747}
LOG=/home/pavilion/Documentos/Cuadrupedo/Experimentos/camaras/tablet_puente.log
while true; do
    echo "$(date '+%H:%M:%S') conectando a $IP:$PUERTO" >> $LOG
    ffmpeg -hide_banner -loglevel error -fflags nobuffer -i "http://$IP:$PUERTO/video" \
        -vf "fps=30,scale=1280:720,format=yuv420p" -f v4l2 /dev/video10 >> $LOG 2>&1
    echo "$(date '+%H:%M:%S') conexión perdida; reintento en 2 s" >> $LOG
    sleep 2
done
