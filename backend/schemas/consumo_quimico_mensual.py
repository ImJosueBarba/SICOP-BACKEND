"""
Schemas Pydantic para el modelo ConsumoQuimicoMensual (Matriz 1)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


# Schema base
class ConsumoQuimicoMensualBase(BaseModel):
    """Schema base de Consumo Químico Mensual"""
    fecha: date
    mes: int = Field(..., ge=1, le=12)
    anio: int = Field(..., ge=2020, le=2100)
    
    # Sulfato de Aluminio
    sulfato_con: Optional[Decimal] = None
    sulfato_ing: Optional[Decimal] = None
    sulfato_guia: Optional[str] = Field(None, max_length=50)
    sulfato_re: Optional[Decimal] = None
    
    # Cal
    cal_con: Optional[int] = None
    cal_ing: Optional[int] = None
    cal_guia: Optional[str] = Field(None, max_length=50)
    
    # Hipoclorito de Calcio
    hipoclorito_con: Optional[Decimal] = None
    hipoclorito_ing: Optional[Decimal] = None
    hipoclorito_guia: Optional[str] = Field(None, max_length=50)
    
    # Gas Licuado de Cloro
    cloro_gas_con: Optional[Decimal] = None
    cloro_gas_ing_bal: Optional[Decimal] = None
    cloro_gas_ing_bdg: Optional[Decimal] = None
    cloro_gas_guia: Optional[str] = Field(None, max_length=50)
    cloro_gas_egre: Optional[Decimal] = None
    
    # Producción
    produccion_m3_dia: Optional[Decimal] = None
    
    # Resumen mensual
    inicio_mes_kg: Optional[Decimal] = None
    ingreso_mes_kg: Optional[Decimal] = None
    consumo_mes_kg: Optional[Decimal] = None
    egreso_mes_kg: Optional[Decimal] = None
    fin_mes_kg: Optional[Decimal] = None
    
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para crear
class ConsumoQuimicoMensualCreate(ConsumoQuimicoMensualBase):
    """Schema para crear un nuevo registro mensual"""
    pass


# Schema para actualizar
class ConsumoQuimicoMensualUpdate(BaseModel):
    """Schema para actualizar un registro mensual existente"""
    fecha: Optional[date] = None
    sulfato_con: Optional[Decimal] = None
    sulfato_ing: Optional[Decimal] = None
    sulfato_guia: Optional[str] = None
    sulfato_re: Optional[Decimal] = None
    cal_con: Optional[int] = None
    cal_ing: Optional[int] = None
    cal_guia: Optional[str] = None
    hipoclorito_con: Optional[Decimal] = None
    hipoclorito_ing: Optional[Decimal] = None
    hipoclorito_guia: Optional[str] = None
    cloro_gas_con: Optional[Decimal] = None
    cloro_gas_ing_bal: Optional[Decimal] = None
    cloro_gas_ing_bdg: Optional[Decimal] = None
    cloro_gas_guia: Optional[str] = None
    cloro_gas_egre: Optional[Decimal] = None
    produccion_m3_dia: Optional[Decimal] = None
    inicio_mes_kg: Optional[Decimal] = None
    ingreso_mes_kg: Optional[Decimal] = None
    consumo_mes_kg: Optional[Decimal] = None
    egreso_mes_kg: Optional[Decimal] = None
    fin_mes_kg: Optional[Decimal] = None
    observaciones: Optional[str] = None
    usuario_id: Optional[int] = None


# Schema para respuesta
class ConsumoQuimicoMensualResponse(ConsumoQuimicoMensualBase):
    """Schema de respuesta con datos completos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
