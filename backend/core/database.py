"""
Configuración de la base de datos PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:UTM123@localhost:5432/planta_esperanza"
)

# Crear engine con codificación UTF-8
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    echo=False,  # Cambia a True para ver las queries SQL en consola
    future=True,
    poolclass=NullPool if "sqlite" in DATABASE_URL else None,
    connect_args={"client_encoding": "utf8"}  # Forzar UTF-8
)

# Crear SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener una sesión de base de datos
    Se usa en FastAPI con Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")


def drop_db():
    """
    Elimina todas las tablas (usar con precaución)
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Todas las tablas han sido eliminadas")
