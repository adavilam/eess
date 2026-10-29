#!/usr/bin/env python3
"""Publica en el sitio web lo que el Director autoriza, sin sus orientaciones privadas.

Uso:
    python scripts/publicar.py [--raiz RUTA]

Meditaciones
    Lee       privado/**/Semana_N_Dia_M_Titulo.md   (formato de la skill: encabezado, meditación y,
                                                     tras la línea `=== DIRECTOR ===`, lo privado)
              privado/**/Introduccion_Dia_M_Titulo.md  (Principio y Fundamento; `semana: 0`)
              Con `publicar: no` en el encabezado, el archivo no se publica.
              Con `grupo: Nombre` en el encabezado, el menú agrupa las meditaciones de una Semana
              bajo un tema desplegable (por ejemplo, `grupo: Encarnación y Nacimiento`).
    Escribe   contenido/meditaciones/Semana_N/*.md  (solo lo que ve el ejercitante)

Discernimiento de espíritus
    Lee       privado/discernimiento/*.md           (encabezado: titulo, orden, publicar)
    Escribe   contenido/discernimiento/*.md         (solo los que tienen `publicar: si`)
    Las reglas de cada Semana se publican cuando el Director cambia `publicar: no` por
    `publicar: si` (Anotaciones 9 y 10: las de la Segunda Semana no se dan antes de tiempo).

Actualiza contenido/indice.json (secciones marcadas "generada": true).
La carpeta `privado/` está en .gitignore: nada de lo que hay en ella llega al repositorio.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

DIRECTOR_MARK = re.compile(r"^\s*=== DIRECTOR ===\s*$", re.M)
TEXTO_PRIVADO = re.compile(r"orientaciones\s+para\s+el\s+director", re.I)
NOMBRE = re.compile(r"^(?:Semana_(\d+)|Introduccion)_Dia_(\d+)_.+\.md$")
SI = {"si", "sí", "true", "yes"}


def leer(ruta):
    """Devuelve (encabezado, texto visible para el ejercitante)."""
    texto = ruta.read_text(encoding="utf-8-sig")
    meta, cuerpo = {}, texto
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", texto, re.S)
    if m:
        for linea in m.group(1).splitlines():
            if ":" in linea:
                clave, valor = linea.split(":", 1)
                meta[clave.strip().lower()] = valor.strip().strip('"').strip("'")
        cuerpo = texto[m.end():]
    return meta, DIRECTOR_MARK.split(cuerpo, maxsplit=1)[0].strip()


def comprobar(ruta, texto):
    if TEXTO_PRIVADO.search(texto):
        sys.exit(f"{ruta}: aparece 'orientaciones para el Director' antes de la marca "
                 "=== DIRECTOR ===. No se publica nada.")


def recoger_meditaciones(origen):
    paginas = []  # (semana, dia, nombre_semana, archivo, texto)
    for ruta in sorted(origen.rglob("*.md")):
        m = NOMBRE.match(ruta.name)
        if not m or "discernimiento" in ruta.parts:
            continue
        meta, meditacion = leer(ruta)
        if meta.get("publicar", "si").lower() not in SI:
            continue
        meta.setdefault("semana", m.group(1) or "0")
        meta.setdefault("dia", m.group(2))
        if not meta.get("titulo"):
            sys.exit(f"{ruta}: falta 'titulo' en el encabezado.")
        marca = meta.get("etiqueta") or f"Semana {meta['semana']} – Día {meta['dia']}"
        partes = [f"# {marca} · {meta['titulo']}"]
        if meta.get("semana_probable"):
            partes.append(f"*Semana ignaciana: {meta['semana_probable']}*")
        partes.append(meditacion)
        texto = "\n\n".join(partes) + "\n"
        comprobar(ruta, texto)
        paginas.append((int(meta["semana"]), int(meta["dia"]), meta.get("semana_nombre", ""),
                        ruta.name, texto, meta.get("grupo", "")))
    return sorted(paginas)


def recoger_discernimiento(origen):
    paginas = []  # (orden, archivo, titulo, texto)
    for ruta in sorted((origen / "discernimiento").glob("*.md")):
        meta, texto = leer(ruta)
        if meta.get("publicar", "no").lower() not in SI:
            continue
        if not meta.get("titulo"):
            sys.exit(f"{ruta}: falta 'titulo' en el encabezado.")
        texto += "\n"
        comprobar(ruta, texto)
        paginas.append((int(meta.get("orden", 99)), ruta.name, meta["titulo"], texto))
    return sorted(paginas)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent.parent,
                    help="carpeta del repositorio (por defecto, la que contiene scripts/)")
    raiz = ap.parse_args().raiz.resolve()
    origen = raiz / "privado"
    contenido = raiz / "contenido"
    indice_ruta = contenido / "indice.json"

    meditaciones = recoger_meditaciones(origen)
    discernimiento = recoger_discernimiento(origen)

    for carpeta in (contenido / "meditaciones", contenido / "discernimiento"):
        if carpeta.exists():
            shutil.rmtree(carpeta)

    generadas = []
    if discernimiento:
        (contenido / "discernimiento").mkdir(parents=True)
        items = []
        for _, archivo, titulo, texto in discernimiento:
            (contenido / "discernimiento" / archivo).write_text(texto, encoding="utf-8")
            items.append({"titulo": titulo, "ruta": f"contenido/discernimiento/{archivo}"})
        generadas.append({"titulo": "Discernimiento de espíritus", "generada": True, "items": items})

    semanas = {}
    for semana, dia, nombre, archivo, texto, subgrupo in meditaciones:
        nombre_carpeta = "Introduccion" if semana == 0 else f"Semana_{semana}"
        carpeta = contenido / "meditaciones" / nombre_carpeta
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / archivo).write_text(texto, encoding="utf-8")
        titulo = texto.splitlines()[0].lstrip("# ").split(" · ", 1)[-1]
        grupo = semanas.setdefault(semana, {"nombre": "", "items": []})
        grupo["nombre"] = nombre or grupo["nombre"]
        item = {"titulo": f"Día {dia} · {titulo}",
                "ruta": f"contenido/meditaciones/{nombre_carpeta}/{archivo}"}
        if subgrupo:
            item["grupo"] = subgrupo
        grupo["items"].append(item)
    for semana in sorted(semanas):
        nombre = semanas[semana]["nombre"]
        if semana == 0:
            etiqueta = nombre or "Introducción"
        else:
            etiqueta = f"Semana {semana}" + (f" · {nombre}" if nombre else "")
        generadas.append({"titulo": etiqueta, "generada": True, "secuencia": True,
                          "items": semanas[semana]["items"]})

    indice = json.loads(indice_ruta.read_text(encoding="utf-8"))
    indice["secciones"] = [s for s in indice["secciones"] if not s.get("generada")] + generadas
    indice_ruta.write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Publicadas {len(meditaciones)} meditaciones y {len(discernimiento)} páginas de discernimiento.")


if __name__ == "__main__":
    main()
