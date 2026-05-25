# Start staging stack (auth enabled, prod images, nginx)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$EnvFile = ".env.staging"
if (-not (Test-Path $EnvFile)) {
    Copy-Item ".env.staging.example" $EnvFile
    Write-Host "Created $EnvFile — edit secrets before production UAT."
}

$Compose = "deployment/docker/docker-compose.staging.yml"
docker compose -f $Compose --env-file $EnvFile up -d --build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Staging stack:"
Write-Host "  App (nginx)  http://localhost (port 80)"
Write-Host "  Grafana      http://localhost:3001"
Write-Host "  Prometheus   http://localhost:9090"
Write-Host ""
Write-Host "UAT login (seeded): demo@pdfeditor.local / demo-password-change-me"
Write-Host "Set AUTH_DISABLED=false in .env.staging for JWT enforcement."
docker compose -f $Compose --env-file $EnvFile ps
