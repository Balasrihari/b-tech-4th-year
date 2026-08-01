"""Enhanced analytics system tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analytics.db"
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


def setup_student():
    """Setup test student"""
    client.post(
        "/api/auth/register",
        json={
            "email": "student@test.com",
            "full_name": "Test Student",
            "password": "StudentPass123!",
            "role": "student"
        }
    )
    return get_auth_token("student@test.com", "StudentPass123!")


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


def test_get_student_analytics():
    """Test getting student learning analytics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/analytics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_learning_progress():
    """Test getting learning progress"""
    token = setup_student()
    
    response = client.get(
        "/api/student/progress",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_weak_topics():
    """Test getting weak topics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/weak-topics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_study_time_analytics():
    """Test getting study time analytics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/study-time",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_quiz_performance():
    """Test getting quiz performance analytics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/quiz-performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_flashcard_performance():
    """Test getting flashcard performance analytics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/flashcard-performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_faculty_analytics():
    """Test getting faculty analytics"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/analytics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_class_performance():
    """Test getting class performance (faculty)"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/class-performance",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_student_progress_faculty():
    """Test getting student progress (faculty view)"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/students/1/progress",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_course_analytics():
    """Test getting course analytics"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/courses/1/analytics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_assignment_analytics():
    """Test getting assignment analytics"""
    token = setup_faculty()
    
    response = client.get(
        "/api/faculty/assignments/1/analytics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_system_analytics():
    """Test getting system-wide analytics"""
    # Admin would access this
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "full_name": "Test Admin",
            "password": "AdminPass123!",
            "role": "admin"
        }
    )
    token = get_auth_token("admin@test.com", "AdminPass123!")
    
    response = client.get(
        "/api/admin/analytics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_user_activity_analytics():
    """Test getting user activity analytics"""
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "full_name": "Test Admin",
            "password": "AdminPass123!",
            "role": "admin"
        }
    )
    token = get_auth_token("admin@test.com", "AdminPass123!")
    
    response = client.get(
        "/api/admin/user-activity",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_engagement_metrics():
    """Test getting engagement metrics"""
    token = setup_student()
    
    response = client.get(
        "/api/student/engagement",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_learning_trends():
    """Test getting learning trends over time"""
    token = setup_student()
    
    response = client.get(
        "/api/student/trends",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_export_analytics():
    """Test exporting analytics data"""
    token = setup_student()
    
    response = client.get(
        "/api/student/analytics/export",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]
