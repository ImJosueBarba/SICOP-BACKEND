from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.usuario import Usuario

db = SessionLocal()

try:
    usuarios = db.query(Usuario).all()
    
    print("\n" + "="*60)
    print("USUARIOS EN LA BASE DE DATOS")
    print("="*60 + "\n")
    
    if not usuarios:
        print("No hay usuarios en la base de datos")
    else:
        for user in usuarios:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Nombre: {user.nombre} {user.apellido}")
            print(f"Email: {user.email}")
            print(f"Activo: {user.activo}")
            print(f"Rol ID: {user.rol_id}")
            print("-" * 60)
    
    print(f"\nTotal de usuarios: {len(usuarios)}\n")
    
finally:
    db.close()
