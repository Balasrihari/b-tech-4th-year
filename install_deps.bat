@echo off
echo Installing dependencies for Python 3.14...
echo.

cd backend

REM Activate virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo Installing core dependencies...
echo ========================================
echo.

REM Install core packages first
pip install --upgrade pip
pip install --prefer-binary fastapi uvicorn[standard] sqlalchemy alembic

echo.
echo ========================================
echo Installing pydantic packages...
echo ========================================
echo.

REM Try installing pydantic with --prefer-binary
pip install --prefer-binary pydantic pydantic-settings

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pydantic installation failed. Trying without version constraints...
    pip install pydantic pydantic-settings --no-cache-dir
)

echo.
echo ========================================
echo Installing security packages...
echo ========================================
echo.

pip install python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv httpx

echo.
echo ========================================
echo Installing document processing...
echo ========================================
echo.

pip install PyPDF2 python-docx python-pptx openpyxl beautifulsoup4 requests rank-bm25 loguru

echo.
echo ========================================
echo Installing Pillow (may fail on Python 3.14)...
echo ========================================
echo.

pip install --prefer-binary Pillow

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Pillow installation failed. OCR features may not work.
    echo You can try installing Visual Studio Build Tools to compile from source.
)

echo.
echo ========================================
echo Installing pytesseract (may fail on Python 3.14)...
echo ========================================
echo.

pip install --prefer-binary pytesseract

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pytesseract installation failed. OCR features may not work.
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Some packages may have failed due to Python 3.14 compatibility.
echo The core application should still work without the failed packages.
echo.
echo Next steps:
echo   alembic upgrade head
echo   python scripts/generate_demo_data.py
echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.

pause
