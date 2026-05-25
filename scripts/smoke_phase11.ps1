# Phase 11 QA smoke — generate fixtures + pytest + optional k6
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Generating test PDFs..."
python "$Root\scripts\generate_test_pdfs.py"

Write-Host "Running pytest (backend)..."
Push-Location "$Root\backend"
python -m pytest tests/ -q --tb=short -m "not slow"
$code = $LASTEXITCODE
Pop-Location

if ($code -ne 0) { exit $code }

if (Get-Command k6 -ErrorAction SilentlyContinue) {
    Write-Host "Running k6 smoke..."
    k6 run "$Root\deployment\load\k6-smoke.js"
}

Write-Host "Phase 11 smoke complete."
