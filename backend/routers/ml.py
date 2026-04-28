"""
API Router para Machine Learning.

Endpoints para entrenamiento, predicción y detección de anomalías.
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import logging

from core.database import get_db
from core.exceptions import (
    ValidationException,
    InsufficientDataException,
    MLModelException,
    ResourceNotFoundException
)
from ml.data.repository import PlantDataRepository
from ml.data.preprocessor import DataPreprocessor
from ml.features.feature_engineer import FeatureEngineer
from ml.models.trainer import ChemicalConsumptionTrainer
from ml.models.evaluator import ModelEvaluator
from ml.inference.predictor_service import ChemicalConsumptionPredictor
from ml.inference.anomaly_service import AnomalyDetectorService
from ml.utils.logger import MLLogger
from ml.utils.config_manager import get_config
from ml.utils.validation import MLValidationError, InsufficientDataError as MLInsufficientData

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Logging
logger = logging.getLogger("app")
ml_logger = MLLogger.get_inference_logger()
config = get_config()

# Instancias singleton de servicios
predictor = ChemicalConsumptionPredictor()
anomaly_detector = AnomalyDetectorService()


# ============================================================================
# Schemas (Pydantic Models)
# ============================================================================

class PredictionRequest(BaseModel):
    """Request para predicción de consumo con validaciones robustas."""
    turbedad_ac: float = Field(
        ...,
        ge=0,
        le=500,
        description="Turbidez agua cruda (FTU)",
        example=25.5
    )
    turbedad_at: float = Field(
        ...,
        ge=0,
        le=10,
        description="Turbidez agua tratada (FTU)",
        example=0.8
    )
    ph_ac: float = Field(
        ...,
        ge=6.0,
        le=9.5,
        description="pH agua cruda",
        example=7.2
    )
    ph_at: float = Field(
        ...,
        ge=6.0,
        le=9.5,
        description="pH agua tratada",
        example=7.5
    )
    temperatura_ac: float = Field(
        ...,
        ge=0,
        le=50,
        description="Temperatura agua cruda (°C)",
        example=22.0
    )
    caudal_total: Optional[float] = Field(
        None,
        ge=0,
        description="Caudal total (m³/día)",
        example=5000.0
    )
    dosis_sulfato: Optional[float] = Field(
        None,
        ge=0,
        description="Dosis sulfato (l/s)",
        example=1.5
    )
    dosis_cal: Optional[float] = Field(
        None,
        ge=0,
        description="Dosis cal (l/s)",
        example=0.8
    )
    cloro_residual: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Cloro residual (mg/L)",
        example=0.6
    )
    
    @validator('turbedad_at')
    def turbedad_at_lower_than_ac(cls, v, values):
        """Valida que turbidez tratada sea menor que cruda."""
        if 'turbedad_ac' in values and v > values['turbedad_ac']:
            raise ValueError(
                'La turbidez del agua tratada no puede ser mayor que la del agua cruda'
            )
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "turbedad_ac": 25.5,
                "turbedad_at": 0.8,
                "ph_ac": 7.2,
                "ph_at": 7.5,
                "temperatura_ac": 22.0,
                "caudal_total": 5000.0,
                "dosis_sulfato": 1.5,
                "dosis_cal": 0.8,
                "cloro_residual": 0.6
            }
        }


class PredictionResponse(BaseModel):
    """Response de predicción con información detallada."""
    sulfato_kg: float = Field(..., description="Predicción de sulfato en kg")
    cal_kg: float = Field(..., description="Predicción de cal en kg")
    hipoclorito_kg: float = Field(..., description="Predicción de hipoclorito en kg")
    cloro_gas_kg: float = Field(..., description="Predicción de cloro gas en kg")
    confidence: float = Field(..., ge=0, le=1, description="Confianza del modelo (0-1)")
    model_name: str = Field(..., description="Nombre del modelo utilizado")
    estimated_cost_usd: float = Field(..., description="Costo estimado en USD")
    prediction_date: str = Field(..., description="Fecha de predicción (ISO format)")


class TrainingRequest(BaseModel):
    """Request para entrenamiento de modelo."""
    start_date: Optional[date] = Field(
        None,
        description="Fecha inicio de datos (YYYY-MM-DD)"
    )
    end_date: Optional[date] = Field(
        None,
        description="Fecha fin de datos (YYYY-MM-DD)"
    )
    perform_cv: bool = Field(
        True,
        description="Realizar validación cruzada"
    )
    feature_engineering: bool = Field(
        True,
        description="Aplicar feature engineering"
    )
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        """Valida que fecha fin sea posterior a inicio."""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('La fecha fin debe ser posterior a la fecha de inicio')
        return v


class TrainingResponse(BaseModel):
    """Response de entrenamiento."""
    status: str
    best_model: str
    metrics: Dict[str, Any]
    training_duration_seconds: float
    model_path: str


class AnomalyResponse(BaseModel):
    """Response de detección de anomalías."""
    status: str = Field(..., description="Estado de la operación")
    total_records: int = Field(..., description="Total de registros analizados", example=150)
    anomalies_detected: int = Field(..., description="Número de anomalías detectadas", example=5)
    anomaly_rate_pct: float = Field(..., description="Porcentaje de anomalías (%)", example=3.33)
    by_severity: Dict[str, int] = Field(..., description="Anomalías por severidad")
    date_range: Dict[str, str] = Field(..., description="Rango de fechas analizado")
    anomalies: List[Dict[str, Any]] = Field(..., description="Lista de anomalías detectadas")
    
    class Config:
        schema_extra = {
            "example": {
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
                "anomalies": [
                    {
                        "fecha": "2026-02-15",
                        "parametro": "turbedad_ac",
                        "valor": 350.5,
                        "severidad": "critico",
                        "is_anomaly": True
                    }
                ]
            }
        }


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/predict", response_model=PredictionResponse)
async def predict_consumption(
    request: PredictionRequest
) -> PredictionResponse:
    """
    Predice consumo de químicos basado en parámetros operativos.
    
    **Parámetros de entrada:**
    - `turbedad_ac`: Turbidez agua cruda (0-500 FTU)
    - `turbedad_at`: Turbidez agua tratada (0-10 FTU)
    - `ph_ac`, `ph_at`: pH (6.0-9.5)
    - `temperatura_ac`: Temperatura °C (0-50)
    - Opcionales: `caudal_total`, `dosis_sulfato`, `dosis_cal`, `cloro_residual`
    
    **Retorna:**
    - Predicción de consumo en kg para cada químico
    - Confianza del modelo (0-1)
    - Costo estimado en USD
    
    **Ejemplo:**
    ```json
    {
      "turbedad_ac": 25.5,
      "turbedad_at": 0.8,
      "ph_ac": 7.2,
      "ph_at": 7.5,
      "temperatura_ac": 22.0
    }
    ```
    """
    try:
        logger.info(
            f"🔮 REQUEST: Predicción ML",
            extra={
                "turbedad_ac": request.turbedad_ac,
                "turbedad_at": request.turbedad_at,
                "ph_ac": request.ph_ac,
                "temperatura": request.temperatura_ac
            }
        )
        
        # Realizar predicción
        result = predictor.predict(
            turbedad_ac=request.turbedad_ac,
            turbedad_at=request.turbedad_at,
            ph_ac=request.ph_ac,
            ph_at=request.ph_at,
            temperatura_ac=request.temperatura_ac,
            caudal_total=request.caudal_total,
            dosis_sulfato=request.dosis_sulfato,
            dosis_cal=request.dosis_cal,
            cloro_residual=request.cloro_residual
        )
        
        # Convertir a response
        response = PredictionResponse(
            sulfato_kg=result.sulfato_predicho,
            cal_kg=result.cal_predicha,
            hipoclorito_kg=result.hipoclorito_predicho,
            cloro_gas_kg=result.cloro_gas_predicho,
            confidence=result.confidence_score,
            model_name=result.model_name,
            estimated_cost_usd=result.estimated_cost,
            prediction_date=result.prediction_date.isoformat()
        )
        
        logger.info(
            f"✅ PREDICCIÓN: Sulfato={response.sulfato_kg:.2f}kg, "
            f"Confianza={response.confidence:.2%}"
        )
        
        return response
    
    except MLValidationError as e:
        logger.error(f"⚠️ Error de validación ML: {str(e)}")
        raise ValidationException(
            f"Error de validación en predicción: {str(e)}",
            details={"error": str(e)}
        )
    
    except Exception as e:
        logger.error(
            f"❌ Error inesperado en predicción: {type(e).__name__}",
            exc_info=True
        )
        raise MLModelException(
            "Error interno en predicción",
            details={"exception_type": type(e).__name__, "message": str(e)}
        )


@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> TrainingResponse:
    """
    Entrena un nuevo modelo con datos históricos.
    
    **Proceso:**
    1. Extrae datos de la base de datos
    2. Preprocesa y genera features
    3. Entrena múltiples modelos (RF, XGBoost, LightGBM)
    4. Selecciona el mejor por validación cruzada
    5. Guarda modelo y metadata
    
    **Parámetros:**
    - `start_date`, `end_date`: Rango de datos (opcional, usa todos si no se especifica)
    - `perform_cv`: Realizar validación cruzada (recomendado)
    - `feature_engineering`: Generar features adicionales
    
    **Retorna:**
    - Nombre del mejor modelo
    - Métricas de evaluación
    - Duración del entrenamiento
    - Ruta del modelo guardado
    
    **Nota:** El entrenamiento se ejecuta de forma síncrona. Puede tomar varios minutos.
    """
    try:
        logger.info(
            f"🎓 TRAINING: Iniciando entrenamiento",
            extra={
                "start_date": str(request.start_date) if request.start_date else "All",
                "end_date": str(request.end_date) if request.end_date else "All",
                "perform_cv": request.perform_cv,
                "feature_engineering": request.feature_engineering
            }
        )
        start_time = datetime.now()
        
        # 1. Obtener datos
        repository = PlantDataRepository(db)
        df = repository.get_combined_dataset(
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        logger.info(f"📊 Datos obtenidos: {len(df)} registros")
        
        # Validar datos suficientes
        if len(df) < config.min_training_samples:
            raise InsufficientDataException(
                f"Se requieren al menos {config.min_training_samples} muestras para entrenar",
                required=config.min_training_samples,
                found=len(df)
            )
        
        # 2. Feature Engineering
        if request.feature_engineering:
            logger.info("🔧 Aplicando feature engineering...")
            df = FeatureEngineer.engineer_features(df)
        
        # 3. Preprocesamiento
        logger.info("⚙️ Preprocesando datos...")
        preprocessor = DataPreprocessor(
            scaling_method=config.scaling_method
        )
        
        target_columns = config.target_variables
        X, y = preprocessor.prepare_dataset(
            df,
            target_columns=target_columns,
            handle_outliers_flag=True,
            scale=True
        )
        
        # 4. Entrenamiento
        logger.info("🤖 Entrenando modelos...")
        trainer = ChemicalConsumptionTrainer()
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.split_data(X, y)
        logger.info(
            f"📦 Split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}"
        )
        
        # Train all models
        scores = trainer.train_all_models(
            X_train, y_train,
            X_val, y_val,
            perform_cv=request.perform_cv
        )
        
        # Select best
        best_name, best_model = trainer.select_best_model()
        logger.info(f"🏆 Mejor modelo: {best_name}")
        
        # Feature importance
        trainer.extract_feature_importance(preprocessor.feature_names)
        
        # Evaluate on test set
        y_test_pred = best_model.predict(X_test)
        test_metrics = ModelEvaluator.calculate_metrics(
            y_test, y_test_pred,
            target_names=target_columns
        )
        
        # 5. Save model
        model_path = trainer.save_model(preprocessor)
        logger.info(f"💾 Modelo guardado: {model_path}")
        
        # Duration
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Entrenamiento completado en {duration:.2f}s")
        
        response = TrainingResponse(
            status="success",
            best_model=best_name,
            metrics=test_metrics,
            training_duration_seconds=duration,
            model_path=str(model_path)
        )
        
        # Reload predictor with new model in background
        logger.info("🔄 Recargando predictor con nuevo modelo...")
        background_tasks.add_task(predictor.load_model, model_path)
        
        return response
    
    except InsufficientDataException:
        raise
    
    except MLInsufficientData as e:
        logger.error(f"⚠️ Datos insuficientes: {str(e)}")
        raise InsufficientDataException(
            str(e),
            required=config.min_training_samples,
            found=0
        )
    
    except Exception as e:
        logger.error(
            f"❌ Error en entrenamiento: {type(e).__name__}",
            exc_info=True
        )
        raise MLModelException(
            f"Error al entrenar modelo: {str(e)}",
            details={"exception_type": type(e).__name__}
        )
        
        # 4. Entrenamiento
        trainer = ChemicalConsumptionTrainer()
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.split_data(X, y)
        
        # Train all models
        scores = trainer.train_all_models(
            X_train, y_train,
            X_val, y_val,
            perform_cv=request.perform_cv
        )
        
        # Select best
        best_name, best_model = trainer.select_best_model()
        
        # Feature importance
        trainer.extract_feature_importance(preprocessor.feature_names)
        
        # Evaluate on test set
        y_test_pred = best_model.predict(X_test)
        test_metrics = ModelEvaluator.calculate_metrics(
            y_test, y_test_pred,
            target_names=target_columns
        )
        
        # 5. Save model
        model_path = trainer.save_model(preprocessor)
        
        # Duration
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Entrenamiento completado en {duration:.2f}s")
        
        response = TrainingResponse(
            status="success",
            best_model=best_name,
            metrics=test_metrics,
            training_duration_seconds=duration,
            model_path=str(model_path)
        )
        
        # Reload predictor with new model in background
        background_tasks.add_task(predictor.load_model, model_path)
        
        return response
    
    except InsufficientDataError as e:
        logger.error(f"Datos insuficientes: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Datos insuficientes para entrenamiento: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en entrenamiento: {str(e)}")


@router.get("/anomalies", response_model=AnomalyResponse)
async def detect_anomalies(
    days: Optional[int] = Query(
        7,
        ge=1,
        le=365,
        description="Últimos N días a analizar (si no se especifican fechas)"
    ),
    fecha_inicio: Optional[date] = Query(
        None,
        description="Fecha de inicio (YYYY-MM-DD) - sobrescribe 'days'"
    ),
    fecha_fin: Optional[date] = Query(
        None,
        description="Fecha de fin (YYYY-MM-DD) - sobrescribe 'days'"
    ),
    use_model: bool = Query(
        True,
        description="Usar modelo ML para detección"
    ),
    use_thresholds: bool = Query(
        True,
        description="Usar umbrales estadísticos"
    ),
    db: Session = Depends(get_db)
) -> AnomalyResponse:
    """
    Detecta anomalías en datos operativos.
    
    **Parámetros:**
    - `days`: Analiza los últimos N días (por defecto 7)
    - `fecha_inicio` y `fecha_fin`: Rango de fechas específico (sobrescribe `days`)
    - `use_model`: Usar modelo ML para detección
    - `use_thresholds`: Usar umbrales estadísticos
    
    **Retorna:**
    - Lista de anomalías detectadas con severidad
    - Estadísticas del análisis
    - Rango de fechas analizado
    
    **Ejemplo:**
    ```
    GET /api/ml/anomalies?days=7
    GET /api/ml/anomalies?fecha_inicio=2026-01-01&fecha_fin=2026-01-31
    ```
    """
    try:
        # Determinar rango de fechas
        if fecha_inicio and fecha_fin:
            # Usar fechas específicas
            start_date = fecha_inicio
            end_date = fecha_fin
            logger.info(f"📊 Detectando anomalías: {start_date} a {end_date}")
        else:
            # Calcular desde 'days'
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            logger.info(f"📊 Detectando anomalías últimos {days} días: {start_date} a {end_date}")
        
        # Validar rango de fechas
        if start_date > end_date:
            raise ValidationException(
                "La fecha de inicio no puede ser posterior a la fecha de fin",
                details={"fecha_inicio": str(start_date), "fecha_fin": str(end_date)}
            )
        
        # Obtener datos
        repository = PlantDataRepository(db)
        df = repository.get_operational_data(
            start_date=start_date,
            end_date=end_date
        )
        
        # Verificar datos suficientes
        if df.empty or len(df) == 0:
            logger.warning(f"⚠️ No hay datos disponibles para el rango {start_date} a {end_date}")
            return AnomalyResponse(
                status="success",
                total_records=0,
                anomalies_detected=0,
                anomaly_rate_pct=0.0,
                by_severity={"critico": 0, "sospechoso": 0, "normal": 0},
                date_range={"start": str(start_date), "end": str(end_date)},
                anomalies=[]
            )
        
        logger.info(f"✅ Datos cargados: {len(df)} registros")
        
        # Detectar anomalías
        results = anomaly_detector.analyze_operational_data(df)
        
        # Convertir a dict
        anomalies = [result.to_dict() for result in results]
        
        # Estadísticas
        total_records = len(df)
        anomalies_detected = len(anomalies)
        anomaly_rate = (anomalies_detected / total_records * 100) if total_records > 0 else 0
        
        by_severity = {
            'critico': sum(1 for a in results if a.severidad == 'critico'),
            'sospechoso': sum(1 for a in results if a.severidad == 'sospechoso'),
            'normal': sum(1 for a in results if a.severidad == 'normal')
        }
        
        logger.info(
            f"🔍 Anomalías detectadas: {anomalies_detected}/{total_records} "
            f"({anomaly_rate:.2f}%) - Críticas: {by_severity['critico']}"
        )
        
        return AnomalyResponse(
            status="success",
            total_records=total_records,
            anomalies_detected=anomalies_detected,
            anomaly_rate_pct=round(anomaly_rate, 2),
            by_severity=by_severity,
            date_range={"start": str(start_date), "end": str(end_date)},
            anomalies=anomalies
        )
    
    except ValidationException:
        raise
    
    except MLInsufficientData as e:
        # Caso esperado: no hay datos en el rango solicitado
        logger.warning(f"⚠️ No hay datos disponibles para el rango {start_date} a {end_date}: {str(e)}")
        return AnomalyResponse(
            status="success",
            total_records=0,
            anomalies_detected=0,
            anomaly_rate_pct=0.0,
            by_severity={"critico": 0, "sospechoso": 0, "normal": 0},
            date_range={"start": str(start_date), "end": str(end_date)},
            anomalies=[]
        )
    
    except Exception as e:
        logger.error(f"❌ Error en detección de anomalías: {type(e).__name__} - {str(e)}", exc_info=True)
        raise MLModelException(
            f"Error al detectar anomalías: {str(e)}",
            details={"exception_type": type(e).__name__}
        )


@router.get("/model/info")
async def get_model_info() -> JSONResponse:
    """
    Obtiene información del modelo actual en producción.
    
    **Retorna:**
    - Nombre del modelo
    - Versión y fecha de entrenamiento
    - Métricas de evaluación
    - Features utilizadas
    
    **Ejemplo de respuesta:**
    ```json
    {
      "model_name": "XGBoost",
      "version": "1.0.0",
      "trained_at": "2026-02-18T10:30:00",
      "metrics": {"r2": 0.95, "mae": 2.3}
    }
    ```
    """
    try:
        logger.info("📊 REQUEST: Información del modelo")
        info = predictor.get_model_info()
        logger.info(f"✅ Modelo actual: {info.get('model_name', 'N/A')}")
        return JSONResponse(content=info)
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo info del modelo: {type(e).__name__}", exc_info=True)
        raise MLModelException(
            "Error al obtener información del modelo",
            details={"exception_type": type(e).__name__, "message": str(e)}
        )


@router.get("/stats")
async def get_ml_stats(
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Obtiene estadísticas generales del sistema ML.
    
    **Incluye:**
    - Disponibilidad de datos históricos
    - Información del modelo actual
    - Configuración del sistema ML
    
    **Respuesta:**
    - `data_availability`: Cantidad de datos por tipo
    - `current_model`: Info del modelo en producción
    - `config`: Parámetros de configuración ML
    """
    try:
        logger.info("📊 REQUEST: Estadísticas ML")
        
        repository = PlantDataRepository(db)
        data_stats = repository.get_data_statistics()
        
        model_info = predictor.get_model_info()
        
        stats = {
            'data_availability': data_stats,
            'current_model': model_info,
            'config': {
                'min_training_samples': config.min_training_samples,
                'enabled_models': config.enabled_models,
                'primary_metric': config.primary_metric
            }
        }
        
        logger.info(
            f"✅ Stats: {data_stats.get('total_records', 0)} registros disponibles"
        )
        
        return JSONResponse(content=stats)
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {type(e).__name__}", exc_info=True)
        raise MLModelException(
            "Error al obtener estadísticas ML",
            details={"exception_type": type(e).__name__, "message": str(e)}
        )


@router.post("/model/reload")
async def reload_model() -> JSONResponse:
    """
    Recarga el modelo más reciente en memoria.
    
    **Uso:**
    - Después de entrenar un nuevo modelo
    - Si el modelo en memoria está corrupto
    - Para forzar actualización
    
    **Retorna:**
    - Estado de la operación
    - Información del modelo recargado
    
    **Nota:** Esta operación es rápida (< 1 segundo)
    """
    try:
        logger.info("🔄 REQUEST: Recargar modelo")
        
        predictor.load_model()
        info = predictor.get_model_info()
        
        logger.info(f"✅ Modelo recargado: {info.get('model_name', 'N/A')}")
        
        return JSONResponse(content={
            'status': 'success',
            'message': 'Modelo recargado exitosamente',
            'model_info': info
        })
    
    except Exception as e:
        logger.error(f"❌ Error recargando modelo: {type(e).__name__}", exc_info=True)
        raise MLModelException(
            "Error al recargar modelo",
            details={"exception_type": type(e).__name__, "message": str(e)}
        )
