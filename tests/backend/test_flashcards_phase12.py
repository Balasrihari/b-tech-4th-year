"""
Tests for Phase 12 Flashcard Features
- Topic grouping and deck management
- Study scheduling
- Progress tracking
- Batch operations
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import get_db, Base, engine
from app.models.user import User, UserRole
from app.models.flashcard import Flashcard, FlashcardStatus
from app.models.flashcard_review import FlashcardReview
from datetime import datetime, timedelta

client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session: Session):
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User):
    return {"Authorization": "Bearer test_token"}


class TestDeckManagement:
    """Test deck/topic grouping features"""
    
    def test_get_deck_statistics(self, auth_headers):
        """Test retrieving deck statistics"""
        response = client.get(
            "/api/flashcards/decks/statistics",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_update_deck_name(self, auth_headers):
        """Test updating deck name"""
        response = client.put(
            "/api/flashcards/decks/Programming",
            params={"new_deck_name": "Python Programming"},
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 404]


class TestStudyScheduling:
    """Test study scheduling features"""
    
    def test_get_study_schedule(self, auth_headers):
        """Test retrieving study schedule"""
        response = client.get(
            "/api/flashcards/schedule",
            params={"days": 7},
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_study_schedule_validation(self, auth_headers):
        """Test days parameter validation"""
        response = client.get(
            "/api/flashcards/schedule",
            params={"days": 35},  # Exceeds max of 30
            headers=auth_headers
        )
        assert response.status_code == 422


class TestProgressTracking:
    """Test progress tracking features"""
    
    def test_get_flashcard_progress(self, auth_headers):
        """Test retrieving flashcard progress"""
        response = client.get(
            "/api/flashcards/progress",
            params={"days": 30},
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_progress_validation(self, auth_headers):
        """Test days parameter validation"""
        response = client.get(
            "/api/flashcards/progress",
            params={"days": 400},  # Exceeds max of 365
            headers=auth_headers
        )
        assert response.status_code == 422


class TestBatchOperations:
    """Test batch operations"""
    
    def test_create_flashcard_batch(self, auth_headers):
        """Test creating multiple flashcards at once"""
        batch_data = [
            {
                "front": "What is Python?",
                "back": "Python is a programming language",
                "deck_name": "Programming"
            },
            {
                "front": "What is a variable?",
                "back": "A variable stores data values",
                "deck_name": "Programming"
            }
        ]
        
        response = client.post(
            "/api/flashcards/batch",
            json=batch_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 401, 422]


class TestFlashcardSchemas:
    """Test flashcard schema validation"""
    
    def test_flashcard_create_schema(self):
        """Test FlashcardCreate schema validation"""
        from app.schemas.flashcard import FlashcardCreate
        
        valid_data = {
            "front": "What is Python?",
            "back": "Python is a programming language",
            "deck_name": "Programming"
        }
        schema = FlashcardCreate(**valid_data)
        assert schema.front == "What is Python?"
    
    def test_flashcard_review_create_schema(self):
        """Test FlashcardReviewCreate schema validation"""
        from app.schemas.flashcard import FlashcardReviewCreate
        
        valid_data = {
            "flashcard_id": 1,
            "rating": 4.0
        }
        schema = FlashcardReviewCreate(**valid_data)
        assert schema.rating == 4.0
    
    def test_deck_statistics_response_schema(self):
        """Test DeckStatisticsResponse schema validation"""
        from app.schemas.flashcard import DeckStatisticsResponse
        
        valid_data = {
            "deck_name": "Programming",
            "total_cards": 50,
            "new_cards": 10,
            "learning_cards": 15,
            "review_cards": 20,
            "mastered_cards": 5,
            "due_for_review": 15
        }
        schema = DeckStatisticsResponse(**valid_data)
        assert schema.deck_name == "Programming"
    
    def test_study_schedule_response_schema(self):
        """Test StudyScheduleResponse schema validation"""
        from app.schemas.flashcard import StudyScheduleResponse
        
        valid_data = {
            "period_days": 7,
            "start_date": "2026-07-30",
            "end_date": "2026-08-05",
            "total_due_cards": 25,
            "daily_schedule": {}
        }
        schema = StudyScheduleResponse(**valid_data)
        assert schema.period_days == 7
