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
    "sqlite:///./planta_esperanza.db"
)

# Detectar tipo de base de datos
is_sqlite = DATABASE_URL.startswith("sqlite")

# Configurar engine según el tipo de base de datos
if is_sqlite:
    # Configuración para SQLite
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}  # Necesario para SQLite con FastAPI
    )
else:
    # Configuración para PostgreSQL (Supabase)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        connect_args={
            "client_encoding": "utf8",
            "connect_timeout": 10
        }
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
