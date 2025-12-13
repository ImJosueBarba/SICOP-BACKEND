"""
Router para operaciones CRUD de Monitoreo Fisicoquímico (Matriz 6)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
from schemas.monitoreo_fisicoquimico import (
    MonitoreoFisicoquimicoCreate,
    MonitoreoFisicoquimicoUpdate,
    MonitoreoFisicoquimicoResponse
)

router = APIRouter()


@router.get("/", response_model=List[MonitoreoFisicoquimicoResponse])
def get_monitoreos(
    skip: int = 0,
    limit: int = 100,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de monitoreos fisicoquímicos"""
    query = db.query(MonitoreoFisicoquimico)
    
    if fecha:
        query = query.filter(MonitoreoFisicoquimico.fecha == fecha)
    
    monitoreos = query.order_by(
        MonitoreoFisicoquimico.fecha.desc(),
        MonitoreoFisicoquimico.muestra_numero
    ).offset(skip).limit(limit).all()
    
    return monitoreos


@router.get("/fecha/{fecha_consulta}", response_model=List[MonitoreoFisicoquimicoResponse])
def get_monitoreos_por_fecha(fecha_consulta: date, db: Session = Depends(get_db)):
    """Obtener todos los monitoreos de un día específico (3 muestras)"""
    monitoreos = db.query(MonitoreoFisicoquimico).filter(
        MonitoreoFisicoquimico.fecha == fecha_consulta
    ).order_by(MonitoreoFisicoquimico.muestra_numero).all()
    
    return monitoreos


@router.get("/{monitoreo_id}", response_model=MonitoreoFisicoquimicoResponse)
def get_monitoreo(monitoreo_id: int, db: Session = Depends(get_db)):
    """Obtener un monitoreo por ID"""
    monitoreo = db.query(MonitoreoFisicoquimico).filter(
        MonitoreoFisicoquimico.id == monitoreo_id
    ).first()
    
    if not monitoreo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitoreo con ID {monitoreo_id} no encontrado"
        )
    
    return monitoreo


@router.post("/", response_model=MonitoreoFisicoquimicoResponse, status_code=status.HTTP_201_CREATED)
def create_monitoreo(monitoreo: MonitoreoFisicoquimicoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de monitoreo fisicoquímico"""
    # Verificar si ya existe un registro para esa fecha y número de muestra
    existing = db.query(MonitoreoFisicoquimico).filter(
        MonitoreoFisicoquimico.fecha == monitoreo.fecha,
        MonitoreoFisicoquimico.muestra_numero == monitoreo.muestra_numero
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe la muestra {monitoreo.muestra_numero} para {monitoreo.fecha}"
        )
    
    db_monitoreo = MonitoreoFisicoquimico(**monitoreo.model_dump())
    db.add(db_monitoreo)
    db.commit()
    db.refresh(db_monitoreo)
    return db_monitoreo


@router.put("/{monitoreo_id}", response_model=MonitoreoFisicoquimicoResponse)
def update_monitoreo(
    monitoreo_id: int,
    monitoreo: MonitoreoFisicoquimicoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un monitoreo existente"""
    db_monitoreo = db.query(MonitoreoFisicoquimico).filter(
        MonitoreoFisicoquimico.id == monitoreo_id
    ).first()
    
    if not db_monitoreo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitoreo con ID {monitoreo_id} no encontrado"
        )
    
    update_data = monitoreo.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_monitoreo, key, value)
    
    db.commit()
    db.refresh(db_monitoreo)
    return db_monitoreo


@router.delete("/{monitoreo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitoreo(monitoreo_id: int, db: Session = Depends(get_db)):
    """Eliminar un monitoreo"""
    db_monitoreo = db.query(MonitoreoFisicoquimico).filter(
        MonitoreoFisicoquimico.id == monitoreo_id
    ).first()
    
    if not db_monitoreo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitoreo con ID {monitoreo_id} no encontrado"
        )
    
    db.delete(db_monitoreo)
    db.commit()
    return None
