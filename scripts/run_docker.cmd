@echo off
setlocal
cd /d "%~dp0\.."

echo [HMS] Starting docker setup...

docker --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker command not found.
  echo Install Docker Desktop: https://www.docker.com/products/docker-desktop/
  echo Restart your terminal and verify with: docker --version
  exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker Compose plugin is unavailable.
  echo Verify with: docker compose version
  exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python is required for preflight checks.
  echo Install Python 3.11+ and retry.
  exit /b 1
)

if not exist ".env" (
  copy /Y ".env.docker.example" ".env" >nul
  echo [HMS] Created .env from .env.docker.example
)

echo [HMS] Running preflight checks...
python scripts\preflight.py --mode docker
if errorlevel 1 exit /b 1

if /I "%1"=="--no-up" (
  echo [HMS] Preflight complete. Container startup skipped by --no-up.
  exit /b 0
)

echo [HMS] Starting containers...
docker compose up --build
