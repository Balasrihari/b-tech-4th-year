@echo off
echo Setting up environment configuration...

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
echo # CORS Settings (comma-separated)
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
echo Environment setup complete!
echo You can now run the application using the SETUP_GUIDE.md instructions.
