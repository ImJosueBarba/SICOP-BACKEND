@echo off
REM Script de instalacion rapida - Backend SICOP
REM Instala dependencias evitando problemas de certificados SSL

echo ========================================================================
echo   Instalacion Backend SICOP - Planta La Esperanza
echo ========================================================================
echo.

echo [1/3] Actualizando pip...
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

echo.
echo [2/3] Instalando dependencias (esto puede tardar 3-5 minutos)...
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudieron instalar las dependencias
    echo Revise el log arriba para mas detalles
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando instalacion...
python -c "import fastapi; import pandas; import sklearn; import xgboost; print('OK: Todos los modulos instalados correctamente')"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Algunos modulos no se instalaron correctamente
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================================================
echo.
echo Proximos pasos:
echo   1. Inicializar base de datos: python init_database.py
echo   2. Insertar datos de prueba: python insert_test_data.py
echo   3. Iniciar servidor: python -m uvicorn main:app --reload
echo.
echo ========================================================================
pause
