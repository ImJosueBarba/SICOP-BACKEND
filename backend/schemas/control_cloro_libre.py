"""
Schemas Pydantic para el modelo ControlCloroLibre (Matriz 5)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime


# Schema base
class ControlCloroLibreBase(BaseModel):
    """Schema base de Control de Cloro Libre"""
    fecha_mes: date
    documento_soporte: Optional[str] = Field(None, max_length=100)
    proveedor_solicitante: Optional[str] = Field(None, max_length=100)
    codigo: Optional[str] = Field(None, max_length=50)
    especificacion: Optional[str] = Field(None, max_length=200)
    
    # Movimientos
    cantidad_entra: int = 0
    cantidad_sale: int = 0
    cantidad_saldo: Optional[int] = None
    
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para crear
class ControlCloroLibreCreate(ControlCloroLibreBase):
    """Schema para crear un nuevo registro de cloro libre"""
    pass


# Schema para actualizar
class ControlCloroLibreUpdate(BaseModel):
    """Schema para actualizar un registro de cloro libre existente"""
    fecha_mes: Optional[date] = None
    documento_soporte: Optional[str] = None
    proveedor_solicitante: Optional[str] = None
    codigo: Optional[str] = None
    especificacion: Optional[str] = None
    cantidad_entra: Optional[int] = None
    cantidad_sale: Optional[int] = None
    cantidad_saldo: Optional[int] = None
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para respuesta
class ControlCloroLibreResponse(ControlCloroLibreBase):
    """Schema de respuesta con datos completos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
