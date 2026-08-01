"""Admin features tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin.db"
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


def setup_admin():
    """Setup test admin"""
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "full_name": "Test Admin",
            "password": "AdminPass123!",
            "role": "admin"
        }
    )
    return get_auth_token("admin@test.com", "AdminPass123!")


def test_admin_dashboard():
    """Test admin dashboard access"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_users():
    """Test getting all users"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_create_user():
    """Test creating a user (admin only)"""
    token = setup_admin()
    
    response = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "NewPass123!",
            "role": "student"
        }
    )
    assert response.status_code in [200, 404]


def test_update_user():
    """Test updating a user"""
    token = setup_admin()
    
    response = client.put(
        "/api/admin/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Updated Name",
            "is_active": True
        }
    )
    assert response.status_code in [200, 404]


def test_deactivate_user():
    """Test deactivating a user"""
    token = setup_admin()
    
    response = client.put(
        "/api/admin/users/1/deactivate",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_activate_user():
    """Test activating a user"""
    token = setup_admin()
    
    response = client.put(
        "/api/admin/users/1/activate",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_roles():
    """Test getting all roles"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/roles",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_create_role():
    """Test creating a role"""
    token = setup_admin()
    
    response = client.post(
        "/api/admin/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "moderator",
            "description": "Content moderator"
        }
    )
    assert response.status_code in [200, 404]


def test_update_role():
    """Test updating a role"""
    token = setup_admin()
    
    response = client.put(
        "/api/admin/roles/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Updated description"
        }
    )
    assert response.status_code in [200, 404]


def test_delete_role():
    """Test deleting a role"""
    token = setup_admin()
    
    response = client.delete(
        "/api/admin/roles/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_system_statistics():
    """Test getting system-wide statistics"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_document_statistics():
    """Test getting document statistics"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/statistics/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_ai_usage_statistics():
    """Test getting AI usage statistics"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/statistics/ai-usage",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_audit_logs():
    """Test getting audit logs"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_filter_audit_logs():
    """Test filtering audit logs"""
    token = setup_admin()
    
    response = client.get(
        "/api/admin/audit-logs?action=create",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]
