from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.deps import api_router
from app.db.database import engine, Base
from app.core.exceptions import AppException
# Import all models to ensure they're registered with SQLAlchemy
from app.models import (
    User, Role, Course, Document, DocumentChunk,
    Assignment, AssignmentSubmission, Todo, Quiz, QuizQuestion,
    QuizAttempt, Flashcard, FlashcardReview, Enrollment,
    LearningProgress, WeakTopic, Analytics, Notification, AuditLog, Note
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="AI-Powered Smart Student Learning Assistant API with comprehensive learning features including quizzes, flashcards, analytics, and AI-powered assistance."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


# Custom exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "type": "app_error"
        },
    )


@app.get("/")
def root():
    return {
        "message": "AI-Powered Smart Student Learning Assistant API",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
