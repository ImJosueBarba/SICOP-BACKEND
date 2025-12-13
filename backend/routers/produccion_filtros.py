"""
Router para operaciones CRUD de Producción de Filtros (Matriz 3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.produccion_filtro import ProduccionFiltro
from schemas.produccion_filtro import (
    ProduccionFiltroCreate,
    ProduccionFiltroUpdate,
    ProduccionFiltroResponse
)

router = APIRouter()


@router.get("/", response_model=List[ProduccionFiltroResponse])
def get_producciones(
    skip: int = 0,
    limit: int = 100,
    fecha: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de producciones por filtro"""
    query = db.query(ProduccionFiltro)
    
    if fecha:
        query = query.filter(ProduccionFiltro.fecha == fecha)
    
    producciones = query.order_by(
        ProduccionFiltro.fecha.desc(),
        ProduccionFiltro.hora.desc()
    ).offset(skip).limit(limit).all()
    
    return producciones


@router.get("/fecha/{fecha_consulta}", response_model=List[ProduccionFiltroResponse])
def get_producciones_por_fecha(fecha_consulta: date, db: Session = Depends(get_db)):
    """Obtener todas las producciones de un día específico"""
    producciones = db.query(ProduccionFiltro).filter(
        ProduccionFiltro.fecha == fecha_consulta
    ).order_by(ProduccionFiltro.hora).all()
    
    return producciones


@router.get("/{produccion_id}", response_model=ProduccionFiltroResponse)
def get_produccion(produccion_id: int, db: Session = Depends(get_db)):
    """Obtener una producción por ID"""
    produccion = db.query(ProduccionFiltro).filter(
        ProduccionFiltro.id == produccion_id
    ).first()
    
    if not produccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producción con ID {produccion_id} no encontrada"
        )
    
    return produccion


@router.post("/", response_model=ProduccionFiltroResponse, status_code=status.HTTP_201_CREATED)
def create_produccion(produccion: ProduccionFiltroCreate, db: Session = Depends(get_db)):
    """Crear un nuevo registro de producción"""
    # Verificar si ya existe un registro para esa fecha y hora
    existing = db.query(ProduccionFiltro).filter(
        ProduccionFiltro.fecha == produccion.fecha,
        ProduccionFiltro.hora == produccion.hora
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un registro para {produccion.fecha} a las {produccion.hora}"
        )
    
    db_produccion = ProduccionFiltro(**produccion.model_dump())
    db.add(db_produccion)
    db.commit()
    db.refresh(db_produccion)
    return db_produccion


@router.put("/{produccion_id}", response_model=ProduccionFiltroResponse)
def update_produccion(
    produccion_id: int,
    produccion: ProduccionFiltroUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una producción existente"""
    db_produccion = db.query(ProduccionFiltro).filter(
        ProduccionFiltro.id == produccion_id
    ).first()
    
    if not db_produccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producción con ID {produccion_id} no encontrada"
        )
    
    update_data = produccion.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_produccion, key, value)
    
    db.commit()
    db.refresh(db_produccion)
    return db_produccion


@router.delete("/{produccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produccion(produccion_id: int, db: Session = Depends(get_db)):
    """Eliminar una producción"""
    db_produccion = db.query(ProduccionFiltro).filter(
        ProduccionFiltro.id == produccion_id
    ).first()
    
    if not db_produccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producción con ID {produccion_id} no encontrada"
        )
    
    db.delete(db_produccion)
    db.commit()
    return None
