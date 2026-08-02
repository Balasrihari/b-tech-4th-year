# Setup Guide - AI-Powered Smart Student Learning Assistant

This guide will help you set up and run the application for real-time development on Windows.

## Prerequisites

### Required Software

1. **Python 3.10-3.13** - [Download here](https://www.python.org/downloads/)
   - **IMPORTANT:** Python 3.14 has compatibility issues with some packages
   - During installation, check "Add Python to PATH"
   - Recommended: Python 3.11 or 3.12

2. **Node.js 18+** - [Download here](https://nodejs.org/)
   - Includes npm package manager

3. **Git** - [Download here](https://git-scm.com/download/win)

### Optional Software

4. **Tesseract OCR** (for image document processing)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH

## Quick Start (Recommended)

### Step 1: Run Environment Setup

```bash
.\setup_env.bat
```

This automatically creates the `.env` files with your Gemini API key configured.

### Step 2: Set Up Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
cd backend
venv\Scripts\activate
alembic upgrade head
```

### Step 4: Generate Demo Data (Optional)

```bash
cd backend
venv\Scripts\activate
python scripts/generate_demo_data.py
```

**Demo Credentials:**
- Students: `student1@university.edu` / `StudentPass123!`
- Faculty: `faculty1@university.edu` / `FacultyPass123!`
- Admin: `admin@university.edu` / `AdminPass123!`

### Step 5: Start Backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### Step 6: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:5173

## One-Command Startup

Use the provided startup script:

```bash
.\start.bat
```

This will start both backend and frontend in separate windows.

## Manual Setup (If Quick Start Fails)

### Backend Setup

#### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter errors with psycopg2, the project is configured to use SQLite by default (no PostgreSQL required).

#### 3. Configure Environment

Create `backend/.env` file:

```bash
# Database Configuration (SQLite - no PostgreSQL needed)
DATABASE_URL=sqlite:///./student_learning.db

# Redis Configuration (Optional - will work without Redis)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Application Settings
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_DIR=logs

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads

# Vector Database
CHROMA_DB_PATH=./chroma_db
```

#### 4. Initialize Database

```bash
cd backend
venv\Scripts\activate
alembic upgrade head
```

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

Create `frontend/.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### PostgreSQL Not Required

The project now uses SQLite by default, so you don't need to install PostgreSQL. If you want to use PostgreSQL instead:

1. Install PostgreSQL 15+
2. Create database: `student_learning_db`
3. Change `DATABASE_URL` in `.env` to:
   ```
   DATABASE_URL=postgresql://postgres:your-password@localhost:5432/student_learning_db
   ```
4. Uncomment `psycopg2-binary` in `requirements.txt`

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Python Module Not Found

```bash
cd backend
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Virtual Environment Issues

```bash
# Delete and recreate venv
cd backend
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Development Workflow

### Backend Development

- Backend auto-reloads on file changes
- API docs available at http://localhost:8000/docs
- Logs stored in `backend/logs/` directory

### Frontend Development

- Frontend hot-reloads on file changes
- React DevTools recommended for debugging

### Running Tests

```bash
# Backend tests
cd backend
venv\Scripts\activate
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Project Structure

```
b-tech-4th-year/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/            # Backend tests
│   ├── scripts/          # Utility scripts
│   └── main.py           # Application entry
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utilities
│   └── public/           # Static assets
├── uploads/              # File uploads
├── logs/                 # Application logs
└── chroma_db/           # Vector database
```

## Access Points

Once running:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Interactive API:** http://localhost:8000/redoc

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review logs in `backend/logs/`
- Check GitHub issues

## License

This project is developed for academic purposes.
