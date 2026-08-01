import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.core.security import validate_password_strength, get_password_hash, verify_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPass123!",
            "role": "student"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_register_duplicate_user():
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "full_name": "Duplicate User",
            "password": "TestPass123!",
            "role": "student"
        }
    )
    
    # Try to register same user again
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "full_name": "Duplicate User",
            "password": "TestPass123!",
            "role": "student"
        }
    )
    assert response.status_code == 400


def test_register_weak_password():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "full_name": "Weak User",
            "password": "weak",  # Too short and no complexity
            "role": "student"
        }
    )
    assert response.status_code == 400


def test_login_user():
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "full_name": "Login User",
            "password": "LoginPass123!",
            "role": "student"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "LoginPass123!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "currentuser@example.com",
            "full_name": "Current User",
            "password": "CurrentPass123!",
            "role": "student"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "currentuser@example.com",
            "password": "CurrentPass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "currentuser@example.com"


def test_password_validation():
    # Test valid password
    is_valid, message = validate_password_strength("TestPass123!")
    assert is_valid is True
    
    # Test too short
    is_valid, message = validate_password_strength("Test1!")
    assert is_valid is False
    
    # Test no uppercase
    is_valid, message = validate_password_strength("testpass123!")
    assert is_valid is False
    
    # Test no digit
    is_valid, message = validate_password_strength("TestPass!")
    assert is_valid is False
    
    # Test no special character
    is_valid, message = validate_password_strength("TestPass123")
    assert is_valid is False


def test_password_hashing():
    password = "TestPass123!"
    hashed = get_password_hash(password)
    
    # Verify hash is different from original
    assert hashed != password
    
    # Verify hash can be verified
    assert verify_password(password, hashed) is True
    
    # Verify wrong password fails
    assert verify_password("WrongPass123!", hashed) is False


def test_role_registration():
    # Test student registration
    response = client.post(
        "/api/auth/register",
        json={
            "email": "student@example.com",
            "full_name": "Student User",
            "password": "StudentPass123!",
            "role": "student"
        }
    )
    assert response.status_code == 200
    assert response.json()["role"] == "student"
    
    # Test faculty registration
    response = client.post(
        "/api/auth/register",
        json={
            "email": "faculty@example.com",
            "full_name": "Faculty User",
            "password": "FacultyPass123!",
            "role": "faculty"
        }
    )
    assert response.status_code == 200
    assert response.json()["role"] == "faculty"
    
    # Test admin registration
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": "AdminPass123!",
            "role": "admin"
        }
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
