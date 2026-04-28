"""
Sistema de Machine Learning para Optimización de Consumo de Químicos
Planta de Tratamiento de Agua "La Esperanza"

Arquitectura:
    - domain/: Entidades de dominio y lógica de negocio
    - data/: Capa de acceso a datos y repositorios
    - features/: Feature engineering y transformaciones
    - models/: Entrenamiento, evaluación y gestión de modelos
    - inference/: Servicios de predicción en producción
    - utils/: Utilidades comunes (config, logging, validación)
    
Principios:
    - Clean Architecture
    - SOLID
    - Separation of Concerns
    - Dependency Inversion
"""

__version__ = "1.0.0"
__author__ = "SICOP Team - Planta La Esperanza"

# Lazy imports para evitar cargar dependencias ML al inicio
# Solo se importarán cuando se usen explícitamente
def __getattr__(name):
    """Lazy loading de servicios ML."""
    if name == "ChemicalConsumptionPredictor":
        from .inference.predictor_service import ChemicalConsumptionPredictor
        return ChemicalConsumptionPredictor
    elif name == "AnomalyDetectorService":
        from .inference.anomaly_service import AnomalyDetectorService
        return AnomalyDetectorService
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "ChemicalConsumptionPredictor",
    "AnomalyDetectorService",
]
