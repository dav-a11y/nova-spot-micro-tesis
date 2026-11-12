#!/usr/bin/env bash
set -euo pipefail

# 22-oct-2026: compilación explícita (pdflatex + biber + pdflatex ×2). latexmk elegía bibtex en
# lugar de biber por archivos antiguos en esta carpeta y dejaba las citas sin resolver.
cd "$(dirname "$0")"
mkdir -p build
P=(pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Thesis.tex)
"${P[@]}" > /dev/null
biber build/Thesis > /dev/null
"${P[@]}" > /dev/null
"${P[@]}" > /dev/null
if grep -qE "LaTeX Warning: (Reference|Citation).*undefined" build/Thesis.log; then
    echo "AVISO: quedan referencias o citas sin resolver (ver build/Thesis.log)"
fi
cp build/Thesis.pdf Documento_TESIS_PRELIMINAR.pdf
# Thesis.pdf es el archivo que se suele abrir en el visor: se mantiene igual a la última compilación.
cp build/Thesis.pdf Thesis.pdf
printf 'PDF generado: %s\n' "$(pwd)/Documento_TESIS_PRELIMINAR.pdf"
