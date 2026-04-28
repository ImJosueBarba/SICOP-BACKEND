"""
Entrenador de modelos ML para predicción de consumo de químicos.

Implementa pipeline completo de entrenamiento con comparación de múltiples algoritmos.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.multioutput import MultiOutputRegressor
import xgboost as xgb
import lightgbm as lgb
from datetime import datetime
from pathlib import Path

from ..utils.logger import MLLogger
from ..utils.config_manager import get_config
from ..data.preprocessor import DataPreprocessor
from ..features.feature_engineer import FeatureEngineer

logger = MLLogger.get_training_logger()
config = get_config()


class ChemicalConsumptionTrainer:
    """
    Entrenador de modelos para predicción de consumo de químicos.
    
    Responsabilidades:
    - Entrenar múltiples modelos (Random Forest, XGBoost, LightGBM)
    - Comparar rendimiento
    - Seleccionar mejor modelo
    - Validación cruzada
    - Persistir modelo y metadata
    
    Arquitectura:
    - Strategy Pattern: Diferentes algoritmos intercambiables
    - Template Method: Pipeline común para todos los modelos
    """
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scores: Dict[str, Dict[str, float]] = {}
        self.best_model_name: Optional[str] = None
        self.best_model: Optional[Any] = None
        self.feature_importance: Optional[pd.DataFrame] = None
        self.training_metadata: Dict[str, Any] = {}
        
    def _initialize_models(self) -> Dict[str, Any]:
        """
        Inicializa modelos según configuración.
        
        Returns:
            Diccionario con modelos instanciados
        """
        models_dict = {}
        
        # Random Forest
        if 'random_forest' in config.enabled_models:
            rf_params = config.get_model_params('random_forest')
            models_dict['random_forest'] = MultiOutputRegressor(
                RandomForestRegressor(**rf_params)
            )
            logger.info("Random Forest inicializado")
        
        # XGBoost
        if 'xgboost' in config.enabled_models:
            xgb_params = config.get_model_params('xgboost')
            models_dict['xgboost'] = MultiOutputRegressor(
                xgb.XGBRegressor(**xgb_params)
            )
            logger.info("XGBoost inicializado")
        
        # LightGBM
        if 'lightgbm' in config.enabled_models:
            lgb_params = config.get_model_params('lightgbm')
            models_dict['lightgbm'] = MultiOutputRegressor(
                lgb.LGBMRegressor(**lgb_params)
            )
            logger.info("LightGBM inicializado")
        
        return models_dict
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame,
               pd.DataFrame, pd.DataFrame]:
        """
        Divide datos en train, validation y test.
        
        Args:
            X: Features
            y: Targets
            
        Returns:
            Tupla (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        logger.info("Dividiendo dataset en train/val/test")
        
        test_size = config.test_size
        val_size = config.validation_size
        random_state = config.random_state
        
        # Primera división: train+val / test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            shuffle=True
        )
        
        # Segunda división: train / val
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=random_state,
            shuffle=True
        )
        
        logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_model(
        self,
        model: Any,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        X_val: pd.DataFrame,
        y_val: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Entrena un modelo individual y calcula métricas.
        
        Args:
            model: Modelo a entrenar
            model_name: Nombre del modelo
            X_train: Features de entrenamiento
            y_train: Targets de entrenamiento
            X_val: Features de validación
            y_val: Targets de validación
            
        Returns:
            Diccionario con métricas de validación
        """
        logger.info(f"Entrenando modelo: {model_name}")
        
        # Entrenar
        model.fit(X_train, y_train)
        
        # Predecir en validación
        y_pred = model.predict(X_val)
        
        # Calcular métricas
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_val - y_pred) / (y_val + 1e-10))) * 100
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape
        }
        
        logger.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, "
                   f"R²: {r2:.4f}, MAPE: {mape:.2f}%")
        
        return metrics
    
    def cross_validate_model(
        self,
        model: Any,
        model_name: str,
        X: pd.DataFrame,
        y: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Realiza validación cruzada.
        
        Args:
            model: Modelo a validar
            model_name: Nombre del modelo
            X: Features completas
            y: Targets completos
            
        Returns:
            Diccionario con métricas promedio
        """
        logger.info(f"Validación cruzada: {model_name}")
        
        n_splits = config.cv_splits
        kfold = KFold(n_splits=n_splits, shuffle=True, random_state=config.random_state)
        
        # Scoring para regresión
        cv_mae = -cross_val_score(
            model, X, y,
            cv=kfold,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )
        
        cv_rmse = np.sqrt(-cross_val_score(
            model, X, y,
            cv=kfold,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        ))
        
        cv_r2 = cross_val_score(
            model, X, y,
            cv=kfold,
            scoring='r2',
            n_jobs=-1
        )
        
        metrics = {
            'cv_mae_mean': cv_mae.mean(),
            'cv_mae_std': cv_mae.std(),
            'cv_rmse_mean': cv_rmse.mean(),
            'cv_rmse_std': cv_rmse.std(),
            'cv_r2_mean': cv_r2.mean(),
            'cv_r2_std': cv_r2.std()
        }
        
        logger.info(f"{model_name} CV - MAE: {metrics['cv_mae_mean']:.2f} ± {metrics['cv_mae_std']:.2f}, "
                   f"R²: {metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}")
        
        return metrics
    
    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        X_val: pd.DataFrame,
        y_val: pd.DataFrame,
        perform_cv: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """
        Entrena todos los modelos configurados.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Targets de entrenamiento
            X_val: Features de validación
            y_val: Targets de validación
            perform_cv: Si se realiza validación cruzada
            
        Returns:
            Diccionario con scores de todos los modelos
        """
        logger.info("=== Iniciando entrenamiento de todos los modelos ===")
        
        self.models = self._initialize_models()
        all_scores = {}
        
        for model_name, model in self.models.items():
            # Entrenar y evaluar en validación
            val_metrics = self.train_model(
                model, model_name,
                X_train, y_train,
                X_val, y_val
            )
            
            all_scores[model_name] = val_metrics
            
            # Validación cruzada (opcional)
            if perform_cv:
                # Combinar train + val para CV
                X_combined = pd.concat([X_train, X_val])
                y_combined = pd.concat([y_train, y_val])
                
                cv_metrics = self.cross_validate_model(
                    model, model_name,
                    X_combined, y_combined
                )
                all_scores[model_name].update(cv_metrics)
        
        self.scores = all_scores
        logger.info("=== Entrenamiento completado ===")
        
        return all_scores
    
    def select_best_model(self) -> Tuple[str, Any]:
        """
        Selecciona el mejor modelo según métrica configurada.
        
        Returns:
            Tupla (nombre_modelo, modelo)
        """
        logger.info("Seleccionando mejor modelo")
        
        primary_metric = config.primary_metric
        minimize = config.get('models.selection_criteria.minimize', True)
        
        best_score = float('inf') if minimize else float('-inf')
        best_name = None
        
        for model_name, metrics in self.scores.items():
            score = metrics.get(primary_metric, float('inf') if minimize else float('-inf'))
            
            if minimize:
                if score < best_score:
                    best_score = score
                    best_name = model_name
            else:
                if score > best_score:
                    best_score = score
                    best_name = model_name
        
        self.best_model_name = best_name
        self.best_model = self.models[best_name]
        
        logger.info(f"Mejor modelo: {best_name} con {primary_metric}={best_score:.4f}")
        
        return best_name, self.best_model
    
    def extract_feature_importance(
        self,
        feature_names: List[str],
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Extrae importancia de features del mejor modelo.
        
        Args:
            feature_names: Nombres de features
            top_n: Top N features más importantes
            
        Returns:
            DataFrame con importancias ordenadas
        """
        if self.best_model is None:
            logger.warning("No hay modelo seleccionado")
            return pd.DataFrame()
        
        logger.info("Extrayendo importancia de features")
        
        try:
            # MultiOutputRegressor contiene estimadores base
            base_estimator = self.best_model.estimators_[0]
            
            if hasattr(base_estimator, 'feature_importances_'):
                importances = base_estimator.feature_importances_
                
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importances
                }).sort_values('importance', ascending=False)
                
                self.feature_importance = importance_df.head(top_n)
                
                logger.info(f"Top 5 features:")
                for idx, row in self.feature_importance.head(5).iterrows():
                    logger.info(f"  {row['feature']}: {row['importance']:.4f}")
                
                return self.feature_importance
            
        except Exception as e:
            logger.warning(f"No se pudo extraer importancia: {e}")
        
        return pd.DataFrame()
    
    def save_model(
        self,
        preprocessor: DataPreprocessor,
        save_dir: Optional[Path] = None
    ) -> Path:
        """
        Guarda el mejor modelo con metadata.
        
        Args:
            preprocessor: Preprocesador utilizado
            save_dir: Directorio donde guardar (opcional)
            
        Returns:
            Path donde se guardó
        """
        if self.best_model is None:
            raise ValueError("No hay modelo para guardar. Ejecute select_best_model() primero.")
        
        if save_dir is None:
            save_dir = config.models_dir
        
        # Crear directorio con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = save_dir / f"model_{self.best_model_name}_{timestamp}"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Guardando modelo en: {model_dir}")
        
        # Guardar modelo
        import joblib
        joblib.dump(self.best_model, model_dir / "model.pkl", compress=3)
        
        # Guardar preprocesador
        preprocessor.save(model_dir)
        
        # Guardar metadata
        metadata = {
            'model_name': self.best_model_name,
            'training_date': datetime.now().isoformat(),
            'metrics': self.scores[self.best_model_name],
            'feature_names': preprocessor.feature_names,
            'config': {
                'test_size': config.test_size,
                'validation_size': config.validation_size,
                'random_state': config.random_state,
            }
        }
        
        if self.feature_importance is not None:
            metadata['top_features'] = self.feature_importance.to_dict('records')
        
        joblib.dump(metadata, model_dir / "metadata.pkl")
        
        logger.info(f"Modelo guardado exitosamente en {model_dir}")
        
        return model_dir
