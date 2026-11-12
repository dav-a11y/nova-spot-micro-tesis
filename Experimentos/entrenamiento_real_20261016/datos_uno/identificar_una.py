#!/usr/bin/env python3
"""Mueve una sola articulación (orden '!' + índice) y dice qué canal MUX la sigue."""
import os, sys, time, termios
import numpy as np
NOM = ["Coxa 1","Coxa 2","Coxa 3","Coxa 4","Fémur 1","Fémur 2","Fémur 3","Fémur 4","Tibia 1","Tibia 2","Tibia 3","Tibia 4"]
idx = int(sys.argv[1]); car = "0123456789ab"[idx]
fd = os.open('/dev/ttyACM0', os.O_RDWR | os.O_NOCTTY)
a = termios.tcgetattr(fd); a[4] = a[5] = termios.B115200; a[3] = 0; a[0] = 0; a[1] = 0
a[2] |= termios.CLOCAL | termios.CREAD; a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 2
termios.tcsetattr(fd, termios.TCSANOW, a)
time.sleep(2.5); os.read(fd, 65536)
os.write(fd, ("!" + car).encode())
buf, fin = b"", time.time() + 9
while time.time() < fin: buf += os.read(fd, 4096)
os.close(fd)
filas = []
for l in buf.decode(errors="replace").splitlines():
    p = l.strip().split(",")
    if len(p) == 31 and p[0] == "DATA" and p[2] == f"UNA_I{idx}":
        filas.append([int(x) for x in p[3:]])
if len(filas) < 10:
    print(f"{NOM[idx]}: pocas tramas ({len(filas)})"); sys.exit()
F = np.array(filas, float); o = F[:, idx]; A = F[:, 12:]
res = []
for ch in range(16):
    if A[:, ch].std() < 0.5: res.append((0, ch, 0, A[:, ch].ptp())); continue
    rr = max((np.corrcoef(o[:len(o)-l], A[l:, ch])[0, 1] for l in range(4)), key=abs)
    res.append((abs(rr), ch, rr, A[:, ch].ptp()))
res.sort(reverse=True)
top = res[0]
veredicto = "CONFIRMADO" if top[0] >= 0.8 and top[3] >= 15 else ("DUDOSO" if top[0] >= 0.5 else "SIN SENSOR que responda")
print("   detalle:", ", ".join(f"C{c} r={r2:+.2f} ({p:.0f})" for _,c,r2,p in res[:4]))
print(f"{NOM[idx]} (orden {o.min():.0f}-{o.max():.0f}°): mejor C{top[1]} r={top[2]:+.2f} variación {top[3]:.0f} cuentas | segundo C{res[1][1]} r={res[1][2]:+.2f} -> {veredicto}")
