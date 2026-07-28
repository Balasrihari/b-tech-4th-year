# AI-Powered Smart Student Learning Assistant

A comprehensive full-stack academic project providing AI-powered learning assistance for students, faculty, and administrators.

## Project Overview

This B.Tech final-year project implements an intelligent learning platform with:
- Advanced RAG (Retrieval-Augmented Generation) system
- Multi-agent AI architecture using LangChain and LangGraph
- Support for multiple document formats (PDF, DOCX, PPTX, XLSX, TXT, Markdown, Images, URLs)
- Role-based access control (Student, Faculty, Admin)
- Learning analytics and personalized recommendations
- Real AI integration with Google Gemini API

## Technology Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios
- TanStack Query
- Recharts
- Lucide Icons

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- PostgreSQL
- Redis
- LangChain
- LangGraph
- Google Gemini API

## Project Structure

```
.
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── hooks/           # Custom hooks
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.js
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database configuration
│   │   └── auth/           # Authentication
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── main.py
├── database/               # Database utilities
│   └── seed_data.py       # Seed data script
├── docs/                  # Documentation
├── scripts/               # Development scripts
├── tests/                 # Test suites
│   ├── backend/
│   ├── frontend/
│   └── integration/
├── .env.example          # Environment variables template
├── .gitignore
├── README.md
├── PROJECT_FEATURES_LOCK.md
├── PROJECT_ARCHITECTURE.md
└── DEVELOPMENT_STATUS.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 54b1
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

5. Set up PostgreSQL database:
```bash
# Create database
createdb student_learning_db

# Run migrations
cd backend
alembic upgrade head

# Seed initial data
cd ../database
python seed_data.py
```

6. Start Redis server:
```bash
redis-server
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Default Users

After running seed_data.py, the following users are available:

- **Admin**: admin@example.com / admin123
- **Faculty**: faculty@example.com / faculty123
- **Student**: student@example.com / student123

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## Features

### Student Features
- Personal dashboard
- Document upload and management
- AI-powered Q&A with citations
- Document summaries
- Study notes
- AI coding assistant
- Personalized learning roadmap
- Smart scheduler
- To-do list
- Adaptive quizzes
- Flashcards with spaced repetition
- Learning analytics
- Weak-topic detection
- AI recommendations

### Faculty Features
- Faculty dashboard
- Upload study materials
- Course management
- Assignment creation
- Student viewing
- Performance monitoring
- Learning progress tracking

### Administrator Features
- User management
- Role management
- User activation/deactivation
- System statistics
- Document statistics
- AI usage statistics
- Audit logs

## Documentation

- [PROJECT_FEATURES_LOCK.md](./PROJECT_FEATURES_LOCK.md) - Complete feature requirements
- [PROJECT_ARCHITECTURE.md](./PROJECT_ARCHITECTURE.md) - System architecture
- [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md) - Implementation progress

## Contributing

This is a final-year B.Tech project. For questions or suggestions, please contact the development team.

## License

This project is developed for academic purposes.
