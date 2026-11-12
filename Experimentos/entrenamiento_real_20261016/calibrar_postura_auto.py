#!/usr/bin/env python3
"""Calibración automática del punto neutro de cada fémur con las cámaras laterales.

En la simulación las dos patas de un mismo lado están paralelas en la postura base. Con
el robot sostenido en su postura base (calibracion_postura.json aplicado), cada fémur
oscila ±5° (0,5 Hz, 3 ciclos) mientras graban la cámara de su lado y la tablet:
- portátil 2 (lado derecho: patas 1 y 3; delante del robot = izquierda de la imagen),
- Logitech (lado izquierdo: patas 2 y 4; delante = derecha de la imagen).
Los píxeles cuyo brillo sigue a la oscilación son la pata (sin confundirse con el fondo);
su eje principal en la postura base da la inclinación de la pata. En cada lado, la
diferencia delantera − trasera es el error (la pata entera gira con el fémur, 1° = 1°),
que se corrige repartido entre las dos. Se repite hasta que la diferencia sea < 1,5°.

Uso: calibrar_postura_auto.py [--iteraciones 3]
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
import ejecutar_politica_robot as R  # noqa: E402

CAM = HERE.parent / "camaras"
SSH = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]
LADOS = {"derecho": dict(patas=(1, 3), delante=-1), "izquierdo": dict(patas=(2, 4), delante=+1)}
AMP, FREC, CICLOS = 5.0, 0.5, 3


def oscilar(fd, lec, stand):
    """Postura base sostenida; cada fémur oscila por turno. Devuelve {pata: (tiempos, Δ°)}."""
    def enviar(g):
        os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode()); lec.linea(timeout=0.3); time.sleep(0.03)
    base = R.a_grados_servo(stand)
    for _ in range(60):
        enviar(base)
    pruebas = {}
    for pata in (1, 2, 3, 4):
        i = 3 + pata
        ts, ds = [], []
        t0 = time.time()
        while time.time() - t0 < CICLOS / FREC:
            d = AMP * np.sin(2 * np.pi * FREC * (time.time() - t0))
            g = list(base); g[i] = int(round(base[i] + R.SIGNO_FEMUR[pata] * d))
            enviar(g); ts.append(time.time()); ds.append(d)
        for _ in range(30):
            enviar(base)
        pruebas[pata] = (np.array(ts), np.array(ds))
    return pruebas


def grabar_inicio(carpeta):
    import cv2  # noqa: F401  (comprobación temprana de OpenCV del sistema no necesaria aquí)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteraciones", type=int, default=3)
    a = ap.parse_args()
    carpeta = CAM / "grabaciones" / time.strftime("calibracion_postura_%Y%m%d_%H%M%S")
    carpeta.mkdir(parents=True)
    stand = np.tile(E.STAND, 4).astype(float)
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
    while True:
        l = lec.linea(timeout=8.0)
        if l is None:
            sys.exit("El Uno no respondió STREAM_LISTO")
        if l.startswith("STREAM_LISTO"):
            break
    historial = []
    try:
        for it in range(a.iteraciones):
            cal = json.loads((HERE / "calibracion_postura.json").read_text())
            R.CAL_POSTURA.clear(); R.CAL_POSTURA.update(cal["femur_offset_deg"])
            sub = carpeta / f"iteracion_{it + 1}"; sub.mkdir()
            # Grabación: Logitech (local), portátil 2 (remota) y tablet (/dev/video10).
            loc = subprocess.Popen(["ffmpeg", "-v", "error", "-f", "v4l2", "-input_format", "yuyv422", "-video_size",
                                    "640x480", "-framerate", "30", "-use_wallclock_as_timestamps", "1", "-i", "/dev/video3",
                                    "-c:v", "mjpeg", "-q:v", "4", "-copyts", str(sub / "logitech.mkv")], stdin=subprocess.PIPE)
            tab = subprocess.Popen(["ffmpeg", "-v", "error", "-f", "v4l2", "-use_wallclock_as_timestamps", "1", "-i",
                                    "/dev/video10", "-c:v", "mjpeg", "-q:v", "5", "-copyts", str(sub / "tablet.mkv")],
                                   stdin=subprocess.PIPE)
            t1 = time.time(); rh = float(subprocess.check_output(["ssh", *SSH, "pc2-camara", "date +%s.%N"]))
            desfase = rh - (t1 + time.time()) / 2
            rem = subprocess.Popen(["ssh", *SSH, "pc2-camara", "exec ffmpeg -v error -f v4l2 -input_format mjpeg "
                                    "-video_size 1280x720 -framerate 30 -use_wallclock_as_timestamps 1 -i /dev/video0 "
                                    "-c:v copy -copyts -y /tmp/calib.mkv"], stdin=subprocess.PIPE)
            time.sleep(2.0)
            pruebas = oscilar(fd, lec, stand)
            for p in (loc, tab, rem):
                p.stdin.write(b"q"); p.stdin.flush(); p.wait(timeout=20)
            subprocess.run(["scp", "-q", *SSH, "pc2-camara:/tmp/calib.mkv", str(sub / "hp_pc2.mkv")], check=True)
            np.savez(sub / "ordenes.npz", desfase=desfase, **{f"t{p}": v[0] for p, v in pruebas.items()},
                     **{f"d{p}": v[1] for p, v in pruebas.items()})
            # Medición con el Python del sistema (OpenCV).
            r = subprocess.run(["/usr/bin/python3", "-I", str(HERE / "medir_inclinacion_oscilacion.py"), str(sub)],
                               capture_output=True, text=True)
            print(r.stdout.strip(), r.stderr.strip()[-300:], flush=True)
            med = json.loads((sub / "inclinaciones.json").read_text())
            nuevo = dict(cal["femur_offset_deg"]); ok = True; resumen = {}
            for lado, info in LADOS.items():
                f, t = info["patas"]
                if str(f) not in med or str(t) not in med:
                    print(f"  {lado}: no se midieron las dos patas; sin cambio", flush=True); ok = False; continue
                diff = med[str(f)] - med[str(t)]          # + = la delantera más adelantada que la trasera
                resumen[lado] = diff
                if abs(diff) >= 1.5:
                    ok = False
                    nuevo[str(f)] = round(nuevo[str(f)] - diff / 2, 1)
                    nuevo[str(t)] = round(nuevo[str(t)] + diff / 2, 1)
                print(f"  {lado}: pata {f} {med[str(f)]:+.1f}°, pata {t} {med[str(t)]:+.1f}° -> diferencia {diff:+.1f}°", flush=True)
            historial.append(dict(iteracion=it + 1, correccion=cal["femur_offset_deg"], diferencias=resumen))
            if ok:
                print(f"Calibración terminada: los dos lados quedan paralelos ({cal['femur_offset_deg']}).", flush=True)
                break
            cal["femur_offset_deg"] = nuevo
            cal["nota"] = ("20-oct: corrección del punto neutro de cada fémur (+ = pie hacia delante), calibrada "
                           "automáticamente con las cámaras laterales (calibrar_postura_auto.py): patas de cada lado paralelas.")
            (HERE / "calibracion_postura.json").write_text(json.dumps(cal, indent=2, ensure_ascii=False))
            print(f"  nueva corrección: {nuevo}", flush=True)
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd)
        (carpeta / "historial.json").write_text(json.dumps(historial, indent=2, ensure_ascii=False))
        subprocess.run(["ssh", *SSH, "pc2-camara", "rm -f /tmp/calib.mkv"])


if __name__ == "__main__":
    main()
