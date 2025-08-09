#!/usr/bin/env bash
set -e

fuente="fuente"
cd "$fuente"

salida="chastack_bdd/pruebas/reportes"
mkdir -p "$salida"

rcfile="chastack_bdd/pruebas/.coveragerc"
modulo_base="chastack_bdd.pruebas.__main__"

if [ "$#" -gt 0 ]; then
    targets=()
    for arg in "$@"; do
        if [[ "$arg" != *.* ]]; then
            targets+=("${modulo_base}.${arg}")
        else
            targets+=("$arg")
        fi
    done
    coverage run --omit="*/pruebas/*" --rcfile="$rcfile" -m unittest "${targets[@]}"
else
    coverage run --omit="*/pruebas/*" --rcfile="$rcfile" -m chastack_bdd.pruebas
fi

coverage report --rcfile="$rcfile" | tee "$salida/informe.txt"
coverage html --rcfile="$rcfile"
coverage xml --rcfile="$rcfile"

echo
echo "Reporte guardado en $salida"
cd ..
