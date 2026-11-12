#!/usr/bin/env python3
"""Ventana con las 5 cámaras en vivo DURANTE las caminatas (21-oct).

La grabación (grabar_caminata.py) deja en vivo/ una imagen de cada cámara dos veces por segundo;
esta ventana las muestra en un mosaico 3 + 2 con su antigüedad. No abre ninguna cámara, así que
puede estar abierta todo el tiempo sin estorbar a las grabaciones. Entre caminatas las imágenes se
quedan quietas (se marca «sin caminata»). Tecla q o Esc: cerrar.

Uso: python3 vista_vivo.py
"""
import fcntl
import sys
import time
from pathlib import Path

import cv2
import numpy as np

VIVO = Path(__file__).resolve().parent / "vivo"
CAMARAS = [("1_hp_pc.jpg", "1 HP de este PC"), ("logitech.jpg", "2 Logitech"), ("general.jpg", "3 General Webcam"),
           ("portatil2.jpg", "4 Portatil 2"), ("windows.jpg", "5 PC Windows (abajo)")]
ANCHO, ALTO = 640, 360


def panel(archivo, titulo):
    img = np.zeros((ALTO, ANCHO, 3), np.uint8)
    f = VIVO / archivo
    edad = None
    if f.exists():
        edad = time.time() - f.stat().st_mtime
        im = cv2.imread(str(f))
        if im is not None:
            h, w = im.shape[:2]
            e = min(ANCHO / w, ALTO / h)
            peq = cv2.resize(im, (int(w * e), int(h * e)))
            y0, x0 = (ALTO - peq.shape[0]) // 2, (ANCHO - peq.shape[1]) // 2
            img[y0:y0 + peq.shape[0], x0:x0 + peq.shape[1]] = peq
    if edad is None:
        estado, color = "sin imagen todavia", (0, 0, 255)
    elif edad < 3:
        estado, color = "EN VIVO", (0, 220, 0)
    else:
        estado, color = f"sin caminata (hace {edad:.0f} s)", (0, 200, 255)
    cv2.rectangle(img, (0, 0), (ANCHO, 30), (0, 0, 0), -1)
    cv2.putText(img, titulo, (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, estado, (ANCHO - 260, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    return img


def main():
    # 26-oct: una sola ventana; grabar_caminata.py la abre sola si no está abierta.
    global _cerrojo
    _cerrojo = open("/tmp/vista_vivo.lock", "w")
    try:
        fcntl.flock(_cerrojo, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(0)
    VIVO.mkdir(exist_ok=True)
    cv2.namedWindow("Camaras en vivo (caminatas)", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camaras en vivo (caminatas)", 3 * ANCHO * 3 // 4, 2 * ALTO * 3 // 4)
    vista = False
    while True:
        p = [panel(a, t) for a, t in CAMARAS] + [np.zeros((ALTO, ANCHO, 3), np.uint8)]
        cv2.imshow("Camaras en vivo (caminatas)", np.vstack([np.hstack(p[:3]), np.hstack(p[3:])]))
        if cv2.waitKey(300) & 0xFF in (ord("q"), 27):
            break
        v = cv2.getWindowProperty("Camaras en vivo (caminatas)", cv2.WND_PROP_VISIBLE)
        if v >= 1:
            vista = True
        elif vista:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
