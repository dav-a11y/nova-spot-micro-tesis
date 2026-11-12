#!/usr/bin/env python3
"""Comprime a H.264 los videos MJPEG de una caminata (≈10 veces menos espacio).

Para cada video.mkv de la carpeta (principal, remota/ y extra_*/) que siga en MJPEG:
recomprime con libx264 (CRF 23, preset veryfast) conservando las marcas de tiempo
absolutas (-copyts), comprueba que el número de fotogramas y la hora del primer
fotograma coinciden con el original y solo entonces sustituye el original.

Uso: python3 comprimir_videos.py grabaciones/<caminata> [más carpetas]
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def info(video):
    s = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-count_packets", "-show_entries",
         "stream=codec_name,nb_read_packets", "-of", "json", str(video)]))["streams"][0]
    p = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                 "packet=pts_time", "-read_intervals", "%+#1", "-of", "csv=p=0", str(video)])
    return s["codec_name"], int(s["nb_read_packets"]), float(p.decode().split()[0])


def comprimir(video):
    codec, n, t0 = info(video)
    if codec != "mjpeg":
        return f"{video.parent.name}/{video.name}: ya en {codec}"
    tmp = video.with_suffix(".h264.mkv")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-copyts", "-i", str(video), "-map", "0:v",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                        "-vsync", "passthrough", str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        tmp.unlink(missing_ok=True)
        return f"{video}: ERROR {r.stderr.strip()[-200:]}"
    _, n2, t2 = info(tmp)
    if abs(n2 - n) > 2 or abs(t2 - t0) > 0.05:
        tmp.unlink()
        return f"{video}: NO coincide (fotogramas {n} -> {n2}, inicio {t0:.3f} -> {t2:.3f}); se conserva el original"
    antes, despues = video.stat().st_size, tmp.stat().st_size
    tmp.replace(video)
    return f"{video.parent.name}/{video.name}: {antes / 1e6:.0f} MB -> {despues / 1e6:.0f} MB"


def main():
    videos = [v for c in sys.argv[1:] for v in sorted(Path(c).rglob("video.mkv"))]
    with ThreadPoolExecutor(4) as ex:
        for linea in ex.map(comprimir, videos):
            print("  ", linea, flush=True)


if __name__ == "__main__":
    main()
