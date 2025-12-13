"""
Router para operaciones CRUD de Usuarios
Sistema de Gestión de Usuarios con roles (Administrador y Operador)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.usuario import Usuario, UserRole
from schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioList
)
from core.security import get_password_hash
from core.dependencies import get_current_active_user

router = APIRouter()


def check_admin_role(current_user: Usuario):
    """Verifica que el usuario actual sea administrador"""
    if current_user.rol != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción. Solo administradores."
        )


@router.get("/", response_model=List[UsuarioList])
def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    rol: UserRole = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener lista de usuarios
    - Administradores: pueden ver todos los usuarios
    - Operadores: solo pueden ver su propio perfil
    """
    query = db.query(Usuario)
    
    # Si no es admin, solo puede ver su propio perfil
    if current_user.rol != UserRole.ADMINISTRADOR:
        query = query.filter(Usuario.id == current_user.id)
    else:
        # Filtros solo para administradores
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
        if rol is not None:
            query = query.filter(Usuario.rol == rol)
    
    usuarios = query.offset(skip).limit(limit).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener un usuario por ID
    - Administradores: pueden ver cualquier usuario
    - Operadores: solo pueden ver su propio perfil
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol != UserRole.ADMINISTRADOR and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este usuario"
        )
    
    return usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo usuario (Solo Administradores)
    """
    check_admin_role(current_user)
    
    # Verificar si el email ya existe
    if usuario.email:
        existing = db.query(Usuario).filter(Usuario.email == usuario.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
            
    # Verificar si el username ya existe
    if db.query(Usuario).filter(Usuario.username == usuario.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Crear usuario
    usuario_data = usuario.model_dump()
    hashed_password = get_password_hash(usuario_data.pop("password"))
    db_usuario = Usuario(**usuario_data, hashed_password=hashed_password)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un usuario
    - Administradores: pueden actualizar cualquier usuario
    - Operadores: solo pueden actualizar algunos campos de su propio perfil
    """
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar permisos
    is_admin = current_user.rol == UserRole.ADMINISTRADOR
    is_self = current_user.id == usuario_id
    
    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar este usuario"
        )
    
    # Preparar datos para actualizar
    update_data = usuario_update.model_dump(exclude_unset=True)
    
    # Si no es admin, no puede cambiar ciertos campos
    if not is_admin:
        restricted_fields = ['rol', 'activo']
        for field in restricted_fields:
            if field in update_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tiene permisos para modificar el campo '{field}'"
                )
    
    # Verificar email único si se está actualizando
    if 'email' in update_data and update_data['email']:
        existing = db.query(Usuario).filter(
            Usuario.email == update_data['email'],
            Usuario.id != usuario_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado por otro usuario"
            )
    
    # Actualizar contraseña si se proporciona
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    # Aplicar actualizaciones
    for field, value in update_data.items():
        setattr(db_usuario, field, value)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Eliminar (desactivar) un usuario (Solo Administradores)
    """
    check_admin_role(current_user)
    
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # No permitir que se elimine a sí mismo
    if current_user.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar su propio usuario"
        )
    
    # Desactivar en lugar de eliminar
    db_usuario.activo = False
    db.commit()
    
    return None


@router.post("/{usuario_id}/activar", response_model=UsuarioResponse)
def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Reactivar un usuario desactivado (Solo Administradores)
    """
    check_admin_role(current_user)
    
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    db_usuario.activo = True
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario
