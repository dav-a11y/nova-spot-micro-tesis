#!/usr/bin/env python3
"""Visor de baja latencia para la Logitech C170 y General Webcam USB.

Uso: python3 vista_dos_camaras_rapida.py
Pulsa q o Esc para cerrar. Cada cámara se lee en su propio hilo y descarta
cuadros atrasados para priorizar imagen reciente sobre una cola fluida pero lenta.
"""
import threading
import time

import cv2
import numpy as np

CAMARAS = [("Logitech C170 USB", 3), ("General Webcam USB", 10)]
ANCHO, ALTO = 640, 360


class Lector(threading.Thread):
    def __init__(self, nombre, indice):
        super().__init__(daemon=True)
        self.nombre = nombre
        self.indice = indice
        self.frame = None
        self.fps = 0.0
        self.activo = True
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.indice, cv2.CAP_V4L2)
        # MJPEG reduce el tráfico USB en cámaras que ofrecen ese formato.
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        anterior = time.monotonic()
        while self.activo:
            ok, frame = self.cap.read()
            ahora = time.monotonic()
            if ok:
                dt = ahora - anterior
                if dt > 0:
                    inst = 1.0 / dt
                    self.fps = inst if self.fps == 0 else 0.8 * self.fps + 0.2 * inst
                anterior = ahora
                self.frame = frame
            else:
                time.sleep(0.02)
        self.cap.release()


def mostrar(lector):
    lienzo = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
    if lector.frame is None:
        cv2.putText(lienzo, "Esperando imagen...", (20, ALTO // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2)
    else:
        lienzo = cv2.resize(lector.frame, (ANCHO, ALTO), interpolation=cv2.INTER_AREA)
    cv2.rectangle(lienzo, (0, 0), (ANCHO, 32), (0, 0, 0), -1)
    cv2.putText(lienzo, f"{lector.nombre}  {lector.fps:.1f} fps", (10, 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 255, 140), 2)
    return lienzo


def main():
    lectores = [Lector(nombre, indice) for nombre, indice in CAMARAS]
    for lector in lectores:
        lector.start()
    ventana = "Dos camaras USB - baja latencia"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(ventana, 1280, 360)
    try:
        while True:
            cv2.imshow(ventana, np.hstack([mostrar(l) for l in lectores]))
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        for lector in lectores:
            lector.activo = False
        for lector in lectores:
            lector.join(timeout=2)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
