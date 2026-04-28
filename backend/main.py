"""
Archivo principal de FastAPI
Sistema de Gestión de Planta de Tratamiento de Agua "La Esperanza"
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from core.database import engine
from models import Base
from core.logging_middleware import LoggingMiddleware, setup_logging
from core.exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Importar routers
from routers import (
    usuarios,
    roles,
    quimicos,
    filtros,
    consumo_mensual,
    control_operacion,
    produccion_filtros,
    consumo_diario,
    cloro_libre,
    monitoreo_fisicoquimico,
    auth,
    logs,
    ml
)

# Configurar logging
logger = setup_logging()

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Planta de Tratamiento de Agua",
    description="Sistema de gestión y monitoreo para la Planta La Esperanza",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Registrar exception handlers globales
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Agregar middleware de logging
app.add_middleware(LoggingMiddleware)

# Configurar CORS para permitir peticiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular en desarrollo local
        "http://localhost:8100",  # Ionic en desarrollo local
        "http://localhost",       # Frontend en Docker
        "http://localhost:80"     # Frontend en Docker (explícito)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar carpeta de archivos estáticos para fotos de perfil
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(roles.router, tags=["Roles"])  # Ya tiene su prefix /api/roles
app.include_router(quimicos.router, prefix="/api/quimicos", tags=["Químicos"])
app.include_router(filtros.router, prefix="/api/filtros", tags=["Filtros"])
app.include_router(consumo_mensual.router, prefix="/api/consumo-mensual", tags=["Consumo Mensual"])
app.include_router(control_operacion.router, prefix="/api/control-operacion", tags=["Control Operación"])
app.include_router(produccion_filtros.router, prefix="/api/produccion-filtros", tags=["Producción Filtros"])
app.include_router(consumo_diario.router, prefix="/api/consumo-diario", tags=["Consumo Diario"])
app.include_router(cloro_libre.router, prefix="/api/control-cloro", tags=["Control Cloro"])
app.include_router(monitoreo_fisicoquimico.router, prefix="/api/monitoreo-fisicoquimico", tags=["Monitoreo Fisicoquímico"])
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(logs.router)  # Ya tiene prefix="/api/logs" en el router
app.include_router(ml.router, prefix="/api")  # ML router (ya tiene prefix "/ml")


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    Base.metadata.create_all(bind=engine)
    logger.info("="*60)
    logger.info("🚀 API Planta La Esperanza - INICIADA")
    logger.info(f"📘 Documentación: http://localhost:8000/docs")
    logger.info(f"📗 ReDoc: http://localhost:8000/redoc")
    
    # Cargar modelo ML si existe
    try:
        from ml.inference.predictor_service import ChemicalConsumptionPredictor
        predictor = ChemicalConsumptionPredictor()
        predictor.load_model()
        logger.info("✅ Modelo ML cargado exitosamente")
    except Exception as e:
        logger.warning(f"⚠️  No se pudo cargar el modelo ML: {str(e)}")
        logger.warning("   El sistema funcionará sin predicciones ML")
    
    logger.info("="*60)


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
