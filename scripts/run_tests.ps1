# Run All Tests
Write-Host "Running Tests..." -ForegroundColor Green

# Backend tests
Write-Host "Running Backend Tests..." -ForegroundColor Yellow
cd backend
pytest

# Frontend tests
Write-Host "Running Frontend Tests..." -ForegroundColor Yellow
cd ..\frontend
npm test

Write-Host "Tests complete!" -ForegroundColor Green
