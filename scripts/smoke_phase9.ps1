# Phase 9 smoke validation — requires stack running (docker compose up)
$ErrorActionPreference = "Stop"
$Base = $env:SMOKE_API_BASE ?? "http://localhost:8000/api/v1"

Write-Host "Phase 9 smoke test against $Base"

$health = Invoke-RestMethod -Uri "http://localhost:8000/docs" -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
if (-not $health) {
    Write-Warning "Backend may not be up. Start: docker compose up -d"
}

$statements = Invoke-RestMethod -Uri "$Base/statements" -Method Get -ErrorAction SilentlyContinue
if (-not $statements -or $statements.items.Count -eq 0) {
    Write-Host "SKIP: No statements — upload a PDF first via /preview"
    exit 0
}

$sid = $statements.items[0].id
Write-Host "Statement: $sid"

Invoke-RestMethod -Uri "$Base/statements/$sid/transactions?refresh=true" -Method Get | Out-Null
Write-Host "OK: transactions parsed"

$insights = Invoke-RestMethod -Uri "$Base/ai/insights?statement_id=$sid" -Method Get
Write-Host "OK: insights confidence=$($insights.confidence.overall)"

$anomalies = Invoke-RestMethod -Uri "$Base/ai/anomalies?statement_id=$sid" -Method Get
Write-Host "OK: anomalies count=$($anomalies.anomalies.Count)"

$search = Invoke-RestMethod -Uri "$Base/ai/search?statement_id=$sid&q=travel" -Method Get
Write-Host "OK: semantic search results=$($search.results.Count)"

$status = Invoke-RestMethod -Uri "$Base/ai/status?statement_id=$sid" -Method Get
Write-Host "OK: ai status=$($status.processing.status)"

Write-Host "Phase 9 smoke PASSED"
