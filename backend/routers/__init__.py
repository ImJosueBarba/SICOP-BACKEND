"""
Módulo de routers para la API
"""

from . import (
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

__all__ = [
    "usuarios",
    "roles",
    "quimicos",
    "filtros",
    "consumo_mensual",
    "control_operacion",
    "produccion_filtros",
    "consumo_diario",
    "cloro_libre",
    "monitoreo_fisicoquimico",
    "auth",
    "logs",
    "ml"
]
