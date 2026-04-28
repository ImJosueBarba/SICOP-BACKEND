from core.database import SessionLocal
from core.security import get_password_hash
from models.usuario import Usuario

db = SessionLocal()

try:
    # Actualizar admin
    admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
    if admin:
        admin.hashed_password = get_password_hash('admin123')
        db.commit()
        print('✅ Contraseña de admin actualizada: admin123')
    else:
        print('❌ Usuario admin no encontrado')
    
    # Actualizar jperez
    jperez = db.query(Usuario).filter(Usuario.username == 'jperez').first()
    if jperez:
        jperez.hashed_password = get_password_hash('operador123')
        db.commit()
        print('✅ Contraseña de jperez actualizada: operador123')
    
    # Listar usuarios
    print('\n📋 Usuarios en la base de datos:')
    usuarios = db.query(Usuario).all()
    for u in usuarios:
        print(f'  - {u.username} ({u.nombre} {u.apellido}) - Rol: {u.rol}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    db.rollback()
finally:
    db.close()
