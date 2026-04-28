# Script de verificación rápida del endpoint /ml/anomalies
# Backend SICOP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACIÓN ENDPOINT /ml/anomalies  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# Verificar si el servidor está corriendo
Write-Host "[1/4] Verificando servidor..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "  ✅ Servidor corriendo" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Servidor NO está corriendo" -ForegroundColor Red
    Write-Host "  Ejecuta: .\run_server.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/4] Probando endpoint con days=7..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/ml/anomalies?days=7" -Method Get -ErrorAction Stop
    
    Write-Host "  ✅ Endpoint funciona correctamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Resultados:" -ForegroundColor Cyan
    Write-Host "  -----------" -ForegroundColor Gray
    Write-Host "  Status:              $($response.status)" -ForegroundColor White
    Write-Host "  Total registros:     $($response.total_records)" -ForegroundColor White
    Write-Host "  Anomalías detectadas: $($response.anomalies_detected)" -ForegroundColor White
    Write-Host "  Tasa de anomalías:   $($response.anomaly_rate_pct)%" -ForegroundColor White
    Write-Host ""
    Write-Host "  Por severidad:" -ForegroundColor Cyan
    Write-Host "    - Crítico:   $($response.by_severity.critico)" -ForegroundColor Red
    Write-Host "    - Sospechoso: $($response.by_severity.sospechoso)" -ForegroundColor Yellow
    Write-Host "    - Normal:    $($response.by_severity.normal)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Rango de fechas:" -ForegroundColor Cyan
    Write-Host "    Inicio: $($response.date_range.start)" -ForegroundColor White
    Write-Host "    Fin:    $($response.date_range.end)" -ForegroundColor White
    
} catch {
    Write-Host "  ❌ Error en la petición" -ForegroundColor Red
    Write-Host "  Código: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
    Write-Host "  Mensaje: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[3/4] Probando endpoint con fechas específicas..." -ForegroundColor Yellow

$hoy = Get-Date -Format "yyyy-MM-dd"
$hace30dias = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/api/ml/anomalies?fecha_inicio=$hace30dias&fecha_fin=$hoy" -Method Get -ErrorAction Stop
    Write-Host "  ✅ Endpoint con fechas funciona" -ForegroundColor Green
    Write-Host "  Registros analizados: $($response2.total_records)" -ForegroundColor White
} catch {
    Write-Host "  ⚠️ Advertencia: Endpoint con fechas tuvo problemas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Probando validación de errores..." -ForegroundColor Yellow

try {
    # Intentar con days inválido (debería fallar con 422)
    $errorTest = Invoke-RestMethod -Uri "$baseUrl/api/ml/anomalies?days=500" -Method Get -ErrorAction Stop
    Write-Host "  ⚠️ Validación de errores no funciona correctamente" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 422) {
        Write-Host "  ✅ Validación de errores funciona correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Error inesperado: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  VERIFICACIÓN COMPLETADA ✅" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints disponibles:" -ForegroundColor Cyan
Write-Host "  GET  /api/ml/anomalies?days=7" -ForegroundColor White
Write-Host "  GET  /api/ml/anomalies?fecha_inicio=...&fecha_fin=..." -ForegroundColor White
Write-Host "  POST /api/ml/predict" -ForegroundColor White
Write-Host "  POST /api/ml/train" -ForegroundColor White
Write-Host "  GET  /api/ml/model/info" -ForegroundColor White
Write-Host "  GET  /api/ml/stats" -ForegroundColor White
Write-Host "  POST /api/ml/model/reload" -ForegroundColor White
Write-Host ""
Write-Host "Documentación: $baseUrl/docs" -ForegroundColor Yellow
Write-Host ""
