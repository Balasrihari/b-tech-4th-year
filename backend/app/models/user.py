from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    courses_taught = relationship("Course", back_populates="faculty")
    uploaded_documents = relationship("Document", back_populates="uploader")
    assignments_created = relationship("Assignment", back_populates="faculty")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student")
    todos = relationship("Todo", back_populates="user")
    quizzes_created = relationship("Quiz", back_populates="creator")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    flashcards = relationship("Flashcard", back_populates="user")
    flashcard_reviews = relationship("FlashcardReview", back_populates="user")
    enrollments = relationship("Enrollment", back_populates="student")
    learning_progress = relationship("LearningProgress", back_populates="user")
    weak_topics = relationship("WeakTopic", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    notes = relationship("Note", back_populates="user")
