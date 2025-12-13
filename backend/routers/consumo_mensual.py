"""
Router para operaciones CRUD de Consumo Químico Mensual (Matriz 1)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
from schemas.consumo_quimico_mensual import (
    ConsumoQuimicoMensualCreate,
    ConsumoQuimicoMensualUpdate,
    ConsumoQuimicoMensualResponse
)

router = APIRouter()


@router.get("/", response_model=List[ConsumoQuimicoMensualResponse])
def get_consumos_mensuales(
    skip: int = 0,
    limit: int = 100,
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de consumos mensuales"""
    query = db.query(ConsumoQuimicoMensual)
    
    if anio:
        query = query.filter(ConsumoQuimicoMensual.anio == anio)
    
    if mes:
        query = query.filter(ConsumoQuimicoMensual.mes == mes)
    
    consumos = query.order_by(
        ConsumoQuimicoMensual.anio.desc(),
        ConsumoQuimicoMensual.mes.desc()
    ).offset(skip).limit(limit).all()
    
    return consumos


@router.get("/{consumo_id}", response_model=ConsumoQuimicoMensualResponse)
def get_consumo_mensual(consumo_id: int, db: Session = Depends(get_db)):
    """Obtener un consumo mensual por ID"""
    consumo = db.query(ConsumoQuimicoMensual).filter(
        ConsumoQuimicoMensual.id == consumo_id
    ).first()
    
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo mensual con ID {consumo_id} no encontrado"
        )
    
    return consumo


@router.post("/", response_model=ConsumoQuimicoMensualResponse, status_code=status.HTTP_201_CREATED)
def create_consumo_mensual(consumo: ConsumoQuimicoMensualCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de consumo mensual"""
    # Verificar si ya existe un registro para ese mes y año
    existing = db.query(ConsumoQuimicoMensual).filter(
        ConsumoQuimicoMensual.mes == consumo.mes,
        ConsumoQuimicoMensual.anio == consumo.anio
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un registro para {consumo.mes}/{consumo.anio}"
        )
    
    db_consumo = ConsumoQuimicoMensual(**consumo.model_dump())
    db.add(db_consumo)
    db.commit()
    db.refresh(db_consumo)
    return db_consumo


@router.put("/{consumo_id}", response_model=ConsumoQuimicoMensualResponse)
def update_consumo_mensual(
    consumo_id: int,
    consumo: ConsumoQuimicoMensualUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un consumo mensual existente"""
    db_consumo = db.query(ConsumoQuimicoMensual).filter(
        ConsumoQuimicoMensual.id == consumo_id
    ).first()
    
    if not db_consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo mensual con ID {consumo_id} no encontrado"
        )
    
    update_data = consumo.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_consumo, key, value)
    
    db.commit()
    db.refresh(db_consumo)
    return db_consumo


@router.delete("/{consumo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumo_mensual(consumo_id: int, db: Session = Depends(get_db)):
    """Eliminar un consumo mensual"""
    db_consumo = db.query(ConsumoQuimicoMensual).filter(
        ConsumoQuimicoMensual.id == consumo_id
    ).first()
    
    if not db_consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo mensual con ID {consumo_id} no encontrado"
        )
    
    db.delete(db_consumo)
    db.commit()
    return None
