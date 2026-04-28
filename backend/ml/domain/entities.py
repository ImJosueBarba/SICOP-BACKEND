"""
Entidades de dominio para el sistema ML.

Representan los conceptos del negocio de tratamiento de agua
con sus reglas y validaciones.
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional
from decimal import Decimal


@dataclass
class OperationalData:
    """
    Representa un registro de operación de la planta.
    
    Contiene mediciones operativas en un momento específico del día,
    incluyendo parámetros fisicoquímicos y dosis de químicos aplicadas.
    """
    
    # Identificación temporal
    fecha: date
    hora: time
    
    # Turbidez (FTU - Formazin Turbidity Unit)
    turbedad_ac: Optional[Decimal] = None  # Agua Cruda
    turbedad_at: Optional[Decimal] = None  # Agua Tratada
    
    # pH
    ph_ac: Optional[Decimal] = None  # Agua Cruda
    ph_sulfato: Optional[Decimal] = None  # Con sulfato aplicado
    ph_at: Optional[Decimal] = None  # Agua Tratada
    
    # Dosis de químicos aplicadas (l/s)
    dosis_sulfato: Optional[Decimal] = None
    dosis_cal: Optional[Decimal] = None
    dosis_floergel: Optional[Decimal] = None
    
    # Parámetros operativos
    presion_total: Optional[Decimal] = None  # kg/h
    cloro_residual: Optional[Decimal] = None  # mg/l
    
    # Temperatura y conductividad (del monitoreo fisicoquímico)
    temperatura_ac: Optional[Decimal] = None  # °C
    temperatura_at: Optional[Decimal] = None
    conductividad_ac: Optional[Decimal] = None  # μS/cm
    conductividad_at: Optional[Decimal] = None
    tds_ac: Optional[Decimal] = None  # Total Dissolved Solids (ppm)
    tds_at: Optional[Decimal] = None
    
    # Metadatos
    usuario_id: Optional[int] = None
    
    @property
    def turbedad_ratio(self) -> Optional[float]:
        """Ratio de reducción de turbidez (AC/AT)."""
        if self.turbedad_ac and self.turbedad_at and self.turbedad_at > 0:
            return float(self.turbedad_ac / self.turbedad_at)
        return None
    
    @property
    def ph_delta(self) -> Optional[float]:
        """Diferencia de pH entre agua cruda y tratada."""
        if self.ph_ac and self.ph_at:
            return float(self.ph_ac - self.ph_at)
        return None
    
    @property
    def treatment_efficiency(self) -> Optional[float]:
        """
        Eficiencia del tratamiento basada en reducción de turbidez (%).
        """
        if self.turbedad_ac and self.turbedad_at and self.turbedad_ac > 0:
            reduction = (self.turbedad_ac - self.turbedad_at) / self.turbedad_ac
            return float(reduction * 100)
        return None


@dataclass
class ChemicalConsumption:
    """
    Representa el consumo mensual de químicos en la planta.
    
    Registra las cantidades consumidas de cada tipo de químico
    utilizado en el proceso de tratamiento.
    """
    
    # Identificación temporal
    fecha: date
    mes: int
    anio: int
    
    # Sulfato de Aluminio (kg)
    sulfato_consumo_kg: Optional[Decimal] = None
    
    # Cal (kg)
    cal_consumo_kg: Optional[Decimal] = None
    
    # Hipoclorito de Calcio (kg)
    hipoclorito_consumo_kg: Optional[Decimal] = None
    
    # Gas Licuado de Cloro (kg)
    cloro_gas_consumo_kg: Optional[Decimal] = None
    
    # Producción total del mes
    produccion_m3: Optional[Decimal] = None
    
    # Metadata
    usuario_id: Optional[int] = None
    
    @property
    def sulfato_per_m3(self) -> Optional[float]:
        """Consumo de sulfato por m³ producido."""
        if self.sulfato_consumo_kg and self.produccion_m3 and self.produccion_m3 > 0:
            return float(self.sulfato_consumo_kg / self.produccion_m3)
        return None
    
    @property
    def cal_per_m3(self) -> Optional[float]:
        """Consumo de cal por m³ producido."""
        if self.cal_consumo_kg and self.produccion_m3 and self.produccion_m3 > 0:
            return float(self.cal_consumo_kg / self.produccion_m3)
        return None
    
    @property
    def total_chemical_cost_estimate(self) -> Optional[float]:
        """
        Estimación simplificada de costo total de químicos.
        
        Precios aproximados (USD/kg):
        - Sulfato de Aluminio: $0.50/kg
        - Cal: $0.30/kg
        - Hipoclorito: $2.00/kg
        - Cloro Gas: $1.50/kg
        """
        total = Decimal(0)
        
        if self.sulfato_consumo_kg:
            total += self.sulfato_consumo_kg * Decimal('0.50')
        if self.cal_consumo_kg:
            total += self.cal_consumo_kg * Decimal('0.30')
        if self.hipoclorito_consumo_kg:
            total += self.hipoclorito_consumo_kg * Decimal('2.00')
        if self.cloro_gas_consumo_kg:
            total += self.cloro_gas_consumo_kg * Decimal('1.50')
        
        return float(total) if total > 0 else None


@dataclass
class PredictionResult:
    """
    Resultado de una predicción de consumo de químicos.
    
    Encapsula los valores predichos con metadatos de confianza y explicabilidad.
    """
    
    # Predicciones (kg)
    sulfato_predicho: float
    cal_predicha: float
    hipoclorito_predicho: float
    cloro_gas_predicho: float
    
    # Métricas de confianza
    confidence_score: float = field(default=0.0)  # 0-1
    model_name: str = field(default="unknown")
    prediction_date: date = field(default_factory=date.today)
    
    # Intervalos de confianza (opcional)
    sulfato_lower: Optional[float] = None
    sulfato_upper: Optional[float] = None
    cal_lower: Optional[float] = None
    cal_upper: Optional[float] = None
    
    @property
    def estimated_cost(self) -> float:
        """Costo estimado total basado en predicciones."""
        return (
            self.sulfato_predicho * 0.50 +
            self.cal_predicha * 0.30 +
            self.hipoclorito_predicho * 2.00 +
            self.cloro_gas_predicho * 1.50
        )
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            'sulfato_kg': self.sulfato_predicho,
            'cal_kg': self.cal_predicha,
            'hipoclorito_kg': self.hipoclorito_predicho,
            'cloro_gas_kg': self.cloro_gas_predicho,
            'confidence': self.confidence_score,
            'model': self.model_name,
            'estimated_cost_usd': self.estimated_cost,
            'prediction_date': self.prediction_date.isoformat()
        }


@dataclass
class AnomalyResult:
    """
    Resultado de detección de anomalías en parámetros operativos.
    """
    
    fecha: date
    hora: time
    parametro: str
    valor: float
    es_anomalia: bool
    severidad: str  # 'normal', 'sospechoso', 'critico'
    anomaly_score: float  # Score del algoritmo (-1 a 1)
    explicacion: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización."""
        return {
            'fecha': self.fecha.isoformat(),
            'hora': self.hora.isoformat(),
            'parametro': self.parametro,
            'valor': self.valor,
            'es_anomalia': self.es_anomalia,
            'severidad': self.severidad,
            'score': self.anomaly_score,
            'explicacion': self.explicacion
        }
