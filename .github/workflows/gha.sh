cd ../..
export MYSQL_ROOT_PASSWORD=$(cat .secretos/mysql_root_p);
chmod +x correr_pruebas.sh;
./correr_pruebas.sh "$@" > fuente/chastack_bdd/pruebas/reportes/resultado.txt 2>&1

resultado=$(cat fuente/chastack_bdd/pruebas/reportes/resultado.txt)
informe=$(<fuente/chastack_bdd/pruebas/reportes/informe.txt)

tieneErrores=$(grep -E 'errors=[1-9]' fuente/chastack_bdd/pruebas/reportes/resultado.txt || true)
tieneFallos=$(grep -E 'failures=[1-9]' fuente/chastack_bdd/pruebas/reportes/resultado.txt || true)
todoOK=$(grep -E 'OK' fuente/chastack_bdd/pruebas/reportes/resultado.txt || true)

lineaTotal=$(grep -E 'TOTAL' fuente/chastack_bdd/pruebas/reportes/informe.txt || true)
if [ -z "$lineaTotal" ]; then
    echo "::error::No se encontró la línea TOTAL"
    exit 1
fi
porcentaje_total=$(echo "$lineaTotal" | awk '{print $NF}' | tr -d '%')

if [ -n "$tieneErrores" ] || [ -z "$porcentaje_total" ] || [ "$porcentaje_total" -lt 50 ]; then
    echo "::error::Cobertura < 50% o errores en las pruebas."
    exit 1
fi

if [ -n "$tieneFallos" ] || ([ "$porcentaje_total" -ge 50 ] && [ "$porcentaje_total" -lt 65 ]); then
    echo "::warning::Pruebas con fallos o cobertura entre 50% y 65%. Revisión manual requerida."
    exit 1
fi

if [ -z "$todoOK" ]; then
    echo "::error::No se detectó salida OK, posible error de parsing."
    exit 1
fi

echo "Pruebas OK y cobertura suficiente."