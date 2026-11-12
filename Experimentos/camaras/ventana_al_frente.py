#!/usr/bin/env python3
"""11-nov: trae al frente y deja «siempre encima» la ventana con el título dado (X11, sin wmctrl).

Uso: ventana_al_frente.py "4 camaras" [segundos_de_espera]
"""
import ctypes as C
import os
import sys
import time

X = C.cdll.LoadLibrary("libX11.so.6")
X.XOpenDisplay.restype = C.c_void_p
X.XOpenDisplay.argtypes = [C.c_char_p]
X.XDefaultRootWindow.restype = C.c_ulong
X.XDefaultRootWindow.argtypes = [C.c_void_p]
X.XInternAtom.restype = C.c_ulong
X.XInternAtom.argtypes = [C.c_void_p, C.c_char_p, C.c_int]
X.XGetWindowProperty.argtypes = [C.c_void_p, C.c_ulong, C.c_ulong, C.c_long, C.c_long, C.c_int, C.c_ulong,
                                 C.POINTER(C.c_ulong), C.POINTER(C.c_int), C.POINTER(C.c_ulong),
                                 C.POINTER(C.c_ulong), C.POINTER(C.c_void_p)]
X.XFree.argtypes = [C.c_void_p]
X.XSendEvent.argtypes = [C.c_void_p, C.c_ulong, C.c_int, C.c_long, C.c_void_p]
X.XFlush.argtypes = [C.c_void_p]
X.XRaiseWindow.argtypes = [C.c_void_p, C.c_ulong]


class ClientMessage(C.Structure):
    _fields_ = [("type", C.c_int), ("serial", C.c_ulong), ("send_event", C.c_int), ("display", C.c_void_p),
                ("window", C.c_ulong), ("message_type", C.c_ulong), ("format", C.c_int), ("data", C.c_long * 5)]


class XEvent(C.Union):
    _fields_ = [("xclient", ClientMessage), ("pad", C.c_long * 24)]


def prop(d, w, nombre, tipo):
    t, f, n, r, p = C.c_ulong(), C.c_int(), C.c_ulong(), C.c_ulong(), C.c_void_p()
    if X.XGetWindowProperty(d, w, X.XInternAtom(d, nombre, 0), 0, 4096, 0, tipo,
                            C.byref(t), C.byref(f), C.byref(n), C.byref(r), C.byref(p)) != 0 or not p.value:
        return None, 0, 0
    return p, n.value, f.value


def enviar(d, raiz, w, tipo, datos):
    e = XEvent()
    e.xclient.type, e.xclient.send_event, e.xclient.display = 33, 1, d   # ClientMessage
    e.xclient.window, e.xclient.message_type, e.xclient.format = w, X.XInternAtom(d, tipo, 0), 32
    for i, v in enumerate(datos):
        e.xclient.data[i] = v
    X.XSendEvent(d, raiz, 0, (1 << 20) | (1 << 19), C.byref(e))   # SubstructureRedirect|Notify


def main():
    titulo = sys.argv[1].encode()
    espera = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
    d = X.XOpenDisplay(os.environ.get("DISPLAY", ":1").encode())
    if not d:
        sys.exit("no se pudo abrir la pantalla X")
    raiz = X.XDefaultRootWindow(d)
    utf8 = X.XInternAtom(d, b"UTF8_STRING", 0)
    fin = time.time() + espera
    while time.time() < fin:
        p, n, _ = prop(d, raiz, b"_NET_CLIENT_LIST", 33)   # XA_WINDOW
        ventanas = list(C.cast(p, C.POINTER(C.c_ulong))[:n]) if p else []
        if p:
            X.XFree(p)
        for w in ventanas:
            q, m, _ = prop(d, w, b"_NET_WM_NAME", utf8)
            nombre = C.string_at(q, m) if q else b""
            if q:
                X.XFree(q)
            if nombre == titulo:
                enviar(d, raiz, w, b"_NET_WM_STATE", [1, X.XInternAtom(d, b"_NET_WM_STATE_ABOVE", 0), 0, 1, 0])
                enviar(d, raiz, w, b"_NET_ACTIVE_WINDOW", [1, 0, 0, 0, 0])
                X.XRaiseWindow(d, w)
                X.XFlush(d)
                print(f"ventana «{titulo.decode()}» al frente (id {w:#x})")
                return
        time.sleep(0.3)
    sys.exit(f"no apareció la ventana «{titulo.decode()}»")


if __name__ == "__main__":
    main()
