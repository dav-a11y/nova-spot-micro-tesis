#!/bin/bash
# 11-nov: mosaico en vivo de las 4 cámaras (HP, USB2.0, GENERAL, Logitech C170).
# La ventana se abre a la derecha de la pantalla (no la tapa la terminal); se cierra con q o Esc.
# Uso: ver_4_camaras.sh                 -> solo ver
#      ver_4_camaras.sh video.mkv       -> ver y grabar el mosaico directo de las cámaras
#                                          (para parar limpio: pkill -INT -f ver_4_camaras_ffmpeg)
B=/dev/v4l/by-id
export DISPLAY=${DISPLAY:-:1}
etq() { echo "scale=640:480,drawtext=text='$1':fontcolor=yellow:fontsize=26:x=10:y=10:box=1:boxcolor=black@0.6"; }
FILTRO="[0]$(etq '1 HP del PC')[a];[1]$(etq '2 USB2.0 Camera')[b];[2]$(etq '3 GENERAL WEBCAM')[c];[3]$(etq '4 Logitech C170')[d];[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,fps=15,drawtext=text='%{localtime\:%H\\\\\:%M\\\\\:%S}':fontcolor=white:fontsize=28:x=w-tw-10:y=10:box=1:boxcolor=black@0.6"
if [ -n "$1" ]; then
  FILTRO="$FILTRO,split=2[ver][grabar]"
  SALIDAS=(-map "[grabar]" -c:v libx264 -preset ultrafast -crf 23 -pix_fmt yuv420p -y "$1"
           -map "[ver]" -c:v rawvideo -pix_fmt yuv420p -f nut -)
else
  SALIDAS=(-c:v rawvideo -pix_fmt yuv420p -f nut -)
fi
( python3 "$(dirname "$0")/ventana_al_frente.py" "4 camaras" 20 >/dev/null 2>&1 & )
exec -a ver_4_camaras_ffmpeg ffmpeg -hide_banner -loglevel error \
  -f v4l2 -thread_queue_size 64 -input_format mjpeg -video_size 640x480 -framerate 30 -i $B/usb-Quanta_HP_Wide_Vision_HD_Camera_0001-video-index0 \
  -f v4l2 -thread_queue_size 64 -input_format yuyv422 -video_size 352x288 -i $B/usb-Etron_Technologies_USB2.0_Camera-video-index0 \
  -f v4l2 -thread_queue_size 64 -input_format mjpeg -video_size 640x480 -framerate 30 -i $B/usb-GENERAL_GENERAL_WEBCAM_JH0319_20200710_v012-video-index0 \
  -f v4l2 -thread_queue_size 64 -input_format yuyv422 -video_size 640x480 -i $B/usb-_Webcam_C170-video-index0 \
  -filter_complex "$FILTRO" "${SALIDAS[@]}" \
| ffplay -hide_banner -loglevel error -window_title "4 camaras" -alwaysontop -left 900 -top 60 -x 1000 -y 750 \
    -fflags nobuffer -flags low_delay -framedrop -
