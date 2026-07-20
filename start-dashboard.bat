@echo off
setlocal

REM Starts backend and frontend in separate visible terminal windows.
REM Keep both windows open while using the dashboard.

set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=%PROJECT_DIR%\backend\venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Could not find a virtualenv Python at:
    echo   %PROJECT_DIR%\.venv\Scripts\python.exe
    echo   %PROJECT_DIR%\backend\venv\Scripts\python.exe
    echo.
    echo Create/activate your virtualenv first, then run this script again.
    pause
    exit /b 1
)

echo Starting backend on port 8000...
start "Governance Agent - Backend" /D "%PROJECT_DIR%" cmd /k ""%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo Starting frontend on port 3000...
start "Governance Agent - Frontend" /D "%PROJECT_DIR%\frontend" cmd /k "set BROWSER=none&& npm.cmd start"

echo.
echo Both servers are launching in separate windows.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:3000
echo.
echo Leave those two windows open while using the app.
pause
