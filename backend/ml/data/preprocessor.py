"""
Preprocesador de datos para el sistema ML.

Implementa limpieza, transformación y preparación de datos
siguiendo buenas prácticas de data science.
"""

from typing import Optional, Tuple, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
import joblib
from pathlib import Path

from ..utils.logger import MLLogger
from ..utils.config_manager import get_config
from ..utils.validation import DataValidator

logger = MLLogger.get_training_logger()
config = get_config()


class DataPreprocessor:
    """
    Preprocesador de datos para ML.
    
    Responsabilidades:
    - Limpieza de datos (missing values, outliers)
    - Transformaciones (scaling, encoding)
    - Separación train/validation/test
    - Persistencia de transformadores
    
    Principios aplicados:
    - Single Responsibility: Solo preprocesamiento
    - Open/Closed: Extensible vía herencia
    - Liskov Substitution: Sustituible por otros preprocessors
    """
    
    def __init__(self, scaling_method: str = "standard"):
        """
        Inicializa el preprocesador.
        
        Args:
            scaling_method: Método de escalado ('standard', 'robust', 'minmax')
        """
        self.scaling_method = scaling_method
        self.scaler: Optional[StandardScaler] = None
        self.imputer: Optional[SimpleImputer] = None
        self.feature_names: List[str] = []
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia el dataset removiendo errores obvios.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame limpio
        """
        logger.info(f"Limpiando datos: {len(df)} registros iniciales")
        
        df_clean = df.copy()
        initial_rows = len(df_clean)
        
        # 1. Remover duplicados
        df_clean = df_clean.drop_duplicates()
        logger.info(f"Duplicados removidos: {initial_rows - len(df_clean)}")
        
        # 2. Validar y limpiar valores negativos en variables que no pueden serlo
        positive_columns = [
            'turbedad_ac', 'turbedad_at', 'dosis_sulfato', 'dosis_cal',
            'produccion_m3', 'sulfato_consumo_kg', 'cal_consumo_kg',
            'hipoclorito_consumo_kg', 'cloro_gas_consumo_kg'
        ]
        
        for col in positive_columns:
            if col in df_clean.columns:
                negative_mask = df_clean[col] < 0
                if negative_mask.any():
                    logger.warning(f"Valores negativos en {col}: {negative_mask.sum()}")
                    df_clean.loc[negative_mask, col] = np.nan
        
        # 3. Validar rangos de pH (debe estar entre 0-14)
        ph_columns = ['ph_ac', 'ph_sulfato', 'ph_at']
        for col in ph_columns:
            if col in df_clean.columns:
                invalid_ph = (df_clean[col] < 0) | (df_clean[col] > 14)
                if invalid_ph.any():
                    logger.warning(f"pH inválido en {col}: {invalid_ph.sum()}")
                    df_clean.loc[invalid_ph, col] = np.nan
        
        # 4. Validar rangos de temperatura (razonable: 0-50°C)
        temp_columns = ['temperatura_ac', 'temperatura_at']
        for col in temp_columns:
            if col in df_clean.columns:
                invalid_temp = (df_clean[col] < 0) | (df_clean[col] > 50)
                if invalid_temp.any():
                    logger.warning(f"Temperatura inválida en {col}: {invalid_temp.sum()}")
                    df_clean.loc[invalid_temp, col] = np.nan
        
        logger.info(f"Datos limpios: {len(df_clean)} registros")
        return df_clean
    
    def handle_outliers(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = "iqr",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Maneja outliers en columnas numéricas.
        
        Args:
            df: DataFrame
            columns: Columnas a procesar
            method: Método ('iqr', 'zscore')
            threshold: Umbral para detección
            
        Returns:
            DataFrame con outliers manejados
        """
        logger.info(f"Manejando outliers método: {method}")
        
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            if method == "iqr":
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                
            elif method == "zscore":
                mean = df_clean[col].mean()
                std = df_clean[col].std()
                z_scores = np.abs((df_clean[col] - mean) / std)
                outliers = z_scores > threshold
            
            else:
                raise ValueError(f"Método desconocido: {method}")
            
            if outliers.any():
                logger.info(f"Outliers detectados en {col}: {outliers.sum()}")
                # Estrategia: reemplazar por NaN (luego será imputado)
                df_clean.loc[outliers, col] = np.nan
        
        return df_clean
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = "median"
    ) -> pd.DataFrame:
        """
        Maneja valores faltantes.
        
        Args:
            df: DataFrame con valores faltantes
            strategy: Estrategia ('mean', 'median', 'forward_fill')
            
        Returns:
            DataFrame sin valores faltantes
        """
        logger.info(f"Manejando valores faltantes: estrategia={strategy}")
        
        df_filled = df.copy()
        
        # Reportar % de missing values
        missing_pct = (df_filled.isnull().sum() / len(df_filled) * 100)
        for col, pct in missing_pct[missing_pct > 0].items():
            logger.info(f"  {col}: {pct:.2f}% missing")
        
        if strategy in ['mean', 'median']:
            if self.imputer is None:
                self.imputer = SimpleImputer(strategy=strategy)
                numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
                df_filled[numeric_cols] = self.imputer.fit_transform(df_filled[numeric_cols])
            else:
                numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
                df_filled[numeric_cols] = self.imputer.transform(df_filled[numeric_cols])
        
        elif strategy == "forward_fill":
            df_filled = df_filled.fillna(method='ffill')
            # Lidiar con primeros valores que no tienen fill
            df_filled = df_filled.fillna(method='bfill')
        
        elif strategy == "interpolate":
            numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
            df_filled[numeric_cols] = df_filled[numeric_cols].interpolate(
                method='linear',
                limit_direction='both'
            )
        
        # Remover filas que aún tienen NaN (si es que quedaron)
        rows_with_nan = df_filled.isnull().any(axis=1).sum()
        if rows_with_nan > 0:
            logger.warning(f"Removiendo {rows_with_nan} filas con NaN persistentes")
            df_filled = df_filled.dropna()
        
        logger.info(f"Valores faltantes manejados: {len(df_filled)} registros resultantes")
        return df_filled
    
    def scale_features(
        self,
        X: pd.DataFrame,
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Escala features numéricas.
        
        Args:
            X: DataFrame con features
            fit: Si True, ajusta el scaler (solo training); si False, usa existente
            
        Returns:
            DataFrame escalado
        """
        logger.info(f"Escalando features: método={self.scaling_method}, fit={fit}")
        
        if fit:
            if self.scaling_method == "standard":
                self.scaler = StandardScaler()
            elif self.scaling_method == "robust":
                self.scaler = RobustScaler()
            elif self.scaling_method == "minmax":
                self.scaler = MinMaxScaler()
            else:
                raise ValueError(f"Método de escalado desconocido: {self.scaling_method}")
            
            X_scaled = self.scaler.fit_transform(X)
        else:
            if self.scaler is None:
                raise ValueError("Scaler no entrenado. Ejecute primero con fit=True")
            X_scaled = self.scaler.transform(X)
        
        # Mantener nombres de columnas
        X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        return X_scaled_df
    
    def split_features_targets(
        self,
        df: pd.DataFrame,
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separa features (X) y targets (y).
        
        Args:
            df: DataFrame completo
            target_columns: Nombres de columnas objetivo
            
        Returns:
            Tupla (X, y)
        """
        logger.info(f"Separando features y targets")
        
        # Verificar que existan las columnas target
        missing_targets = set(target_columns) - set(df.columns)
        if missing_targets:
            raise ValueError(f"Columnas target faltantes: {missing_targets}")
        
        # Remover columnas no numéricas y targets de X
        non_numeric = ['fecha', 'hora', 'anio', 'mes']
        columns_to_drop = non_numeric + target_columns
        
        X = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        y = df[target_columns]
        
        self.feature_names = list(X.columns)
        
        logger.info(f"Features (X): {X.shape}, Targets (y): {y.shape}")
        logger.info(f"Feature names: {self.feature_names}")
        
        return X, y
    
    def prepare_dataset(
        self,
        df: pd.DataFrame,
        target_columns: List[str],
        handle_outliers_flag: bool = True,
        scale: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Pipeline completo de preparación de datos.
        
        Args:
            df: DataFrame crudo
            target_columns: Columnas objetivo
            handle_outliers_flag: Si se manejan outliers
            scale: Si se escalan features
            
        Returns:
            Tupla (X_prepared, y)
        """
        logger.info("=== Iniciando pipeline de preparación de datos ===")
        
        # 1. Limpieza básica
        df_clean = self.clean_data(df)
        
        # 2. Separar features y targets
        X, y = self.split_features_targets(df_clean, target_columns)
        
        # 3. Manejar outliers (solo en features)
        if handle_outliers_flag:
            X = self.handle_outliers(
                X,
                columns=X.columns.tolist(),
                method=config.get('features.transformations.outlier_handling.method', 'iqr')
            )
        
        # 4. Manejar valores faltantes
        strategy = config.get('features.transformations.missing_values.strategy', 'median')
        X = self.handle_missing_values(X, strategy=strategy)
        
        # Sincronizar índices de X e y después de remover filas
        y = y.loc[X.index]
        
        # 5. Escalar features
        if scale:
            X = self.scale_features(X, fit=True)
        
        logger.info(f"=== Preparación completada: X{X.shape}, y{y.shape} ===")
        
        return X, y
    
    def save(self, path: Path) -> None:
        """
        Guarda el preprocesador (scaler, imputer).
        
        Args:
            path: Directorio donde guardar
        """
        path.mkdir(parents=True, exist_ok=True)
        
        if self.scaler:
            joblib.dump(self.scaler, path / "scaler.pkl")
            logger.info(f"Scaler guardado en {path / 'scaler.pkl'}")
        
        if self.imputer:
            joblib.dump(self.imputer, path / "imputer.pkl")
            logger.info(f"Imputer guardado en {path / 'imputer.pkl'}")
        
        # Guardar feature names
        if self.feature_names:
            joblib.dump(self.feature_names, path / "feature_names.pkl")
            logger.info(f"Feature names guardados")
    
    @classmethod
    def load(cls, path: Path) -> 'DataPreprocessor':
        """
        Carga un preprocesador guardado.
        
        Args:
            path: Directorio donde está guardado
            
        Returns:
            Instancia de DataPreprocessor
        """
        preprocessor = cls()
        
        scaler_path = path / "scaler.pkl"
        if scaler_path.exists():
            preprocessor.scaler = joblib.load(scaler_path)
            logger.info("Scaler cargado")
        
        imputer_path = path / "imputer.pkl"
        if imputer_path.exists():
            preprocessor.imputer = joblib.load(imputer_path)
            logger.info("Imputer cargado")
        
        feature_names_path = path / "feature_names.pkl"
        if feature_names_path.exists():
            preprocessor.feature_names = joblib.load(feature_names_path)
            logger.info(f"Feature names cargados: {len(preprocessor.feature_names)} features")
        
        return preprocessor
