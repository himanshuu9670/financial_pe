# Restore Postgres from scripts/../storage/backups/*.sql
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [string]$Host = "localhost",
    [int]$Port = 5433,
    [string]$User = "pdf_editor",
    [string]$Db = "pdf_editor_db",
    [string]$Password = "pdf_editor_secret"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $BackupFile)) {
    Write-Error "Backup not found: $BackupFile"
}

$env:PGPASSWORD = $Password
Write-Host "Restoring $BackupFile to $Db on ${Host}:${Port}..."
psql -h $Host -p $Port -U $User -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$Db' AND pid <> pg_backend_pid();" 2>$null
psql -h $Host -p $Port -U $User -d postgres -c "DROP DATABASE IF EXISTS ${Db}_restore_test;"
psql -h $Host -p $Port -U $User -d postgres -c "CREATE DATABASE ${Db}_restore_test;"
psql -h $Host -p $Port -U $User -d "${Db}_restore_test" -f $BackupFile
Write-Host "Restore validation DB: ${Db}_restore_test — verify then swap manually for production."
