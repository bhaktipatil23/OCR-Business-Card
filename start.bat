@echo off
echo Starting ReCircle OCR Application...

echo.
echo Starting Backend Server...
start "Backend" cmd /k "cd recircle-cardscan-backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8080
echo.
pause