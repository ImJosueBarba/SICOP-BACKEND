# 🚀 Backend SICOP - Planta La Esperanza

> Sistema de Gestión y Machine Learning para Planta de Tratamiento de Agua

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-20+-success.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## ✨ Características Principales

### 🎯 Endpoints ML Profesionales
- ✅ **Predicción de consumo químico** con Machine Learning
- ✅ **Detección de anomalías** en datos operativos
- ✅ **Entrenamiento automático** de modelos
- ✅ **Estadísticas y métricas** en tiempo real

### 🔐 Seguridad y Validación
- ✅ **Validaciones Pydantic** robustas
- ✅ **Exception handlers globales** con mensajes claros
- ✅ **Logging estructurado** profesional
- ✅ **CORS** configurado para frontend

### 🧪 Testing y Calidad
- ✅ **20+ tests** con pytest
- ✅ **Coverage** de endpoints críticos
- ✅ **CI/CD ready** con scripts automatizados

---

## 📦 Instalación Rápida

### Prerequisitos
- Python 3.9+
- pip
- Base de datos SQLite (incluida)

### 1. Clonar repositorio
```bash
cd "D:\Universidad\Proyecto Esperanza\Backend Web y Movil\SICOP-BACKEND\backend"
```

### 2. Crear entorno virtual
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
pip install -r ml_requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tu configuración
```

### 5. Inicializar base de datos
```bash
python init_database.py
```

---

## 🚀 Ejecutar Servidor

### Opción A: Script automatizado (Recomendado)
```powershell
.\run_server.ps1
```

### Opción B: Comando directo
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Salida esperada:
```
============================================================
🚀 API Planta La Esperanza - INICIADA
📘 Documentación: http://localhost:8000/docs
📗 ReDoc: http://localhost:8000/redoc
============================================================
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🧪 Ejecutar Tests

### Opción A: Script automatizado
```powershell
.\run_tests.ps1
```

### Opción B: Pytest directo
```bash
# Todos los tests
pytest tests/test_ml_endpoints.py -v

# Test específico
pytest tests/test_ml_endpoints.py::test_anomalies_with_days_parameter -v

# Con coverage
pytest tests/ --cov=routers --cov=core --cov-report=html
```

---

## 🔍 Verificar Endpoint

Ejecuta el script de verificación:
```powershell
.\verify_endpoint.ps1
```

Este script:
1. ✅ Verifica que el servidor esté corriendo
2. ✅ Prueba el endpoint `/ml/anomalies?days=7`
3. ✅ Prueba con fechas específicas
4. ✅ Valida manejo de errores

---

## 📚 API Endpoints

### Machine Learning

#### 🔍 **GET** `/api/ml/anomalies`
Detecta anomalías en datos operativos.

**Parámetros:**
- `days` (opcional, default=7): Últimos N días a analizar
- `fecha_inicio` (opcional): Fecha inicio (YYYY-MM-DD)
- `fecha_fin` (opcional): Fecha fin (YYYY-MM-DD)

**Ejemplos:**
```bash
# Últimos 7 días (default)
curl "http://localhost:8000/api/ml/anomalies?days=7"

# Últimos 30 días
curl "http://localhost:8000/api/ml/anomalies?days=30"

# Rango específico
curl "http://localhost:8000/api/ml/anomalies?fecha_inicio=2026-01-01&fecha_fin=2026-01-31"
```

**Response:**
```json
{
  "status": "success",
  "total_records": 150,
  "anomalies_detected": 5,
  "anomaly_rate_pct": 3.33,
  "by_severity": {
    "critico": 1,
    "sospechoso": 3,
    "normal": 1
  },
  "date_range": {
    "start": "2026-02-11",
    "end": "2026-02-18"
  },
  "anomalies": [...]
}
```

---

#### 🔮 **POST** `/api/ml/predict`
Predice consumo de químicos.

**Request Body:**
```json
{
  "turbedad_ac": 25.5,
  "turbedad_at": 0.8,
  "ph_ac": 7.2,
  "ph_at": 7.5,
  "temperatura_ac": 22.0
}
```

**Response:**
```json
{
  "sulfato_kg": 120.5,
  "cal_kg": 45.2,
  "hipoclorito_kg": 15.8,
  "cloro_gas_kg": 8.3,
  "confidence": 0.94,
  "model_name": "XGBoost",
  "estimated_cost_usd": 85.50,
  "prediction_date": "2026-02-18T15:30:00"
}
```

---

#### 🎓 **POST** `/api/ml/train`
Entrena un nuevo modelo ML.

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2026-01-31",
  "perform_cv": true,
  "feature_engineering": true
}
```

---

#### 📊 **GET** `/api/ml/model/info`
Obtiene información del modelo actual.

#### 📈 **GET** `/api/ml/stats`
Obtiene estadísticas del sistema ML.

#### 🔄 **POST** `/api/ml/model/reload`
Recarga el modelo más reciente.

---

## 🏗️ Arquitectura

```
backend/
├── core/                      # 🔧 Core utilities
│   ├── exceptions.py          # Custom exceptions y handlers
│   ├── logging_middleware.py  # Middleware de logging
│   ├── database.py            # Database connection
│   └── security.py            # JWT y seguridad
│
├── routers/                   # 🛣️ API Endpoints
│   ├── ml.py                  # Machine Learning endpoints
│   ├── auth.py                # Autenticación
│   ├── reportes/              # Endpoints de reportes
│   └── ...
│
├── ml/                        # 🤖 Machine Learning
│   ├── models/                # Modelos ML (trainer, evaluator)
│   ├── inference/             # Servicios de inferencia
│   ├── data/                  # Repositorios y preprocessors
│   └── features/              # Feature engineering
│
├── models/                    # 📊 SQLAlchemy models
├── schemas/                   # 📝 Pydantic schemas
├── tests/                     # 🧪 Tests con pytest
│   ├── test_ml_endpoints.py   # Tests de endpoints ML
│   └── ...
│
├── main.py                    # 🚀 FastAPI app
├── pytest.ini                 # ⚙️ Configuración pytest
├── requirements.txt           # 📦 Dependencias
└── ml_requirements.txt        # 📦 Dependencias ML
```

---

## 🔥 Nuevas Características (v2.0)

### ✨ Logging Profesional
```
2026-02-18 15:30:45 | INFO     | app | REQUEST: GET /api/ml/anomalies
2026-02-18 15:30:45 | INFO     | app | 📊 Detectando anomalías últimos 7 días
2026-02-18 15:30:45 | INFO     | app | ✅ Datos cargados: 150 registros
2026-02-18 15:30:45 | INFO     | app | 🔍 Anomalías: 5/150 (3.33%)
2026-02-18 15:30:45 | INFO     | app | RESPONSE: GET /api/ml/anomalies - 200
```

### 🔐 Exception Handling Global
```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Error de validación en los parámetros enviados",
  "details": {
    "errors": [
      {
        "field": "days",
        "message": "ensure this value is less than or equal to 365",
        "type": "value_error.number.not_le"
      }
    ]
  },
  "timestamp": "2026-02-18T15:30:00.123456",
  "path": "/api/ml/anomalies"
}
```

### ✅ Validaciones Pydantic
```python
class PredictionRequest(BaseModel):
    turbedad_ac: float = Field(..., ge=0, le=500, description="...")
    
    @validator('turbedad_at')
    def turbedad_at_lower_than_ac(cls, v, values):
        if v > values.get('turbedad_ac', 0):
            raise ValueError('Turbidez tratada no puede ser mayor que cruda')
        return v
```

---

## 📖 Documentación Completa

### FastAPI Docs (Swagger)
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### Health Check
```
http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### Error: "No module named 'uvicorn'"
```bash
pip install uvicorn fastapi
```

### Error: "Port 8000 already in use"
```powershell
# Detener proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Error: "Database locked"
```bash
# Cerrar todas las conexiones activas
python init_database.py
```

### Tests fallan
```bash
# Reinstalar dependencias de tests
pip install pytest pytest-cov httpx
```

---

## 📊 Performance

| Endpoint | Tiempo Promedio | Status |
|----------|----------------|---------|
| `/ml/anomalies?days=7` | < 500ms | ✅ |
| `/ml/predict` | < 300ms | ✅ |
| `/ml/train` | 5-10 min | ⏱️ |
| `/ml/model/info` | < 50ms | ✅ |
| `/ml/stats` | < 200ms | ✅ |

---

## 🤝 Contribución

### Código de Conducta
- ✅ Seguir PEP 8
- ✅ Escribir tests para nuevas features
- ✅ Documentar endpoints con docstrings
- ✅ Usar logging estructurado
- ✅ Validaciones Pydantic obligatorias

### Pull Requests
1. Fork del repositorio
2. Crear feature branch (`git checkout -b feature/nueva-feature`)
3. Commit cambios (`git commit -m 'Add: nueva feature'`)
4. Push al branch (`git push origin feature/nueva-feature`)
5. Abrir Pull Request

---

## 📄 Licencia

Copyright © 2026 Planta La Esperanza

---

## 📞 Soporte

**Documentación completa:** [REFACTORIZACION_BACKEND_COMPLETA.md](REFACTORIZACION_BACKEND_COMPLETA.md)

**Scripts útiles:**
- `run_server.ps1` - Iniciar servidor
- `run_tests.ps1` - Ejecutar tests
- `verify_endpoint.ps1` - Verificar endpoints

---

**✨ Backend v2.0 - Production Ready** 🚀
