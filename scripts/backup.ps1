# Database backup helper (run against local or Docker Postgres)
param(
  [string]$Host = "localhost",
  [int]$Port = 5433,
  [string]$User = "pdf_editor",
  [string]$Db = "pdf_editor_db"
)

$OutDir = Join-Path $PSScriptRoot "..\storage\backups"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$File = Join-Path $OutDir ("pdf_editor_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".sql")
$env:PGPASSWORD = "pdf_editor_secret"
pg_dump -h $Host -p $Port -U $User -d $Db -f $File
Write-Host "Backup written to $File"
