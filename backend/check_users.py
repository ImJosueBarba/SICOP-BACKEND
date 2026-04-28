from core.database import SessionLocal
from models.usuario import Usuario
from models.rol import Rol

db = SessionLocal()

try:
    usuarios = db.query(Usuario).all()
    
    print('\n' + '='*70)
    print('📋 USUARIOS EN LA BASE DE DATOS')
    print('='*70)
    
    for u in usuarios:
        rol = db.query(Rol).filter(Rol.id == u.rol_id).first()
        print(f'\n👤 Usuario: {u.username}')
        print(f'   Nombre: {u.nombre} {u.apellido}')
        print(f'   Email: {u.email}')
        print(f'   Rol: {rol.categoria if rol else "Sin rol"}')
        print(f'   Activo: {"✅ Sí" if u.activo else "❌ No"}')
    
    print('\n' + '='*70)
    print('\n🔐 CREDENCIALES DE ACCESO (según init_database.py):')
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
    print('│  Usuario:     jperez                                │')
    print('│  Contraseña:  operador123                           │')
    print('└─────────────────────────────────────────────────────┘\n')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
