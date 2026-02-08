@echo off
echo Starting Phase 5 Docker containers...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed or not in PATH. Please install Docker Desktop.
    pause
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is not installed or not in PATH.
    pause
    exit /b 1
)

echo Building and starting containers...
docker-compose up --build

pause