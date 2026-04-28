from core.database import SessionLocal
from models.usuario import Usuario
from models.rol import Rol
from core.security import verify_password

db = SessionLocal()

try:
    print('\n' + '='*70)
    print('🔍 PROBANDO CREDENCIALES DE ACCESO')
    print('='*70)
    
    # Probar usuario "operador"
    operador = db.query(Usuario).filter(Usuario.username == 'operador').first()
    if operador:
        print('\n✅ Usuario "operador" encontrado en BD')
        rol = db.query(Rol).filter(Rol.id == operador.rol_id).first()
        print(f'   - Nombre: {operador.nombre} {operador.apellido}')
        print(f'   - Email: {operador.email}')
        print(f'   - Rol: {rol.nombre if rol else "Sin rol"} ({rol.categoria if rol else ""})')
        print(f'   - Activo: {"Sí" if operador.activo else "No"}')
        
        # Probar contraseñas comunes
        passwords_to_test = ['admin123', 'operador123', '12345678', 'password', 'admin', 'operador']
        print('\n   🔐 Probando contraseñas comunes...')
        found_password = None
        for pwd in passwords_to_test:
            if verify_password(pwd, operador.hashed_password):
                found_password = pwd
                print(f'   ✅ CONTRASEÑA ENCONTRADA: {pwd}')
                break
        
        if not found_password:
            print('   ❌ Ninguna contraseña común funcionó')
    else:
        print('\n❌ Usuario "operador" no encontrado')
    
    # Probar admin
    admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
    if admin:
        print('\n✅ Usuario "admin" encontrado en BD')
        rol = db.query(Rol).filter(Rol.id == admin.rol_id).first()
        print(f'   - Nombre: {admin.nombre} {admin.apellido}')
        print(f'   - Rol: {rol.categoria if rol else "Sin rol"}')
    else:
        print('\n❌ Usuario "admin" NO existe en la BD')
    
    # Listar TODOS los usuarios
    print('\n' + '='*70)
    print('📋 TODOS LOS USUARIOS EN LA BASE DE DATOS:')
    print('='*70)
    usuarios = db.query(Usuario).all()
    for u in usuarios:
        rol = db.query(Rol).filter(Rol.id == u.rol_id).first()
        print(f'\n   Usuario: {u.username}')
        print(f'   Contraseña hash: {u.hashed_password[:50]}...')
        print(f'   Rol: {rol.categoria if rol else "Sin rol"}')
    
    print('\n' + '='*70)
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
