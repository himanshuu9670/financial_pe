# Phase 12 - local Docker green run and health validation
# Run from repo root:  .\scripts\smoke_phase12.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-HttpOk {
    param(
        [string]$Url,
        [string]$Name
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Host "[OK] $Name ($($response.StatusCode))" -ForegroundColor Green
            return $true
        }
        Write-Host "[FAIL] $Name status $($response.StatusCode)" -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "[FAIL] $Name - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "=== Phase 12: Local Docker validation ===" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env from .env.example" -ForegroundColor Yellow
    }
    else {
        Write-Host "ERROR: .env.example not found in repo root." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting Docker services..." -ForegroundColor Cyan
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: docker compose up failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Waiting for backend health (up to 3 minutes)..." -ForegroundColor Cyan
$ready = $false
$healthUrl = "http://localhost:8000/api/v1/health"
for ($i = 0; $i -lt 60; $i++) {
    if (Test-HttpOk -Url $healthUrl -Name "Backend Health") {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 3
}

if (-not $ready) {
    Write-Host ""
    Write-Host "ERROR: Backend health check failed." -ForegroundColor Red
    docker compose logs backend --tail 40
    exit 1
}

Write-Host ""
Write-Host "Running Alembic migrations..." -ForegroundColor Cyan
docker compose exec -T backend alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Alembic migration failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Running pytest..." -ForegroundColor Cyan
docker compose exec -T backend pytest tests/ -q -m "not slow" --tb=line
$pytestCode = $LASTEXITCODE

Write-Host ""
Write-Host "Service checks:" -ForegroundColor Cyan
$null = Test-HttpOk -Url $healthUrl -Name "API Health"
$null = Test-HttpOk -Url "http://localhost:8000/api/v1/system-status" -Name "System Status"
$null = Test-HttpOk -Url "http://localhost:5173" -Name "Frontend"

Write-Host ""
Write-Host "Docker containers:" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "Celery worker status:" -ForegroundColor Cyan
docker compose exec -T celery_worker celery -A app.workers.celery_app inspect ping 2>&1 | Select-Object -First 5

if ($pytestCode -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Pytest failed. Fix tests before staging deploy." -ForegroundColor Red
    exit $pytestCode
}

Write-Host ""
Write-Host "Phase 12 local smoke PASSED." -ForegroundColor Green
Write-Host "Next: see docs/PHASE12.md for staging deployment." -ForegroundColor Yellow
exit 0
