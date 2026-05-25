# Benchmark OCR/extraction cache — requires statement with scanned PDF
param(
  [string]$Api = "http://localhost:8000/api/v1",
  [string]$StatementId = ""
)

if (-not $StatementId) {
  $list = Invoke-RestMethod "$Api/statements?limit=1"
  if (-not $list.items.Count) { Write-Host "Upload a statement first"; exit 1 }
  $StatementId = $list.items[0].id
}

Write-Host "Statement: $StatementId"

Write-Host "`nCold parse (refresh=true)..."
$cold = Measure-Command {
  Invoke-RestMethod "$Api/statements/$StatementId/transactions?refresh=true" | Out-Null
}
Write-Host "Cold: $($cold.TotalSeconds.ToString('0.00'))s"

Write-Host "`nWarm parse (cached)..."
$warm = Measure-Command {
  Invoke-RestMethod "$Api/statements/$StatementId/transactions" | Out-Null
}
Write-Host "Warm: $($warm.TotalSeconds.ToString('0.00'))s"

Write-Host "`nCache stats (admin)..."
try {
  $cache = Invoke-RestMethod "$Api/admin/cache-stats"
  $cache.stats.hit_rates | ConvertTo-Json
} catch {
  Write-Host "Admin cache-stats requires auth — check /admin UI"
}

Write-Host "`nDone. See docs/CACHE_PERFORMANCE_REPORT.md"
