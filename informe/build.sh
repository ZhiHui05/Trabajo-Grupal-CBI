#!/bin/sh
# Genera la memoria a partir de informe/secciones/*.md con pandoc.
# Uso (desde cualquier carpeta):  sh informe/build.sh
# Salida: informe/build/Memoria_Grupo_CBI.pdf (o .docx si no hay motor LaTeX).
# Título, idioma y márgenes: informe/metadata.yaml
set -eu

INFORME="$(cd "$(dirname "$0")" && pwd)"
OUT="$INFORME/build"
mkdir -p "$OUT"

command -v pandoc >/dev/null 2>&1 || { echo "No se encuentra pandoc: https://pandoc.org/installing.html" >&2; exit 1; }

ENGINE=""
for e in xelatex lualatex pdflatex; do
    if command -v "$e" >/dev/null 2>&1; then ENGINE="$e"; break; fi
done

set -- "$INFORME"/secciones/*.md \
    --from markdown --toc \
    --metadata-file "$INFORME/metadata.yaml" \
    --resource-path "$INFORME"

if [ -n "$ENGINE" ]; then
    DEST="$OUT/Memoria_Grupo_CBI.pdf"
    pandoc "$@" --pdf-engine="$ENGINE" -o "$DEST"
else
    DEST="$OUT/Memoria_Grupo_CBI.docx"
    echo "Aviso: no hay motor LaTeX; se genera .docx. Expórtalo a PDF desde Word." >&2
    pandoc "$@" -o "$DEST"
fi

echo "Memoria generada: $DEST"
