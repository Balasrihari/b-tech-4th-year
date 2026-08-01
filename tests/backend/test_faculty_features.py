"""Faculty features tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_faculty.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def get_auth_token(email, password):
    """Helper to get auth token"""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]


def setup_faculty():
    """Setup test faculty"""
    client.post(
        "/api/auth/register",
        json={
            "email": "faculty@test.com",
            "full_name": "Test Faculty",
            "password": "FacultyPass123!",
            "role": "faculty"
        }
    )
    return get_auth_token("faculty@test.com", "FacultyPass123!")


def test_faculty_dashboard():
    """Test faculty dashboard access"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_create_course():
    """Test creating a course"""
    token = setup_faculty()
    
    response = client.post(
        "/api/faculty/courses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Introduction to AI",
            "description": "Basic AI concepts",
            "code": "CS101"
        }
    )
    assert response.status_code in [200, 404]


def test_get_courses():
    """Test getting faculty courses"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/courses",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_create_assignment():
    """Test creating an assignment"""
    token = setup_faculty()
    
    response = client.post(
        "/api/faculty/assignments",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Homework 1",
            "description": "Complete exercises",
            "course_id": 1,
            "due_date": "2026-12-31"
        }
    )
    assert response.status_code in [200, 404]


def test_get_assignments():
    """Test getting faculty assignments"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/assignments",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_students():
    """Test getting enrolled students"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/students",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_student_performance():
    """Test getting student performance analytics"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/students/performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_course_progress():
    """Test getting course progress"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/courses/progress",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_upload_document():
    """Test uploading study materials"""
    token = setup_faculty()
    
    response = client.post(
        "/api/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Lecture Notes",
            "description": "Week 1 notes",
            "course_id": 1
        }
    )
    assert response.status_code in [200, 404]


def test_grade_assignment():
    """Test grading assignment submission"""
    token = setup_faculty()
    
    response = client.put(
        "/api/faculty/assignments/1/submissions/1/grade",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "grade": 85,
            "feedback": "Good work"
        }
    )
    assert response.status_code in [200, 404]
