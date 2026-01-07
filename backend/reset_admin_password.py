from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.security import get_password_hash
from models.usuario import Usuario

db = SessionLocal()

try:
    # Buscar usuario admin
    admin = db.query(Usuario).filter(Usuario.username == "admin").first()
    
    if admin:
        # Cambiar contraseña a "admin123"
        nueva_password = "admin123"
        admin.hashed_password = get_password_hash(nueva_password)
        db.commit()
        
        print("\n" + "="*60)
        print("✅ CONTRASEÑA ACTUALIZADA EXITOSAMENTE")
        print("="*60)
        print(f"\nUsuario: admin")
        print(f"Nueva contraseña: {nueva_password}")
        print("\n" + "="*60 + "\n")
    else:
        print("❌ Usuario 'admin' no encontrado")
    
finally:
    db.close()
