#!/usr/bin/env python3
"""Comprueba con las cámaras laterales el sentido físico de cada fémur y tibia.

Con el robot sostenido en su postura (modo @), mueve una articulación cada vez con la
convención del programa: fémur «adelante» (o > 0) y tibia «levantar» (elevación > 0),
de forma senoidal. Con flujo óptico mide hacia dónde va la pata en la imagen:
- cámara del portátil 2 (lado derecho: patas 1 y 3): delante del robot = izquierda de la imagen;
- Logitech (lado izquierdo: patas 2 y 4): delante del robot = derecha de la imagen.
La parte trasera es la carcasa amarilla. Para el fémur se mira el movimiento horizontal
del pie; para la tibia, el vertical (levantar = el pie sube).

Uso: python3 verificar_sentidos.py
"""
import json
import os
import subprocess
import termios
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
BASE = [159, 45, 61, 82, 110, 100, 100, 100, 100, 80, 100, 70]
SIGNO_FEMUR = {1: -1, 2: 1, 3: -1, 4: 1}
SIGNO_TIBIA = {1: -1, 2: -1, 3: -1, 4: -1}
LADO = {1: "derecho", 2: "izquierdo", 3: "derecho", 4: "izquierdo"}
SSH = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]
AMP, FREC, CICLOS = 10.0, 0.5, 3


def primer_fotograma(video):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "packet=pts_time", "-read_intervals", "%+#1", "-of", "csv=p=0", str(video)])
    return float(s.decode().split()[0])


def mover():
    fd = os.open("/dev/ttyACM0", os.O_RDWR | os.O_NOCTTY)
    a = termios.tcgetattr(fd); a[4] = a[5] = termios.B115200; a[0] = a[1] = a[3] = 0
    a[2] |= termios.CLOCAL | termios.CREAD; a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, a)
    time.sleep(2.5); os.read(fd, 65536); os.write(fd, b"@")
    buf, fin = b"", time.time() + 10
    while b"STREAM_LISTO" not in buf and time.time() < fin:
        buf += os.read(fd, 4096)

    def enviar(g):
        os.write(fd, ("S," + ",".join(str(int(round(x))) for x in g) + "\n").encode())
        time.sleep(0.03); os.read(fd, 4096)

    for _ in range(60):
        enviar(BASE)
    pruebas = {}
    for tipo in ("femur", "tibia"):
        for pata in (1, 2, 3, 4):
            i = 3 + pata if tipo == "femur" else 7 + pata
            ts, cs = [], []
            t0 = time.time()
            while time.time() - t0 < CICLOS / FREC:
                s = np.sin(2 * np.pi * FREC * (time.time() - t0))
                if tipo == "femur":
                    c = AMP * s                                   # o > 0 = adelante
                    servo = BASE[i] + SIGNO_FEMUR[pata] * c
                else:
                    c = AMP * max(0.0, s)                         # elevación > 0 = levantar
                    servo = BASE[i] + SIGNO_TIBIA[pata] * c
                g = list(BASE); g[i] = servo
                enviar(g); ts.append(time.time()); cs.append(c)
            for _ in range(30):
                enviar(BASE)
            pruebas[(tipo, pata)] = (np.array(ts), np.array(cs))
            print(f"{tipo} {pata}: ±{AMP:.0f}° hecho", flush=True)
    os.write(fd, b"X\n"); time.sleep(0.3); os.close(fd)
    return pruebas


def flujo(video, t0v, corr, ts, cs, retardo):
    """Correlación del flujo horizontal y vertical de la zona que se mueve con la orden."""
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, (ts[0] + corr + retardo - t0v) * 1000))
    previo, dxs, dys, tt = None, [], [], []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = t0v + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 - corr - retardo
        if t > ts[-1]:
            break
        g = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (320, 180))
        if previo is not None:
            f = cv2.calcOpticalFlowFarneback(previo, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag = np.hypot(f[..., 0], f[..., 1])
            m = mag > np.percentile(mag, 97)                       # zona que más se mueve
            dxs.append(float(f[..., 0][m].mean())); dys.append(float(f[..., 1][m].mean())); tt.append(t)
        previo = g
    cap.release()
    if len(tt) < 20:
        return None
    vel = np.gradient(np.interp(tt, ts, cs), tt)                   # velocidad de la orden
    rx = float(np.corrcoef(dxs, vel)[0, 1]); ry = float(np.corrcoef(dys, vel)[0, 1])
    return rx, ry


def main():
    carpeta = AQUI / "grabaciones" / time.strftime("sentidos_%Y%m%d_%H%M%S")
    carpeta.mkdir(parents=True)
    log = subprocess.Popen(["ffmpeg", "-v", "error", "-f", "v4l2", "-input_format", "yuyv422", "-video_size", "640x480",
                            "-framerate", "30", "-use_wallclock_as_timestamps", "1", "-i", "/dev/video3",
                            "-c:v", "mjpeg", "-q:v", "4", "-copyts", str(carpeta / "logitech.mkv")], stdin=subprocess.PIPE)
    t1 = time.time(); rh = float(subprocess.check_output(["ssh", *SSH, "pc2-camara", "date +%s.%N"]))
    desfase = rh - (t1 + time.time()) / 2
    rem = subprocess.Popen(["ssh", *SSH, "pc2-camara", "exec ffmpeg -v error -f v4l2 -input_format mjpeg -video_size "
                            "1280x720 -framerate 30 -use_wallclock_as_timestamps 1 -i /dev/video0 -c:v copy -copyts "
                            "-y /tmp/sentidos.mkv"], stdin=subprocess.PIPE)
    time.sleep(2)
    pruebas = mover()
    for p in (log, rem):
        p.stdin.write(b"q"); p.stdin.flush(); p.wait(timeout=20)
    subprocess.run(["scp", "-q", *SSH, "pc2-camara:/tmp/sentidos.mkv", str(carpeta / "hp_pc2.mkv")], check=True)
    subprocess.run(["ssh", *SSH, "pc2-camara", "rm -f /tmp/sentidos.mkv"])
    camaras = {"derecho": (carpeta / "hp_pc2.mkv", desfase, -1, 0.06), "izquierdo": (carpeta / "logitech.mkv", 0.0, 1, 0.12)}
    resultado = {}
    for (tipo, pata), (ts, cs) in pruebas.items():
        video, corr, delante, retardo = camaras[LADO[pata]]
        r = flujo(video, primer_fotograma(video), corr, ts, cs, retardo)
        if r is None:
            resultado[f"{tipo}{pata}"] = "sin datos"; continue
        rx, ry = r
        if tipo == "femur":
            sentido = rx * delante
            texto = ("ADELANTE (correcto)" if sentido > 0.3 else "ATRÁS (signo INVERTIDO)" if sentido < -0.3
                     else "no concluyente")
        else:
            texto = ("SUBE (correcto)" if ry < -0.3 else "BAJA (signo INVERTIDO)" if ry > 0.3 else "no concluyente")
        resultado[f"{tipo}{pata}"] = dict(r_horizontal=round(rx, 2), r_vertical=round(ry, 2), conclusion=texto)
        print(f"{tipo} {pata} ({LADO[pata]}): r_x {rx:+.2f} r_y {ry:+.2f} -> {texto}")
    (carpeta / "sentidos.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(carpeta)


if __name__ == "__main__":
    main()
