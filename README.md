# AI-Powered Smart Student Learning Assistant

A comprehensive full-stack academic project providing AI-powered learning assistance for students, faculty, and administrators.

## 🚀 Quick Start

### Windows Users
Simply double-click `start.bat` to launch both backend and frontend servers automatically!

### Linux/Mac Users
```bash
chmod +x start.sh
./start.sh
```

### Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Project Overview

This B.Tech final-year project implements an intelligent learning platform with:
- **Advanced RAG (Retrieval-Augmented Generation)** system with BM25, vector search, hybrid retrieval, reranking, and context compression
- **Multi-agent AI architecture** using LangChain and LangGraph with specialized agents (Academic, RAG, Coding, Quiz, Study Planner, Analytics)
- **Document processing** for multiple formats (PDF, DOCX, PPTX, XLSX, TXT, Markdown, Images, URLs)
- **Role-based access control** (Student, Faculty, Admin)
- **Learning analytics** and personalized recommendations
- **Real AI integration** with Google Gemini API
- **SQLite database** for easy local development (no PostgreSQL required)

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
- Python 3.12.10
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- SQLite
- LangChain
- LangGraph
- Google Gemini API
- Sentence Transformers
- ChromaDB

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
│   ├── Dockerfile
│   └── vite.config.js
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (RAG, Agents, AI)
│   │   ├── db/             # Database configuration
│   │   └── auth/           # Authentication
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── main.py
├── scripts/               # Development scripts
│   └── generate_demo_data.py
├── start.bat             # Windows startup script
├── start.sh              # Linux/Mac startup script
├── docker-compose.yml    # Docker deployment
├── .env.example          # Environment variables template
└── README.md
```

## Installation

### Prerequisites
- Python 3.12.10
- Node.js 18+
- pip (Python package manager)
- npm (Node package manager)

### Manual Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd 54b1
```

2. **Set up backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

3. **Set up database:**
```bash
alembic upgrade head
python ..\scripts\generate_demo_data.py
```

4. **Set up frontend:**
```bash
cd ../frontend
npm install
```

5. **Start servers:**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Docker Deployment

### Using Docker Compose (Recommended for production)

1. **Build and start containers:**
```bash
docker-compose up --build
```

2. **Access the application:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

3. **Stop containers:**
```bash
docker-compose down
```

## Demo Credentials

After running the demo data generation script, the following users are available:

### Students
- john.doe@student.edu / StudentPass123!
- jane.smith@student.edu / StudentPass123!
- mike.johnson@student.edu / StudentPass123!

### Faculty
- dr.williams@faculty.edu / FacultyPass123!
- prof.brown@faculty.edu / FacultyPass123!

### Admin
- admin@university.edu / AdminPass123!

## AI Features

### Multi-Agent System
The application uses a sophisticated multi-agent architecture with LangGraph:

1. **Supervisor Agent** - Routes requests to appropriate specialized agents
2. **Academic Agent** - General academic questions and concept explanations
3. **RAG Agent** - Document-based question answering with context retrieval
4. **Coding Agent** - Programming help and code explanations
5. **Quiz Agent** - Quiz generation and test preparation
6. **Study Planner Agent** - Personalized study plans and scheduling
7. **Analytics Agent** - Performance analysis and learning insights

### Advanced RAG Pipeline
- Query rewriting and optimization
- BM25 keyword search
- Vector semantic search with embeddings
- Hybrid retrieval combining both methods
- Cross-encoder reranking for relevance
- Context compression for token efficiency
- Automatic citation generation

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
- Personal dashboard with learning analytics
- Document upload and management (PDF, DOCX, PPTX, XLSX, Images, URLs)
- AI-powered Q&A with citations from uploaded documents
- Document summaries and key insights
- Study notes with AI assistance
- AI coding assistant for programming help
- Personalized learning roadmap
- Smart scheduler for study planning
- To-do list management
- Adaptive quizzes with AI-generated questions
- Flashcards with spaced repetition
- Learning analytics and progress tracking
- Weak-topic detection and recommendations
- AI-powered study suggestions

### Faculty Features
- Faculty dashboard with course overview
- Upload and manage study materials
- Course creation and management
- Assignment creation and grading
- Student performance monitoring
- Learning progress tracking
- Analytics dashboard

### Administrator Features
- User management and role assignment
- Role management and permissions
- User activation/deactivation
- System statistics and monitoring
- Document statistics and usage tracking
- AI usage statistics
- Comprehensive audit logs

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./student_learning.db
SECRET_KEY=your-secret-key-change-in-production
GEMINI_API_KEY=your-gemini-api-key
DEBUG=False
ENVIRONMENT=development
```

## Sharing the Project

### Option 1: Git Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repository-url>
git push -u origin main
```

### Option 2: Docker Deployment
Build and share the Docker image:
```bash
docker-compose build
docker tag student-learning-backend <your-username>/student-learning-assistant
docker push <your-username>/student-learning-assistant
```

### Option 3: Direct File Sharing
Share the entire project folder via:
- Google Drive
- Dropbox
- GitHub
- GitLab
- Bitbucket

Users can simply:
1. Download/clone the project
2. Run `start.bat` (Windows) or `./start.sh` (Linux/Mac)
3. Access the application at http://localhost:5173

## Documentation

- [PROJECT_FEATURES_LOCK.md](./PROJECT_FEATURES_LOCK.md) - Complete feature requirements
- [PROJECT_ARCHITECTURE.md](./PROJECT_ARCHITECTURE.md) - System architecture
- [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md) - Implementation progress

## Troubleshooting

### Backend won't start
- Ensure Python 3.12.10 is installed
- Check that virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Ensure Node.js 18+ is installed
- Check that dependencies are installed: `npm install`
- Verify you're in the `frontend` directory

### Database errors
- Delete `student_learning.db` and run migrations again
- Run `alembic upgrade head`
- Run demo data generation: `python ..\scripts\generate_demo_data.py`

### AI features not working
- Ensure `GEMINI_API_KEY` is set in `.env` file
- Check that AI dependencies are installed
- Verify internet connection for API calls

## Contributing

This is a final-year B.Tech project. For questions or suggestions, please contact the development team.

## License

This project is developed for academic purposes.
