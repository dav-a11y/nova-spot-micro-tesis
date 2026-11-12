#!/usr/bin/env python3
"""Catálogo de todas las caminatas grabadas, para estudiar estabilidad y repetibilidad.

Recorre grabaciones/*/caminata.csv, ejecuta diagnostico_caminata.py si falta el
diagnóstico y escribe en grabaciones/:
- catalogo.csv: una fila por caminata (marcha, política, equilibrio de coxas, duración,
  ciclos, seguimiento medio por articulación, coxas, sensores perdidos, cámaras);
- ciclos.csv: una fila por caminata × ciclo × articulación (r, error RMS, desfase,
  lecturas perdidas; coxas: desviación media), base para patrones de estabilidad
  por marcha y repetibilidad entre repeticiones.
La marcha y la política salen de caminata.config.json (desde el 19-oct, 20:00); en las
grabaciones anteriores se deducen del nombre de la carpeta.

Uso: python3 catalogo_caminatas.py
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
GRAB = AQUI / "grabaciones"


def configuracion(c):
    cfg = c / "caminata.config.json"
    if cfg.exists():
        d = json.loads(cfg.read_text())
        pol = d.get("politica")
        return dict(fecha=d["fecha"], marcha=d["marcha"], politica=pol or "base",
                    base_coxas="/".join(str(x) for x in d["base_servos"][:4]), fuente_config="config.json")
    nombre = c.name
    filas = list(csv.DictReader((c / "caminata.csv").open()))
    coxas = "/".join(filas[0][f"orden_{i}"] for i in range(4)) if filas else ""
    from datetime import datetime
    ini = c / "caminata.inicio.txt"
    fecha = datetime.fromtimestamp(float(ini.read_text())).strftime("%Y-%m-%d %H:%M:%S") if ini.exists() else ""
    marcha = "paso" if nombre.startswith("paso") else "gateo"
    politica = "base"
    for clave in ("ppo_v10_s71", "ppo_v10_s23", "ppo_v6_s11"):
        if clave in nombre:
            politica = clave
    return dict(fecha=fecha, marcha=marcha, politica=politica, base_coxas=coxas, fuente_config="nombre de carpeta")


def main():
    catalogo, ciclos = [], []
    for c in sorted(GRAB.iterdir()):
        if not (c / "caminata.csv").exists():
            continue
        diag = c / "diagnostico.json"
        if not diag.exists() or diag.stat().st_mtime < (c / "caminata.csv").stat().st_mtime:
            r = subprocess.run([sys.executable, "-I", str(AQUI / "diagnostico_caminata.py"), str(c)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print("sin diagnóstico:", c.name, r.stderr.strip().splitlines()[-1:])
                continue
        d = json.loads(diag.read_text())
        cfg = configuracion(c)
        fila = dict(caminata=c.name, **cfg, duracion_s=round(d["duracion_s"], 1), ciclos=d["ciclos"],
                    periodo_ms=round(d["periodo_ms"]["mediana"], 1), pasos_mas_40ms=d["periodo_ms"]["pasos_mas_de_40ms"],
                    desplazamiento_comun_max=round(d["desplazamiento_comun_C0"]["maximo_cuentas"], 1))
        for n, a in d["articulaciones"].items():
            if a.get("caido"):
                fila[f"{n}_r"], fila[f"{n}_error"], fila[f"{n}_perdidas"] = "", "", a["lecturas_perdidas"]
                continue
            fila[f"{n}_r"], fila[f"{n}_error"] = round(a["r_medio"], 4), round(a["error_rms_medio"], 3)
            fila[f"{n}_perdidas"] = a["lecturas_perdidas"]
            for k, p in enumerate(a["por_ciclo"]):
                ciclos.append(dict(caminata=c.name, marcha=cfg["marcha"], politica=cfg["politica"],
                                   base_coxas=cfg["base_coxas"], ciclo=k + 1, articulacion=n, r=round(p["r"], 4),
                                   error_rms=round(p["error_rms"], 3), desfase=round(p["desfase"], 3),
                                   perdidas=p["perdidas"]))
        for n, x in d["coxas"].items():
            fila[f"{n}_media"], fila[f"{n}_p95"] = round(x["desviacion_media"], 3), round(x["p95"], 3)
            for k, v in enumerate(x["por_ciclo"]):
                ciclos.append(dict(caminata=c.name, marcha=cfg["marcha"], politica=cfg["politica"],
                                   base_coxas=cfg["base_coxas"], ciclo=k + 1, articulacion=n, r="",
                                   error_rms=round(v, 3), desfase="", perdidas=""))
        for cam in ["camara1", "camara2"] + sorted(k for k in d if k.startswith("camara_")):
            if cam in d:
                fila[f"{cam}_fps"] = round(d[cam]["fps_real"], 1)
                fila[f"{cam}_huecos"] = d[cam]["huecos_mas_de_50ms"]
                fila[f"{cam}_fotogramas"] = d[cam]["fotogramas"]
        catalogo.append(fila)
    campos = []
    for f in catalogo:
        campos += [k for k in f if k not in campos]
    with (GRAB / "catalogo.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(catalogo)
    with (GRAB / "ciclos.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ciclos[0])); w.writeheader(); w.writerows(ciclos)
    print(f"{len(catalogo)} caminatas, {len(ciclos)} filas por ciclo -> {GRAB / 'catalogo.csv'}, {GRAB / 'ciclos.csv'}")


if __name__ == "__main__":
    main()
