# Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker build -t picopass-builder .

# Run the container to build the firmware
Write-Host "Compiling firmware..." -ForegroundColor Cyan
$currentDir = Get-Location
docker run --rm -v "${currentDir}/..:/workspace" picopass-builder

Write-Host "Build complete. Check firmware/c/build for .uf2 files." -ForegroundColor Green
