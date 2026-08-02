@echo off
echo Setting up conda environment for Python 3.14...

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Conda not found. Please install Anaconda or Miniconda first.
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Create conda environment from environment.yml
echo Creating conda environment from environment.yml...
conda env create -f environment.yml

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create conda environment.
    pause
    exit /b 1
)

echo Conda environment created successfully!

REM Create backend .env file
cd backend
(
echo # Database Configuration (SQLite - no PostgreSQL needed)
echo DATABASE_URL=sqlite:///./student_learning.db
echo.
echo # Redis Configuration (Optional - will work without Redis)
echo REDIS_URL=redis://localhost:6379/0
echo.
echo # Security
echo SECRET_KEY=dev-secret-key-change-in-production-min-32-chars
echo.
echo # AI Configuration
echo GEMINI_API_KEY=your-gemini-api-key-here
echo.
echo # Application Settings
echo DEBUG=True
echo ENVIRONMENT=development
echo LOG_LEVEL=INFO
echo LOG_DIR=logs
echo.
echo # CORS Settings
echo CORS_ORIGINS=http://localhost:5173,http://localhost:3000
echo.
echo # File Upload Settings
echo MAX_UPLOAD_SIZE=10485760
echo UPLOAD_DIR=uploads
echo.
echo # Vector Database
echo CHROMA_DB_PATH=./chroma_db
) > .env

echo Backend .env file created successfully!

REM Create frontend .env file
cd ..\frontend
(
echo VITE_API_URL=http://localhost:8000
) > .env

echo Frontend .env file created successfully!

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To activate the conda environment:
echo   conda activate student-learning-assistant
echo.
echo Then run:
echo   cd backend
echo   alembic upgrade head
echo   python scripts/generate_demo_data.py
echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo In another terminal:
echo   conda activate student-learning-assistant
echo   cd frontend
echo   npm install
echo   npm run dev
echo.
pause
