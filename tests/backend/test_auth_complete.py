"""
Complete authentication tests for the application.
Tests registration, login, role-based access, and unauthorized access.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash

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


def test_1_registration():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test_new_user@example.com",
            "full_name": "Test New User",
            "password": "testpass123",
            "role": "student"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test_new_user@example.com"
    assert response.json()["role"] == "student"
    print("✓ Test 1: Registration successful")


def test_2_duplicate_registration():
    """Test duplicate email registration fails"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test_new_user@example.com",
            "full_name": "Duplicate User",
            "password": "testpass123",
            "role": "student"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
    print("✓ Test 2: Duplicate registration rejected")


def test_3_login_valid_credentials():
    """Test login with valid credentials"""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "test_login@example.com",
            "full_name": "Test Login User",
            "password": "loginpass123",
            "role": "student"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test_login@example.com",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert response.json()["role"] == "student"
    print("✓ Test 3: Login with valid credentials successful")


def test_4_login_invalid_email():
    """Test login with invalid email"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
    print("✓ Test 4: Login with invalid email rejected")


def test_5_login_invalid_password():
    """Test login with invalid password"""
    # Register a user first
    client.post(
        "/api/auth/register",
        json={
            "email": "test_invalid_pass@example.com",
            "full_name": "Test Invalid Pass",
            "password": "correctpass",
            "role": "student"
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test_invalid_pass@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
    print("✓ Test 5: Login with invalid password rejected")


def test_6_current_user_endpoint():
    """Test /me endpoint with valid token"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "test_me@example.com",
            "full_name": "Test Me User",
            "password": "mepass123",
            "role": "student"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_me@example.com",
            "password": "mepass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access /me endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test_me@example.com"
    print("✓ Test 6: /me endpoint with valid token successful")


def test_7_current_user_no_token():
    """Test /me endpoint without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    print("✓ Test 7: /me endpoint without token rejected")


def test_8_current_user_invalid_token():
    """Test /me endpoint with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    print("✓ Test 8: /me endpoint with invalid token rejected")


def test_9_student_dashboard_access():
    """Test student dashboard access with student role"""
    # Register and login as student
    client.post(
        "/api/auth/register",
        json={
            "email": "test_student_dash@example.com",
            "full_name": "Test Student Dash",
            "password": "studentdash123",
            "role": "student"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_student_dash@example.com",
            "password": "studentdash123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access student dashboard
    response = client.get(
        "/api/students/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Student dashboard" in response.json()["message"]
    print("✓ Test 9: Student dashboard access successful")


def test_10_faculty_dashboard_access():
    """Test faculty dashboard access with faculty role"""
    # Register and login as faculty
    client.post(
        "/api/auth/register",
        json={
            "email": "test_faculty_dash@example.com",
            "full_name": "Test Faculty Dash",
            "password": "facultydash123",
            "role": "faculty"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_faculty_dash@example.com",
            "password": "facultydash123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access faculty dashboard
    response = client.get(
        "/api/faculty/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Faculty dashboard" in response.json()["message"]
    print("✓ Test 10: Faculty dashboard access successful")


def test_11_admin_dashboard_access():
    """Test admin dashboard access with admin role"""
    # Register and login as admin
    client.post(
        "/api/auth/register",
        json={
            "email": "test_admin_dash@example.com",
            "full_name": "Test Admin Dash",
            "password": "admindash123",
            "role": "admin"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_admin_dash@example.com",
            "password": "admindash123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access admin dashboard
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Admin dashboard" in response.json()["message"]
    print("✓ Test 11: Admin dashboard access successful")


def test_12_student_accessing_faculty_dashboard():
    """Test student cannot access faculty dashboard"""
    # Register and login as student
    client.post(
        "/api/auth/register",
        json={
            "email": "test_unauth_student@example.com",
            "full_name": "Test Unauthorized Student",
            "password": "unauth123",
            "role": "student"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_unauth_student@example.com",
            "password": "unauth123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to access faculty dashboard
    response = client.get(
        "/api/faculty/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    print("✓ Test 12: Student accessing faculty dashboard rejected")


def test_13_student_accessing_admin_dashboard():
    """Test student cannot access admin dashboard"""
    # Register and login as student
    client.post(
        "/api/auth/register",
        json={
            "email": "test_unauth_student2@example.com",
            "full_name": "Test Unauthorized Student 2",
            "password": "unauth123",
            "role": "student"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_unauth_student2@example.com",
            "password": "unauth123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to access admin dashboard
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    print("✓ Test 13: Student accessing admin dashboard rejected")


def test_14_faculty_accessing_admin_dashboard():
    """Test faculty cannot access admin dashboard"""
    # Register and login as faculty
    client.post(
        "/api/auth/register",
        json={
            "email": "test_unauth_faculty@example.com",
            "full_name": "Test Unauthorized Faculty",
            "password": "unauth123",
            "role": "faculty"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_unauth_faculty@example.com",
            "password": "unauth123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to access admin dashboard
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    print("✓ Test 14: Faculty accessing admin dashboard rejected")


def test_15_admin_can_access_student_dashboard():
    """Test admin can access student dashboard (admin has all permissions)"""
    # Register and login as admin
    client.post(
        "/api/auth/register",
        json={
            "email": "test_admin_all@example.com",
            "full_name": "Test Admin All",
            "password": "adminall123",
            "role": "admin"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_admin_all@example.com",
            "password": "adminall123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access student dashboard as admin
    response = client.get(
        "/api/students/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    print("✓ Test 15: Admin accessing student dashboard successful")


if __name__ == "__main__":
    print("Running Authentication and Authorization Tests...")
    print("=" * 60)
    
    test_1_registration()
    test_2_duplicate_registration()
    test_3_login_valid_credentials()
    test_4_login_invalid_email()
    test_5_login_invalid_password()
    test_6_current_user_endpoint()
    test_7_current_user_no_token()
    test_8_current_user_invalid_token()
    test_9_student_dashboard_access()
    test_10_faculty_dashboard_access()
    test_11_admin_dashboard_access()
    test_12_student_accessing_faculty_dashboard()
    test_13_student_accessing_admin_dashboard()
    test_14_faculty_accessing_admin_dashboard()
    test_15_admin_can_access_student_dashboard()
    
    print("=" * 60)
    print("All authentication and authorization tests passed!")
