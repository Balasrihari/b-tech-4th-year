@echo off
echo ========================================
echo AI Student Learning Assistant
echo ========================================
echo.
echo Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo Backend server starting on http://localhost:8000
echo.
echo Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "npm run dev"
echo Frontend server starting on http://localhost:5173
echo.
echo ========================================
echo Application is starting...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window (servers will continue running)
pause > nul
