"""
Schemas Pydantic para el modelo ControlConsumoDiario (Matriz 4)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


# Schema base
class ControlConsumoDiarioBase(BaseModel):
    """Schema base de Control de Consumo Diario"""
    fecha: date
    quimico_id: int
    
    # Bodega
    bodega_ingresa: Optional[int] = None
    bodega_egresa: Optional[int] = None
    bodega_stock: Optional[int] = None
    
    # Tanque N1
    tanque1_hora: Optional[time] = None
    tanque1_lectura_inicial: Optional[Decimal] = None
    tanque1_lectura_final: Optional[Decimal] = None
    tanque1_consumo: Optional[Decimal] = None
    
    # Tanque N2
    tanque2_hora: Optional[time] = None
    tanque2_lectura_inicial: Optional[Decimal] = None
    tanque2_lectura_final: Optional[Decimal] = None
    tanque2_consumo: Optional[Decimal] = None
    
    # Total
    total_consumo: Optional[Decimal] = None
    
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para crear
class ControlConsumoDiarioCreate(ControlConsumoDiarioBase):
    """Schema para crear un nuevo registro de consumo diario"""
    pass


# Schema para actualizar
class ControlConsumoDiarioUpdate(BaseModel):
    """Schema para actualizar un registro de consumo diario existente"""
    fecha: Optional[date] = None
    quimico_id: Optional[int] = None
    bodega_ingresa: Optional[int] = None
    bodega_egresa: Optional[int] = None
    bodega_stock: Optional[int] = None
    tanque1_hora: Optional[time] = None
    tanque1_lectura_inicial: Optional[Decimal] = None
    tanque1_lectura_final: Optional[Decimal] = None
    tanque1_consumo: Optional[Decimal] = None
    tanque2_hora: Optional[time] = None
    tanque2_lectura_inicial: Optional[Decimal] = None
    tanque2_lectura_final: Optional[Decimal] = None
    tanque2_consumo: Optional[Decimal] = None
    total_consumo: Optional[Decimal] = None
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para respuesta
class ControlConsumoDiarioResponse(ControlConsumoDiarioBase):
    """Schema de respuesta con datos completos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
