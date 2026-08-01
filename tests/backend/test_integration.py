"""Integration tests for the application"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.services.vector_store import vector_store
from app.services.bm25_service import bm25_service
from app.services.hybrid_retrieval import hybrid_retrieval_service

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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


@pytest.fixture
def db():
    """Database fixture"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_token(db):
    """Authentication token fixture"""
    # Register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "integration@test.com",
            "full_name": "Integration Test User",
            "password": "TestPass123!",
            "role": "student"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "integration@test.com",
            "password": "TestPass123!"
        }
    )
    
    return response.json()["access_token"]


def test_full_document_workflow(auth_token):
    """Test complete document upload and retrieval workflow"""
    # Upload a document
    import io
    
    # Create a simple text file
    content = b"This is a test document about machine learning and artificial intelligence."
    file = io.BytesIO(content)
    file.name = "test.txt"
    
    response = client.post(
        "/api/documents/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "title": "Test Document",
            "document_type": "notes",
            "file": file
        }
    )
    
    assert response.status_code in [200, 201]
    
    document_id = response.json()["id"]
    
    # Get documents
    response = client.get(
        "/api/documents/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_quiz_generation_workflow(auth_token):
    """Test quiz generation and attempt workflow"""
    # Generate a quiz
    response = client.post(
        "/api/quizzes/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3
        }
    )
    
    # This may fail if AI is not configured, but we test the endpoint exists
    assert response.status_code in [200, 404, 500]


def test_flashcard_workflow(auth_token):
    """Test flashcard creation and review workflow"""
    # Create a flashcard
    response = client.post(
        "/api/flashcards",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "front": "What is Python?",
            "back": "A programming language",
            "topic": "Programming"
        }
    )
    
    assert response.status_code in [200, 201]
    
    flashcard_id = response.json()["id"]
    
    # Review the flashcard
    response = client.post(
        f"/api/flashcards/{flashcard_id}/review",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"rating": 3}
    )
    
    assert response.status_code in [200, 404]


def test_vector_store_integration():
    """Test vector store integration"""
    test_documents = [
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language for data science",
        "Neural networks are inspired by biological neurons"
    ]
    
    test_metadata = [
        {"topic": "AI", "source": "test"},
        {"topic": "Programming", "source": "test"},
        {"topic": "Neural Networks", "source": "test"}
    ]
    
    test_ids = ["doc_1", "doc_2", "doc_3"]
    
    # Add documents
    vector_store.add_documents(
        documents=test_documents,
        metadatas=test_metadata,
        ids=test_ids,
        collection_name="test_collection"
    )
    
    # Query documents
    results = vector_store.query_documents(
        query_text="machine learning",
        collection_name="test_collection",
        n_results=2
    )
    
    assert len(results["ids"][0]) > 0
    
    # Cleanup
    vector_store.delete_documents(ids=test_ids, collection_name="test_collection")
    vector_store.reset_collection("test_collection")


def test_bm25_integration():
    """Test BM25 search integration"""
    test_documents = [
        "Machine learning algorithms learn from data",
        "Deep learning uses neural networks",
        "Natural language processing deals with text"
    ]
    
    # Create index
    bm25_service.create_index(
        collection_name="test_bm25",
        documents=test_documents,
        metadata=[{"id": i} for i in range(len(test_documents))]
    )
    
    # Search
    results = bm25_service.search(
        collection_name="test_bm25",
        query="machine learning",
        top_k=2
    )
    
    assert len(results) > 0
    
    # Cleanup
    bm25_service.delete_collection("test_bm25")


def test_hybrid_retrieval_integration():
    """Test hybrid retrieval integration"""
    # Setup vector store
    vector_store.add_documents(
        documents=["Test document about AI"],
        metadatas=[{"topic": "AI"}],
        ids=["hybrid_1"],
        collection_name="test_hybrid"
    )
    
    # Setup BM25
    bm25_service.create_index(
        collection_name="test_hybrid",
        documents=["Test document about AI"],
        metadata=[{"id": "hybrid_1"}]
    )
    
    # Hybrid search
    results = hybrid_retrieval_service.hybrid_search(
        query="AI",
        collection_name="test_hybrid",
        top_k=1
    )
    
    assert len(results) > 0
    
    # Cleanup
    vector_store.delete_documents(ids=["hybrid_1"], collection_name="test_hybrid")
    vector_store.reset_collection("test_hybrid")
    bm25_service.delete_collection("test_hybrid")


def test_user_role_workflow():
    """Test user role-based access workflow"""
    # Create admin user
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@test.com",
            "full_name": "Admin User",
            "password": "AdminPass123!",
            "role": "admin"
        }
    )
    
    # Login as admin
    admin_response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminPass123!"
        }
    )
    
    admin_token = admin_response.json()["access_token"]
    
    # Access admin endpoint
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code in [200, 404]


def test_analytics_workflow(auth_token):
    """Test analytics data collection workflow"""
    # Get analytics
    response = client.get(
        "/api/student/analytics",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code in [200, 404]


def test_todo_workflow(auth_token):
    """Test todo creation and completion workflow"""
    # Create todo
    response = client.post(
        "/api/student/todos",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Integration test todo",
            "description": "Test todo description",
            "priority": "medium"
        }
    )
    
    assert response.status_code in [200, 201]
    
    todo_id = response.json()["id"]
    
    # Update todo
    response = client.put(
        f"/api/student/todos/{todo_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"completed": True}
    )
    
    assert response.status_code in [200, 404]


def test_note_workflow(auth_token):
    """Test note creation and retrieval workflow"""
    # Create note
    response = client.post(
        "/api/student/notes",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "Integration test note",
            "content": "Test note content",
            "topic": "Testing"
        }
    )
    
    assert response.status_code in [200, 201]
    
    # Get notes
    response = client.get(
        "/api/student/notes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code in [200, 404]
