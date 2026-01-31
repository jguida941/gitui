@echo off
setlocal

set "ROOT=%~dp0.."
cd /d "%ROOT%"

call :find_python
if errorlevel 1 (
  echo Python 3.10+ not found.
  set /p ans=Install Python 3.11 with winget now? (y/N):
  if /i "%ans%"=="y" (
    goto :install_python
  )
  if /i "%ans%"=="yes" (
    goto :install_python
  ) else (
    exit /b 1
  )
) else (
  goto :after_python_check
)

:install_python
    where winget >nul 2>&1
    if %errorlevel%==0 (
      winget install -e --id Python.Python.3.11 --source winget
    ) else (
      echo winget not found. Install Python 3.10+ manually and re-run.
      exit /b 1
    )
    call :find_python
    if errorlevel 1 (
      echo Python install not detected. Restart your shell or install manually.
      exit /b 1
    )

:after_python_check
if not exist .venv (
  call %PY% -m venv .venv
  if errorlevel 1 exit /b 1
)

if not exist .venv\Scripts\python.exe (
  echo .venv\Scripts\python.exe not found. Delete .venv and re-run the installer.
  exit /b 1
)

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install .
if errorlevel 1 exit /b 1

echo Install complete!
echo.
echo To launch GitUI:
echo   %ROOT%\.venv\Scripts\python -m app.main
echo.
echo To open a specific repo:
echo   %ROOT%\.venv\Scripts\python -m app.main --repo ^<path^>

exit /b 0

:find_python
set "PY="
where py >nul 2>&1
if %errorlevel%==0 (
  set "PY=py -3"
  call :check_version
  if %errorlevel%==0 exit /b 0
)
where python >nul 2>&1
if %errorlevel%==0 (
  set "PY=python"
  call :check_version
  if %errorlevel%==0 exit /b 0
)
exit /b 1

:check_version
set "PYOK="
for /f "delims=" %%A in ('%PY% -c "import sys, os; exe=sys.executable or \"\"; ok=sys.version_info >= (3,10) and \"windowsapps\" not in exe.lower(); print(\"PYOK\" if ok else \"PYNO\"); raise SystemExit(0 if ok else 1)" 2^>nul') do (
  if "%%A"=="PYOK" set "PYOK=1"
)
if defined PYOK exit /b 0
exit /b 1
