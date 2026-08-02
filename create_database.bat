@echo off
echo Creating PostgreSQL database...

REM Check if psql is available
where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL psql command not found in PATH.
    echo Please install PostgreSQL or add it to your PATH.
    echo.
    echo Alternative: Use pgAdmin to create database manually:
    echo 1. Open pgAdmin
    echo 2. Connect to your PostgreSQL server
    echo 3. Right-click on "Databases" ^> Create ^> Database
    echo 4. Name: student_learning_db
    echo 5. Click "Save"
    pause
    exit /b 1
)

REM Create database using psql
echo Enter PostgreSQL password (default: postgres):
psql -U postgres -c "CREATE DATABASE student_learning_db;"

if %ERRORLEVEL% EQU 0 (
    echo Database created successfully!
) else (
    echo Failed to create database. It may already exist.
    echo You can continue if the database already exists.
)

pause
