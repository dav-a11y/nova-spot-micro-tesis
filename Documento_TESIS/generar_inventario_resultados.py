#!/usr/bin/env python3
"""Inventario de entrenamientos y ensayos para el capítulo de resultados.

Cuenta, a partir de las carpetas de Experimentos, los entrenamientos PPO (fase de simulación de
septiembre y fase con el modelo del robot real de octubre) y las caminatas grabadas en el robot,
y escribe Chapters/datos/inventario_resultados.tex con dos tablas y macros con los totales.

Reglas de conteo:
- Un entrenamiento es una carpeta de semilla con policy.zip, metadata o training_trace.csv.
- Semillas «distintas»: las que no repiten las primeras filas de training_trace.csv de otra
  semilla de la misma campaña (las campañas del ciclo de mejora repitieron una sola ejecución).
- Fase de septiembre: carpetas de semilla con policy.zip o traza, y políticas politica_semilla_*.npz.
- En curso: semilla con un proceso entrenar_ppo_real.py activo; incompleta: sin policy.zip y sin proceso.
- Caminatas de comparación: carpetas rep_* de camaras/grabaciones; las *_fallo_* son descartadas.
Uso: python3 generar_inventario_resultados.py   (después ./compilar.sh)
"""
import collections
import csv
import datetime
import hashlib
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parent / "Experimentos"
REAL = EXP / "entrenamiento_real_20261016"
GRAB = EXP / "camaras" / "grabaciones"
SALIDA = AQUI / "Chapters" / "datos" / "inventario_resultados.tex"


def es_entrenamiento(d):
    return (d / "policy.zip").exists() or (d / "training_trace.csv").exists()


def huella(d):
    f = d / "training_trace.csv"
    if not f.exists():
        return str(d)
    return hashlib.md5("".join(f.read_text().splitlines(True)[:20]).encode()).hexdigest()


def marcha(nombre):
    for m in ("gateo", "trote", "paso", "carrera", "galope"):
        if m in nombre:
            return m
    return "previas"


def activos():
    """{(carpeta de salida, semilla)} de los entrenamientos que están corriendo."""
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout
    res = set()
    for linea in ps.splitlines():
        semilla, salida = re.search(r"--seed (\d+)", linea), re.search(r"--output (\S+)", linea)
        if "entrenar_ppo_real.py" in linea and semilla and salida:
            res.add((Path(salida.group(1)).name, semilla.group(1)))
    return res


def fase_real():
    corriendo = activos()
    filas = collections.OrderedDict((m, dict(campanas=[], total=0, distintas=0, curso=0, incompletas=0))
                                    for m in ("gateo", "trote", "paso", "carrera", "galope", "previas"))
    for c in sorted(REAL.iterdir()):
        semillas = [d for d in sorted(c.glob("semilla_*")) if d.is_dir() and es_entrenamiento(d)] if c.is_dir() else []
        if not semillas:
            continue
        f = filas[marcha(c.name)]
        f["campanas"].append(f"{c.name.removeprefix('ppo_').replace('_', ' ')} ({len(semillas)})")
        f["total"] += len(semillas)
        f["distintas"] += len({huella(d) for d in semillas})
        for d in semillas:
            if (c.name, d.name.removeprefix("semilla_")) in corriendo:
                f["curso"] += 1
            elif not (d / "policy.zip").exists():
                f["incompletas"] += 1
    return filas


def fase_simulacion():
    """{campaña: número de entrenamientos} de la fase con el modelo nominal."""
    cuenta = collections.Counter()
    for d in EXP.rglob("*"):
        if REAL in d.parents or "semilla" not in d.name.lower():
            continue
        if (d.is_dir() and "semilla" not in d.parent.name.lower() and es_entrenamiento(d)) or \
                (d.is_file() and d.name.startswith("politica_semilla_") and d.suffix == ".npz"):
            campana = re.sub(r"_2026\d{4}$", "", d.relative_to(EXP).parts[0])
            cuenta[campana.removeprefix("campana_").replace("_", " ")] += 1
    return cuenta


def ensayos_robot():
    validas = fallo = otras = 0
    for d in GRAB.iterdir():
        if not d.is_dir():
            continue
        if d.name.startswith("rep_"):
            if "_fallo" in d.name:
                fallo += 1
            else:
                validas += 1
        else:
            otras += 1
    sesiones = []
    for f in sorted((EXP / "camaras").glob("repetibilidad_*.csv")):
        n = {}
        for r in csv.DictReader(f.open()):
            n[r["condicion"]] = int(r["n"])
        if n:
            sesiones.append((f.stem.removeprefix("repetibilidad_"), n))
    return validas, fallo, otras, sesiones


def tex(s):
    return s.replace("_", r"\_")


def main():
    real = fase_real()
    campanas_sim = fase_simulacion()
    sim = sum(campanas_sim.values())
    validas, fallo, otras, sesiones = ensayos_robot()
    t_real = sum(f["total"] for f in real.values())
    d_real = sum(f["distintas"] for f in real.values())
    curso = sum(f["curso"] for f in real.values())
    incompletas = sum(f["incompletas"] for f in real.values())
    nombres = dict(gateo="Gateo", trote="Trote", paso="Paso", carrera="Carrera", galope="Galope", previas="Versiones previas del entorno")
    L = [f"% Generado por generar_inventario_resultados.py el {datetime.datetime.now():%Y-%m-%d %H:%M}. No editar a mano.",
         rf"\newcommand{{\InvSimulacion}}{{{sim}}}",
         rf"\newcommand{{\InvReal}}{{{t_real}}}",
         rf"\newcommand{{\InvRealDistintas}}{{{d_real}}}",
         rf"\newcommand{{\InvTotal}}{{{sim + t_real}}}",
         rf"\newcommand{{\InvEnCurso}}{{{curso}}}",
         rf"\newcommand{{\InvIncompletas}}{{{incompletas}}}",
         rf"\newcommand{{\InvCaminatasValidas}}{{{validas}}}",
         rf"\newcommand{{\InvCaminatasFallo}}{{{fallo}}}",
         rf"\newcommand{{\InvGrabaciones}}{{{validas + fallo + otras}}}",
         r"\begin{table}[H]", r"\centering", r"\small",
         r"\caption{Entrenamientos PPO realizados por fase y marcha.}",
         r"\label{tab:inventario-entrenamientos}",
         r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.47\textwidth}rrr}",
         r"\toprule", r"Marcha & Campañas (semillas) & Semillas & Distintas & En curso \\", r"\midrule",
         rf"\multicolumn{{5}}{{l}}{{\textit{{Fase de simulación con el modelo nominal (septiembre)}}}} \\",
         rf"Todas & {tex(', '.join(f'{c} ({n})' for c, n in sorted(campanas_sim.items())))} & {sim} & --- & 0 \\",
         rf"\multicolumn{{5}}{{l}}{{\textit{{Fase con el modelo del robot real (octubre y noviembre)}}}} \\"]
    for m, f in real.items():
        if f["total"]:
            L.append(rf"{nombres[m]} & {tex(', '.join(f['campanas']))} & {f['total']} & {f['distintas']} & {f['curso']} \\")
    L += [r"\midrule", rf"\textbf{{Total}} & & \textbf{{{sim + t_real}}} & & {curso} \\",
          rf"\multicolumn{{5}}{{p{{0.9\textwidth}}}}{{\footnotesize «Distintas» descuenta las semillas que repitieron la misma ejecución (campañas del ciclo de mejora, error corregido el 22 de octubre). {incompletas} entrenamientos de octubre se detuvieron antes de su política final y se conservan solo con copias intermedias.}} \\",
          r"\bottomrule", r"\end{tabular}",
          r"\end{table}", "",
          r"\begin{table}[H]", r"\centering", r"\small",
          r"\caption{Caminatas de comparación en el robot suspendido por sesión (repeticiones por condición).}",
          r"\label{tab:inventario-ensayos}",
          r"\begin{tabular}{l>{\raggedright\arraybackslash}p{0.7\textwidth}}", r"\toprule",
          r"Sesión & Condiciones (repeticiones analizadas) \\", r"\midrule"]
    for s, n in sesiones:
        L.append(rf"{tex(s)} & {tex(', '.join(f'{c} ({k})' for c, k in n.items()))} \\")
    L += [r"\midrule",
          rf"\multicolumn{{2}}{{p{{0.9\textwidth}}}}{{\footnotesize Caminatas de comparación grabadas: {validas} válidas y {fallo} descartadas por la comprobación de salud; {otras} grabaciones adicionales de calibración, cámaras y sincronía.}} \\",
          r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("\n".join(L) + "\n")
    print(f"simulación {sim} {dict(campanas_sim)}, real {t_real} ({d_real} distintas, {curso} en curso, {incompletas} incompletas), "
          f"caminatas {validas} válidas + {fallo} fallo + {otras} otras -> {SALIDA.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
