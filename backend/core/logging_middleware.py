"""
Middleware de logging profesional para FastAPI.
Registra todas las requests y responses con información estructurada.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

logger = logging.getLogger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging estructurado de requests/responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercepta requests y responses para logging."""
        
        # Generar ID único para la request
        request_id = f"{int(time.time() * 1000)}"
        
        # Información de la request
        start_time = time.time()
        
        # Log de request entrante
        logger.info(
            f"REQUEST: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Procesar request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log de error
            logger.error(
                f"ERROR en request: {type(e).__name__}",
                extra={
                    "request_id": request_id,
                    "exception": str(e),
                },
                exc_info=True
            )
            raise
        
        # Calcular duración
        duration_ms = (time.time() - start_time) * 1000
        
        # Log de response
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            f"RESPONSE: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        )
        
        # Agregar header con request ID
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        
        return response


def setup_logging():
    """Configura el logging estructurado de la aplicación."""
    
    # Formato del logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger principal
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # Handler para consola con formato estructurado
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato con más detalles
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    app_logger.addHandler(console_handler)
    
    # Logger para ML
    ml_logger = logging.getLogger("ml")
    ml_logger.setLevel(logging.INFO)
    ml_logger.addHandler(console_handler)
    
    # Silenciar logs verbosos de librerías
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return app_logger
