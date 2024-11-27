# Get the root directory of the project (2 levels up from script location)
$projectRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName

# Navigate to project root where docker-compose.yml is located
Set-Location $projectRoot

Write-Host "[INFO] Stopping any running containers..." -ForegroundColor Yellow
docker-compose down -v

Write-Host "[INFO] Cleaning up any dangling images..." -ForegroundColor Yellow
docker system prune -f

Write-Host "[INFO] Building containers..." -ForegroundColor Green
docker-compose build --no-cache

Write-Host "[INFO] Starting containers..." -ForegroundColor Green
docker-compose up -d

Write-Host "`n[SUCCESS] Process completed!" -ForegroundColor Green
Write-Host "[INFO] To view logs run: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "[INFO] To stop containers run: docker-compose down" -ForegroundColor Yellow