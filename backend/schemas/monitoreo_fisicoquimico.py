"""
Schemas Pydantic para el modelo MonitoreoFisicoquimico (Matriz 6)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


# Schema base
class MonitoreoFisicoquimicoBase(BaseModel):
    """Schema base de Monitoreo Fisicoquímico"""
    fecha: date
    usuario_id: Optional[int] = None
    lugar_agua_cruda: Optional[str] = Field(None, max_length=200)
    lugar_agua_tratada: Optional[str] = Field(None, max_length=200)
    
    muestra_numero: int = Field(..., ge=1, le=3)
    hora: time
    
    # Agua Cruda
    ac_ph: Optional[Decimal] = None
    ac_ce: Optional[Decimal] = None
    ac_tds: Optional[Decimal] = None
    ac_salinidad: Optional[Decimal] = None
    ac_temperatura: Optional[Decimal] = None
    
    # Agua Tratada
    at_ph: Optional[Decimal] = None
    at_ce: Optional[Decimal] = None
    at_tds: Optional[Decimal] = None
    at_salinidad: Optional[Decimal] = None
    at_temperatura: Optional[Decimal] = None
    
    observaciones: Optional[str] = None


# Schema para crear
class MonitoreoFisicoquimicoCreate(MonitoreoFisicoquimicoBase):
    """Schema para crear un nuevo registro de monitoreo"""
    pass


# Schema para actualizar
class MonitoreoFisicoquimicoUpdate(BaseModel):
    """Schema para actualizar un registro de monitoreo existente"""
    fecha: Optional[date] = None
    usuario_id: Optional[int] = None
    lugar_agua_cruda: Optional[str] = None
    lugar_agua_tratada: Optional[str] = None
    muestra_numero: Optional[int] = Field(None, ge=1, le=3)
    hora: Optional[time] = None
    ac_ph: Optional[Decimal] = None
    ac_ce: Optional[Decimal] = None
    ac_tds: Optional[Decimal] = None
    ac_salinidad: Optional[Decimal] = None
    ac_temperatura: Optional[Decimal] = None
    at_ph: Optional[Decimal] = None
    at_ce: Optional[Decimal] = None
    at_tds: Optional[Decimal] = None
    at_salinidad: Optional[Decimal] = None
    at_temperatura: Optional[Decimal] = None
    observaciones: Optional[str] = None


# Schema para respuesta
class MonitoreoFisicoquimicoResponse(MonitoreoFisicoquimicoBase):
    """Schema de respuesta con datos completos"""
    id: int
    diferencia_ph: Optional[float]
    diferencia_tds: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
