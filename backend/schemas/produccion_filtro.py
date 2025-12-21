"""
Schemas Pydantic para el modelo ProduccionFiltro (Matriz 3)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal


# Schema base
class ProduccionFiltroBase(BaseModel):
    """Schema base de Producción por Filtro"""
    fecha: date
    hora: time
    
    # Filtro 1
    filtro1_h: Optional[Decimal] = None
    filtro1_q: Optional[Decimal] = None
    
    # Filtro 2
    filtro2_h: Optional[Decimal] = None
    filtro2_q: Optional[Decimal] = None
    
    # Filtro 3
    filtro3_h: Optional[Decimal] = None
    filtro3_q: Optional[Decimal] = None
    
    # Filtro 4
    filtro4_h: Optional[Decimal] = None
    filtro4_q: Optional[Decimal] = None
    
    # Filtro 5
    filtro5_h: Optional[Decimal] = None
    filtro5_q: Optional[Decimal] = None
    
    # Filtro 6
    filtro6_h: Optional[Decimal] = None
    filtro6_q: Optional[Decimal] = None
    
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para crear
class ProduccionFiltroCreate(ProduccionFiltroBase):
    """Schema para crear un nuevo registro de producción"""
    pass


# Schema para actualizar
class ProduccionFiltroUpdate(BaseModel):
    """Schema para actualizar un registro de producción existente"""
    fecha: Optional[date] = None
    hora: Optional[time] = None
    filtro1_h: Optional[Decimal] = None
    filtro1_q: Optional[Decimal] = None
    filtro2_h: Optional[Decimal] = None
    filtro2_q: Optional[Decimal] = None
    filtro3_h: Optional[Decimal] = None
    filtro3_q: Optional[Decimal] = None
    filtro4_h: Optional[Decimal] = None
    filtro4_q: Optional[Decimal] = None
    filtro5_h: Optional[Decimal] = None
    filtro5_q: Optional[Decimal] = None
    filtro6_h: Optional[Decimal] = None
    filtro6_q: Optional[Decimal] = None
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para respuesta
class ProduccionFiltroResponse(ProduccionFiltroBase):
    """Schema de respuesta con datos completos"""
    id: int
    caudal_total: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
