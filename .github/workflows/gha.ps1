cd ../..
$env:MYQL_ROOT_PASSWORD= Get-Content .secretos\mysql_root_p -Raw;
$ErrorActionPreference = "Stop"
$salida = "fuente/chastack_bdd/pruebas/reportes"
$proceso = Start-Process `
    -FilePath "powershell" `
    -ArgumentList "-ExecutionPolicy Bypass -File correr_pruebas.ps1" `
    -RedirectStandardOutput "$salida/informe.txt" `
    -RedirectStandardError "$salida/resultado.txt" `
    -NoNewWindow `
    -Wait `
    -PassThru

$resultado = Get-Content "$salida/resultado.txt"
$informe = Get-Content "$salida/informe.txt"

$tieneErrores  = $resultado -match 'FAILED\s+\((.*?errors=\d+)'
$tieneFallos   = $resultado -match 'FAILED\s+\((.*?failures=\d+)'
$todoOK       = $resultado | Where-Object { $_ -match '^\s*OK\s*$' }

echo ("::notice::Resultado".PadRight(50) +": $($resultado[-1])")


$lineaTotal = $informe | Where-Object { $_ -match 'TOTAL' }
if (-not $lineaTotal) {
    echo ("::error::No se encontró la línea de cobertura de sobrecargar.py")
    exit 1
}

$campos = $lineaTotal -split '\s+'
$porcentaje = $campos[-1].TrimEnd('%') -as [double]
echo ("::notice::Cobertura total".PadRight(50) + ": $porcentaje%")

if ($tieneErrores -or $porcentaje -lt 50) {
    echo ("::error::Cobertura < 50% o errores en las pruebas.")
    exit 1
}

if ($tieneFallos -or ($porcentaje -ge 50 -and $porcentaje -lt 65)) {
    echo ("::warning::Pruebas con fallos o cobertura entre 50% y 65%. Revisión manual requerida.")
    exit 1
}

if (-not $todoOK) {
    echo ("::error::No se detectó salida OK, posible error de parsing.")
    exit 1
}

Write-Host "Pruebas OK y cobertura suficiente." -ForegroundColor Green