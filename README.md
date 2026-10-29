# Ejercicios Espirituales 2026

Sitio web estático con el plan diario, el calendario y las meditaciones de los Ejercicios Espirituales de San Ignacio en la vida ordinaria. No necesita compilación: son HTML, CSS y JavaScript que leen archivos Markdown.

## Estructura

| Carpeta o archivo | Contenido |
|---|---|
| `index.html`, `assets/` | El sitio web |
| `contenido/` | Lo que se ve en la web: plan diario, calendario, duración y meditaciones publicadas |
| `contenido/indice.json` | Menú del sitio |
| `privado/` | Fuentes de las meditaciones con las orientaciones del Director. **Ignorada por git**: nunca se sube |
| `scripts/publicar.py` | Pasa las meditaciones de `privado/` a `contenido/` sin lo privado y actualiza el menú |

## Ver el sitio en tu computadora

```bash
python -m http.server 8000
```

Abre `http://localhost:8000`.

## Añadir una meditación

1. Guarda el archivo del día en `privado/Semana_N/Semana_N_Dia_M_Titulo.md`, con el formato de la skill (encabezado, meditación, `=== DIRECTOR ===` y orientaciones).
2. Ejecuta `python scripts/publicar.py`. El script copia a `contenido/meditaciones/` solo la parte del ejercitante y la agrega al menú.
3. Revisa, haz commit y sube los cambios.

El script se detiene sin publicar nada si encuentra «orientaciones para el Director» antes de la marca `=== DIRECTOR ===`.

## Discernimiento de espíritus por Semana

Las reglas de cada Semana están en `privado/discernimiento/semana-N.md`. Cada archivo tiene `publicar: no` o `publicar: si` en el encabezado. Por defecto solo está publicada la Primera Semana: San Ignacio pide no adelantar las reglas de la Segunda (Anotaciones 9 y 10). Cuando comience una Semana, cambia su archivo a `publicar: si` y ejecuta `python scripts/publicar.py`.

`privado/` no se sube a git, así que tampoco queda respaldada ahí: haz copia de esa carpeta por tu cuenta.

## Publicar en GitHub Pages

En GitHub: *Settings → Pages → Deploy from a branch → `main` / `(root)`*. El archivo `.nojekyll` evita que GitHub procese el sitio con Jekyll.

Con una cuenta gratuita, GitHub Pages requiere un repositorio público. En un repositorio privado hace falta un plan de pago.
