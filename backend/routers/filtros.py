"""
Router para operaciones CRUD de Filtros
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.filtro import Filtro
from schemas.filtro import (
    FiltroCreate,
    FiltroUpdate,
    FiltroResponse,
    FiltroList
)

router = APIRouter()


@router.get("/", response_model=List[FiltroList])
def get_filtros(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    estado: str = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de filtros"""
    query = db.query(Filtro)
    
    if activo is not None:
        query = query.filter(Filtro.activo == activo)
    
    if estado:
        query = query.filter(Filtro.estado == estado)
    
    filtros = query.offset(skip).limit(limit).all()
    return filtros


@router.get("/{filtro_id}", response_model=FiltroResponse)
def get_filtro(filtro_id: int, db: Session = Depends(get_db)):
    """Obtener un filtro por ID"""
    filtro = db.query(Filtro).filter(Filtro.id == filtro_id).first()
    
    if not filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filtro con ID {filtro_id} no encontrado"
        )
    
    return filtro


@router.post("/", response_model=FiltroResponse, status_code=status.HTTP_201_CREATED)
def create_filtro(filtro: FiltroCreate, db: Session = Depends(get_db)):
    """Crear un nuevo filtro"""
    # Verificar si el número ya existe
    existing = db.query(Filtro).filter(Filtro.numero == filtro.numero).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un filtro con el número {filtro.numero}"
        )
    
    db_filtro = Filtro(**filtro.model_dump())
    db.add(db_filtro)
    db.commit()
    db.refresh(db_filtro)
    return db_filtro


@router.put("/{filtro_id}", response_model=FiltroResponse)
def update_filtro(
    filtro_id: int,
    filtro: FiltroUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un filtro existente"""
    db_filtro = db.query(Filtro).filter(Filtro.id == filtro_id).first()
    
    if not db_filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filtro con ID {filtro_id} no encontrado"
        )
    
    update_data = filtro.model_dump(exclude_unset=True)
    
    # Verificar número duplicado
    if "numero" in update_data:
        existing = db.query(Filtro).filter(
            Filtro.numero == update_data["numero"],
            Filtro.id != filtro_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un filtro con el número {update_data['numero']}"
            )
    
    for key, value in update_data.items():
        setattr(db_filtro, key, value)
    
    db.commit()
    db.refresh(db_filtro)
    return db_filtro


@router.delete("/{filtro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_filtro(filtro_id: int, db: Session = Depends(get_db)):
    """Eliminar un filtro (soft delete)"""
    db_filtro = db.query(Filtro).filter(Filtro.id == filtro_id).first()
    
    if not db_filtro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Filtro con ID {filtro_id} no encontrado"
        )
    
    db_filtro.activo = False
    db.commit()
    return None
