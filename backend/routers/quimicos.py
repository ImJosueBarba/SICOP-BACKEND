"""
Router para operaciones CRUD de Químicos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.quimico import Quimico
from schemas.quimico import (
    QuimicoCreate,
    QuimicoUpdate,
    QuimicoResponse,
    QuimicoList
)

router = APIRouter()


@router.get("/", response_model=List[QuimicoList])
def get_quimicos(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    tipo: str = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de químicos"""
    query = db.query(Quimico)
    
    if activo is not None:
        query = query.filter(Quimico.activo == activo)
    
    if tipo:
        query = query.filter(Quimico.tipo == tipo)
    
    quimicos = query.offset(skip).limit(limit).all()
    return quimicos


@router.get("/alertas-stock", response_model=List[QuimicoList])
def get_alertas_stock(db: Session = Depends(get_db)):
    """Obtener químicos con stock bajo o crítico"""
    quimicos = db.query(Quimico).filter(
        Quimico.activo == True,
        Quimico.stock_actual <= Quimico.stock_minimo * 1.5
    ).all()
    return quimicos


@router.get("/{quimico_id}", response_model=QuimicoResponse)
def get_quimico(quimico_id: int, db: Session = Depends(get_db)):
    """Obtener un químico por ID"""
    quimico = db.query(Quimico).filter(Quimico.id == quimico_id).first()
    
    if not quimico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Químico con ID {quimico_id} no encontrado"
        )
    
    return quimico


@router.post("/", response_model=QuimicoResponse, status_code=status.HTTP_201_CREATED)
def create_quimico(quimico: QuimicoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo químico"""
    # Verificar si el código ya existe
    existing = db.query(Quimico).filter(Quimico.codigo == quimico.codigo).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código del químico ya está registrado"
        )
    
    db_quimico = Quimico(**quimico.model_dump())
    db.add(db_quimico)
    db.commit()
    db.refresh(db_quimico)
    return db_quimico


@router.put("/{quimico_id}", response_model=QuimicoResponse)
def update_quimico(
    quimico_id: int,
    quimico: QuimicoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un químico existente"""
    db_quimico = db.query(Quimico).filter(Quimico.id == quimico_id).first()
    
    if not db_quimico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Químico con ID {quimico_id} no encontrado"
        )
    
    update_data = quimico.model_dump(exclude_unset=True)
    
    # Verificar código duplicado
    if "codigo" in update_data:
        existing = db.query(Quimico).filter(
            Quimico.codigo == update_data["codigo"],
            Quimico.id != quimico_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código del químico ya está registrado"
            )
    
    for key, value in update_data.items():
        setattr(db_quimico, key, value)
    
    db.commit()
    db.refresh(db_quimico)
    return db_quimico


@router.delete("/{quimico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quimico(quimico_id: int, db: Session = Depends(get_db)):
    """Eliminar un químico (soft delete)"""
    db_quimico = db.query(Quimico).filter(Quimico.id == quimico_id).first()
    
    if not db_quimico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Químico con ID {quimico_id} no encontrado"
        )
    
    db_quimico.activo = False
    db.commit()
    return None
