# Script para ejecutar servidor FastAPI con logging mejorado
# Backend SICOP - Planta La Esperanza

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BACKEND SICOP - PLANTA LA ESPERANZA  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar ubicación
$scriptPath = $PSScriptRoot
if (-not (Test-Path "$scriptPath\main.py")) {
    Write-Host "ERROR: main.py no encontrado" -ForegroundColor Red
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

Write-Host "[2/3] Verificando dependencias..." -ForegroundColor Yellow

# Verificar que uvicorn esté instalado
$uvicornCheck = python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ! uvicorn no encontrado. Instalando..." -ForegroundColor Yellow
    pip install uvicorn fastapi -q
}

Write-Host "[3/3] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SERVIDOR INICIADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  API:          http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ReDoc:        http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host "  Health:       http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Prueba:       curl http://localhost:8000/api/ml/anomalies?days=7" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Presiona Ctrl+C para detener" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

# Iniciar uvicorn con reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
