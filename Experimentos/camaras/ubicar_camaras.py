#!/usr/bin/env python3
"""Ubica las cámaras moviendo una pata cada vez.

Graba a la vez las 4 cámaras (HP de este PC, Logitech, celular y HP del portátil 2)
con el robot sostenido en su postura base (modo @) mientras mueve, uno tras otro, los
fémures de las patas 1-4 de forma senoidal (±12°, 0,5 Hz, 3 ciclos). Para cada cámara y
pata calcula, píxel a píxel, la correlación del brillo con la orden: solo la pata que se
mueve sigue ese ritmo (la gente, los cables y los cambios de exposición no). Con el tamaño (cerca/lejos) y la posición horizontal de cada pata
se deduce desde qué lado mira cada cámara (patas 1 y 3 = lado derecho del robot,
2 y 4 = izquierdo; 1 y 2 delante, 3 y 4 detrás).
Deja en grabaciones/ubicacion_<hora>/: un mosaico por cámara, ubicacion.json y el resumen.

Uso: python3 ubicar_camaras.py
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
LADO = {1: "derecho", 2: "izquierdo", 3: "derecho", 4: "izquierdo"}
EXTREMO = {1: "delante", 2: "delante", 3: "detrás", 4: "detrás"}
SSH = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]


def primer_fotograma(video):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "packet=pts_time", "-read_intervals", "%+#1", "-of", "csv=p=0", str(video)])
    return float(s.decode().split()[0])


def fotograma(video, t_abs, t0):
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, (t_abs - t0) * 1000))
    ok, img = cap.read()
    cap.release()
    return img if ok else None


BASE = [159, 45, 61, 82, 110, 100, 100, 100, 100, 80, 100, 70]
AMPLITUD, FRECUENCIA, CICLOS = 12.0, 0.5, 3


def mover_femures():
    """Modo @: postura base sostenida y cada fémur oscilando por turno.

    Devuelve {pata: (tiempos, desviación de la orden en grados)} con la hora real de cada orden."""
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
    ordenes = {}
    for pata in (1, 2, 3, 4):
        i, ts, ds = 3 + pata, [], []
        t0 = time.time()
        while time.time() - t0 < CICLOS / FRECUENCIA:
            d = AMPLITUD * np.sin(2 * np.pi * FRECUENCIA * (time.time() - t0))
            g = list(BASE); g[i] = BASE[i] + d
            enviar(g); ts.append(time.time()); ds.append(d)
        for _ in range(40):
            enviar(BASE)
        ordenes[pata] = (np.array(ts), np.array(ds))
        print(f"pata {pata}: fémur oscilando ±{AMPLITUD:.0f}° alrededor de {BASE[i]}°", flush=True)
    os.write(fd, b"X\n"); time.sleep(0.3); os.close(fd)
    return ordenes


def retardo_camara(video, t0, corr, pruebas):
    """Retardo de la cámara (0-1,5 s): el que maximiza la correlación de los píxeles más ligados a la orden."""
    mejor = (0.12, -1.0)
    for retardo in np.arange(0.0, 1.51, 0.06):
        puntos = []
        for ts, ds in pruebas.values():
            mapa, _ = correlacion(video, t0, corr, ts, ds, retardo)
            if mapa is not None:
                puntos.append(np.percentile(mapa, 99.5))
        if puntos and np.mean(puntos) > mejor[1]:
            mejor = (float(retardo), float(np.mean(puntos)))
    return mejor


def correlacion(video, t0, corr, ts, ds, retardo=0.12):
    """Mapa |r| entre el brillo de cada píxel (160×90) y la orden, durante la oscilación."""
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, (ts[0] + corr + retardo - t0) * 1000))
    imgs, tiempos = [], []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = t0 + cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 - corr
        if t > ts[-1] + retardo:
            break
        imgs.append(cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (160, 90)).astype(np.float32))
        tiempos.append(t)
        ultimo = img
    cap.release()
    if len(imgs) < 10:
        return None, None
    X = np.array(imgs).reshape(len(imgs), -1)
    o = np.interp(np.array(tiempos) - retardo, ts, ds)
    X -= X.mean(0); o -= o.mean()
    r = (o @ X) / (np.linalg.norm(o) * np.linalg.norm(X, axis=0) + 1e-9)
    return np.abs(r).reshape(90, 160), ultimo


def main():
    carpeta = AQUI / "grabaciones" / time.strftime("ubicacion_%Y%m%d_%H%M%S")
    carpeta.mkdir(parents=True)
    camaras = [("hp_pc1", ["-input_format", "mjpeg", "-video_size", "1280x720", "-framerate", "30"], "/dev/video1",
                ["-c:v", "copy"])]
    for c in json.loads((AQUI / "camaras_extra.json").read_text())["camaras"]:
        for ajuste in c.get("previo", []):
            subprocess.run(["v4l2-ctl", "-d", c["dispositivo"], "-c", ajuste], capture_output=True)
        camaras.append((c["nombre"], c["entrada"], c["dispositivo"], c["salida"]))
    procs = []
    for nombre, entrada, disp, salida in camaras:
        procs.append(subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "v4l2", *entrada,
                                       "-use_wallclock_as_timestamps", "1", "-i", disp, *salida, "-copyts",
                                       str(carpeta / f"{nombre}.mkv")], stdin=subprocess.PIPE))
    t1 = time.time(); rh = float(subprocess.check_output(["ssh", *SSH, "pc2-camara", "date +%s.%N"]))
    desfase = rh - (t1 + time.time()) / 2
    remoto = subprocess.Popen(["ssh", *SSH, "pc2-camara", "exec ffmpeg -hide_banner -loglevel error -f v4l2 "
                               "-input_format mjpeg -video_size 1280x720 -framerate 30 -use_wallclock_as_timestamps 1 "
                               "-i /dev/video0 -c:v copy -copyts -y /tmp/ubicacion.mkv"], stdin=subprocess.PIPE)
    time.sleep(2.0)
    pruebas = mover_femures()
    np.savez(carpeta / "ordenes.npz", **{f"t{p}": v[0] for p, v in pruebas.items()},
             **{f"d{p}": v[1] for p, v in pruebas.items()})
    time.sleep(0.5)
    for p in procs + [remoto]:
        p.stdin.write(b"q"); p.stdin.flush()
    for p in procs + [remoto]:
        p.wait(timeout=20)
    subprocess.run(["scp", "-q", *SSH, "pc2-camara:/tmp/ubicacion.mkv", str(carpeta / "hp_pc2.mkv")], check=True)
    videos = {n: (carpeta / f"{n}.mkv", 0.0) for n, *_ in camaras}
    videos["hp_pc2"] = (carpeta / "hp_pc2.mkv", desfase)
    resultado = {}
    for nombre, (video, corr) in videos.items():
        t0 = primer_fotograma(video)
        fila, celdas = {}, []
        retardo, r99 = retardo_camara(video, t0, corr, pruebas)
        print(f"{nombre}: retardo {retardo * 1000:.0f} ms (r99,5 = {r99:.2f})", flush=True)
        for pata, (ts, ds) in pruebas.items():
            mapa, a_img = correlacion(video, t0, corr, ts, ds, retardo)
            if mapa is None:
                fila[pata] = dict(visible=False); continue
            mascara_peq = cv2.morphologyEx((mapa > 0.6).astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
            h, w = a_img.shape[:2]
            mascara = cv2.resize(mascara_peq.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
            area = float(mascara_peq.mean())
            ys, xs = np.nonzero(mascara)
            fila[pata] = dict(visible=area > 0.003, area_pct=round(100 * area, 2),
                              x=round(float(xs.mean() / w), 2) if len(xs) else None,
                              y=round(float(ys.mean() / h), 2) if len(ys) else None)
            marcada = a_img.copy(); marcada[mascara] = (0.4 * marcada[mascara] + [0, 0, 150]).astype(np.uint8)
            cv2.putText(marcada, f"{nombre}: pata {pata} ({area * 100:.1f}%)", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            celdas.append(cv2.resize(marcada, (480, int(480 * h / w))))
        if celdas:
            cv2.imwrite(str(carpeta / f"{nombre}_patas.jpg"), np.hstack(celdas))
        vistas = {p: d for p, d in fila.items() if d.get("visible")}
        conclusion = "no ve ninguna pata moverse"
        if vistas:
            cerca = max(vistas, key=lambda p: vistas[p]["area_pct"])
            der = sum(vistas[p]["area_pct"] for p in vistas if LADO[p] == "derecho")
            izq = sum(vistas[p]["area_pct"] for p in vistas if LADO[p] == "izquierdo")
            dl = sum(vistas[p]["area_pct"] for p in vistas if EXTREMO[p] == "delante")
            dt = sum(vistas[p]["area_pct"] for p in vistas if EXTREMO[p] == "detrás")
            lado = "derecho" if der > 1.5 * izq else "izquierdo" if izq > 1.5 * der else "centro (de frente o de atrás)"
            extremo = "delantero" if dl > 1.5 * dt else "trasero" if dt > 1.5 * dl else "centro (de lado)"
            orden_x = " → ".join(f"P{p}" for p in sorted(vistas, key=lambda p: vistas[p]["x"]))
            conclusion = (f"ve las patas {sorted(vistas)}; la más cercana es la {cerca}; lado {lado}, "
                          f"extremo {extremo}; de izquierda a derecha en la imagen: {orden_x}")
        resultado[nombre] = dict(patas=fila, conclusion=conclusion, retardo_s=retardo)
        print(f"{nombre:9s} {conclusion}", flush=True)
    (carpeta / "ubicacion.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(carpeta)


if __name__ == "__main__":
    main()
