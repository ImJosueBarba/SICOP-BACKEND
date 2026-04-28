"""
Utilidades para gestión de configuración del sistema ML.

Proporciona acceso centralizado a la configuración yaml con validación de tipos.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache


class MLConfig:
    """
    Gestor de configuración del sistema ML.
    
    Implementa Singleton pattern para evitar múltiples lecturas del archivo.
    Proporciona acceso type-safe a parámetros de configuración.
    """
    
    _instance: Optional['MLConfig'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Carga la configuración desde el archivo YAML."""
        config_path = Path(__file__).parent.parent / "config" / "ml_config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {config_path}"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de punto.
        
        Args:
            key_path: Ruta al valor (ej: 'models.random_forest.params.n_estimators')
            default: Valor por defecto si no existe la clave
            
        Returns:
            Valor de configuración o default
            
        Example:
            config = MLConfig()
            n_estimators = config.get('models.random_forest.params.n_estimators', 100)
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def min_training_samples(self) -> int:
        """Mínimo de muestras requeridas para entrenamiento."""
        return self.get('data.min_training_samples', 90)
    
    @property
    def test_size(self) -> float:
        """Proporción de datos para test."""
        return self.get('data.train_test_split.test_size', 0.20)
    
    @property
    def validation_size(self) -> float:
        """Proporción de datos para validación."""
        return self.get('data.train_test_split.validation_size', 0.15)
    
    @property
    def random_state(self) -> int:
        """Semilla aleatoria para reproducibilidad."""
        return self.get('data.train_test_split.random_state', 42)
    
    @property
    def input_features(self) -> list[str]:
        """Lista de variables de entrada."""
        return self.get('features.input_variables', [])
    
    @property
    def target_variables(self) -> list[str]:
        """Lista de variables objetivo."""
        return self.get('features.target_variables', [])
    
    @property
    def scaling_method(self) -> str:
        """Método de escalado de features."""
        return self.get('features.transformations.scaling.method', 'standard')
    
    @property
    def models_dir(self) -> Path:
        """Directorio para almacenar modelos entrenados."""
        base_dir = Path(__file__).parent.parent
        models_path = self.get('persistence.models_dir', 'ml/trained_models')
        return base_dir / models_path
    
    @property
    def enabled_models(self) -> list[str]:
        """Lista de modelos habilitados para entrenamiento."""
        models_config = self.get('models.algorithms', {})
        return [
            name for name, config in models_config.items()
            if config.get('enabled', False)
        ]
    
    @property
    def primary_metric(self) -> str:
        """Métrica principal para selección de modelo."""
        return self.get('models.selection_criteria.primary_metric', 'rmse')
    
    @property
    def min_r2_score(self) -> float:
        """R² mínimo aceptable."""
        return self.get('evaluation.thresholds.min_r2_score', 0.70)
    
    @property
    def cv_splits(self) -> int:
        """Número de folds para validación cruzada."""
        return self.get('models.cross_validation.n_splits', 5)
    
    def get_model_params(self, model_name: str) -> Dict[str, Any]:
        """
        Obtiene los hiperparámetros de un modelo específico.
        
        Args:
            model_name: Nombre del modelo (random_forest, xgboost, lightgbm)
            
        Returns:
            Diccionario con hiperparámetros
        """
        return self.get(f'models.algorithms.{model_name}.params', {})
    
    def ensure_directories(self) -> None:
        """Crea los directorios necesarios si no existen."""
        base_dir = Path(__file__).parent.parent
        
        directories = [
            self.get('paths.data_dir'),
            self.get('paths.models_dir'),
            self.get('paths.logs_dir'),
            self.get('paths.reports_dir'),
        ]
        
        for directory in directories:
            if directory:
                path = base_dir / directory
                path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_config() -> MLConfig:
    """
    Factory function para obtener instancia singleton de configuración.
    
    Returns:
        Instancia de MLConfig
    """
    return MLConfig()
