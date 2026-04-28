"""Inference services package initialization."""

from .predictor_service import ChemicalConsumptionPredictor
from .anomaly_service import AnomalyDetectorService

__all__ = [
    "ChemicalConsumptionPredictor",
    "AnomalyDetectorService",
]
