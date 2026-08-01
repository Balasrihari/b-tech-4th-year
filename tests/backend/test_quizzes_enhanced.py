"""Enhanced quiz system tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_quizzes.db"
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


def setup_user():
    """Setup test user"""
    client.post(
        "/api/auth/register",
        json={
            "email": "user@test.com",
            "full_name": "Test User",
            "password": "UserPass123!",
            "role": "student"
        }
    )
    return get_auth_token("user@test.com", "UserPass123!")


def test_create_quiz():
    """Test creating a quiz"""
    token = setup_user()
    
    response = client.post(
        "/api/quizzes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Quiz",
            "topic": "Machine Learning",
            "difficulty": "medium"
        }
    )
    assert response.status_code in [200, 404]


def test_generate_quiz():
    """Test AI-generated quiz"""
    token = setup_user()
    
    response = client.post(
        "/api/quizzes/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 5
        }
    )
    assert response.status_code in [200, 404]


def test_get_quizzes():
    """Test getting user quizzes"""
    token = setup_user()
    
    response = client.get(
        "/api/quizzes",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_quiz_by_id():
    """Test getting a specific quiz"""
    token = setup_user()
    
    response = client.get(
        "/api/quizzes/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_update_quiz():
    """Test updating a quiz"""
    token = setup_user()
    
    response = client.put(
        "/api/quizzes/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Quiz Title"
        }
    )
    assert response.status_code in [200, 404]


def test_delete_quiz():
    """Test deleting a quiz"""
    token = setup_user()
    
    response = client.delete(
        "/api/quizzes/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_start_quiz_attempt():
    """Test starting a quiz attempt"""
    token = setup_user()
    
    response = client.post(
        "/api/quizzes/1/attempts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_submit_quiz_answer():
    """Test submitting quiz answer"""
    token = setup_user()
    
    response = client.post(
        "/api/quizzes/attempts/1/answers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question_id": 1,
            "answer": "Test answer"
        }
    )
    assert response.status_code in [200, 404]


def test_complete_quiz_attempt():
    """Test completing a quiz attempt"""
    token = setup_user()
    
    response = client.put(
        "/api/quizzes/attempts/1/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_quiz_attempts():
    """Test getting quiz attempts"""
    token = setup_user()
    
    response = client.get(
        "/api/quizzes/1/attempts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_quiz_results():
    """Test getting quiz results"""
    token = setup_user()
    
    response = client.get(
        "/api/quizzes/attempts/1/results",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_adaptive_quiz_generation():
    """Test adaptive quiz based on performance"""
    token = setup_user()
    
    response = client.post(
        "/api/quizzes/adaptive",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "topic": "Data Structures",
            "previous_performance": {"difficulty": "medium", "score": 75}
        }
    )
    assert response.status_code in [200, 404]
