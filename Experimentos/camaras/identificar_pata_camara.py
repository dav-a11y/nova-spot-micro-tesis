#!/usr/bin/env python3
"""Identifica en las cámaras qué pata es cada articulación.

Graba las dos cámaras mientras el firmware mueve una sola articulación ±10° (orden
'!' + índice: 0-3 coxas, 4-7 fémures, 8-b tibias) y marca en rojo la zona que se
mueve entre los dos extremos. Guarda identificacion_<índice>.jpg en grabaciones/identificacion/.

Uso: python3 identificar_pata_camara.py 4        (fémur 1, pata 1)
"""
import os
import subprocess
import sys
import termios
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
NOMBRES = ["coxa 1", "coxa 2", "coxa 3", "coxa 4", "femur 1", "femur 2", "femur 3", "femur 4",
           "tibia 1", "tibia 2", "tibia 3", "tibia 4"]


def primer_fotograma(video):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "packet=pts_time", "-read_intervals", "%+#1", "-of", "csv=p=0", str(video)])
    return float(s.decode().split()[0])


def fotograma(video, t_abs, t0):
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, (t_abs - t0) * 1000))
    ok, img = cap.read()
    cap.release()
    return img


def main():
    idx = int(sys.argv[1], 16) if len(sys.argv[1]) == 1 else int(sys.argv[1])
    car = "0123456789ab"[idx]
    carpeta = AQUI / "grabaciones" / "identificacion"
    carpeta.mkdir(parents=True, exist_ok=True)
    local, remoto_local = carpeta / f"l_{idx}.mkv", carpeta / f"r_{idx}.mkv"
    ff = ["-v", "error", "-y", "-f", "v4l2", "-input_format", "mjpeg", "-video_size", "1280x720",
          "-framerate", "30", "-use_wallclock_as_timestamps", "1"]
    pl = subprocess.Popen(["ffmpeg", *ff, "-i", "/dev/video1", "-c:v", "copy", "-copyts", str(local)],
                          stdin=subprocess.PIPE)
    t1 = time.time(); rh = float(subprocess.check_output(["ssh", "-o", "BatchMode=yes", "pc2-camara", "date +%s.%N"]))
    desfase = rh - (t1 + time.time()) / 2
    pr = subprocess.Popen(["ssh", "-o", "BatchMode=yes", "pc2-camara",
                           "exec ffmpeg " + " ".join(ff) + " -i /dev/video0 -c:v copy -copyts /tmp/ident.mkv"],
                          stdin=subprocess.PIPE)
    time.sleep(1.5)
    fd = os.open("/dev/ttyACM0", os.O_RDWR | os.O_NOCTTY)
    a = termios.tcgetattr(fd); a[4] = a[5] = termios.B115200; a[0] = a[1] = a[3] = 0
    a[2] |= termios.CLOCAL | termios.CREAD; a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, a)
    time.sleep(2.5); os.read(fd, 65536); os.write(fd, ("!" + car).encode())
    extremos, buf, fin = {}, b"", time.time() + 10
    while time.time() < fin:
        buf += os.read(fd, 4096)
        while b"\n" in buf:
            l, buf = buf.split(b"\n", 1)
            p = l.decode(errors="replace").strip().split(",")
            if len(p) == 31 and p[0] == "DATA" and p[2] == f"UNA_I{idx}":
                extremos.setdefault(int(p[3 + idx]), time.time())   # primera vez en cada ángulo
    os.close(fd)
    time.sleep(0.5)
    for proc in (pl, pr):
        proc.stdin.write(b"q"); proc.stdin.flush(); proc.wait(timeout=10)
    subprocess.run(["scp", "-q", "pc2-camara:/tmp/ident.mkv", str(remoto_local)], check=True)
    angulos = sorted(extremos)
    alto, bajo = extremos[angulos[-1]] + 0.35, extremos[angulos[0]] + 0.35   # tras llegar y asentarse
    filas = []
    for nombre, video, corr in (("camara 1", local, 0.0), ("camara 2", remoto_local, desfase)):
        t0 = primer_fotograma(video)
        a_img, b_img = fotograma(video, alto + corr, t0), fotograma(video, bajo + corr, t0)
        dif = cv2.GaussianBlur(cv2.absdiff(cv2.cvtColor(a_img, cv2.COLOR_BGR2GRAY),
                                           cv2.cvtColor(b_img, cv2.COLOR_BGR2GRAY)), (21, 21), 0)
        mascara = dif > max(25, np.percentile(dif, 99.5) * 0.5)
        marcada = a_img.copy(); marcada[mascara] = (0.4 * marcada[mascara] + [0, 0, 150]).astype(np.uint8)
        ys, xs = np.nonzero(mascara)
        if len(xs):
            cv2.rectangle(marcada, (int(np.percentile(xs, 2)), int(np.percentile(ys, 2))),
                          (int(np.percentile(xs, 98)), int(np.percentile(ys, 98))), (0, 0, 255), 4)
        for img, txt in ((marcada, f"{nombre}: {NOMBRES[idx]} en {angulos[-1]}"), (b_img, f"en {angulos[0]}")):
            cv2.putText(img, txt, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3)
        filas.append(np.hstack([cv2.resize(marcada, (640, 360)), cv2.resize(b_img, (640, 360))]))
    salida = carpeta / f"identificacion_{idx}.jpg"
    cv2.imwrite(str(salida), np.vstack(filas))
    print(salida)


if __name__ == "__main__":
    main()
