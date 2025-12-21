"""
Router para Logs de Auditoría
Solo accesible por ADMINISTRADOR
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import get_db
from core.dependencies import get_current_user
from models.log import LogAuditoria
from models.usuario import Usuario, UserRole
from schemas.log import LogAuditoriaResponse, LogAuditoriaFilter

router = APIRouter(
    prefix="/api/logs",
    tags=["logs"]
)


def require_admin(current_user: Usuario = Depends(get_current_user)):
    """Verificar que el usuario actual sea administrador"""
    # Verificar usando el nuevo sistema de roles
    if not current_user.rol_obj or current_user.rol_obj.categoria != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a los logs"
        )
    return current_user


@router.get("", response_model=dict)
def get_logs(
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    entidad: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener logs de auditoría con filtros opcionales
    Solo accesible por ADMINISTRADOR
    """
    query = db.query(LogAuditoria)
    
    # Aplicar filtros
    if usuario_id:
        query = query.filter(LogAuditoria.usuario_id == usuario_id)
    
    if accion:
        query = query.filter(LogAuditoria.accion == accion)
    
    if entidad:
        query = query.filter(LogAuditoria.entidad == entidad)
    
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
            query = query.filter(LogAuditoria.created_at >= fecha_inicio_dt)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
            query = query.filter(LogAuditoria.created_at <= fecha_fin_dt)
        except ValueError:
            pass
    
    # Contar total
    total = query.count()
    
    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(desc(LogAuditoria.created_at))
    
    # Aplicar paginación
    logs = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [LogAuditoriaResponse.model_validate(log) for log in logs]
    }


@router.get("/acciones", response_model=List[str])
def get_acciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener lista de acciones únicas registradas en los logs
    """
    acciones = db.query(LogAuditoria.accion).distinct().all()
    return [accion[0] for accion in acciones if accion[0]]


@router.get("/entidades", response_model=List[str])
def get_entidades(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener lista de entidades únicas registradas en los logs
    """
    entidades = db.query(LogAuditoria.entidad).distinct().all()
    return [entidad[0] for entidad in entidades if entidad[0]]


@router.get("/{log_id}", response_model=LogAuditoriaResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Obtener un log específico por ID
    """
    log = db.query(LogAuditoria).filter(LogAuditoria.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log no encontrado"
        )
    return log
