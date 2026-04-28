"""
Sistema de logging estructurado para el módulo ML.

Proporciona loggers configurados para diferentes subsistemas.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class MLLogger:
    """
    Gestor centralizado de logging para el sistema ML.
    
    Proporciona loggers específicos para:
    - Entrenamiento de modelos
    - Inferencia/predicción
    - Detección de anomalías
    - Errores críticos
    """
    
    _loggers: dict[str, logging.Logger] = {}
    
    @classmethod
    def _setup_logger(
        cls,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO
    ) -> logging.Logger:
        """
        Configura un logger con formato estructurado.
        
        Args:
            name: Nombre del logger
            log_file: Ruta del archivo de log (opcional)
            level: Nivel de logging
            
        Returns:
            Logger configurado
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Evitar duplicación de handlers
        if logger.handlers:
            return logger
        
        # Formato estructurado
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo (si se especifica)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @classmethod
    def get_training_logger(cls) -> logging.Logger:
        """Logger para procesos de entrenamiento."""
        if 'training' not in cls._loggers:
            cls._loggers['training'] = cls._setup_logger(
                name='ml.training',
                log_file='logs/ml_training.log',
                level=logging.INFO
            )
        return cls._loggers['training']
    
    @classmethod
    def get_inference_logger(cls) -> logging.Logger:
        """Logger para inferencia y predicciones."""
        if 'inference' not in cls._loggers:
            cls._loggers['inference'] = cls._setup_logger(
                name='ml.inference',
                log_file='logs/ml_inference.log',
                level=logging.INFO
            )
        return cls._loggers['inference']
    
    @classmethod
    def get_anomaly_logger(cls) -> logging.Logger:
        """Logger para detección de anomalías."""
        if 'anomaly' not in cls._loggers:
            cls._loggers['anomaly'] = cls._setup_logger(
                name='ml.anomaly',
                log_file='logs/ml_anomaly.log',
                level=logging.INFO
            )
        return cls._loggers['anomaly']
    
    @classmethod
    def get_error_logger(cls) -> logging.Logger:
        """Logger para errores críticos."""
        if 'error' not in cls._loggers:
            cls._loggers['error'] = cls._setup_logger(
                name='ml.error',
                log_file='logs/ml_errors.log',
                level=logging.ERROR
            )
        return cls._loggers['error']


def log_function_call(logger: logging.Logger):
    """
    Decorador para logging automático de llamadas a funciones.
    
    Args:
        logger: Logger a utilizar
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Ejecutando {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} completado exitosamente")
                return result
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator
