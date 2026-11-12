#!/usr/bin/env python3
"""Ventana en directo con las 4 cámaras (2×2) para encuadrarlas.

HP de este PC (/dev/video1), Logitech (/dev/video3), celular DroidCam (/dev/video0, girada)
y HP del portátil 2 (pc2-camara /dev/video0, por SSH en MJPEG). Cada vista lleva una cruz
central, tercios y los fps reales; si una cámara no da imagen sale «SIN IMAGEN».
Tecla q, Esc o la X de la ventana: cerrar (libera las cámaras para grabar).

Uso: python3 vista_camaras.py
"""
import fcntl
import subprocess
import sys
import threading
import time

import cv2
import numpy as np

ANCHO, ALTO = 800, 450


class Camara(threading.Thread):
    def __init__(self, nombre, abrir, girar=False):
        super().__init__(daemon=True)
        self.nombre, self.abrir, self.girar = nombre, abrir, girar
        self.imagen, self.t, self.fps, self.vivo = None, 0.0, 0.0, True

    def guardar(self, img):
        if self.girar:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        ahora = time.time()
        if self.t:
            self.fps = 0.9 * self.fps + 0.1 / max(1e-3, ahora - self.t)
        self.imagen, self.t = img, ahora

    def run(self):
        while self.vivo:
            try:
                self.abrir(self)
            except Exception:
                pass
            time.sleep(1.0)          # reintento si la cámara se cae


def local(dispositivo, ancho=None, alto=None, mjpg=False):
    def abrir(cam):
        cap = cv2.VideoCapture(dispositivo, cv2.CAP_V4L2)
        if mjpg:
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        if ancho:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
        while cam.vivo:
            ok, img = cap.read()
            if not ok:
                break
            cam.guardar(img)
        cap.release()
    return abrir


def remota(alias, dispositivo):
    def abrir(cam):
        # 27-oct: -nostdin; sin él, ffmpeg en Windows se quedaba a veces colgado sin enviar imagen.
        p = subprocess.Popen(["ssh", "-n", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", alias,
                              f"exec ffmpeg -hide_banner -loglevel error -f v4l2 -input_format mjpeg "
                              f"-video_size 1280x720 -framerate 30 -i {dispositivo} -c:v copy -f mjpeg -"],
                             stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        buf = b""
        while cam.vivo:
            d = p.stdout.read(65536)
            if not d:
                break
            buf += d
            fin = buf.rfind(b"\xff\xd9")
            if fin < 0:
                continue
            ini = buf.rfind(b"\xff\xd8", 0, fin)
            if ini >= 0:
                img = cv2.imdecode(np.frombuffer(buf[ini:fin + 2], np.uint8), cv2.IMREAD_COLOR)
                if img is not None:
                    cam.guardar(img)
            buf = buf[fin + 2:]
        p.kill()
    return abrir


def panel(cam):
    if cam.imagen is None or time.time() - cam.t > 2.0:
        img = np.zeros((ALTO, ANCHO, 3), np.uint8)
        cv2.putText(img, "SIN IMAGEN", (ANCHO // 2 - 130, ALTO // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
    else:
        h, w = cam.imagen.shape[:2]
        e = min(ANCHO / w, ALTO / h)
        peq = cv2.resize(cam.imagen, (int(w * e), int(h * e)))
        img = np.zeros((ALTO, ANCHO, 3), np.uint8)
        y0, x0 = (ALTO - peq.shape[0]) // 2, (ANCHO - peq.shape[1]) // 2
        img[y0:y0 + peq.shape[0], x0:x0 + peq.shape[1]] = peq
        for k in (1, 2):                                  # tercios
            cv2.line(img, (ANCHO * k // 3, 0), (ANCHO * k // 3, ALTO), (0, 200, 0), 1)
            cv2.line(img, (0, ALTO * k // 3), (ANCHO, ALTO * k // 3), (0, 200, 0), 1)
        cv2.drawMarker(img, (ANCHO // 2, ALTO // 2), (0, 255, 255), cv2.MARKER_CROSS, 40, 2)
    cv2.rectangle(img, (0, 0), (ANCHO, 34), (0, 0, 0), -1)
    cv2.putText(img, f"{cam.nombre}   {cam.fps:4.1f} fps", (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return img


def local_ffmpeg(dispositivo, entrada, ancho, alto):
    """Cámara local leída con ffmpeg (Logitech y General Webcam cuelgan a OpenCV con la ventana abierta)."""
    def abrir(cam):
        dec = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "v4l2", *entrada, "-i", dispositivo,
                                "-vf", f"scale={ancho}:{alto}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        n = ancho * alto * 3
        while cam.vivo:
            d = dec.stdout.read(n)
            if len(d) < n:
                break
            cam.guardar(np.frombuffer(d, np.uint8).reshape(alto, ancho, 3))
        dec.kill()
    return abrir


def windows(alias, ffmpeg_exe, dispositivo):
    """Cámara del PC con Windows: H.264 por SSH (la Wi-Fi no da para MJPEG 720p), decodificado aquí."""
    def abrir(cam):
        # 27-oct: -nostdin; sin él, ffmpeg en Windows se quedaba a veces colgado sin enviar imagen.
        p = subprocess.Popen(["ssh", "-n", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", alias,
                              f'"{ffmpeg_exe}" -nostdin -hide_banner -loglevel error -f dshow -rtbufsize 300M -vcodec mjpeg '
                              f'-video_size 1280x720 -framerate 30 -i video="{dispositivo}" -c:v libx264 -preset ultrafast '
                              f'-tune zerolatency -g 30 -b:v 2500k -pix_fmt yuv420p -f mpegts -'],
                             stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        dec = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-fflags", "nobuffer", "-f", "mpegts",
                                "-i", "pipe:0", "-vf", "scale=960:540", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdin=p.stdout, stdout=subprocess.PIPE)
        p.stdout.close()
        n = 960 * 540 * 3
        while cam.vivo:
            d = dec.stdout.read(n)
            if len(d) < n:
                break
            cam.guardar(np.frombuffer(d, np.uint8).reshape(540, 960, 3))
        dec.kill(); p.kill()
        subprocess.run(["ssh", "-o", "BatchMode=yes", alias, "taskkill /IM ffmpeg.exe /F"], capture_output=True)
    return abrir


FFMPEG_WIN = (r"C:\Users\rapio\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
              r"\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe")


def main():
    # 26-oct: una sola ventana a la vez; dos copias se quitaban las cámaras entre sí (y la de Windows).
    global _cerrojo
    _cerrojo = open("/tmp/vista_camaras.lock", "w")
    try:
        fcntl.flock(_cerrojo, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit("vista_camaras.py ya está abierta; ciérrala (tecla q) antes de abrir otra.")
    # 21-oct: cinco cámaras; las USB por su ruta fija (/dev/v4l/by-id), que no cambia al reconectarlas.
    camaras = [
        Camara("1 HP de este PC", local_ffmpeg("/dev/v4l/by-id/usb-Quanta_HP_Wide_Vision_HD_Camera_0001-video-index0",
                                                     ["-input_format", "mjpeg", "-video_size", "1280x720", "-framerate", "30"], 960, 540)),
        Camara("2 Logitech C170", local_ffmpeg("/dev/v4l/by-id/usb-_Webcam_C170-video-index0",
                                                     ["-input_format", "yuyv422", "-video_size", "640x480", "-framerate", "30"], 640, 480)),
        Camara("3 General Webcam USB", local_ffmpeg("/dev/v4l/by-id/usb-GENERAL_GENERAL_WEBCAM_JH0319_20200710_v012-video-index0",
                                                          ["-input_format", "mjpeg", "-video_size", "1280x720", "-framerate", "30"], 960, 540)),
        Camara("4 Portatil 2 (Ethernet)", remota("pc2-camara", "/dev/video0")),
        Camara("5 PC Windows (Wi-Fi)", windows("pc-windows", FFMPEG_WIN, "HP Wide Vision HD Camera")),
    ]
    for c in camaras:
        c.start()
    cv2.namedWindow("Cuadrar camaras", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Cuadrar camaras", 2 * ANCHO, 4 * ALTO // 3)
    vista = False
    while True:
        p = [panel(c) for c in camaras]
        p.append(np.zeros_like(p[0]))                     # sexta casilla vacía
        cv2.imshow("Cuadrar camaras", np.vstack([np.hstack(p[:3]), np.hstack(p[3:])]))
        if cv2.waitKey(50) & 0xFF in (ord("q"), 27):
            break
        # 20-oct: cerrar la ventana con la X también termina el programa y libera las cámaras.
        # 21-oct: solo cuenta como cerrada si la ventana ya llegó a verse (al arrancar aún no lo está).
        visible = cv2.getWindowProperty("Cuadrar camaras", cv2.WND_PROP_VISIBLE)
        if visible >= 1:
            vista = True
        elif vista:
            break
    for c in camaras:
        c.vivo = False
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
