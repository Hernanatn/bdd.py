$env:PG_ROOT_PASSWORD= Get-Content ..\.secretos\pg_root_p -Raw;
$env:MYSQL_ROOT_PASSWORD= Get-Content ..\.secretos\mysql_root_p -Raw;
$salida = "chastack_bdd/pruebas/reportes"
if (-not (Test-Path $salida)) {
    New-Item -ItemType Directory -Path $salida | Out-Null
}

$rcfile = "chastack_bdd/pruebas/.coveragerc"

coverage run --rcfile=$rcfile -m chastack_bdd.pruebas
coverage report --rcfile=$rcfile
coverage html --rcfile=$rcfile
coverage xml --rcfile=$rcfile

Write-Host "`nReporte guardado en $salida" -ForegroundColor Green