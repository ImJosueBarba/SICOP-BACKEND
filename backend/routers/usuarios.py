"""
Router para operaciones CRUD de Usuarios
Sistema de Gestión de Usuarios con roles (Administrador y Operador)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import shutil
from pathlib import Path
import uuid

from core.database import get_db
from models.usuario import Usuario, UserRole
from models.rol import Rol
from models.log import LogAuditoria
from schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioList
)
from core.security import get_password_hash
from core.dependencies import get_current_active_user
from sqlalchemy.orm import joinedload

router = APIRouter()

# Directorio para guardar fotos de perfil
UPLOAD_DIR = Path("uploads/profile_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def create_log(
    db: Session,
    current_user: Usuario,
    accion: str,
    entidad: str = None,
    entidad_id: int = None,
    detalles: str = None,
    request: Request = None
):
    """Función auxiliar para crear logs"""
    log = LogAuditoria(
        usuario_id=current_user.id,
        usuario_nombre=f"{current_user.nombre} {current_user.apellido}",
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalles=detalles,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log)
    db.commit()


def check_admin_role(current_user: Usuario):
    """Verifica que el usuario actual sea administrador"""
    if not current_user.rol_obj or current_user.rol_obj.categoria != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción. Solo administradores."
        )


@router.get("/", response_model=List[UsuarioList])
def get_usuarios(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    rol_id: int = None,
    categoria: str = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener lista de usuarios
    - Administradores: pueden ver todos los usuarios
    - Operadores: solo pueden ver su propio perfil
    """
    query = db.query(Usuario).options(joinedload(Usuario.rol_obj))
    
    # Si no es admin, solo puede ver su propio perfil
    is_admin = current_user.rol_obj and current_user.rol_obj.categoria == "ADMINISTRADOR"
    
    if not is_admin:
        query = query.filter(Usuario.id == current_user.id)
    else:
        # Filtros solo para administradores
        if activo is not None:
            query = query.filter(Usuario.activo == activo)
        if rol_id is not None:
            query = query.filter(Usuario.rol_id == rol_id)
        if categoria is not None:
            query = query.join(Rol).filter(Rol.categoria == categoria)
    
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
    usuario = db.query(Usuario).options(joinedload(Usuario.rol_obj)).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar permisos
    is_admin = current_user.rol_obj and current_user.rol_obj.categoria == "ADMINISTRADOR"
    if not is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este usuario"
        )
    
    return usuario


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario: UsuarioCreate,
    request: Request,
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
    
    # Verificar que el rol existe y está activo
    rol = db.query(Rol).filter(Rol.id == usuario.rol_id, Rol.activo == True).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol especificado no existe o está inactivo"
        )
    
    # Crear usuario
    usuario_data = usuario.model_dump()
    hashed_password = get_password_hash(usuario_data.pop("password"))
    db_usuario = Usuario(**usuario_data, hashed_password=hashed_password)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Registrar log de creación
    create_log(
        db=db,
        current_user=current_user,
        accion="CREATE",
        entidad="usuarios",
        entidad_id=db_usuario.id,
        detalles=json.dumps({
            "usuario_creado": f"{db_usuario.nombre} {db_usuario.apellido}",
            "username": db_usuario.username,
            "rol": db_usuario.rol_obj.nombre if db_usuario.rol_obj else "Sin rol"
        }),
        request=request
    )
    
    return db_usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    request: Request,
    nombre: Optional[str] = Form(None),
    apellido: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    telefono: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    rol_id: Optional[int] = Form(None),
    activo: Optional[bool] = Form(None),
    foto_perfil: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un usuario (incluye foto de perfil)
    - Administradores: pueden actualizar cualquier usuario
    - Operadores: solo pueden actualizar algunos campos de su propio perfil
    """
    db_usuario = db.query(Usuario).options(joinedload(Usuario.rol_obj)).filter(Usuario.id == usuario_id).first()
    
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar permisos
    is_admin = current_user.rol_obj and current_user.rol_obj.categoria == "ADMINISTRADOR"
    is_self = current_user.id == usuario_id
    
    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar este usuario"
        )
    
    # Campos modificados para el log
    campos_modificados = []
    
    # Actualizar campos básicos
    if nombre is not None:
        db_usuario.nombre = nombre
        campos_modificados.append('nombre')
    
    if apellido is not None:
        db_usuario.apellido = apellido
        campos_modificados.append('apellido')
    
    # Actualizar username (verificar unicidad)
    if username is not None:
        existing = db.query(Usuario).filter(
            Usuario.username == username,
            Usuario.id != usuario_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )
        db_usuario.username = username
        campos_modificados.append('username')
    
    if telefono is not None:
        db_usuario.telefono = telefono
        campos_modificados.append('telefono')
    
    # Actualizar email (verificar unicidad)
    if email is not None:
        existing = db.query(Usuario).filter(
            Usuario.email == email,
            Usuario.id != usuario_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado por otro usuario"
            )
        db_usuario.email = email
        campos_modificados.append('email')
    
    # Actualizar contraseña
    if password is not None and password.strip():
        db_usuario.hashed_password = get_password_hash(password)
        campos_modificados.append('password')
    
    # Solo admin puede cambiar rol y estado activo
    if is_admin:
        if rol_id is not None:
            # Verificar que el rol existe y está activo
            rol = db.query(Rol).filter(Rol.id == rol_id, Rol.activo == True).first()
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol con ID {rol_id} no existe o está inactivo"
                )
            db_usuario.rol_id = rol_id
            campos_modificados.append('rol')
        
        if activo is not None:
            db_usuario.activo = activo
            campos_modificados.append('activo')
    else:
        # Operadores no pueden cambiar estos campos
        if rol_id is not None or activo is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para modificar rol o estado activo"
            )
    
    # Manejar foto de perfil
    if foto_perfil and foto_perfil.filename:
        # Validar tipo de archivo
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(foto_perfil.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de imagen no permitido. Use JPG, PNG, GIF o WEBP"
            )
        
        # Eliminar foto anterior si existe
        if db_usuario.foto_perfil:
            # Extraer solo el nombre del archivo de la ruta guardada
            # Ejemplo: /uploads/profile_photos/abc-123.jpg -> abc-123.jpg
            old_filename = Path(db_usuario.foto_perfil).name
            old_file_path = UPLOAD_DIR / old_filename
            
            if old_file_path.exists():
                try:
                    os.remove(old_file_path)
                    print(f"✅ Foto anterior eliminada: {old_file_path}")
                except Exception as e:
                    print(f"⚠️ Error al eliminar foto anterior: {e}")
            else:
                print(f"ℹ️ Foto anterior no encontrada en: {old_file_path}")
        
        # Guardar nueva foto
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / file_name
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(foto_perfil.file, buffer)
        
        # Guardar la ruta relativa en la base de datos
        db_usuario.foto_perfil = f"/uploads/profile_photos/{file_name}"
        campos_modificados.append('foto_perfil')
    
    db.commit()
    db.refresh(db_usuario)
    
    # Registrar log de actualización
    if campos_modificados:
        create_log(
            db=db,
            current_user=current_user,
            accion="UPDATE",
            entidad="usuarios",
            entidad_id=db_usuario.id,
            detalles=json.dumps({
                "usuario_actualizado": f"{db_usuario.nombre} {db_usuario.apellido}",
                "campos_modificados": campos_modificados
            }),
            request=request
        )
    
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: int,
    request: Request,
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
    
    # Guardar información antes de desactivar
    usuario_nombre = f"{db_usuario.nombre} {db_usuario.apellido}"
    usuario_username = db_usuario.username
    
    # Desactivar en lugar de eliminar
    db_usuario.activo = False
    db.commit()
    
    # Registrar log de eliminación
    create_log(
        db=db,
        current_user=current_user,
        accion="DELETE",
        entidad="usuarios",
        entidad_id=usuario_id,
        detalles=json.dumps({
            "usuario_eliminado": usuario_nombre,
            "username": usuario_username,
            "nota": "Usuario desactivado"
        }),
        request=request
    )
    
    return None


@router.post("/{usuario_id}/activar", response_model=UsuarioResponse)
def activar_usuario(
    usuario_id: int,
    request: Request,
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
    
    # Registrar log de activación
    create_log(
        db=db,
        current_user=current_user,
        accion="ACTIVAR",
        entidad="usuarios",
        entidad_id=usuario_id,
        detalles=json.dumps({
            "usuario_activado": f"{db_usuario.nombre} {db_usuario.apellido}",
            "username": db_usuario.username
        }),
        request=request
    )
    
    return db_usuario
