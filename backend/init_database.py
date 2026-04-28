from core.database import SessionLocal, engine, Base
from core.security import get_password_hash
from models.usuario import Usuario
from models.rol import Rol

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verificar si ya existen roles
    roles_count = db.query(Rol).count()
    
    if roles_count == 0:
        print('📝 Creando roles...')
        # Crear roles
        rol_admin = Rol(
            nombre='Coordinación General',
            categoria='ADMINISTRADOR',
            nivel_acceso=1,
            descripcion='Acceso total al sistema'
        )
        rol_operador = Rol(
            nombre='Operador',
            categoria='OPERADOR',
            nivel_acceso=4,
            descripcion='Registro de datos operacionales'
        )
        db.add(rol_admin)
        db.add(rol_operador)
        db.commit()
        db.refresh(rol_admin)
        db.refresh(rol_operador)
        print('✅ Roles creados')
    else:
        rol_admin = db.query(Rol).filter(Rol.categoria == 'ADMINISTRADOR').first()
        rol_operador = db.query(Rol).filter(Rol.categoria == 'OPERADOR').first()
        print(f'✅ Roles encontrados: {roles_count}')
    
    # Verificar si ya existe el admin
    admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
    
    if not admin:
        print('📝 Creando usuario administrador...')
        # Crear admin
        admin = Usuario(
            nombre='Administrador',
            apellido='Sistema',
            email='admin@plantaesperanza.com',
            telefono='00000000',
            username='admin',
            hashed_password=get_password_hash('admin123'),
            rol_id=rol_admin.id,
            activo=True
        )
        db.add(admin)
        db.commit()
        print('✅ Usuario admin creado')
    else:
        # Actualizar contraseña
        admin.hashed_password = get_password_hash('admin123')
        db.commit()
        print('✅ Contraseña de admin actualizada')
    
    # Verificar usuario operador
    jperez = db.query(Usuario).filter(Usuario.username == 'jperez').first()
    
    if not jperez and rol_operador:
        print('📝 Creando usuario operador...')
        jperez = Usuario(
            nombre='Juan',
            apellido='Pérez',
            email='jperez@plantaesperanza.com',
            telefono='11111111',
            username='jperez',
            hashed_password=get_password_hash('operador123'),
            rol_id=rol_operador.id,
            activo=True
        )
        db.add(jperez)
        db.commit()
        print('✅ Usuario jperez creado')
    
    print('\n' + '='*60)
    print('🎉 INICIALIZACIÓN COMPLETADA')
    print('='*60)
    print('\n📋 CREDENCIALES DE ACCESO:\n')
    print('┌─────────────────────────────────────────────────────┐')
    print('│  ADMINISTRADOR                                      │')
    print('├─────────────────────────────────────────────────────┤')
    print('│  Usuario:     admin                                 │')
    print('│  Contraseña:  admin123                              │')
    print('└─────────────────────────────────────────────────────┘')
    print('\n┌─────────────────────────────────────────────────────┐')
    print('│  OPERADOR                                           │')
    print('├─────────────────────────────────────────────────────┤')
    print('│  Usuario:     jperez                                │')
    print('│  Contraseña:  operador123                           │')
    print('└─────────────────────────────────────────────────────┘\n')
    
    # Listar todos los usuarios
    print('📋 Usuarios en la base de datos:')
    usuarios = db.query(Usuario).all()
    for u in usuarios:
        rol_obj = db.query(Rol).filter(Rol.id == u.rol_id).first()
        rol_nombre = rol_obj.categoria if rol_obj else 'Sin rol'
        print(f'  ✓ {u.username} - {u.nombre} {u.apellido} ({rol_nombre})')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
