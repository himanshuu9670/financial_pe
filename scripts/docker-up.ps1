# Start StatementForge stack (Windows-friendly)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
} elseif (-not (Select-String -Path ".env" -Pattern "POSTGRES_HOST_PORT" -Quiet)) {
    Add-Content ".env" "`nPOSTGRES_HOST_PORT=5433"
    Write-Host "Added POSTGRES_HOST_PORT=5433 to .env (avoids port 5432 conflicts)"
}

# Free stuck containers from a previous failed run (ignore errors)
docker compose down --remove-orphans 2>$null

Write-Host "Building and starting services (first run may take several minutes)..."
docker compose up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Compose failed. Common fixes:"
    Write-Host "  1. Start Docker Desktop and wait until it shows Running"
    Write-Host "  2. Port 5433 in use? Set POSTGRES_HOST_PORT=5434 in .env"
    Write-Host "  3. Port 8000/5173 in use? Stop other dev servers"
    Write-Host "  4. Run: docker compose logs backend --tail 50"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Services:"
Write-Host "  Frontend  http://localhost:5173"
Write-Host "  API       http://localhost:8000/docs"
Write-Host "  Postgres  localhost:5433 (host) -> 5432 (container)"
docker compose ps
