# 🚀 Guía de Inicio Rápido - Sistema ML

Esta guía te llevará paso a paso desde la instalación hasta tu primera predicción.

---

## ⏱️ Tiempo estimado: 15-20 minutos

---

## 📋 Prerequisitos

- ✅ Python 3.11 o superior instalado
- ✅ Base de datos SQLite configurada
- ✅ Git (opcional)

---

## 🛠️ Paso 1: Instalación de Dependencias

### Opción A: Instalación Automática (Recomendado)

```powershell
# En el directorio del backend
cd "D:\Universidad\Proyecto Esperanza\Backend Web y Movil\SICOP-BACKEND\backend"

# Ejecutar script de instalación (evita problemas de SSL)
.\install_dependencies.bat
```

### Opción B: Instalación Manual

```powershell
# Si tienes problemas con certificados SSL, usa:
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Si tu conexión SSL funciona correctamente:
pip install -r requirements.txt
```

**Nota**: El archivo `requirements.txt` ahora incluye TODAS las dependencias (backend + ML), ya no necesitas `ml_requirements.txt`.

**Tiempo**: ~5 minutos (dependiendo de conexión a internet)

---

## ✅ Paso 2: Verificar Instalación

Ejecuta el script de setup para verificar que todo esté configurado correctamente:

```powershell
python setup_ml.py
```

**Resultado esperado**: 
```
✅ SETUP COMPLETADO EXITOSAMENTE

Próximos pasos:
1. Entrenar modelo: python train_ml_model.py
2. Iniciar API: python -m uvicorn main:app --reload
3. Documentación: ml/README.md
```

**¿Errores?** Consulta la sección de [Solución de Problemas](#-solución-de-problemas) al final.

---

## 📊 Paso 3: Generar Datos de Prueba

Si tu base de datos tiene menos de 90 registros, necesitas generar datos sintéticos:

```powershell
python generate_ml_data.py
```

**Menú**:
- Opción 1: **180 días (6 meses)** ← Recomendado para mejores resultados
- Opción 2: 90 días (3 meses) - Mínimo necesario
- Opción 3: 365 días (1 año) - Para modelos más robustos

**Tiempo**: ~30 segundos

---

## 🤖 Paso 4: Entrenar tu Primer Modelo

```powershell
python train_ml_model.py
```

Este script hará:
1. ✅ Extraer datos históricos de la base de datos
2. ✅ Aplicar feature engineering
3. ✅ Entrenar 3 modelos (Random Forest, XGBoost, LightGBM)
4. ✅ Seleccionar el mejor modelo automáticamente
5. ✅ Guardar el modelo entrenado

**Tiempo**: ~3-5 minutos (dependiendo de la cantidad de datos)

**Resultado esperado**:
```
✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE
Modelo: xgboost
R² Score: 0.8542
RMSE: 12.34 kg
Ruta: ml/trained_models/model_20240115_153045.pkl
```

---

## 🚀 Paso 5: Iniciar la API

```powershell
python -m uvicorn main:app --reload --port 8000
```

**Resultado esperado**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Deja este terminal abierto. La API está corriendo en segundo plano.

---

## 🧪 Paso 6: Probar la API

### Opción A: Usar el navegador (Swagger UI)

1. Abre tu navegador en: http://localhost:8000/docs
2. Expande el endpoint `POST /api/ml/predict`
3. Click en "Try it out"
4. Usa este JSON de prueba:

```json
{
  "turbedad_at": 50.0,
  "turbedad_ac": 5.0,
  "ph_at": 7.2,
  "ph_ac": 7.5,
  "temperatura": 22.0,
  "cloro_residual": 0.8,
  "conductividad_at": 400.0,
  "conductividad_ac": 380.0,
  "caudal": 250.0,
  "presion_entrada": 3.0,
  "presion_salida": 2.5,
  "solidos_totales": 200.0
}
```

5. Click "Execute"

### Opción B: Usar PowerShell (curl)

```powershell
$body = @{
    turbedad_at = 50.0
    turbedad_ac = 5.0
    ph_at = 7.2
    ph_ac = 7.5
    temperatura = 22.0
    cloro_residual = 0.8
    conductividad_at = 400.0
    conductividad_ac = 380.0
    caudal = 250.0
    presion_entrada = 3.0
    presion_salida = 2.5
    solidos_totales = 200.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/ml/predict" -Method POST -Body $body -ContentType "application/json"
```

### Respuesta esperada

```json
{
  "success": true,
  "predictions": {
    "sulfato_aluminio": 125.34,
    "cal": 32.15,
    "hipoclorito_calcio": 14.87,
    "cloro_gas": 9.56
  },
  "confidence": 0.89,
  "estimated_cost": 85.45,
  "model_version": "xgboost_20240115_153045",
  "predicted_at": "2024-01-15T16:30:45"
}
```

---

## 🎯 ¡Listo! Ahora puedes:

### 1. Ver información del modelo actual
```
GET http://localhost:8000/api/ml/model/info
```

### 2. Detectar anomalías
```
GET http://localhost:8000/api/ml/anomalies?days=7
```

### 3. Ver estadísticas del sistema
```
GET http://localhost:8000/api/ml/stats
```

### 4. Re-entrenar con nuevos datos
```powershell
python train_ml_model.py
```

### 5. Recargar modelo sin reiniciar API
```
POST http://localhost:8000/api/ml/model/reload
```

---

## 📚 Siguiente nivel

Ahora que tienes el sistema funcionando:

1. **Lee la documentación completa**: [ml/README.md](ml/README.md)
2. **Explora los endpoints**: http://localhost:8000/docs
3. **Personaliza la configuración**: [ml/config/ml_config.yaml](ml/config/ml_config.yaml)
4. **Revisa los logs**: `logs/ml_training.log`, `logs/ml_inference.log`
5. **Integra con tu app móvil**: Consulta la sección de API en README

---

## 🔧 Solución de Problemas

### ❌ Error: "Could not find a suitable TLS CA certificate bundle"

Este error ocurre cuando pip no puede verificar certificados SSL, generalmente por una configuración de PostgreSQL.

**Solución 1**: Usar el script de instalación
```powershell
.\install_dependencies.bat
# O en PowerShell:
.\install_dependencies.ps1
```

**Solución 2**: Instalar con hosts confiables
```powershell
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Solución 3**: Limpiar variable de entorno
```powershell
# Temporalmente (solo esta sesión)
$env:REQUESTS_CA_BUNDLE = ""
$env:SSL_CERT_FILE = ""
pip install -r requirements.txt
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'sklearn'"

**Solución**:
```powershell
# Usar el script de instalación
.\install_dependencies.bat
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'pandas'"

Esto significa que las dependencias ML no se instalaron. Ahora están incluidas en `requirements.txt`.

**Solución**:
```powershell
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

### ❌ Error: "InsufficientDataError: Se requieren al menos 90 registros"

**Solución**: Genera datos de prueba
```powershell
python generate_ml_data.py
# Selecciona opción 1 (180 días)
```

---

### ❌ Error: "ModelNotFoundError: No se encontró ningún modelo entrenado"

**Solución**: Entrena un modelo primero
```powershell
python train_ml_model.py
```

---

### ❌ Error: "Port 8000 is already in use"

**Solución 1**: Detén el proceso que usa el puerto 8000
```powershell
# Encontrar proceso
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID con el número del proceso)
taskkill /PID <PID> /F
```

**Solución 2**: Usa otro puerto
```powershell
python -m uvicorn main:app --reload --port 8001
```

---

### ❌ El modelo tiene baja precisión (R² < 0.70)

**Posibles causas**:
1. **Pocos datos**: Necesitas al menos 90 registros, idealmente 180+
2. **Datos sintéticos**: Son de prueba, con datos reales mejorará
3. **Datos inconsistentes**: Verifica la calidad de los datos

**Solución**:
```powershell
# Genera más datos
python generate_ml_data.py  # Opción 3 (1 año)

# Re-entrena
python train_ml_model.py
```

---

### ❌ Predicciones parecen incorrectas

**Verificaciones**:
1. Verifica que los valores de entrada estén en rangos normales
2. Revisa la configuración: `ml/config/ml_config.yaml`
3. Consulta los logs: `logs/ml_inference.log`

---

## 📞 Soporte

- **Documentación completa**: [ml/README.md](ml/README.md)
- **Logs del sistema**: Directorio `logs/`
- **Configuración**: [ml/config/ml_config.yaml](ml/config/ml_config.yaml)

---

## 🎓 Para tu Tesis

### Métricas importantes a reportar:

1. **R² Score**: Coeficiente de determinación (> 0.70 es bueno)
2. **RMSE**: Error cuadrático medio en kg
3. **MAE**: Error absoluto medio en kg
4. **MAPE**: Error porcentual absoluto medio (< 15% es bueno)

### Capturas de pantalla útiles:

1. Output del entrenamiento (`python train_ml_model.py`)
2. Response de predicción (Swagger UI)
3. Gráficas de importancia de features
4. Tabla de métricas comparativas de modelos

### Arquitectura del sistema:

Consulta los diagramas ASCII en [ml/README.md](ml/README.md) para incluir en tu documento.

---

**¡Éxito con tu proyecto! 🎉**
