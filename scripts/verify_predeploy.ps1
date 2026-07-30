# ===========================================================
# AulaMind Enterprise 3.0
# scripts/verify_predeploy.ps1
# -----------------------------------------------------------
# Verificación pre-deploy (wrapper PowerShell).
#
# Uso (desde la raíz del proyecto):
#   powershell -ExecutionPolicy Bypass -File scripts\verify_predeploy.ps1
#
# Exit code 0 = todo OK, 1 = falló algo (no desplegar).
# ===========================================================

$ErrorActionPreference = "Stop"

# Ir a la raíz del proyecto (este script vive en scripts\)
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " AulaMind 3.0 - Verificacion pre-deploy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Elegir intérprete: venv local si existe, si no el del sistema
$Python = "python"
$Candidates = @(
    ".venv\Scripts\python.exe",
    "venv\Scripts\python.exe"
)
foreach ($Candidate in $Candidates) {
    if (Test-Path (Join-Path $Root $Candidate)) {
        $Python = Join-Path $Root $Candidate
        break
    }
}

Write-Host ""
Write-Host "Interpretador: $Python" -ForegroundColor DarkGray

& $Python "scripts\verify_predeploy.py"
$ExitCode = $LASTEXITCODE

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "VERIFICACION EXITOSA - puedes hacer push" -ForegroundColor Green
} else {
    Write-Host "VERIFICACION FALLIDA - NO hagas push (exit $ExitCode)" -ForegroundColor Red
}

exit $ExitCode
