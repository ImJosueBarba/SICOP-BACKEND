# Script para ejecutar tests con pytest
# Backend SICOP - Planta La Esperanza

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EJECUTANDO TESTS - BACKEND SICOP     " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar ubicación
$scriptPath = $PSScriptRoot
if (-not (Test-Path "$scriptPath\tests\test_ml_endpoints.py")) {
    Write-Host "ERROR: tests/test_ml_endpoints.py no encontrado" -ForegroundColor Red
    Write-Host "Ejecuta este script desde la carpeta 'backend'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Verificando entorno virtual..." -ForegroundColor Yellow

# Activar venv si existe
if (Test-Path "$scriptPath\venv\Scripts\Activate.ps1") {
    Write-Host "  > Activando venv..." -ForegroundColor Gray
    & "$scriptPath\venv\Scripts\Activate.ps1"
} else {
    Write-Host "  ! venv no encontrado. Usando Python global" -ForegroundColor Yellow
}

Write-Host "[2/3] Verificando pytest..." -ForegroundColor Yellow

# Verificar que pytest esté instalado
$pytestCheck = python -c "import pytest" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! pytest no encontrado. Instalando..." -ForegroundColor Yellow
    pip install pytest pytest-cov -q
}

Write-Host "[3/3] Ejecutando tests..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

# Ejecutar pytest
pytest tests/test_ml_endpoints.py -v --tb=short

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  TESTS COMPLETADOS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Coverage opcional
$response = Read-Host "¿Ejecutar coverage report? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    Write-Host ""
    Write-Host "Generando coverage..." -ForegroundColor Yellow
    pytest tests/test_ml_endpoints.py --cov=routers --cov=core --cov-report=html
    Write-Host ""
    Write-Host "Coverage report guardado en: htmlcov/index.html" -ForegroundColor Green
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
