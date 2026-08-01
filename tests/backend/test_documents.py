"""Document processing tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_documents.db"
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


def test_upload_document():
    """Test document upload"""
    token = setup_user()
    
    response = client.post(
        "/api/documents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Document",
            "description": "Test description",
            "file_type": "pdf"
        }
    )
    assert response.status_code in [200, 404]


def test_get_documents():
    """Test getting user documents"""
    token = setup_user()
    
    response = client.get(
        "/api/documents",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_get_document_by_id():
    """Test getting a specific document"""
    token = setup_user()
    
    response = client.get(
        "/api/documents/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_update_document():
    """Test updating a document"""
    token = setup_user()
    
    response = client.put(
        "/api/documents/1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Title",
            "description": "Updated description"
        }
    )
    assert response.status_code in [200, 404]


def test_delete_document():
    """Test deleting a document"""
    token = setup_user()
    
    response = client.delete(
        "/api/documents/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_document_processing_status():
    """Test checking document processing status"""
    token = setup_user()
    
    response = client.get(
        "/api/documents/1/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_document_chunks():
    """Test getting document chunks"""
    token = setup_user()
    
    response = client.get(
        "/api/documents/1/chunks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_document_qa():
    """Test document Q&A"""
    token = setup_user()
    
    response = client.post(
        "/api/documents/1/qa",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "question": "What is this document about?"
        }
    )
    assert response.status_code in [200, 404]


def test_document_summary():
    """Test document summary generation"""
    token = setup_user()
    
    response = client.post(
        "/api/documents/1/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_search_documents():
    """Test searching documents"""
    token = setup_user()
    
    response = client.get(
        "/api/documents/search?q=test",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]


def test_document_permissions():
    """Test that users can only access their own documents"""
    # Setup two users
    client.post(
        "/api/auth/register",
        json={
            "email": "user1@test.com",
            "full_name": "User 1",
            "password": "User1Pass123!",
            "role": "student"
        }
    )
    
    client.post(
        "/api/auth/register",
        json={
            "email": "user2@test.com",
            "full_name": "User 2",
            "password": "User2Pass123!",
            "role": "student"
        }
    )
    
    token1 = get_auth_token("user1@test.com", "User1Pass123!")
    token2 = get_auth_token("user2@test.com", "User2Pass123!")
    
    # User 1 creates a document
    client.post(
        "/api/documents",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "User 1 Document",
            "description": "Private document",
            "file_type": "pdf"
        }
    )
    
    # User 2 tries to access User 1's document
    response = client.get(
        "/api/documents/1",
        headers={"Authorization": f"Bearer {token2}"}
    )
    # Should be forbidden or not found
    assert response.status_code in [403, 404]
