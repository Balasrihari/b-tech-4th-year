from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.deps import api_router
from app.db.database import engine, Base
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
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "AI-Powered Smart Student Learning Assistant API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
