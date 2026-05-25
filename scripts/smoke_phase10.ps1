# Phase 10 production smoke — health, metrics, system status
$ErrorActionPreference = "Stop"
$Api = $env:SMOKE_API_BASE ?? "http://localhost:8000/api/v1"

Write-Host "Phase 10 smoke: $Api"

$h = Invoke-RestMethod "$Api/../health" -ErrorAction SilentlyContinue
if (-not $h) { $h = Invoke-RestMethod "$Api/health" }
Write-Host "Health: $($h.status)"

$sys = Invoke-RestMethod "$Api/system-status"
Write-Host "System: $($sys.status) db=$($sys.database) redis=$($sys.redis) workers=$($sys.celery_workers)"

try {
    $metrics = Invoke-WebRequest "$Api/metrics" -UseBasicParsing
    if ($metrics.Content -match "http_requests_total") {
        Write-Host "OK: Prometheus metrics endpoint"
    }
} catch {
    Write-Warning "Metrics endpoint not reachable"
}

Write-Host "Phase 10 smoke complete"
