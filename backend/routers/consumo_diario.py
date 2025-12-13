"""
Router para operaciones CRUD de Control de Consumo Diario (Matriz 4)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.control_consumo_diario import ControlConsumoDiario
from schemas.control_consumo_diario import (
    ControlConsumoDiarioCreate,
    ControlConsumoDiarioUpdate,
    ControlConsumoDiarioResponse
)

router = APIRouter()


@router.get("/", response_model=List[ControlConsumoDiarioResponse])
def get_consumos_diarios(
    skip: int = 0,
    limit: int = 100,
    fecha: Optional[date] = None,
    quimico_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de consumos diarios"""
    query = db.query(ControlConsumoDiario)
    
    if fecha:
        query = query.filter(ControlConsumoDiario.fecha == fecha)
    
    if quimico_id:
        query = query.filter(ControlConsumoDiario.quimico_id == quimico_id)
    
    consumos = query.order_by(
        ControlConsumoDiario.fecha.desc()
    ).offset(skip).limit(limit).all()
    
    return consumos


@router.get("/fecha/{fecha_consulta}", response_model=List[ControlConsumoDiarioResponse])
def get_consumos_por_fecha(fecha_consulta: date, db: Session = Depends(get_db)):
    """Obtener todos los consumos de un día específico"""
    consumos = db.query(ControlConsumoDiario).filter(
        ControlConsumoDiario.fecha == fecha_consulta
    ).all()
    
    return consumos


@router.get("/{consumo_id}", response_model=ControlConsumoDiarioResponse)
def get_consumo_diario(consumo_id: int, db: Session = Depends(get_db)):
    """Obtener un consumo diario por ID"""
    consumo = db.query(ControlConsumoDiario).filter(
        ControlConsumoDiario.id == consumo_id
    ).first()
    
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo diario con ID {consumo_id} no encontrado"
        )
    
    return consumo


@router.post("/", response_model=ControlConsumoDiarioResponse, status_code=status.HTTP_201_CREATED)
def create_consumo_diario(consumo: ControlConsumoDiarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de consumo diario"""
    db_consumo = ControlConsumoDiario(**consumo.model_dump())
    db.add(db_consumo)
    db.commit()
    db.refresh(db_consumo)
    return db_consumo


@router.put("/{consumo_id}", response_model=ControlConsumoDiarioResponse)
def update_consumo_diario(
    consumo_id: int,
    consumo: ControlConsumoDiarioUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un consumo diario existente"""
    db_consumo = db.query(ControlConsumoDiario).filter(
        ControlConsumoDiario.id == consumo_id
    ).first()
    
    if not db_consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo diario con ID {consumo_id} no encontrado"
        )
    
    update_data = consumo.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_consumo, key, value)
    
    db.commit()
    db.refresh(db_consumo)
    return db_consumo


@router.delete("/{consumo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumo_diario(consumo_id: int, db: Session = Depends(get_db)):
    """Eliminar un consumo diario"""
    db_consumo = db.query(ControlConsumoDiario).filter(
        ControlConsumoDiario.id == consumo_id
    ).first()
    
    if not db_consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumo diario con ID {consumo_id} no encontrado"
        )
    
    db.delete(db_consumo)
    db.commit()
    return None
