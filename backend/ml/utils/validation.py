"""
Validadores y excepciones personalizadas para el sistema ML.
"""

from typing import Any, Optional
from datetime import date, datetime
import numpy as np
import pandas as pd


class MLValidationError(Exception):
    """Excepción base para errores de validación ML."""
    pass


class InsufficientDataError(MLValidationError):
    """Se lanza cuando no hay suficientes datos para entrenamiento."""
    pass


class InvalidFeatureError(MLValidationError):
    """Se lanza cuando una feature tiene valores inválidos."""
    pass


class ModelNotFoundError(Exception):
    """Se lanza quando no se encuentra un modelo entrenado."""
    pass


class DataValidator:
    """
    Validador de datos de entrada para el sistema ML.
    
    Implementa validaciones de negocio y técnicas para garantizar
    calidad de datos antes del entrenamiento o inferencia.
    """
    
    @staticmethod
    def validate_turbidity(value: float, is_raw_water: bool = True) -> None:
        """
        Valida valores de turbidez.
        
        Args:
            value: Valor de turbidez en FTU
            is_raw_water: True si es agua cruda, False si es tratada
            
        Raises:
            InvalidFeatureError: Si el valor está fuera de rango
        """
        if value < 0:
            raise InvalidFeatureError("La turbidez no puede ser negativa")
        
        if is_raw_water and value > 500:
            raise InvalidFeatureError(
                f"Turbidez de agua cruda excesivamente alta: {value} FTU"
            )
        
        if not is_raw_water and value > 5:
            raise InvalidFeatureError(
                f"Turbidez de agua tratada fuera de norma: {value} FTU"
            )
    
    @staticmethod
    def validate_ph(value: float) -> None:
        """
        Valida valores de pH.
        
        Args:
            value: Valor de pH
            
        Raises:
            InvalidFeatureError: Si el pH está fuera de rango válido
        """
        if not (0 <= value <= 14):
            raise InvalidFeatureError(
                f"pH fuera de rango válido (0-14): {value}"
            )
        
        if value < 6.0 or value > 9.5:
            raise InvalidFeatureError(
                f"pH fuera de rango operativo seguro (6.0-9.5): {value}"
            )
    
    @staticmethod
    def validate_temperature(value: float) -> None:
        """
        Valida temperatura del agua.
        
        Args:
            value: Temperatura en °C
            
        Raises:
            InvalidFeatureError: Si la temperatura está fuera de rango
        """
        if not (0 <= value <= 50):
            raise InvalidFeatureError(
                f"Temperatura fuera de rango esperado (0-50°C): {value}"
            )
    
    @staticmethod
    def validate_chlorine(value: float) -> None:
        """
        Valida cloro residual.
        
        Args:
            value: Cloro residual en mg/L
            
        Raises:
            InvalidFeatureError: Si el cloro está fuera de norma
        """
        if value < 0:
            raise InvalidFeatureError("Cloro residual no puede ser negativo")
        
        if value > 5:
            raise InvalidFeatureError(
                f"Cloro residual excesivamente alto: {value} mg/L"
            )
    
    @staticmethod
    def validate_chemical_consumption(value: float, chemical_name: str) -> None:
        """
        Valida consumo de químico.
        
        Args:
            value: Cantidad consumida en kg
            chemical_name: Nombre del químico
            
        Raises:
            InvalidFeatureError: Si el consumo es inválido
        """
        if value < 0:
            raise InvalidFeatureError(
                f"Consumo de {chemical_name} no puede ser negativo"
            )
        
        # Límites razonables por tipo de químico (kg/día)
        limits = {
            'sulfato': 5000,
            'cal': 2000,
            'hipoclorito': 1000,
            'cloro_gas': 500
        }
        
        for key, limit in limits.items():
            if key in chemical_name.lower() and value > limit:
                raise InvalidFeatureError(
                    f"Consumo de {chemical_name} excesivamente alto: {value} kg"
                )
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        required_columns: list[str],
        min_rows: int = 1
    ) -> None:
        """
        Valida estructura de DataFrame.
        
        Args:
            df: DataFrame a validar
            required_columns: Columnas requeridas
            min_rows: Mínimo de filas requeridas
            
        Raises:
            MLValidationError: Si la validación falla
        """
        if df.empty:
            raise MLValidationError("DataFrame vacío")
        
        if len(df) < min_rows:
            raise InsufficientDataError(
                f"Insuficientes registros: {len(df)}, mínimo requerido: {min_rows}"
            )
        
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise MLValidationError(
                f"Columnas faltantes: {missing_cols}"
            )
        
        # Verificar tipos de datos básicos
        for col in required_columns:
            if col in df.columns and df[col].dtype == object:
                # Intentar convertir a numérico si es posible
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    raise MLValidationError(
                        f"Columna '{col}' tiene tipo de dato inválido"
                    )
    
    @staticmethod
    def validate_date_range(
        start_date: date,
        end_date: date,
        min_year: int = 2020
    ) -> None:
        """
        Valida rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            min_year: Año mínimo válido
            
        Raises:
            MLValidationError: Si el rango es inválido
        """
        if start_date > end_date:
            raise MLValidationError(
                "Fecha de inicio posterior a fecha de fin"
            )
        
        if start_date.year < min_year:
            raise MLValidationError(
                f"Fecha de inicio anterior al año mínimo ({min_year})"
            )
        
        if end_date > date.today():
            raise MLValidationError(
                "Fecha de fin en el futuro"
            )
    
    @staticmethod
    def validate_prediction_input(input_data: dict[str, Any]) -> None:
        """
        Valida datos de entrada para predicción.
        
        Args:
            input_data: Diccionario con features de entrada
            
        Raises:
            MLValidationError: Si los datos son inválidos
        """
        required_keys = [
            'turbedad_ac', 'turbedad_at', 'ph_ac', 'ph_at',
            'temperatura_ac', 'caudal_total'
        ]
        
        missing = [k for k in required_keys if k not in input_data]
        if missing:
            raise MLValidationError(
                f"Features faltantes para predicción: {missing}"
            )
        
        # Validar rangos
        if 'turbedad_ac' in input_data:
            DataValidator.validate_turbidity(
                input_data['turbedad_ac'], is_raw_water=True
            )
        
        if 'turbedad_at' in input_data:
            DataValidator.validate_turbidity(
                input_data['turbedad_at'], is_raw_water=False
            )
        
        if 'ph_ac' in input_data:
            DataValidator.validate_ph(input_data['ph_ac'])
        
        if 'ph_at' in input_data:
            DataValidator.validate_ph(input_data['ph_at'])
        
        if 'temperatura_ac' in input_data:
            DataValidator.validate_temperature(input_data['temperatura_ac'])
        
        if 'cloro_residual' in input_data:
            DataValidator.validate_chlorine(input_data['cloro_residual'])
