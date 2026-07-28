# Setup Backend Environment
Write-Host "Setting up Backend Environment..." -ForegroundColor Green

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
cd backend
alembic upgrade head

# Seed database
Write-Host "Seeding database..." -ForegroundColor Yellow
cd ..\database
python seed_data.py

Write-Host "Backend setup complete!" -ForegroundColor Green
