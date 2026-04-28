"""
Tests unitarios y de integración para el módulo ML.

Ejecutar con:
    pytest tests/test_ml_endpoints.py -v
    pytest tests/test_ml_endpoints.py::test_anomalies_with_days -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

# Importar la aplicación
import sys
sys.path.insert(0, '..')
from main import app

client = TestClient(app)


# ============================================================================
# Tests para /ml/anomalies
# ============================================================================

def test_anomalies_with_days_parameter():
    """Test endpoint /ml/anomalies con parámetro days."""
    
    response = client.get("/api/ml/anomalies?days=7")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "status" in data
    assert "total_records" in data
    assert "anomalies_detected" in data
    assert "anomaly_rate_pct" in data
    assert "by_severity" in data
    assert "date_range" in data
    assert "anomalies" in data
    
    # Verificar tipos
    assert isinstance(data["total_records"], int)
    assert isinstance(data["anomalies_detected"], int)
    assert isinstance(data["anomaly_rate_pct"], (int, float))
    assert isinstance(data["by_severity"], dict)
    assert isinstance(data["anomalies"], list)
    
    # Verificar by_severity
    assert "critico" in data["by_severity"]
    assert "sospechoso" in data["by_severity"]
    assert "normal" in data["by_severity"]
    
    # Verificar date_range
    assert "start" in data["date_range"]
    assert "end" in data["date_range"]


def test_anomalies_with_date_range():
    """Test endpoint /ml/anomalies con rango de fechas específico."""
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/api/ml/anomalies?fecha_inicio={start_date}&fecha_fin={end_date}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["date_range"]["start"] == start_date
    assert data["date_range"]["end"] == end_date


def test_anomalies_invalid_days():
    """Test endpoint /ml/anomalies con days inválido (fuera de rango)."""
    
    # days muy grande
    response = client.get("/api/ml/anomalies?days=500")
    assert response.status_code == 422
    
    # days negativo
    response = client.get("/api/ml/anomalies?days=-5")
    assert response.status_code == 422
    
    # days 0
    response = client.get("/api/ml/anomalies?days=0")
    assert response.status_code == 422


def test_anomalies_invalid_date_range():
    """Test endpoint /ml/anomalies con rango de fechas inválido."""
    
    yesterday = (date.today() - timedelta(days=1)). isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # Fecha inicio posterior a fecha fin
    response = client.get(
        f"/api/ml/anomalies?fecha_inicio={tomorrow}&fecha_fin={yesterday}"
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"] is True
    assert "message" in data


def test_anomalies_default_days():
    """Test que days por defecto sea 7."""
    
    response = client.get("/api/ml/anomalies")
    
    assert response.status_code == 200
    data = response.json()
    
    # Calcular diferencia de fechas
    start = date.fromisoformat(data["date_range"]["start"])
    end = date.fromisoformat(data["date_range"]["end"])
    diff = (end - start).days
    
    assert diff == 7, "El valor por defecto de days debe ser 7"


def test_anomalies_empty_data():
    """Test endpoint cuando no hay datos disponibles."""
    
    # Usar fechas muy antiguas donde probablemente no haya datos
    response = client.get(
        "/api/ml/anomalies?fecha_inicio=2000-01-01&fecha_fin=2000-01-07"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_records"] == 0
    assert data["anomalies_detected"] == 0
    assert data["anomaly_rate_pct"] == 0.0
    assert len(data["anomalies"]) == 0


# ============================================================================
# Tests para /ml/predict
# ============================================================================

def test_predict_valid_request():
    """Test predicción con datos válidos."""
    
    payload = {
        "turbedad_ac": 25.5,
        "turbedad_at": 0.8,
        "ph_ac": 7.2,
        "ph_at": 7.5,
        "temperatura_ac": 22.0
    }
    
    response = client.post("/api/ml/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar respuesta
    assert "sulfato_kg" in data
    assert "cal_kg" in data
    assert "hipoclorito_kg" in data
    assert "cloro_gas_kg" in data
    assert "confidence" in data
    assert "model_name" in data
    assert "estimated_cost_usd" in data
    assert "prediction_date" in data
    
    # Verificar que sean números positivos
    assert data["sulfato_kg"] >= 0
    assert data["cal_kg"] >= 0
    assert data["confidence"] >= 0 and data["confidence"] <= 1


def test_predict_invalid_turbedad():
    """Test predicción con turbidez inválida."""
    
    payload = {
        "turbedad_ac": 600,  # Fuera de rango (máx 500)
        "turbedad_at": 0.8,
        "ph_ac": 7.2,
        "ph_at": 7.5,
        "temperatura_ac": 22.0
    }
    
    response = client.post("/api/ml/predict", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"] is True


def test_predict_turbedad_at_greater_than_ac():
    """Test que turbidez tratada no puede ser mayor que cruda."""
    
    payload = {
        "turbedad_ac": 10.0,
        "turbedad_at": 15.0,  # Mayor que AC
        "ph_ac": 7.2,
        "ph_at": 7.5,
        "temperatura_ac": 22.0
    }
    
    response = client.post("/api/ml/predict", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_predict_missing_required_fields():
    """Test predicción sin campos requeridos."""
    
    payload = {
        "turbedad_ac": 25.5,
        # Faltan campos requeridos
    }
    
    response = client.post("/api/ml/predict", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "details" in data
    assert "errors" in data["details"]


# ============================================================================
# Tests para /ml/model/info
# ============================================================================

def test_model_info():
    """Test obtener información del modelo."""
    
    response = client.get("/api/ml/model/info")
    
    assert response.status_code == 200
    data = response.json()
    
    # Debe tener al menos información básica del modelo
    assert isinstance(data, dict)


def test_model_reload():
    """Test recargar modelo."""
    
    response = client.post("/api/ml/model/reload")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "model_info" in data
    assert "message" in data


def test_stats():
    """Test obtener estadísticas ML."""
    
    response = client.get("/api/ml/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "data_availability" in data
    assert "current_model" in data
    assert "config" in data


# ============================================================================
# Tests de validación de errores
# ============================================================================

def test_error_response_structure():
    """Test que la estructura de errores sea consistente."""
    
    # Generar un error de validación
    response = client.get("/api/ml/anomalies?days=-10")
    
    assert response.status_code == 422
    data = response.json()
    
    # Verificar estructura de error
    assert "error" in data
    assert data["error"] is True
    assert "error_code" in data
    assert "message" in data
    assert "details" in data
    assert "timestamp" in data
    assert "path" in data


def test_error_logging():
    """Test que los errores se logueen correctamente."""
    
    # Este test verifica que el sistema no crashee con errores inesperados
    response = client.get("/api/ml/anomalies?days=abc")
    
    # Debe retornar 422 en lugar de 500
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


# ============================================================================
# Tests de performance
# ============================================================================

def test_anomalies_response_time():
    """Test que la respuesta sea rápida (< 5 segundos)."""
    
    import time
    start = time.time()
    
    response = client.get("/api/ml/anomalies?days=7")
    
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 5.0, f"Respuesta muy lenta: {duration:.2f}s"


# ============================================================================
# Fixtures y Mocks
# ============================================================================

@pytest.fixture
def mock_empty_database():
    """Mock de base de datos vacía."""
    with patch('routers.ml.PlantDataRepository') as mock:
        mock_instance = MagicMock()
        mock_instance.get_operational_data.return_value = pd.DataFrame()
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_database_with_data():
    """Mock de base de datos con datos."""
    with patch('routers.ml.PlantDataRepository') as mock:
        mock_instance = MagicMock()
        # Crear DataFrame de ejemplo
        df = pd.DataFrame({
            'fecha': pd.date_range('2026-01-01', periods=100),
            'turbedad_ac': [25.5] * 100,
            'ph_ac': [7.2] * 100
        })
        mock_instance.get_operational_data.return_value = df
        mock.return_value = mock_instance
        yield mock


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
