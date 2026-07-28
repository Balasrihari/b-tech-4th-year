# Start Backend Server
Write-Host "Starting Backend Server..." -ForegroundColor Green
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
