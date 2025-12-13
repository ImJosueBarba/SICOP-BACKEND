"""
Router para operaciones CRUD de Control de Cloro Libre (Matriz 5)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.control_cloro_libre import ControlCloroLibre
from schemas.control_cloro_libre import (
    ControlCloroLibreCreate,
    ControlCloroLibreUpdate,
    ControlCloroLibreResponse
)

router = APIRouter()


@router.get("/", response_model=List[ControlCloroLibreResponse])
def get_controles_cloro(
    skip: int = 0,
    limit: int = 100,
    codigo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de controles de cloro libre"""
    query = db.query(ControlCloroLibre)
    
    if codigo:
        query = query.filter(ControlCloroLibre.codigo == codigo)
    
    controles = query.order_by(
        ControlCloroLibre.fecha_mes.desc()
    ).offset(skip).limit(limit).all()
    
    return controles


@router.get("/saldo-actual", response_model=ControlCloroLibreResponse)
def get_saldo_actual(db: Session = Depends(get_db)):
    """Obtener el saldo actual más reciente de cloro libre"""
    control = db.query(ControlCloroLibre).order_by(
        ControlCloroLibre.fecha_mes.desc()
    ).first()
    
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay registros de cloro libre"
        )
    
    return control


@router.get("/{control_id}", response_model=ControlCloroLibreResponse)
def get_control_cloro(control_id: int, db: Session = Depends(get_db)):
    """Obtener un control de cloro libre por ID"""
    control = db.query(ControlCloroLibre).filter(
        ControlCloroLibre.id == control_id
    ).first()
    
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de cloro libre con ID {control_id} no encontrado"
        )
    
    return control


@router.post("/", response_model=ControlCloroLibreResponse, status_code=status.HTTP_201_CREATED)
def create_control_cloro(control: ControlCloroLibreCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de control de cloro libre"""
    db_control = ControlCloroLibre(**control.model_dump())
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control


@router.put("/{control_id}", response_model=ControlCloroLibreResponse)
def update_control_cloro(
    control_id: int,
    control: ControlCloroLibreUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un control de cloro libre existente"""
    db_control = db.query(ControlCloroLibre).filter(
        ControlCloroLibre.id == control_id
    ).first()
    
    if not db_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de cloro libre con ID {control_id} no encontrado"
        )
    
    update_data = control.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_control, key, value)
    
    db.commit()
    db.refresh(db_control)
    return db_control


@router.delete("/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_control_cloro(control_id: int, db: Session = Depends(get_db)):
    """Eliminar un control de cloro libre"""
    db_control = db.query(ControlCloroLibre).filter(
        ControlCloroLibre.id == control_id
    ).first()
    
    if not db_control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Control de cloro libre con ID {control_id} no encontrado"
        )
    
    db.delete(db_control)
    db.commit()
    return None
