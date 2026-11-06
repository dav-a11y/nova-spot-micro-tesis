#!/usr/bin/env python3
"""Video de evidencia de una caminata (5-nov): las cámaras sincronizadas en un mosaico 2×2 con un rótulo.

Cada cámara se recorta desde el inicio de la caminata (caminata.inicio.txt) usando la hora de su primer fotograma
(video.inicio.txt, ya en la escala de tiempo del PC de control). Se usan las cámaras con video válido, en este orden:
frontal (PC), trasera (portátil 2), derecha (Logitech), debajo (PC con Windows), izquierda (General).

Uso: video_evidencia.py grabaciones/<caminata> --titulo "Gateo · política v27 s7013 · robot suspendido" [--salida x.mp4]
"""
import argparse
import subprocess
from pathlib import Path

CAMARAS = [("Frontal", "."), ("Trasera", "remota"), ("Derecha", "extra_logitech"), ("Debajo", "extra_windows"),
           ("Izquierda", "extra_general")]
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fotogramas(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(v)], capture_output=True, text=True)
    try:
        return int(r.stdout.strip().split(",")[0])
    except ValueError:
        return 0


def texto(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caminata", type=Path)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--duracion", type=float, default=62.0)
    ap.add_argument("--salida", type=Path)
    a = ap.parse_args()
    inicio = float((a.caminata / "caminata.inicio.txt").read_text())
    entradas, filtros, usadas = [], [], []
    for nombre, sub in CAMARAS:
        d = a.caminata / sub
        v = d / "video.mkv"
        if not v.exists() or not (d / "video.inicio.txt").exists() or fotogramas(v) < 300:
            continue
        desde = max(0.0, inicio - float((d / "video.inicio.txt").read_text()))
        k = len(usadas)
        entradas += ["-ss", f"{desde:.3f}", "-t", f"{a.duracion:.1f}", "-i", str(v)]
        filtros.append(f"[{k}:v]setpts=PTS-STARTPTS,fps=30,scale=640:360:force_original_aspect_ratio=decrease,"
                       f"pad=640:360:(ow-iw)/2:(oh-ih)/2,drawtext=fontfile={FUENTE}:text='{texto(nombre)}':x=10:y=10:"
                       f"fontsize=22:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=6[c{k}]")
        usadas.append(nombre)
        if len(usadas) == 4:
            break
    if not usadas:
        raise SystemExit("ninguna cámara con video válido")
    while len(usadas) < 4:                       # celdas vacías en negro
        k = len(usadas)
        filtros.append(f"color=c=black:s=640x360:r=30:d={a.duracion}[c{k}]")
        usadas.append("—")
    filtros.append("[c0][c1][c2][c3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[m]")
    filtros.append(f"[m]pad=1280:780:0:60:black,drawtext=fontfile={FUENTE}:text='{texto(a.titulo)}':x=(w-tw)/2:y=18:"
                   f"fontsize=28:fontcolor=white,drawtext=fontfile={FUENTE}:text='%{{pts\\:hms}}':x=w-tw-14:y=22:"
                   f"fontsize=20:fontcolor=white@0.8[out]")
    salida = a.salida or a.caminata / "evidencia.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", ";".join(filtros), "-map", "[out]",
           "-t", f"{a.duracion:.1f}", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(salida)]
    subprocess.run(cmd, check=True)
    print(f"{salida} ({', '.join(u for u in usadas if u != '—')})")


if __name__ == "__main__":
    main()
