@echo off
title LexAudit - Start Services
echo ===================================================
echo   LexAudit: Legal/Contract Compliance Auditor
echo ===================================================

:: Check python environment
echo.
echo [1/3] Verifying Python Virtual Environment...
if not exist "venv" (
    echo Python virtual environment not found. Creating one...
    python -m venv venv
)
echo Installing backend python packages...
call venv\Scripts\pip install -r backend\requirements.txt

:: Check Node environment
echo.
echo [2/3] Installing Node.js Frontend dependencies...
cd frontend
call npm install
cd ..

:: Pick a free backend port (8000 is the default, but it may already be taken
:: by another service such as Apache). Falls back to 8008 / 8010 / 8020.
set "BACKEND_PORT=8000"
for /f "usebackq tokens=*" %%P in (`powershell -NoProfile -Command "foreach ($p in 8000,8008,8010,8020) { if (-not (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue)) { Write-Output $p; break } }"`) do set "BACKEND_PORT=%%P"

:: Tell the frontend where the backend is (read by src/constants.js via Vite).
set "VITE_API_BASE=http://127.0.0.1:%BACKEND_PORT%/api"

:: Start both servers in parallel
echo.
echo [3/3] Booting FastAPI backend and React frontend...
echo.
echo Starting FastAPI Backend on http://127.0.0.1:%BACKEND_PORT%...
start "LexAudit Backend" cmd /c "venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload"

echo Starting React Vite Frontend on http://localhost:5173...
start "LexAudit Frontend" cmd /c "cd frontend && npm run dev -- --port 5173"

echo.
echo ===================================================
echo Success! Both services have been launched.
echo   - Backend: http://127.0.0.1:%BACKEND_PORT%
echo   - Frontend: http://localhost:5173
echo ===================================================
echo.
pause
