#!/usr/bin/env python3
"""Sostiene el robot en su postura base y lleva las tibias a los ángulos de servo pedidos (27-oct).

Los ángulos se leen en cada paso de un archivo JSON ({"9": 85, "11": 54}: índice del firmware -> grados;
tibia 2 = 9, tibia 4 = 11), así que se pueden cambiar en vivo sin soltar el robot. Se mueve como máximo
1° por paso. Cada segundo escribe en pantalla la orden y la lectura de los sensores de las tibias 2 y 4.
Termina al borrar el archivo de control o con Ctrl+C (deja fémures y tibias sin fuerza).

Uso: sostener_tibias.py control.json
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrenar_ppo_real as E  # noqa: E402
import ejecutar_politica_robot as R  # noqa: E402


def main():
    control = Path(sys.argv[1])
    E.APERTURA_DEG = 8.0
    stand = np.tile(E.STAND, 4).astype(float)
    for pata, b in E.LEG_JOINT_BASE.items():
        stand[b + 1] = E.STAND[1] - E.apertura(pata)
    base = R.a_grados_servo(stand)
    cal = json.loads(R.CALIBRACION.read_text())
    fd = R.abrir("/dev/ttyACM0"); lec = R.Lector(fd)
    time.sleep(2.0); os.read(fd, 4096); os.write(fd, b"@")
    while not (lec.linea(timeout=8.0) or "").startswith("STREAM_LISTO"):
        pass

    def enviar(g):
        os.write(fd, ("S," + ",".join(map(str, g)) + "\n").encode())
        r = lec.linea(timeout=0.3)
        time.sleep(0.03)
        return {n: int(x) for n, x in zip(R.SENSORES, r.split(",")[2:])} if r and r.startswith("R,") else {}

    ref = enviar(list(R.BASE))
    actual = list(R.BASE)
    ultimo = 0.0
    try:
        while control.exists():
            try:
                datos = json.loads(control.read_text())
                topes = {int(k): int(v) for k, v in datos.pop("tope_max", {}).items()}   # 27-oct: solo para pruebas
                pedido = {int(k): int(v) for k, v in datos.items()}
            except (ValueError, OSError):
                pedido, topes = {}, {}
            objetivo = list(base)
            for i, v in pedido.items():
                objetivo[i] = int(min(max(v, R.TOPE_MIN[i]), topes.get(i, R.TOPE_MAX[i])))
            actual = [c + int(np.clip(o - c, -1, 1)) for c, o in zip(actual, objetivo)]
            v = enviar(actual)
            if time.time() - ultimo > 1.0 and v:
                ultimo = time.time()
                s2 = R.BASE[9] + (((v["ENC_T2"] - ref["ENC_T2"]) * 360 / 4096 + 180) % 360 - 180) / cal["front_left_tibia_joint"]["k"]
                s4 = R.BASE[11] + (v["C10"] - ref["C10"]) / cal["rear_left_tibia_joint"]["k"]
                print(f"orden T2 {actual[9]}° T4 {actual[11]}° | sensores T2 {s2:.0f}° T4 {s4:.0f}°", flush=True)
    finally:
        os.write(fd, b"X\n"); time.sleep(0.2); os.close(fd)


if __name__ == "__main__":
    main()
