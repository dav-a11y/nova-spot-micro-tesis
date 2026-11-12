#!/usr/bin/env python3
"""Graba la caminata con la webcam mientras se ejecuta en el robot.

1) Empieza a grabar (ffmpeg, MJPEG 1280×720 a 30 fps) y anota la hora real de inicio.
2) Lanza ejecutar_politica_robot.py (base o PPO) con los mismos argumentos.
3) Al terminar la caminata, graba 2 s más y para.
Deja en grabaciones/<nombre>/: video.mkv, video.inicio.txt, caminata.csv y
caminata.inicio.txt, y en remota/ el video del segundo portátil (pc2-camara) ya
sincronizado con el reloj de este PC. Desde el 20-oct también graba las cámaras locales
de camaras_extra.json (Logitech y celular) en extra_<nombre>/, con la misma estructura.

Uso:
  python3 grabar_caminata.py --nombre base_01 -- --ciclos 10 --dt 0.03 --tibia 10
  python3 grabar_caminata.py --nombre ppo_01 -- --ciclos 10 --politica ppo_v4/semilla_37/policy.zip
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
EJECUTOR = RAIZ / "Experimentos/entrenamiento_real_20261016/ejecutar_politica_robot.py"
PYTHON = RAIZ / ".venv-mujoco/bin/python"


def primer_fotograma(video):
    """Hora (epoch, reloj de quien grabó) del primer fotograma; requiere grabar con -copyts."""
    salida = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                      "packet=pts_time", "-read_intervals", "%+#1", "-of", "json", str(video)])
    return float(json.loads(salida)["packets"][0]["pts_time"])


# 21-oct: imagen en vivo de cada cámara durante la grabación (2 por segundo, 640 px) en vivo/,
# para verlas con vista_vivo.py mientras el robot camina (la grabación ocupa las cámaras).
VIVO = AQUI / "vivo"
VIVO_LOCAL = ["-vf", "fps=2,scale=640:-1", "-update", "1", "-y"]
VIVO_REMOTO = "-vf fps=2,scale=640:-1 -c:v mjpeg -q:v 6 -f image2pipe -"


def lector_vivo(tubo, destino):
    """Lee JPEG seguidos de un tubo y deja el último en destino (escritura atómica)."""
    import threading

    def bucle():
        buf = b""
        while True:
            d = tubo.read(65536)
            if not d:
                break
            buf += d
            fin = buf.rfind(b"\xff\xd9")
            ini = buf.rfind(b"\xff\xd8", 0, fin) if fin >= 0 else -1
            if ini >= 0:
                tmp = destino.with_suffix(".tmp")
                tmp.write_bytes(buf[ini:fin + 2]); tmp.replace(destino)
                buf = buf[fin + 2:]
            elif len(buf) > 4_000_000:
                buf = b""
    threading.Thread(target=bucle, daemon=True).start()


def desfase_windows(alias, n=5):
    """Hora de Windows − hora local (s): «echo %TIME%» por SSH (centésimas), la de menor ida y vuelta.
    Windows usa su reloj CMOS sin sincronizar, así que se mide en cada caminata."""
    import datetime
    medidas = []
    for _ in range(n):
        t1 = time.time()
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", alias, "echo %TIME%"],
                           capture_output=True, text=True, timeout=15).stdout.strip().replace(",", ".")
        t2 = time.time()
        h, m, sg = r.split(":")
        ref = datetime.datetime.fromtimestamp((t1 + t2) / 2)
        hora = ref.replace(hour=int(h), minute=int(m), second=0, microsecond=0).timestamp() + float(sg)
        medidas.append((t2 - t1, hora - (t1 + t2) / 2))
    return min(medidas)[1]


def caminata_en_pi(alias, argumentos, carpeta):
    """27-oct: ejecuta caminar.py en la Raspberry y trae su registro a la carpeta, con la hora de inicio
    pasada al reloj de este PC (caminata.inicio.txt), igual que el ejecutor local."""
    SSHX = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=5"]
    t1 = time.time()
    hora_pi = float(subprocess.check_output(["ssh", *SSHX, alias, "date +%s.%N"], timeout=20).decode())
    desfase = hora_pi - (t1 + time.time()) / 2
    (carpeta / "pi.desfase.txt").write_text(f"{desfase:.6f}\n")
    cmd = "cd ~/nova_caminata_pi && python3 caminar.py " + " ".join(shlex.quote(x) for x in argumentos)
    r = subprocess.run(["ssh", *SSHX, alias, cmd])
    ultimo = subprocess.check_output(["ssh", *SSHX, alias, "ls -t ~/nova_caminata_pi/registros/*.csv | head -1"],
                                     timeout=20).decode().strip()
    subprocess.run(["scp", "-q", *SSHX, f"{alias}:{ultimo}", str(carpeta / "caminata.csv")], check=True, timeout=120)
    subprocess.run(["scp", "-q", *SSHX, f"{alias}:{ultimo[:-4]}.config.json", str(carpeta / "caminata.config.json")],
                   check=True, timeout=120)
    cfg = json.loads((carpeta / "caminata.config.json").read_text())
    (carpeta / "caminata.inicio.txt").write_text(f"{cfg['inicio_epoch'] - desfase:.6f}\n")
    return r


def main():
    if "--" in sys.argv:
        i = sys.argv.index("--"); propios, resto = sys.argv[1:i], sys.argv[i + 1:]
    else:
        propios, resto = sys.argv[1:], []
    p = argparse.ArgumentParser()
    p.add_argument("--nombre", required=True)
    p.add_argument("--dispositivo", default="/dev/video1")
    p.add_argument("--remota", default="pc2-camara",
                   help="alias SSH del segundo portátil ('' para grabar solo con este PC)")
    p.add_argument("--dispositivo-remoto", default="/dev/video0")
    p.add_argument("--sin-extras", action="store_true", help="no grabar las cámaras de camaras_extra.json")
    # 27-oct: caminatas en el piso con solo dos cámaras (diagonales) y la marcha ejecutada en la Raspberry.
    p.add_argument("--solo-camaras", help="lista separada por comas: hp, portatil2, logitech, general, windows")
    p.add_argument("--remoto-pi", help="alias SSH de la Raspberry: ejecuta caminar.py de ~/nova_caminata_pi "
                                       "con los argumentos tras «--» y trae su registro")
    p.add_argument("--ejecutor", type=Path, default=EJECUTOR,
                   help="programa que mueve el robot (21-oct: identificar_patas_robot.py para identificar patas)")
    a = p.parse_args(propios)
    solo = set(a.solo_camaras.split(",")) if a.solo_camaras else None
    if solo is not None and "portatil2" not in solo:
        a.remota = ""
    # 21-oct: núcleos 0-1 reservados para el bucle de control del robot; este programa y sus ffmpeg en el resto.
    NUCLEOS_CONTROL = {0, 1}
    try:
        os.sched_setaffinity(0, set(range(os.cpu_count())) - NUCLEOS_CONTROL)
    except (AttributeError, OSError):
        pass
    carpeta = AQUI / "grabaciones" / a.nombre
    carpeta.mkdir(parents=True, exist_ok=False)
    video = carpeta / "video.mkv"
    VIVO.mkdir(exist_ok=True)
    # 26-oct: el operador quiere ver las cámaras en vivo cada vez que el robot se mueve: se abre
    # vista_vivo.py (si ya está abierta, la nueva copia sale sola por su cerrojo).
    if os.environ.get("DISPLAY") or Path("/tmp/.X11-unix/X1").exists():
        subprocess.Popen([sys.executable, str(AQUI / "vista_vivo.py")], cwd=AQUI, start_new_session=True,
                         env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":1")},
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ff = None if solo is not None and "hp" not in solo else subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "v4l2", "-input_format", "mjpeg",
         "-video_size", "1280x720", "-framerate", "30", "-use_wallclock_as_timestamps", "1",
         "-i", a.dispositivo, "-c:v", "copy", "-copyts", str(video), *VIVO_LOCAL, str(VIVO / "1_hp_pc.jpg")],
        stdin=subprocess.PIPE)
    t_video = time.time()
    (carpeta / "video.lanzamiento.txt").write_text(f"{t_video:.6f}\n")
    extras = []
    cfg_extra = AQUI / "camaras_extra.json"
    if cfg_extra.exists() and not a.sin_extras:
        for c in json.loads(cfg_extra.read_text())["camaras"]:
            # 21-oct: cámaras desactivadas o no conectadas se saltan sin detener la grabación.
            if not c.get("activa", True) or (solo is not None and c["nombre"] not in solo):
                continue
            if c.get("dispositivo", "").startswith("/dev/") and not Path(c["dispositivo"]).exists():
                print(f"AVISO: la cámara {c['nombre']} ({c['dispositivo']}) no está conectada; se salta.", flush=True)
                continue
            d = carpeta / f"extra_{c['nombre']}"; d.mkdir()
            if c.get("ssh"):
                # 21-oct: cámara de un PC remoto (Windows): graba en su disco con la hora de su
                # reloj (H.264, poco peso) y al final se trae; aquí se mide el desfase de relojes.
                SSHX = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "-o", "ServerAliveInterval=5"]
                try:
                    subprocess.run(["ssh", *SSHX, c["ssh"], c["parar"]], capture_output=True, timeout=20)
                    (d / "desfase.txt").write_text(f"{desfase_windows(c['ssh']):.6f}\n")
                    proc = subprocess.Popen(["ssh", *SSHX, c["ssh"], c["remoto"] + " " + VIVO_REMOTO], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=open(d / "remoto.log", "w"))
                    lector_vivo(proc.stdout, VIVO / f"{c['nombre']}.jpg")
                    extras.append((c["nombre"], d, proc, c))
                except (subprocess.SubprocessError, OSError, ValueError) as e:
                    print(f"AVISO: la cámara {c['nombre']} ({c['ssh']}) no arrancó: {e}", flush=True)
                    (d / "error.txt").write_text(f"{e}\n")
                continue
            for ajuste in c.get("previo", []):
                subprocess.run(["v4l2-ctl", "-d", c["dispositivo"], "-c", ajuste], capture_output=True)
            # 20-oct: "formato" permite fuentes que no son v4l2 (la tablet por HTTP de DroidCam).
            formato = ["-f", c.get("formato", "v4l2")] if c.get("formato", "v4l2") else []
            proc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", *formato, *c["entrada"],
                                     "-use_wallclock_as_timestamps", "1", "-i", c["dispositivo"], *c["salida"],
                                     "-copyts", str(d / "video.mkv"), *VIVO_LOCAL, str(VIVO / f"{c['nombre']}.jpg")],
                                    stdin=subprocess.PIPE)
            extras.append((c["nombre"], d, proc, None))
    remoto = None
    SSH = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "-o", "ServerAliveInterval=5", "-o", "ServerAliveCountMax=3"]
    if a.remota and subprocess.run(["ssh", *SSH, a.remota, "true"], capture_output=True).returncode != 0:
        # 19-oct: sin enlace con el segundo portátil se graba solo con esta cámara.
        print(f"AVISO: {a.remota} no responde; se graba solo con la cámara local.", flush=True)
        (carpeta / "remota.error.txt").write_text("sin conexión al empezar\n")
        a.remota = ""
    if a.remota:
        # Diferencia de reloj: hora remota − hora local (punto medio de la consulta).
        t1 = time.time()
        r_hora = float(subprocess.check_output(["ssh", *SSH, a.remota, "date +%s.%N"]).decode())
        t2 = time.time()
        desfase = r_hora - (t1 + t2) / 2
        (carpeta / "remota.desfase.txt").write_text(f"{desfase:.6f}\n")
        remoto = subprocess.Popen(
            ["ssh", *SSH, a.remota,
             f"pkill -INT -f 'ffmpeg.*/tmp/cam_remota.mkv'; sleep 1; "   # 20-oct: grabación anterior colgada
             f"date +%s.%N > /tmp/cam_remota.inicio.txt; exec ffmpeg -hide_banner -loglevel error -f v4l2 "
             f"-input_format mjpeg -video_size 1280x720 -framerate 30 -use_wallclock_as_timestamps 1 "
             f"-i {a.dispositivo_remoto} -c:v copy -copyts -y /tmp/cam_remota.mkv {VIVO_REMOTO}"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        lector_vivo(remoto.stdout, VIVO / "portatil2.jpg")
    time.sleep(2.0)
    if ff is not None and ff.poll() is not None:
        raise SystemExit("La cámara no arrancó (¿la está usando otro programa?).")
    try:
        caminata = carpeta / "caminata.csv"
        if a.remoto_pi:
            r = caminata_en_pi(a.remoto_pi, resto, carpeta)
        else:
            r = subprocess.run(["taskset", "-c", ",".join(map(str, sorted(NUCLEOS_CONTROL))),
                                str(PYTHON), "-I", str(a.ejecutor), *resto, "--salida", str(caminata)],
                               cwd=a.ejecutor.parent)
        time.sleep(2.0)
    finally:
        if ff is not None:
            ff.stdin.write(b"q"); ff.stdin.flush()
            try:
                ff.wait(timeout=10)
            except subprocess.TimeoutExpired:
                ff.terminate()
            # 19-oct: hora real del primer fotograma (la cámara tarda ~0,3-0,4 s en arrancar).
            (carpeta / "video.inicio.txt").write_text(f"{primer_fotograma(video):.6f}\n")
        for nombre, d, proc, remoto_extra in extras:
            try:
                if remoto_extra is None:
                    proc.stdin.write(b"q"); proc.stdin.flush(); proc.wait(timeout=15)
                else:
                    c = remoto_extra
                    proc.stdin.write(b"q"); proc.stdin.flush()
                    try:
                        proc.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        subprocess.run(["ssh", "-o", "BatchMode=yes", c["ssh"], c["parar"]], capture_output=True, timeout=20)
                        proc.terminate()
                    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", f"{c['ssh']}:{c['archivo']}", str(d / "video.mkv")],
                                   check=True, timeout=600)
                    ini = primer_fotograma(d / "video.mkv") - float((d / "desfase.txt").read_text())
                    (d / "video.inicio.txt").write_text(f"{ini:.6f}\n")
                    for f in ("caminata.csv", "caminata.inicio.txt", "caminata.config.json"):
                        if (carpeta / f).exists():
                            (d / f).write_bytes((carpeta / f).read_bytes())
                    continue
            except (OSError, subprocess.SubprocessError):
                proc.terminate()
            try:
                (d / "video.inicio.txt").write_text(f"{primer_fotograma(d / 'video.mkv'):.6f}\n")
                for f in ("caminata.csv", "caminata.inicio.txt", "caminata.config.json"):
                    if (carpeta / f).exists():
                        (d / f).write_bytes((carpeta / f).read_bytes())
            except (subprocess.SubprocessError, OSError, ValueError, KeyError, IndexError) as e:
                print(f"AVISO: la cámara {nombre} no grabó bien: {e}", flush=True)
                (d / "error.txt").write_text(f"{e}\n")
        if remoto is not None:
            try:
                remoto.stdin.write(b"q"); remoto.stdin.flush()
            except OSError:
                pass
            try:
                remoto.wait(timeout=10)
            except subprocess.TimeoutExpired:
                remoto.terminate()
            remota = carpeta / "remota"; remota.mkdir(exist_ok=True)
            try:
                # Copia con límite de tiempo: si se corta el cable no se queda colgado.
                subprocess.run(["scp", "-q", *SSH, f"{a.remota}:/tmp/cam_remota.mkv", str(remota / "video.mkv")],
                               check=True, timeout=600)
                # Hora del primer fotograma remoto, pasada al reloj de este PC.
                ini = primer_fotograma(remota / "video.mkv") - float((carpeta / "remota.desfase.txt").read_text())
                (remota / "video.inicio.txt").write_text(f"{ini:.6f}\n")
                for f in ("caminata.csv", "caminata.inicio.txt", "caminata.config.json"):
                    if (carpeta / f).exists():
                        (remota / f).write_bytes((carpeta / f).read_bytes())
            except (subprocess.SubprocessError, OSError, ValueError, KeyError, IndexError) as e:
                print(f"AVISO: no se pudo traer el video de {a.remota}: {e}", flush=True)
                (carpeta / "remota.error.txt").write_text(f"{e}\n")
    print(f"Grabación en {carpeta} (caminata terminó con código {r.returncode})")


if __name__ == "__main__":
    main()
