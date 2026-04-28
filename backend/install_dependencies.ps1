# Script de instalacion rapida - Backend SICOP
# Instala dependencias evitando problemas de certificados SSL

Write-Host ""
Write-Host "========================================================================"
Write-Host "  Instalacion Backend SICOP - Planta La Esperanza"
Write-Host "========================================================================"
Write-Host ""

# Paso 1: Actualizar pip
Write-Host "[1/3] Actualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: No se pudo actualizar pip" -ForegroundColor Red
    Write-Host "Continuando de todas formas..." -ForegroundColor Yellow
}

# Paso 2: Instalar dependencias
Write-Host ""
Write-Host "[2/3] Instalando dependencias (esto puede tardar 3-5 minutos)..." -ForegroundColor Cyan
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Write-Host "Revise el log arriba para mas detalles" -ForegroundColor Yellow
    Read-Host -Prompt "Presione Enter para salir"
    exit 1
}

# Paso 3: Verificar instalacion
Write-Host ""
Write-Host "[3/3] Verificando instalacion..." -ForegroundColor Cyan
python -c "import fastapi; import pandas; import sklearn; import xgboost; print('OK: Todos los modulos instalados correctamente')"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Algunos modulos no se instalaron correctamente" -ForegroundColor Red
    Read-Host -Prompt "Presione Enter para salir"
    exit 1
}

# Exito
Write-Host ""
Write-Host "========================================================================"
Write-Host "  INSTALACION COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================================================"
Write-Host ""
Write-Host "Proximos pasos:"
Write-Host "  1. Inicializar base de datos: python init_database.py"
Write-Host "  2. Insertar datos de prueba: python insert_test_data.py"
Write-Host "  3. Iniciar servidor: python -m uvicorn main:app --reload"
Write-Host ""
Write-Host "========================================================================"
Write-Host ""
