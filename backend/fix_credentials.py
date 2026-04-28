from core.database import SessionLocal
from core.security import get_password_hash
from models.usuario import Usuario
from models.rol import Rol

db = SessionLocal()

try:
    # Buscar o crear rol de Administrador
    rol_admin = db.query(Rol).filter(Rol.categoria == 'ADMINISTRADOR').first()
    if not rol_admin:
        print('📝 Creando rol ADMINISTRADOR...')
        rol_admin = Rol(
            codigo='ADMIN',
            nombre='Coordinación General',
            categoria='ADMINISTRADOR',
            nivel_jerarquia=1,
            descripcion='Acceso total al sistema',
            activo=True
        )
        db.add(rol_admin)
        db.commit()
        db.refresh(rol_admin)
        print('✅ Rol ADMINISTRADOR creado')
    
    # Buscar o crear usuario admin
    admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
    if not admin:
        print('📝 Creando usuario admin...')
        admin = Usuario(
            nombre='Administrador',
            apellido='Sistema',
            email='admin@esperanza.com',
            telefono='00000000',
            username='admin',
            hashed_password=get_password_hash('admin123'),
            rol_id=rol_admin.id,
            activo=True
        )
        db.add(admin)
        print('✅ Usuario admin creado')
    else:
        print('📝 Actualizando contraseña de admin...')
        admin.hashed_password = get_password_hash('admin123')
        admin.rol_id = rol_admin.id
        print('✅ Contraseña de admin actualizada')
    
    # Buscar rol de Operador
    rol_operador = db.query(Rol).filter(Rol.categoria.in_(['OPERADOR', 'Operativo'])).first()
    if not rol_operador:
        print('📝 Creando rol OPERADOR...')
        rol_operador = Rol(
            codigo='OPER',
            nombre='Operador',
            categoria='OPERADOR',
            nivel_jerarquia=4,
            descripcion='Registro de datos operacionales',
            activo=True
        )
        db.add(rol_operador)
        db.commit()
        db.refresh(rol_operador)
        print('✅ Rol OPERADOR creado')
    
    # Actualizar usuario operador existente
    operador = db.query(Usuario).filter(Usuario.username == 'operador').first()
    if operador:
        print('📝 Actualizando contraseña de operador...')
        operador.hashed_password = get_password_hash('operador123')
        print('✅ Contraseña de operador actualizada')
    
    db.commit()
    
    print('\n' + '='*70)
    print('🎉 CREDENCIALES ACTUALIZADAS EXITOSAMENTE')
    print('='*70)
    print('\n┌─────────────────────────────────────────────────────┐')
    print('│  ADMINISTRADOR                                      │')
    print('├─────────────────────────────────────────────────────┤')
    print('│  Usuario:     admin                                 │')
    print('│  Contraseña:  admin123                              │')
    print('└─────────────────────────────────────────────────────┘')
    print('\n┌─────────────────────────────────────────────────────┐')
    print('│  OPERADOR                                           │')
    print('├─────────────────────────────────────────────────────┤')
    print('│  Usuario:     operador                              │')
    print('│  Contraseña:  operador123                           │')
    print('└─────────────────────────────────────────────────────┘\n')
    
    # Listar usuarios
    print('📋 Usuarios en la base de datos:')
    usuarios = db.query(Usuario).all()
    for u in usuarios:
        rol = db.query(Rol).filter(Rol.id == u.rol_id).first()
        print(f'  ✓ {u.username} - {u.nombre} {u.apellido} ({rol.categoria if rol else "Sin rol"})')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
