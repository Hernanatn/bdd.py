$env:MYQL_ROOT_PASSWORD= Get-Content .secretos\mysql_root_p -Raw;
$fuente = "fuente"
cd $fuente;
$salida = "chastack_bdd/pruebas/reportes"
if (-not (Test-Path $salida)) {
    New-Item -ItemType Directory -Path $salida | Out-Null
}

$rcfile = "chastack_bdd/pruebas/.coveragerc"
$modulo_base = "chastack_bdd.pruebas.__main__"

if ($args.Count -gt 0) {
    # Si los argumentos no contienen punto, se asume que es una clase de test (como "PruebasExtendidas")
    # y se completa con el nombre del módulo
    $targets = $args | ForEach-Object {
        if ($_ -notmatch "\.") {
            "$modulo_base.$_"
        } else {
            $_
        }
    }

    $tests = $targets -join " "
    coverage run --omit="*/pruebas/*" --rcfile=$rcfile -m unittest $tests
} else {
    coverage run --omit="*/pruebas/*" --rcfile=$rcfile -m chastack_bdd.pruebas
}

coverage report --rcfile=$rcfile
coverage html --rcfile=$rcfile
coverage xml --rcfile=$rcfile

Write-Host "`nReporte guardado en $salida" -ForegroundColor Green
cd ..