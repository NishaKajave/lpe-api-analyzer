# LoopLens PowerShell Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting LoopLens - Loop Engineering Control Center" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$pyCmd = "py"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pyCmd = ".\.venv\Scripts\python.exe"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} else {
    Write-Error "Neither 'py' nor 'python' was found in your PATH."
    exit 1
}

Write-Host "Using Python launcher: $pyCmd" -ForegroundColor Green
Write-Host "Opening browser: http://127.0.0.1:8000" -ForegroundColor Yellow
Start-Process "http://127.0.0.1:8000"

Write-Host "Launching server on http://127.0.0.1:8000 (Press Ctrl+C to stop)..." -ForegroundColor White
& $pyCmd -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

