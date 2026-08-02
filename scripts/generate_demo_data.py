"""
Demo Database Generator for AI-Powered Smart Student Learning Assistant

This script generates sample data for testing and demonstration purposes.
Run with: python scripts/generate_demo_data.py
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.database import Base, get_db
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.assignment import Assignment
from app.models.assignment_submission import AssignmentSubmission
from app.models.todo import Todo
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt
from app.models.flashcard import Flashcard
from app.models.flashcard_review import FlashcardReview
from app.models.enrollment import Enrollment
from app.models.learning_progress import LearningProgress
from app.models.note import Note
from app.models.analytics import Analytics

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./student_learning.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def create_demo_users(db):
    """Create demo users for all roles"""
    print("Creating demo users...")
    
    users = [
        # Students
        User(
            email="john.doe@student.edu",
            full_name="John Doe",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",  # StudentPass123!
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            email="jane.smith@student.edu",
            full_name="Jane Smith",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",
            role=UserRole.STUDENT,
            is_active=True
        ),
        User(
            email="mike.johnson@student.edu",
            full_name="Mike Johnson",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",
            role=UserRole.STUDENT,
            is_active=True
        ),
        # Faculty
        User(
            email="dr.williams@faculty.edu",
            full_name="Dr. Sarah Williams",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",  # FacultyPass123!
            role=UserRole.FACULTY,
            is_active=True
        ),
        User(
            email="prof.brown@faculty.edu",
            full_name="Prof. James Brown",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",
            role=UserRole.FACULTY,
            is_active=True
        ),
        # Admin
        User(
            email="admin@university.edu",
            full_name="System Administrator",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY1qY1qY1qY",  # AdminPass123!
            role=UserRole.ADMIN,
            is_active=True
        ),
    ]
    
    db.add_all(users)
    db.commit()
    print(f"Created {len(users)} demo users")
    return users


def create_demo_courses(db, faculty_users):
    """Create demo courses"""
    print("Creating demo courses...")
    
    courses = [
        Course(
            title="Introduction to Machine Learning",
            code="CS401",
            description="Fundamental concepts of machine learning algorithms",
            faculty_id=faculty_users[0].id
        ),
        Course(
            title="Data Structures and Algorithms",
            code="CS201",
            description="Core computer science concepts",
            faculty_id=faculty_users[0].id
        ),
        Course(
            title="Web Development",
            code="CS301",
            description="Modern web application development",
            faculty_id=faculty_users[1].id
        ),
        Course(
            title="Database Systems",
            code="CS302",
            description="Database design and management",
            faculty_id=faculty_users[1].id
        ),
    ]
    
    db.add_all(courses)
    db.commit()
    print(f"Created {len(courses)} demo courses")
    return courses


def create_demo_enrollments(db, student_users, courses):
    """Create demo enrollments"""
    print("Creating demo enrollments...")
    
    enrollments = []
    for student in student_users:
        for course in courses[:2]:  # Each student enrolled in 2 courses
            enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id
            )
            enrollments.append(enrollment)
    
    db.add_all(enrollments)
    db.commit()
    print(f"Created {len(enrollments)} demo enrollments")
    return enrollments


def create_demo_documents(db, users, courses):
    """Create demo documents"""
    print("Creating demo documents...")
    
    documents = [
        Document(
            title="Machine Learning Basics",
            document_type="pdf",
            file_size=1024000,
            page_count=20,
            uploaded_by=users[3].id,  # Faculty
            course_id=courses[0].id
        ),
        Document(
            title="Data Structures Notes",
            document_type="pdf",
            file_size=2048000,
            page_count=40,
            uploaded_by=users[3].id,
            course_id=courses[1].id
        ),
        Document(
            title="React Tutorial",
            document_type="pdf",
            file_size=1536000,
            page_count=30,
            uploaded_by=users[4].id,
            course_id=courses[2].id
        ),
    ]
    
    db.add_all(documents)
    db.commit()
    
    # Create document chunks
    chunks = []
    for doc in documents:
        for i in range(5):
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=f"Sample content chunk {i+1} for document {doc.title}"
            )
            chunks.append(chunk)
    
    db.add_all(chunks)
    db.commit()
    print(f"Created {len(documents)} demo documents and {len(chunks)} chunks")
    return documents


def create_demo_assignments(db, faculty_users, courses):
    """Create demo assignments"""
    print("Creating demo assignments...")
    
    assignments = [
        Assignment(
            title="ML Project 1",
            description="Implement a simple classifier",
            course_id=courses[0].id,
            faculty_id=faculty_users[0].id,
            due_date=datetime.now() + timedelta(days=7),
            max_score=100
        ),
        Assignment(
            title="DSA Homework",
            description="Solve algorithm problems",
            course_id=courses[1].id,
            faculty_id=faculty_users[0].id,
            due_date=datetime.now() + timedelta(days=5),
            max_score=50
        ),
        Assignment(
            title="Web App Project",
            description="Build a full-stack application",
            course_id=courses[2].id,
            faculty_id=faculty_users[1].id,
            due_date=datetime.now() + timedelta(days=14),
            max_score=100
        ),
    ]
    
    db.add_all(assignments)
    db.commit()
    print(f"Created {len(assignments)} demo assignments")
    return assignments


def create_demo_quizzes(db, student_users):
    """Create demo quizzes"""
    print("Creating demo quizzes...")
    
    quizzes = [
        Quiz(
            title="Machine Learning Quiz",
            description="Test your ML knowledge",
            difficulty="medium",
            created_by=student_users[0].id
        ),
        Quiz(
            title="Data Structures Quiz",
            description="Test your DSA knowledge",
            difficulty="hard",
            created_by=student_users[0].id
        ),
    ]
    
    db.add_all(quizzes)
    db.commit()
    
    # Create quiz questions
    questions = []
    for quiz in quizzes:
        for i in range(5):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=f"Question {i+1} for {quiz.title}",
                question_type="multiple_choice",
                options='["Option A", "Option B", "Option C", "Option D"]',
                correct_answer="Option A",
                points=10
            )
            questions.append(question)
    
    db.add_all(questions)
    db.commit()
    
    # Create quiz attempts
    attempts = []
    for student in student_users:
        for quiz in quizzes:
            attempt = QuizAttempt(
                quiz_id=quiz.id,
                student_id=student.id,
                score=random.randint(30, 90),
                completed_at=datetime.now() - timedelta(days=random.randint(1, 10))
            )
            attempts.append(attempt)
    
    db.add_all(attempts)
    db.commit()
    print(f"Created {len(quizzes)} quizzes, {len(questions)} questions, and {len(attempts)} attempts")
    return quizzes


def create_demo_flashcards(db, student_users):
    """Create demo flashcards"""
    print("Creating demo flashcards...")
    
    flashcards = []
    for student in student_users:
        for i in range(10):
            flashcard = Flashcard(
                user_id=student.id,
                front=f"Question {i+1}",
                back=f"Answer {i+1}"
            )
            flashcards.append(flashcard)
    
    db.add_all(flashcards)
    db.commit()
    
    # Create flashcard reviews
    reviews = []
    for flashcard in flashcards[:5]:
        review = FlashcardReview(
            flashcard_id=flashcard.id,
            user_id=flashcard.user_id,
            rating=random.randint(1, 5)
        )
        reviews.append(review)
    
    db.add_all(reviews)
    db.commit()
    print(f"Created {len(flashcards)} flashcards and {len(reviews)} reviews")
    return flashcards


def create_demo_todos(db, student_users):
    """Create demo todos"""
    print("Creating demo todos...")
    
    todos = []
    for student in student_users:
        for i in range(5):
            todo = Todo(
                user_id=student.id,
                title=f"Task {i+1}",
                description=f"Description for task {i+1}",
                due_date=datetime.now() + timedelta(days=random.randint(1, 14)),
                priority=random.choice(["low", "medium", "high"])
            )
            todos.append(todo)
    
    db.add_all(todos)
    db.commit()
    print(f"Created {len(todos)} demo todos")
    return todos


def create_demo_notes(db, student_users):
    """Create demo notes"""
    print("Creating demo notes...")
    
    notes = []
    for student in student_users:
        for i in range(3):
            note = Note(
                user_id=student.id,
                title=f"Note {i+1}",
                content=f"Content for note {i+1}"
            )
            notes.append(note)
    
    db.add_all(notes)
    db.commit()
    print(f"Created {len(notes)} demo notes")
    return notes


def create_demo_analytics(db, student_users):
    """Create demo analytics"""
    print("Creating demo analytics...")
    
    analytics = []
    for student in student_users:
        analytics_data = Analytics(
            user_id=student.id,
            metric_name="study_time",
            metric_value=random.randint(100, 500)
        )
        analytics.append(analytics_data)
    
    db.add_all(analytics)
    db.commit()
    print(f"Created {len(analytics)} demo analytics records")
    return analytics


def create_demo_learning_progress(db, student_users, courses):
    """Create demo learning progress"""
    print("Creating demo learning progress...")
    
    progress = []
    for student in student_users:
        for course in courses[:2]:
            lp = LearningProgress(
                user_id=student.id,
                course_id=course.id,
                topic="General",
                mastery_level=random.random(),
                time_spent_minutes=random.randint(10, 100)
            )
            progress.append(lp)
    
    db.add_all(progress)
    db.commit()
    print(f"Created {len(progress)} demo learning progress records")
    return progress


def main():
    """Main function to generate all demo data"""
    print("=" * 60)
    print("Demo Database Generator")
    print("=" * 60)
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Generate all demo data
        users = create_demo_users(db)
        
        faculty_users = [u for u in users if u.role == UserRole.FACULTY]
        student_users = [u for u in users if u.role == UserRole.STUDENT]
        
        courses = create_demo_courses(db, faculty_users)
        create_demo_enrollments(db, student_users, courses)
        create_demo_documents(db, users, courses)
        create_demo_assignments(db, faculty_users, courses)
        create_demo_quizzes(db, student_users)
        create_demo_flashcards(db, student_users)
        create_demo_todos(db, student_users)
        create_demo_notes(db, student_users)
        create_demo_analytics(db, student_users)
        create_demo_learning_progress(db, student_users, courses)
        
        print("\n" + "=" * 60)
        print("Demo data generation completed successfully!")
        print("=" * 60)
        print("\nDemo credentials:")
        print("Students:")
        print("  - john.doe@student.edu / StudentPass123!")
        print("  - jane.smith@student.edu / StudentPass123!")
        print("  - mike.johnson@student.edu / StudentPass123!")
        print("\nFaculty:")
        print("  - dr.williams@faculty.edu / FacultyPass123!")
        print("  - prof.brown@faculty.edu / FacultyPass123!")
        print("\nAdmin:")
        print("  - admin@university.edu / AdminPass123!")
        
    except Exception as e:
        print(f"\nError generating demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import random
    main()
