"""
Exception handlers globales y custom exceptions para FastAPI.
Manejo profesional de errores con logging estructurado.
"""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger("app")


class APIException(Exception):
    """Exception base personalizada para la API."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Exception para errores de validación."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ResourceNotFoundException(APIException):
    """Exception para recursos no encontrados."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} con identificador '{identifier}' no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)}
        )


class InsufficientDataException(APIException):
    """Exception para datos insuficientes en ML."""
    
    def __init__(self, message: str, required: int, found: int):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INSUFFICIENT_DATA",
            details={"required": required, "found": found}
        )


class MLModelException(APIException):
    """Exception para errores del modelo ML."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="ML_MODEL_ERROR",
            details=details
        )


# ============================================================================
# Exception Handlers
# ============================================================================

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handler para APIException personalizada."""
    
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handler mejorado para errores de validación de Pydantic."""
    
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    logger.warning(
        f"Validation Error en {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors,
            "query_params": str(request.query_params),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Error de validación en los parámetros enviados",
            "details": {
                "errors": errors,
                "received_params": dict(request.query_params) if request.query_params else {}
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler para excepciones no capturadas."""
    
    # Log con stack trace completo
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # En producción, no revelar detalles internos
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Ha ocurrido un error interno en el servidor",
            "details": {
                "type": type(exc).__name__,
                "message": str(exc)  # En producción, omitir esto
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )
