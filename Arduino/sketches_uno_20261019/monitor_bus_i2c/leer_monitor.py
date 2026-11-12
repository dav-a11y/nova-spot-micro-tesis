#!/usr/bin/env python3
"""Lee el monitor del bus I2C del Uno e imprime solo los cambios (con hora)."""
import os, sys, termios, time
fd = os.open('/dev/ttyACM0', os.O_RDWR | os.O_NOCTTY)
a = termios.tcgetattr(fd); a[4] = a[5] = termios.B115200; a[3] = 0; a[0] = 0; a[1] = 0
a[2] |= termios.CLOCAL | termios.CREAD; a[6][termios.VMIN] = 0; a[6][termios.VTIME] = 5
termios.tcsetattr(fd, termios.TCSANOW, a)
buf, ultimo, fin = b"", None, time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 600)
while time.time() < fin:
    buf += os.read(fd, 512)
    while b"\n" in buf:
        linea, buf = buf.split(b"\n", 1)
        l = linea.decode(errors="replace").strip()
        if l.startswith("LINEAS") and l != ultimo:
            print(time.strftime("%H:%M:%S"), l, flush=True)
            ultimo = l
