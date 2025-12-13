"""
Archivo principal de FastAPI
Sistema de Gestión de Planta de Tratamiento de Agua "La Esperanza"
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from models import Base

# Importar routers
from routers import (
    usuarios,
    quimicos,
    filtros,
    consumo_mensual,
    control_operacion,
    produccion_filtros,
    consumo_diario,
    cloro_libre,
    consumo_diario,
    cloro_libre,
    monitoreo_fisicoquimico,
    auth
)

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Planta de Tratamiento de Agua",
    description="Sistema de gestión y monitoreo para la Planta La Esperanza",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir peticiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL de Angular en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(quimicos.router, prefix="/api/quimicos", tags=["Químicos"])
app.include_router(filtros.router, prefix="/api/filtros", tags=["Filtros"])
app.include_router(consumo_mensual.router, prefix="/api/consumo-mensual", tags=["Consumo Mensual"])
app.include_router(control_operacion.router, prefix="/api/control-operacion", tags=["Control Operación"])
app.include_router(produccion_filtros.router, prefix="/api/produccion-filtros", tags=["Producción Filtros"])
app.include_router(consumo_diario.router, prefix="/api/consumo-diario", tags=["Consumo Diario"])
app.include_router(cloro_libre.router, prefix="/api/cloro-libre", tags=["Cloro Libre"])
app.include_router(monitoreo_fisicoquimico.router, prefix="/api/monitoreo-fisicoquimico", tags=["Monitoreo Fisicoquímico"])
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    print("🚀 Iniciando API de Planta de Tratamiento de Agua...")
    print("ℹ️  Para crear las tablas, ejecuta el script database_schema.sql en PostgreSQL")
    # Crear tablas automáticamente si no existen
    Base.metadata.create_all(bind=engine)
    print("✅ API inicializada")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "API Planta de Tratamiento de Agua - La Esperanza",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "service": "Planta La Esperanza API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
