@echo off
title LoopLens Test Runner
echo ===================================================
echo   Running LoopLens Automated Pytest Test Suite
echo ===================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    py --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=py"
    ) else (
        set "PY_CMD=python"
    )
)

%PY_CMD% -m pytest tests/test_api.py tests/test_live_prober.py -v -p no:langsmith
echo.
pause

