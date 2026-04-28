"""
Servicio de predicción de consumo de químicos en producción.

Proporciona interfaz de alto nivel para inferencia con modelo entrenado.
"""

from typing import Dict, Any, Optional, List
from datetime import date
import pandas as pd
import numpy as np
from pathlib import Path

from ..models.model_manager import ModelManager
from ..features.feature_engineer import FeatureEngineer
from ..domain.entities import PredictionResult
from ..utils.logger import MLLogger
from ..utils.validation import DataValidator, MLValidationError
from ..utils.config_manager import get_config

logger = MLLogger.get_inference_logger()
config = get_config()


class ChemicalConsumptionPredictor:
    """
    Servicio de predicción de consumo de químicos.
    
    Responsabilidades:
    - Cargar modelo entrenado
    - Preparar datos de entrada
    - Realizar predicciones
    - Calcular intervalos de confianza
    - Logging de predicciones
    
    Arquitectura:
    - Facade Pattern: Interfaz simplificada para predicción
    - Singleton: Una instancia compartida en la aplicación
    """
    
    _instance: Optional['ChemicalConsumptionPredictor'] = None
    
    def __new__(cls):
        """Implementa patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el predictor."""
        if self._initialized:
            return
        
        self.model_manager = ModelManager()
        self.model = None
        self.preprocessor = None
        self.metadata = None
        self.feature_names = []
        self._is_loaded = False
        self._initialized = True
    
    def load_model(self, model_path: Optional[Path] = None) -> None:
        """
        Carga el modelo para inferencia.
        
        Args:
            model_path: Ruta específica (opcional, usa último por defecto)
            
        Raises:
            ModelNotFoundError: Si no se encuentra el modelo
        """
        logger.info("Cargando modelo para inferencia")
        
        self.model, self.preprocessor, self.metadata = (
            self.model_manager.load_model(model_path)
        )
        
        self.feature_names = self.metadata.get('feature_names', [])
        self._is_loaded = True
        
        logger.info(f"Predictor listo: modelo '{self.metadata.get('model_name')}'")
    
    def _ensure_model_loaded(self) -> None:
        """
        Asegura que el modelo esté cargado antes de predecir.
        
        Raises:
            RuntimeError: Si el modelo no está cargado
        """
        if not self._is_loaded:
            # Intentar cargar automáticamente el último modelo
            try:
                self.load_model()
            except Exception as e:
                raise RuntimeError(
                    "Modelo no cargado y no se pudo cargar automáticamente. "
                    "Ejecute primero load_model(). Error: " + str(e)
                )
    
    def _prepare_input_features(
        self,
        input_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Prepara features de entrada para el modelo.
        
        Args:
            input_data: Diccionario con parámetros operativos
            
        Returns:
            DataFrame con features preparadas
            
        Raises:
            MLValidationError: Si los datos son inválidos
        """
        # Validar datos de entrada
        DataValidator.validate_prediction_input(input_data)
        
        # Crear DataFrame base
        df = pd.DataFrame([input_data])
        
        # Aplicar feature engineering (mismas transformaciones que entrenamiento)
        df_engineered = FeatureEngineer.engineer_features(
            df,
            create_ratios=True,
            create_deltas=True,
            create_interactions=True,
            create_temporal=False,  # No hay fecha en predicción online
            create_rolling=False,  # No aplicable en predicción única
            create_lags=False  # No aplicable en predicción única
        )
        
        # Seleccionar solo las features que el modelo espera
        # (algunas features engineered pueden no estar disponibles sin histórico)
        available_features = [f for f in self.feature_names if f in df_engineered.columns]
        
        if len(available_features) < len(self.feature_names) * 0.7:  # Al menos 70%
            missing = set(self.feature_names) - set(available_features)
            logger.warning(f"Features faltantes: {missing}")
        
        # Crear DataFrame con todas las features esperadas, rellenar con 0 las faltantes
        X = pd.DataFrame(columns=self.feature_names)
        for feature in self.feature_names:
            if feature in df_engineered.columns:
                X[feature] = df_engineered[feature]
            else:
                X[feature] = 0  # Valor por defecto para features faltantes
        
        # Aplicar mismo preprocesamiento (scaling)
        X_scaled = self.preprocessor.scale_features(X, fit=False)
        
        return X_scaled
    
    def predict(
        self,
        turbedad_ac: float,
        turbedad_at: float,
        ph_ac: float,
        ph_at: float,
        temperatura_ac: float,
        caudal_total: Optional[float] = None,
        dosis_sulfato: Optional[float] = None,
        dosis_cal: Optional[float] = None,
        cloro_residual: Optional[float] = None,
        **kwargs
    ) -> PredictionResult:
        """
        Realiza predicción de consumo de químicos.
        
        Args:
            turbedad_ac: Turbidez agua cruda (FTU)
            turbedad_at: Turbidez agua tratada (FTU)
            ph_ac: pH agua cruda
            ph_at: pH agua tratada
            temperatura_ac: Temperatura agua cruda (°C)
            caudal_total: Caudal total (m³/día) (opcional)
            dosis_sulfato: Dosis actual de sulfato (l/s) (opcional)
            dosis_cal: Dosis actual de cal (l/s) (opcional)
            cloro_residual: Cloro residual (mg/L) (opcional)
            **kwargs: Parámetros adicionales
            
        Returns:
            PredictionResult con predicciones
            
        Raises:
            MLValidationError: Si los datos son inválidos
            RuntimeError: Si el modelo no está cargado
        """
        self._ensure_model_loaded()
        
        logger.info("Realizando predicción de consumo")
        
        # Preparar input
        input_data = {
            'turbedad_ac': turbedad_ac,
            'turbedad_at': turbedad_at,
            'ph_ac': ph_ac,
            'ph_at': ph_at,
            'temperatura_ac': temperatura_ac,
            'caudal_total': caudal_total or 5000.0,  # Default razonable
            'dosis_sulfato': dosis_sulfato or 0.0,
            'dosis_cal': dosis_cal or 0.0,
            'cloro_residual': cloro_residual or 0.5
        }
        
        # Agregar kwargs
        input_data.update(kwargs)
        
        try:
            # Preparar features
            X = self._prepare_input_features(input_data)
            
            # Predecir
            y_pred = self.model.predict(X)
            
            # Asegurar valores no negativos
            y_pred = np.maximum(y_pred, 0)
            
            # Extraer predicciones individuales
            sulfato = float(y_pred[0, 0])
            cal = float(y_pred[0, 1])
            hipoclorito = float(y_pred[0, 2])
            cloro_gas = float(y_pred[0, 3])
            
            # Calcular confianza basada en métricas del modelo
            r2_score = self.metadata.get('metrics', {}).get('r2', 0.5)
            confidence = min(max(r2_score, 0.0), 1.0)  # Clamp entre 0-1
            
            result = PredictionResult(
                sulfato_predicho=sulfato,
                cal_predicha=cal,
                hipoclorito_predicho=hipoclorito,
                cloro_gas_predicho=cloro_gas,
                confidence_score=confidence,
                model_name=self.metadata.get('model_name', 'unknown'),
                prediction_date=date.today()
            )
            
            logger.info(f"Predicción exitosa - Sulfato: {sulfato:.2f} kg, "
                       f"Cal: {cal:.2f} kg, Hipoclorito: {hipoclorito:.2f} kg, "
                       f"Cloro Gas: {cloro_gas:.2f} kg")
            
            return result
        
        except Exception as e:
            logger.error(f"Error en predicción: {e}", exc_info=True)
            raise
    
    def predict_batch(
        self,
        inputs: List[Dict[str, Any]]
    ) -> List[PredictionResult]:
        """
        Realiza predicciones en lote.
        
        Args:
            inputs: Lista de diccionarios con parámetros
            
        Returns:
            Lista de PredictionResult
        """
        self._ensure_model_loaded()
        
        logger.info(f"Predicción en lote: {len(inputs)} registros")
        
        results = []
        for input_data in inputs:
            try:
                result = self.predict(**input_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error en predicción individual: {e}")
                # Agregar resultado con errores
                results.append(PredictionResult(
                    sulfato_predicho=0,
                    cal_predicha=0,
                    hipoclorito_predicho=0,
                    cloro_gas_predicho=0,
                    confidence_score=0.0,
                    model_name="error"
                ))
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo actual.
        
        Returns:
            Diccionario con información
        """
        if not self._is_loaded:
            return {'status': 'not_loaded'}
        
        return self.model_manager.get_model_info()
    
    def calculate_cost_savings(
        self,
        predicted_consumption: Dict[str, float],
        actual_consumption: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula ahorro estimado comparando consumo predicho vs real.
        
        Args:
            predicted_consumption: Consumo predicho (kg)
            actual_consumption: Consumo real (kg)
            
        Returns:
            Diccionario con ahorro por químico y total
        """
        # Precios aproximados (USD/kg)
        prices = {
            'sulfato': 0.50,
            'cal': 0.30,
            'hipoclorito': 2.00,
            'cloro_gas': 1.50
        }
        
        savings = {}
        total_savings = 0.0
        
        for chemical in prices.keys():
            predicted = predicted_consumption.get(chemical, 0)
            actual = actual_consumption.get(chemical, 0)
            
            diff_kg = actual - predicted
            savings_usd = diff_kg * prices[chemical]
            
            savings[f'{chemical}_kg_diff'] = diff_kg
            savings[f'{chemical}_usd_savings'] = savings_usd
            total_savings += savings_usd
        
        savings['total_savings_usd'] = total_savings
        savings['optimization_pct'] = (total_savings / sum(
            actual_consumption.get(k, 0) * prices[k] for k in prices
        )) * 100 if actual_consumption else 0
        
        return savings
