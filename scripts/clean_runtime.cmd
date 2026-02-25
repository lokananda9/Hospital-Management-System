@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\.."

set "FAILED=0"
set "WARNED=0"
echo [HMS] Cleaning runtime artifacts...

for %%f in (server*.log localhost_boot.log schema_check.yml) do (
  if exist "%%f" (
    del /f /q "%%f" >nul 2>&1
    if exist "%%f" (
      echo [WARN] Could not remove file: %%f
      set "WARNED=1"
    )
  )
)

for /r %%f in (*.pyc *.pyo) do (
  if exist "%%f" (
    del /f /q "%%f" >nul 2>&1
    if exist "%%f" (
      echo [WARN] Could not remove file: %%f
      set "FAILED=1"
    )
  )
)

for /d /r %%d in (__pycache__) do (
  if exist "%%d" (
    rd /s /q "%%d" >nul 2>&1
    if exist "%%d" (
      echo [WARN] Could not remove directory: %%d
      set "FAILED=1"
    )
  )
)

if "!FAILED!"=="1" (
  echo [ERROR] Cleanup failed for blocking artifacts (^*.pyc/__pycache__^). Stop running Python servers and retry.
  exit /b 1
)

if "!WARNED!"=="1" (
  echo [HMS] Cleanup finished with warnings. Continuing.
)

echo [HMS] Runtime cleanup complete.
exit /b 0
