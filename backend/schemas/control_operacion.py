"""
Schemas Pydantic para el modelo ControlOperacion (Matriz 2)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


# Schema base
class ControlOperacionBase(BaseModel):
    """Schema base de Control de Operación"""
    fecha: date
    hora: time
    
    # Turbedad
    turbedad_ac: Optional[Decimal] = None
    turbedad_at: Optional[Decimal] = None
    
    # Color
    color: Optional[str] = Field(None, max_length=50)
    
    # pH
    ph_ac: Optional[Decimal] = None
    ph_sulf: Optional[Decimal] = None
    ph_at: Optional[Decimal] = None
    
    # Dosis Químicos
    dosis_sulfato: Optional[Decimal] = None
    dosis_cal: Optional[Decimal] = None
    dosis_floergel: Optional[Decimal] = None
    
    # Factor de Forma
    ff: Optional[Decimal] = None
    
    # Clarificación
    clarificacion_is: Optional[Decimal] = None
    clarificacion_cs: Optional[Decimal] = None
    clarificacion_fs: Optional[Decimal] = None
    
    # Presión
    presion_psi: Optional[Decimal] = None
    presion_pre: Optional[Decimal] = None
    presion_pos: Optional[Decimal] = None
    presion_total: Optional[Decimal] = None
    
    # Cloración
    cloro_residual: Optional[Decimal] = None
    
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para crear
class ControlOperacionCreate(ControlOperacionBase):
    """Schema para crear un nuevo registro de control"""
    pass


# Schema para actualizar
class ControlOperacionUpdate(BaseModel):
    """Schema para actualizar un registro de control existente"""
    fecha: Optional[date] = None
    hora: Optional[time] = None
    turbedad_ac: Optional[Decimal] = None
    turbedad_at: Optional[Decimal] = None
    color: Optional[str] = None
    ph_ac: Optional[Decimal] = None
    ph_sulf: Optional[Decimal] = None
    ph_at: Optional[Decimal] = None
    dosis_sulfato: Optional[Decimal] = None
    dosis_cal: Optional[Decimal] = None
    dosis_floergel: Optional[Decimal] = None
    ff: Optional[Decimal] = None
    clarificacion_is: Optional[Decimal] = None
    clarificacion_cs: Optional[Decimal] = None
    clarificacion_fs: Optional[Decimal] = None
    presion_psi: Optional[Decimal] = None
    presion_pre: Optional[Decimal] = None
    presion_pos: Optional[Decimal] = None
    presion_total: Optional[Decimal] = None
    cloro_residual: Optional[Decimal] = None
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para respuesta
class ControlOperacionResponse(ControlOperacionBase):
    """Schema de respuesta con datos completos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
