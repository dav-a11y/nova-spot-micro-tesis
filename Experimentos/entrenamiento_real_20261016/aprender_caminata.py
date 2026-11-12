"""Identifica, a partir de una sesion de caminata, que canal MUX sigue a cada
articulacion, su retardo y su escala ADC/grado. Solo analiza datos guardados."""
import sqlite3, statistics as st, sys, json
DB = '/home/pavilion/CODIGO/datos_aprendizaje/datos_cuadrupedo.sqlite'
NOM = ["Coxa 1","Coxa 2","Coxa 3","Coxa 4","Femur 1","Femur 2","Femur 3","Femur 4","Tibia 1","Tibia 2","Tibia 3","Tibia 4"]
CONOCIDO = {1:1, 2:3, 3:2, 5:5, 7:6, 9:9, 11:10, 10:11}  # mapa previo (C11 de tibia 3 es solo candidato)

def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    sa = sum((x-ma)**2 for x in a) ** .5; sb = sum((y-mb)**2 for y in b) ** .5
    return sum((x-ma)*(y-mb) for x, y in zip(a, b)) / (sa*sb) if sa and sb else 0.0

def ajuste(x, y):
    mx, my = st.mean(x), st.mean(y)
    b = sum((a-mx)*(c-my) for a, c in zip(x, y)) / sum((a-mx)**2 for a in x)
    a = my - b*mx
    res = [c-(a+b*u) for u, c in zip(x, y)]
    return a, b, (sum(r*r for r in res)/len(res)) ** .5

ses = int(sys.argv[1])
c = sqlite3.connect(DB)
rows = c.execute("select estado," + ",".join(f"orden_ch{i}" for i in range(12)) + "," +
                 ",".join(f"adc_ch{i}" for i in range(16)) +
                 " from trama where sesion_id=? order by id", (ses,)).fetchall()
rows = [r for r in rows if r[0].startswith('CAMINATA_FASE')]
print(f"Sesion {ses}: {len(rows)} tramas de caminata")
resultado = {}
for j in range(12):
    orden = [r[1+j] for r in rows]
    if max(orden) - min(orden) < 2:
        continue
    mejor = None
    for ch in range(16):
        adc = [r[13+ch] for r in rows]
        for lag in range(0, 4):  # 0..300 ms
            o, a = orden[:len(orden)-lag], adc[lag:]
            r_ = corr(o, a)
            if mejor is None or abs(r_) > abs(mejor[0]):
                mejor = (r_, ch, lag)
    r_, ch, lag = mejor
    o, a = [x for x in orden[:len(orden)-lag]], [r[13+ch] for r in rows][lag:]
    off, pend, rms = ajuste(o, a)
    previo = CONOCIDO.get(j)
    estado = "confirma mapa" if previo == ch else (f"distinto del mapa previo C{previo}" if previo is not None else "canal nuevo")
    fiable = abs(r_) >= 0.8
    print(f"{NOM[j]:8s} orden {min(orden)}-{max(orden)} | C{ch:<2d} r={r_:+.2f} retardo={lag*100}ms "
          f"pendiente={pend:+.2f} cuentas/grado ruido={rms:.1f} | {estado}{'' if fiable else ' (NO fiable)'}")
    resultado[NOM[j]] = dict(canal=ch, r=round(r_, 3), retardo_ms=lag*100, cuentas_por_grado=round(pend, 3),
                             offset=round(off, 1), ruido_rms=round(rms, 2), fiable=fiable)
json.dump(resultado, open(f'/home/pavilion/CODIGO/datos_aprendizaje/modelo_caminata_sesion{ses}.json', 'w'), indent=2, ensure_ascii=False)
