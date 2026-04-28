# Sistema ML - Optimización de Consumo de Químicos
## Planta de Tratamiento de Agua "La Esperanza"

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.3+-orange.svg)](https://scikit-learn.org/)

---

## 📋 Descripción

Sistema de **Machine Learning** para predicción y optimización del consumo de químicos en plantas de tratamiento de agua potable. Implementa modelos predictivos de última generación para:

- **Predicción de consumo**: Estima cantidades óptimas de coagulantes, floculantes y desinfectantes
- **Detección de anomalías**: Identifica patrones anormales en parámetros operativos
- **Optimización de costos**: Reduce gastos mediante dosificación inteligente

### 🎯 Objetivos del Proyecto

1. Optimizar consumo de químicos reduciendo costos operativos
2. Mejorar eficiencia del proceso de tratamiento
3. Detección temprana de problemas operativos
4. Proporcionar insights basados en datos para toma de decisiones

---

## 🏗️ Arquitectura

El sistema sigue principios de **Clean Architecture** y **SOLID**, organizado en capas:

```
ml/
├── config/                  # Configuración centralizada
│   └── ml_config.yaml      # Parámetros del sistema
│
├── domain/                  # Entidades de dominio
│   ├── entities.py         # Modelos de negocio
│   └── __init__.py
│
├── data/                    # Capa de acceso a datos
│   ├── repository.py       # Repositorio de datos
│   ├── preprocessor.py     # Limpieza y transformación
│   └── __init__.py
│
├── features/                # Feature Engineering
│   ├── feature_engineer.py # Creación de features derivadas
│   └── __init__.py
│
├── models/                  # Entrenamiento y evaluación
│   ├── trainer.py          # Entrenador de modelos
│   ├── evaluator.py        # Evaluación de rendimiento
│   ├── model_manager.py    # Gestión de versiones
│   └── __init__.py
│
├── inference/               # Servicios de producción
│   ├── predictor_service.py   # Predicción de consumo
│   ├── anomaly_service.py     # Detección de anomalías
│   └── __init__.py
│
├── utils/                   # Utilidades comunes
│   ├── config_manager.py   # Gestor de configuración
│   ├── logger.py           # Sistema de logging
│   ├── validation.py       # Validadores
│   └── __init__.py
│
├── trained_models/          # Modelos entrenados (generado)
├── notebooks/               # Análisis exploratorio
└── __init__.py
```

### 📊 Flujo de Datos

```
┌─────────────────┐
│   Base de       │
│     Datos       │ (SQLite/PostgreSQL)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repository     │ ◄─── Extracción de datos históricos
│    Layer        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │ ◄─── Limpieza, outliers, missing values
│    Layer        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │ ◄─── Ratios, deltas, interacciones
│     Layer       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Training       │ ◄─── Random Forest, XGBoost, LightGBM
│    Layer        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Model          │ ◄─── Persistencia y versionado
│    Manager      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inference      │ ◄─── Predicción en producción
│    Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │ ◄─── Endpoints REST
│   Endpoints     │
└─────────────────┘
```

---

## 🚀 Instalación

### Requisitos

- **Python**: 3.11 o superior
- **Memoria**: Mínimo 4GB RAM
- **Disco**: 500MB libres
- **Sistema Operativo**: Windows, Linux, macOS

### Paso 1: Instalar Dependencias

```bash
# Navegar al directorio del backend
cd "D:\Universidad\Proyecto Esperanza\Backend Web y Movil\SICOP-BACKEND\backend"

# Instalar dependencias core (si no están instaladas)
pip install -r requirements.txt

# Instalar dependencias ML
pip install -r ml_requirements.txt
```

### Paso 2: Configurar Directorios

Los directorios se crean automáticamente, pero puedes verificar:

```bash
# Crear directorios necesarios
mkdir -p ml/trained_models
mkdir -p ml/data
mkdir -p logs
```

### Paso 3: Verificar Instalación

```python
# test_installation.py
from ml.utils.config_manager import get_config
from ml.inference.predictor_service import ChemicalConsumptionPredictor

config = get_config()
print(f"✓ Configuración cargada: {config.get('project.name')}")

predictor = ChemicalConsumptionPredictor()
print("✓ Predictor inicializado")

print("\n✅ Instalación exitosa")
```

---

## 📖 Uso

### 1. Entrenamiento de Modelos

#### Opción A: Via API

```bash
# Iniciar servidor
python -m uvicorn main:app --reload

# Entrenar modelo (via curl o Postman)
curl -X POST "http://localhost:8000/api/ml/train" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01",
    "end_date": "2026-02-01",
    "perform_cv": true,
    "feature_engineering": true
  }'
```

#### Opción B: Via Script Python

```python
# train_model.py
from sqlalchemy.orm import Session
from core.database import SessionLocal
from ml.data.repository import PlantDataRepository
from ml.data.preprocessor import DataPreprocessor
from ml.features.feature_engineer import FeatureEngineer
from ml.models.trainer import ChemicalConsumptionTrainer
from ml.utils.config_manager import get_config

config = get_config()
db = SessionLocal()

# 1. Obtener datos
repo = PlantDataRepository(db)
df = repo.get_combined_dataset()

print(f"Datos obtenidos: {len(df)} registros")

# 2. Feature Engineering
df_features = FeatureEngineer.engineer_features(df)

# 3. Preprocessing
preprocessor = DataPreprocessor()
X, y = preprocessor.prepare_dataset(
    df_features,
    target_columns=config.target_variables
)

# 4. Entrenamiento
trainer = ChemicalConsumptionTrainer()
X_train, X_val, X_test, y_train, y_val, y_test = trainer.split_data(X, y)

scores = trainer.train_all_models(X_train, y_train, X_val, y_val)
best_name, best_model = trainer.select_best_model()

print(f"\n✅ Mejor modelo: {best_name}")
print(f"Métricas: {scores[best_name]}")

# 5. Guardar modelo
model_path = trainer.save_model(preprocessor)
print(f"Modelo guardado en: {model_path}")
```

### 2. Predicción

#### Via API

```bash
curl -X POST "http://localhost:8000/api/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "turbedad_ac": 25.5,
    "turbedad_at": 0.8,
    "ph_ac": 7.2,
    "ph_at": 7.5,
    "temperatura_ac": 22.0,
    "caudal_total": 5000.0
  }'
```

#### Via Python

```python
from ml.inference.predictor_service import ChemicalConsumptionPredictor

predictor = ChemicalConsumptionPredictor()
predictor.load_model()  # Carga último modelo

result = predictor.predict(
    turbedad_ac=25.5,
    turbedad_at=0.8,
    ph_ac=7.2,
    ph_at=7.5,
    temperatura_ac=22.0,
    caudal_total=5000.0
)

print(f"Sulfato predicho: {result.sulfato_predicho:.2f} kg")
print(f"Cal predicha: {result.cal_predicha:.2f} kg")
print(f"Confianza: {result.confidence_score:.2%}")
print(f"Costo estimado: ${result.estimated_cost:.2f}")
```

### 3. Detección de Anomalías

```bash
curl -X GET "http://localhost:8000/api/ml/anomalies?fecha_inicio=2026-01-01&fecha_fin=2026-02-01"
```

---

## 📊 Métricas y Evaluación

El sistema evalúa modelos usando múltiples métricas:

- **MAE** (Mean Absolute Error): Error promedio en kg
- **RMSE** (Root Mean Squared Error): Penaliza errores grandes
- **R²** (Coeficiente de determinación): Calidad del ajuste (0-1)
- **MAPE** (Mean Absolute Percentage Error): Error porcentual

### Umbrales de Aceptación

Configurados en `ml_config.yaml`:

```yaml
evaluation:
  thresholds:
    min_r2_score: 0.70     # R² mínimo aceptable
    max_mape_percent: 15.0  # MAPE máximo aceptable
```

---

## ⚙️ Configuración

### Archivo: `ml/config/ml_config.yaml`

Parámetros clave:

```yaml
# Modelos habilitados
models:
  algorithms:
    random_forest:
      enabled: true
      params:
        n_estimators: 100
        max_depth: 15
    
    xgboost:
      enabled: true
      params:
        n_estimators: 100
        learning_rate: 0.1

# Features
features:
  input_variables:
    - turbedad_ac
    - ph_ac
    - temperatura_ac
    # ...
  
  target_variables:
    - sulfato_consumo_kg
    - cal_consumo_kg
    - hipoclorito_consumo_kg
    - cloro_gas_consumo_kg

# División de datos
data:
  train_test_split:
    test_size: 0.20
    validation_size: 0.15
    random_state: 42
```

---

## 🔧 API Endpoints

Base URL: `http://localhost:8000/api/ml`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/predict` | POST | Predice consumo de químicos |
| `/train` | POST | Entrena nuevo modelo |
| `/anomalies` | GET | Detecta anomalías en rango de fechas |
| `/model/info` | GET | Info del modelo actual |
| `/model/reload` | POST | Recarga modelo en memoria |
| `/stats` | GET | Estadísticas generales |

### Ejemplo de Response

```json
{
  "sulfato_kg": 1250.75,
  "cal_kg": 85.30,
  "hipoclorito_kg": 275.50,
  "cloro_gas_kg": 45.20,
  "confidence": 0.89,
  "model_name": "xgboost",
  "estimated_cost_usd": 1025.43,
  "prediction_date": "2026-02-18"
}
```

---

## 🧪 Testing

```bash
# Ejecutar tests unitarios
pytest ml/tests/

# Con cobertura
pytest --cov=ml ml/tests/
```

---

## 📝 Logging

Logs estructurados en `logs/`:

- `ml_training.log`: Entrenamiento de modelos
- `ml_inference.log`: Predicciones en producción
- `ml_anomaly.log`: Detección de anomalías
- `ml_errors.log`: Errores críticos

Configuración en `ml_config.yaml`:

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## 🚧 Mantenimiento

### Re-entrenamiento

Se recomienda re-entrenar mensualmente o cuando:

- Haya >1000 nuevos registros
- Métricas de producción se degraden >15%
- Cambios significativos en el proceso

### Limpieza de Modelos Antiguos

```python
from ml.models.model_manager import ModelManager

manager = ModelManager()
deleted = manager.cleanup_old_models(keep_last_n=5)
print(f"Modelos eliminados: {deleted}")
```

---

## 📚 Referencias

### Algoritmos Utilizados

- **Random Forest**: Bagging ensemble para regresión robusta
- **XGBoost**: Gradient boosting optimizado
- **LightGBM**: Gradient boosting eficiente
- **Isolation Forest**: Detección de anomalías no supervisado

### Papers y Recursos

1. Breiman, L. (2001). "Random Forests". Machine Learning.
2. Chen, T. & Guestrin, C. (2016). "XGBoost: A Scalable Tree Boosting System"
3. Liu, F. T., et al. (2008). "Isolation Forest"

---

## 👥 Autores

**SICOP Team - Planta La Esperanza**

---

## 📄 Licencia

Proyecto académico - Universidad [Nombre]

---

## 🆘 Soporte

Para problemas o preguntas:

1. Revisar logs en `logs/`
2. Verificar configuración en `ml_config.yaml`
3. Consultar documentación API en `/docs`

---

**Versión:** 1.0.0  
**Última actualización:** Febrero 2026
