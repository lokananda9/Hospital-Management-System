@echo off
setlocal
cd /d "%~dp0\.."

set "VENV_PY=.venv\Scripts\python.exe"

echo [HMS] Starting strict native audit...

call scripts\clean_runtime.cmd
if errorlevel 1 exit /b 1

call scripts\run_native.cmd --no-server
if errorlevel 1 exit /b 1

if not exist "%VENV_PY%" (
  echo [ERROR] Virtual environment python not found at %VENV_PY%
  exit /b 1
)

echo [HMS] Running Django check...
%VENV_PY% manage.py check
if errorlevel 1 exit /b 1

echo [HMS] Running endpoint smoke checks...
%VENV_PY% scripts\smoke_endpoints.py
if errorlevel 1 exit /b 1

echo [HMS] Validating migrations drift...
%VENV_PY% manage.py makemigrations --check --dry-run
if errorlevel 1 exit /b 1

echo [HMS] Running tests...
%VENV_PY% manage.py test
if errorlevel 1 exit /b 1

echo [HMS] Validating OpenAPI schema generation...
%VENV_PY% manage.py spectacular --file NUL
if errorlevel 1 exit /b 1

echo [HMS] Cleaning runtime artifacts generated during checks...
call scripts\clean_runtime.cmd
if errorlevel 1 exit /b 1

echo [HMS] Running file/extension audit...
%VENV_PY% scripts\audit_files.py
if errorlevel 1 exit /b 1

echo [HMS] Native strict audit passed.
exit /b 0
