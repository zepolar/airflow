$ErrorActionPreference = 'Stop'

# Change to repo root (parent of this scripts directory)
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $root

Write-Host 'Starting Airflow (and dependencies) with Docker Compose...' -ForegroundColor Cyan
docker compose up -d airflow

if ($LASTEXITCODE -ne 0) {
  Write-Error 'Failed to start Airflow via docker compose.'
  exit 1
}

Write-Host ''
Write-Host 'Waiting for Airflow webserver to become ready (health endpoint)...' -ForegroundColor Cyan
$readyUrl = 'http://localhost:8080/health'
$maxWait = 180
$sleepSec = 3
$elapsed = 0
while ($true) {
  try {
    $response = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) { break }
  } catch {
    # ignore and retry
  }
  if ($elapsed -ge $maxWait) {
    Write-Error "Airflow webserver not ready after ${maxWait}s. Check logs: docker compose logs -f airflow"
    exit 1
  }
  Start-Sleep -Seconds $sleepSec
  $elapsed += $sleepSec
}

Write-Host 'Airflow is ready. Open:' -ForegroundColor Green
Write-Host '  http://localhost:8080' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Default credentials (first run): admin / admin' -ForegroundColor DarkGray
