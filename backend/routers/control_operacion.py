"""
Router para operaciones CRUD de Control de Operación (Matriz 2)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time

from core.database import get_db
from models.control_operacion import ControlOperacion
from schemas.control_operacion import (
    ControlOperacionCreate,
    ControlOperacionUpdate,
    ControlOperacionResponse
)

router = APIRouter()


@router.get("/", response_model=List[ControlOperacionResponse])
def get_controles_operacion(
    skip: int = 0,
    limit: int = 100,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de controles de operación"""
    query = db.query(ControlOperacion)
    
    if fecha:
        query = query.filter(ControlOperacion.fecha == fecha)
    
    controles = query.order_by(
        ControlOperacion.fecha.desc(),
        ControlOperacion.hora.desc()
    ).offset(skip).limit(limit).all()
    
    return controles


@router.get("/fecha/{fecha_consulta}", response_model=List[ControlOperacionResponse])
def get_controles_por_fecha(fecha_consulta: date, db: Session = Depends(get_db)):
    """Obtener todos los controles de un día específico"""
    controles = db.query(ControlOperacion).filter(
        ControlOperacion.fecha == fecha_consulta
    ).order_by(ControlOperacion.hora).all()
    
    return controles


@router.get("/{control_id}", response_model=ControlOperacionResponse)
def get_control_operacion(control_id: int, db: Session = Depends(get_db)):
    """Obtener un control de operación por ID"""
    control = db.query(ControlOperacion).filter(
        ControlOperacion.id == control_id
    ).first()
    
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de operación con ID {control_id} no encontrado"
        )
    
    return control


@router.post("/", response_model=ControlOperacionResponse, status_code=status.HTTP_201_CREATED)
def create_control_operacion(control: ControlOperacionCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de control de operación"""
    # Verificar si ya existe un registro para esa fecha y hora
    existing = db.query(ControlOperacion).filter(
        ControlOperacion.fecha == control.fecha,
        ControlOperacion.hora == control.hora
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un registro para {control.fecha} a las {control.hora}"
        )
    
    db_control = ControlOperacion(**control.model_dump())
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control


@router.put("/{control_id}", response_model=ControlOperacionResponse)
def update_control_operacion(
    control_id: int,
    control: ControlOperacionUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un control de operación existente"""
    db_control = db.query(ControlOperacion).filter(
        ControlOperacion.id == control_id
    ).first()
    
    if not db_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de operación con ID {control_id} no encontrado"
        )
    
    update_data = control.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_control, key, value)
    
    db.commit()
    db.refresh(db_control)
    return db_control


@router.delete("/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_control_operacion(control_id: int, db: Session = Depends(get_db)):
    """Eliminar un control de operación"""
    db_control = db.query(ControlOperacion).filter(
        ControlOperacion.id == control_id
    ).first()
    
    if not db_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de operación con ID {control_id} no encontrado"
        )
    
    db.delete(db_control)
    db.commit()
    return None
