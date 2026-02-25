@echo off
setlocal
cd /d "%~dp0\.."

echo [HMS] Starting native setup...

set "BASE_PY=python"
set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

%BASE_PY% --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python is not available on PATH.
  echo Install Python 3.11+ and retry.
  exit /b 1
)

if not exist "%VENV_PY%" (
  echo [HMS] Creating virtual environment at %VENV_DIR%...
  %BASE_PY% -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
)

if not exist ".env" (
  copy /Y ".env.native.example" ".env" >nul
  echo [HMS] Created .env from .env.native.example
)

echo [HMS] Installing dependencies...
%VENV_PY% -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo [HMS] Running preflight checks...
%VENV_PY% scripts\preflight.py --mode native --python-executable "%VENV_PY%"
if errorlevel 1 exit /b 1

echo [HMS] Applying migrations...
%VENV_PY% manage.py migrate
if errorlevel 1 exit /b 1

if /I "%1"=="--no-server" (
  echo [HMS] Setup complete. Server startup skipped by --no-server.
  exit /b 0
)

echo [HMS] Starting server at http://127.0.0.1:8000/
%VENV_PY% manage.py runserver 127.0.0.1:8000
