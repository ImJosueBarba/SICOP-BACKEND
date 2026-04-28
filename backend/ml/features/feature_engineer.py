"""
Feature Engineering para el sistema ML.

Crea features derivadas que mejoran el poder predictivo del modelo.
"""

import pandas as pd
import numpy as np
from typing import List, Dict

from ..utils.logger import MLLogger

logger = MLLogger.get_training_logger()


class FeatureEngineer:
    """
    Ingeniero de features para datos de tratamiento de agua.
    
    Crea features derivadas basadas en conocimiento del dominio:
    - Ratios y diferencias entre agua cruda y tratada
    - Features temporales (mes, día de semana, estacionalidad)
    - Rolling statistics (medias móviles)
    - Lag features (valores históricos)
    - Interacciones entre variables
    
    Principios:
    - Domain-Driven Design: Features basadas en conocimiento experto
    - Single Responsibility: Solo creación de features
    """
    
    @staticmethod
    def create_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features de ratios entre agua cruda y tratada.
        
        Los ratios capturan la eficiencia del tratamiento.
        
        Args:
            df: DataFrame con datos originales
            
        Returns:
            DataFrame con features de ratio agregadas
        """
        logger.info("Creando features de ratios")
        
        df_enhanced = df.copy()
        
        # Ratio de turbidez (indicador de eficiencia de clarificación)
        if 'turbedad_ac' in df.columns and 'turbedad_at' in df.columns:
            df_enhanced['turbedad_ratio'] = (
                df_enhanced['turbedad_ac'] / (df_enhanced['turbedad_at'] + 0.01)
            )
            # Eficiencia de remoción de turbidez (%)
            df_enhanced['turbedad_removal_pct'] = (
                (df_enhanced['turbedad_ac'] - df_enhanced['turbedad_at']) /
                (df_enhanced['turbedad_ac'] + 0.01) * 100
            )
        
        # Ratio de conductividad
        if 'conductividad_ac' in df.columns and 'conductividad_at' in df.columns:
            df_enhanced['conductividad_ratio'] = (
                df_enhanced['conductividad_ac'] / (df_enhanced['conductividad_at'] + 0.01)
            )
        
        # Ratio de TDS (Total Dissolved Solids)
        if 'tds_ac' in df.columns and 'tds_at' in df.columns:
            df_enhanced['tds_ratio'] = (
                df_enhanced['tds_ac'] / (df_enhanced['tds_at'] + 0.01)
            )
        
        return df_enhanced
    
    @staticmethod
    def create_delta_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features de diferencias absolutas.
        
        Las deltas indican cambios en parámetros a través del tratamiento.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame con deltas
        """
        logger.info("Creando features de deltas")
        
        df_enhanced = df.copy()
        
        # Delta de pH (cambio a través del tratamiento)
        if 'ph_ac' in df.columns and 'ph_at' in df.columns:
            df_enhanced['ph_delta'] = df_enhanced['ph_ac'] - df_enhanced['ph_at']
        
        # Delta de temperatura
        if 'temperatura_ac' in df.columns and 'temperatura_at' in df.columns:
            df_enhanced['temperatura_delta'] = (
                df_enhanced['temperatura_ac'] - df_enhanced['temperatura_at']
            )
        
        return df_enhanced
    
    @staticmethod
    def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features de interacción entre variables.
        
        Capturarelaciones multiplicativas importantes en el proceso químico.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame con interacciones
        """
        logger.info("Creando features de interacción")
        
        df_enhanced = df.copy()
        
        # Interacción turbidez * dosis sulfato
        # (a mayor turbidez, se espera mayor dosis de coagulante)
        if 'turbedad_ac' in df.columns and 'dosis_sulfato' in df.columns:
            df_enhanced['turbedad_x_sulfato'] = (
                df_enhanced['turbedad_ac'] * df_enhanced['dosis_sulfato']
            )
        
        # Interacción pH * dosis cal
        # (la cal ajusta pH)
        if 'ph_ac' in df.columns and 'dosis_cal' in df.columns:
            df_enhanced['ph_x_cal'] = (
                df_enhanced['ph_ac'] * df_enhanced['dosis_cal']
            )
        
        # Caudal total * turbidez (carga de sólidos total)
        if 'caudal_total' in df.columns and 'turbedad_ac' in df.columns:
            df_enhanced['carga_solidos'] = (
                df_enhanced['caudal_total'] * df_enhanced['turbedad_ac']
            )
        
        return df_enhanced
    
    @staticmethod
    def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features temporales para capturar estacionalidad.
        
        Args:
            df: DataFrame con columna 'fecha'
            
        Returns:
            DataFrame con features temporales
        """
        logger.info("Creando features temporales")
        
        if 'fecha' not in df.columns:
            logger.warning("No se encontró columna 'fecha', saltando features temporales")
            return df
        
        df_enhanced = df.copy()
        
        # Asegurar que fecha es datetime
        df_enhanced['fecha'] = pd.to_datetime(df_enhanced['fecha'])
        
        # Mes del año (captura estacionalidad anual)
        df_enhanced['mes_num'] = df_enhanced['fecha'].dt.month
        
        # Día de la semana (operaciones pueden variar por día)
        df_enhanced['dia_semana'] = df_enhanced['fecha'].dt.dayofweek
        
        # Trimestre
        df_enhanced['trimestre'] = df_enhanced['fecha'].dt.quarter
        
        # Es fin de semana
        df_enhanced['es_fin_semana'] = (
            df_enhanced['dia_semana'].isin([5, 6])
        ).astype(int)
        
        # Componentes cíclicos de mes (sin y cos para mantener continuidad)
        df_enhanced['mes_sin'] = np.sin(2 * np.pi * df_enhanced['mes_num'] / 12)
        df_enhanced['mes_cos'] = np.cos(2 * np.pi * df_enhanced['mes_num'] / 12)
        
        return df_enhanced
    
    @staticmethod
    def create_rolling_features(
        df: pd.DataFrame,
        columns: List[str],
        windows: List[int] = [3, 7, 14]
    ) -> pd.DataFrame:
        """
        Crea features de rolling statistics (medias móviles).
        
        Captura tendencias recientes en los datos.
        
        Args:
            df: DataFrame ordenado por fecha
            columns: Columnas para calcular rolling stats
            windows: Ventanas temporales en días
            
        Returns:
            DataFrame con rolling features
        """
        logger.info(f"Creando rolling features: ventanas={windows}")
        
        df_enhanced = df.copy()
        
        # Asegurar orden temporal
        if 'fecha' in df_enhanced.columns:
            df_enhanced = df_enhanced.sort_values('fecha')
        
        for col in columns:
            if col not in df_enhanced.columns:
                continue
            
            for window in windows:
                # Media móvil
                df_enhanced[f'{col}_rolling_mean_{window}d'] = (
                    df_enhanced[col].rolling(window=window, min_periods=1).mean()
                )
                
                # Desviación estándar móvil (captura volatilidad)
                df_enhanced[f'{col}_rolling_std_{window}d'] = (
                    df_enhanced[col].rolling(window=window, min_periods=1).std()
                )
        
        # Rellenar NaN iniciales con el valor de la columna original
        for col in df_enhanced.columns:
            if 'rolling' in col:
                df_enhanced[col] = df_enhanced[col].fillna(method='bfill')
        
        return df_enhanced
    
    @staticmethod
    def create_lag_features(
        df: pd.DataFrame,
        columns: List[str],
        lags: List[int] = [1, 7, 14]
    ) -> pd.DataFrame:
        """
        Crea lag features (valores históricos).
        
        Captura dependencias temporales y patrones recurrentes.
        
        Args:
            df: DataFrame ordenado por fecha
            columns: Columnas para crear lags
            lags: Desplazamientos temporales en días
            
        Returns:
            DataFrame con lag features
        """
        logger.info(f"Creando lag features: lags={lags}")
        
        df_enhanced = df.copy()
        
        # Asegurar orden temporal
        if 'fecha' in df_enhanced.columns:
            df_enhanced = df_enhanced.sort_values('fecha')
        
        for col in columns:
            if col not in df_enhanced.columns:
                continue
            
            for lag in lags:
                df_enhanced[f'{col}_lag_{lag}d'] = df_enhanced[col].shift(lag)
        
        # Rellenar NaN iniciales con forward fill
        for col in df_enhanced.columns:
            if '_lag_' in col:
                df_enhanced[col] = df_enhanced[col].fillna(method='bfill')
        
        return df_enhanced
    
    @staticmethod
    def engineer_features(
        df: pd.DataFrame,
        create_ratios: bool = True,
        create_deltas: bool = True,
        create_interactions: bool = True,
        create_temporal: bool = True,
        create_rolling: bool = False,  # Computacionalmente costoso
        create_lags: bool = False  # También costoso
    ) -> pd.DataFrame:
        """
        Pipeline completo de feature engineering.
        
        Args:
            df: DataFrame original
            create_ratios: Crear features de ratios
            create_deltas: Crear features de deltas
            create_interactions: Crear interacciones
            create_temporal: Crear features temporales
            create_rolling: Crear rolling statistics
            create_lags: Crear lag features
            
        Returns:
            DataFrame con todas las features engineered
        """
        logger.info("=== Iniciando Feature Engineering ===")
        
        df_enhanced = df.copy()
        initial_features = df_enhanced.shape[1]
        
        if create_ratios:
            df_enhanced = FeatureEngineer.create_ratio_features(df_enhanced)
        
        if create_deltas:
            df_enhanced = FeatureEngineer.create_delta_features(df_enhanced)
        
        if create_interactions:
            df_enhanced = FeatureEngineer.create_interaction_features(df_enhanced)
        
        if create_temporal:
            df_enhanced = FeatureEngineer.create_temporal_features(df_enhanced)
        
        if create_rolling:
            rolling_cols = [
                'turbedad_ac', 'ph_ac', 'dosis_sulfato', 'caudal_total'
            ]
            rolling_cols = [c for c in rolling_cols if c in df_enhanced.columns]
            if rolling_cols:
                df_enhanced = FeatureEngineer.create_rolling_features(
                    df_enhanced, rolling_cols
                )
        
        if create_lags:
            lag_cols = ['turbedad_ac', 'ph_ac', 'dosis_sulfato']
            lag_cols = [c for c in lag_cols if c in df_enhanced.columns]
            if lag_cols:
                df_enhanced = FeatureEngineer.create_lag_features(
                    df_enhanced, lag_cols
                )
        
        new_features = df_enhanced.shape[1] - initial_features
        logger.info(f"=== Feature Engineering completado: +{new_features} features ===")
        logger.info(f"Total features: {df_enhanced.shape[1]}")
        
        return df_enhanced
