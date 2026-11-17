@echo off
title LoopLens Server Launcher
echo ===================================================
echo   Starting LoopLens - Loop Engineering Control Center
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python environment...
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
    echo     Using project virtual environment (.venv)
) else (
    py --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py"
        echo     Using Python launcher: py
    ) else (
        python --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "PY_CMD=python"
            echo     Using system Python: python
        ) else (
            echo [ERROR] Neither 'py' nor 'python' was found in your PATH.
            echo Please ensure Python 3.11+ is installed.
            pause
            exit /b 1
        )
    )
)

echo [2/3] Opening dashboard in your default browser...
start http://127.0.0.1:8000

echo [3/3] Starting Uvicorn web server on http://127.0.0.1:8000 ...
echo Press CTRL+C to stop the server at any time.
echo.

%PY_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server terminated with error code %ERRORLEVEL%.
    pause
)

