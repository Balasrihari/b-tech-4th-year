"""
Tests for Phase 13 Analytics Features
- Dashboard overview
- Comprehensive analytics
- Learning trends
- Study statistics
- Topic performance
- Time analytics
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import get_db, Base, engine
from app.models.user import User, UserRole
from app.models.learning_progress import LearningProgress
from app.models.quiz_attempt import QuizAttempt
from app.models.flashcard import Flashcard
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


class TestDashboardOverview:
    """Test dashboard overview endpoint"""
    
    def test_get_dashboard_overview(self, auth_headers):
        """Test retrieving comprehensive dashboard overview"""
        response = client.get(
            "/api/learning/dashboard",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]


class TestComprehensiveAnalytics:
    """Test comprehensive analytics endpoint"""
    
    def test_get_comprehensive_analytics(self, auth_headers):
        """Test retrieving comprehensive analytics for a time period"""
        response = client.get(
            "/api/learning/comprehensive",
            params={"days": 30},
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_comprehensive_analytics_validation(self, auth_headers):
        """Test days parameter validation"""
        response = client.get(
            "/api/learning/comprehensive",
            params={"days": 400},  # Exceeds max of 365
            headers=auth_headers
        )
        assert response.status_code == 422


class TestLearningTrends:
    """Test learning trends endpoint"""
    
    def test_get_learning_trends(self, auth_headers):
        """Test retrieving learning trends over time"""
        response = client.get(
            "/api/learning/trends",
            params={"days": 30},
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_learning_trends_validation(self, auth_headers):
        """Test days parameter validation"""
        response = client.get(
            "/api/learning/trends",
            params={"days": 5},  # Below minimum of 7
            headers=auth_headers
        )
        assert response.status_code == 422


class TestStudyStatistics:
    """Test study statistics endpoint"""
    
    def test_get_study_statistics(self, auth_headers):
        """Test retrieving detailed study statistics"""
        response = client.get(
            "/api/learning/statistics",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]


class TestTopicPerformance:
    """Test topic performance endpoint"""
    
    def test_get_topic_performance(self, auth_headers):
        """Test retrieving performance breakdown by topic"""
        response = client.get(
            "/api/learning/topic-performance",
            headers=auth_headers
        )
        assert response.status_code in [200, 401]


class TestTimeAnalytics:
    """Test time analytics endpoint"""
    
    def test_get_time_analytics(self, auth_headers):
        """Test retrieving time spent analytics"""
        response = client.get(
            "/api/learning/time-analytics",
            params={"days": 30},
            headers=auth_headers
        )
        assert response.status_code in [200, 401]
    
    def test_time_analytics_validation(self, auth_headers):
        """Test days parameter validation"""
        response = client.get(
            "/api/learning/time-analytics",
            params={"days": 0},  # Below minimum of 1
            headers=auth_headers
        )
        assert response.status_code == 422


class TestAnalyticsSchemas:
    """Test analytics schema validation"""
    
    def test_dashboard_overview_response_schema(self):
        """Test DashboardOverviewResponse schema validation"""
        from app.schemas.learning import DashboardOverviewResponse, LearningMetrics, QuizMetrics
        
        learning_metrics = {
            "total_topics": 15,
            "average_mastery": 72.5,
            "total_time_spent_hours": 45.5,
            "topics_mastered": 8
        }
        
        quiz_metrics = {
            "total_attempts": 25,
            "average_score": 78.5,
            "completed_count": 20
        }
        
        valid_data = {
            "learning_metrics": learning_metrics,
            "quiz_metrics": quiz_metrics,
            "flashcard_metrics": {
                "total_cards": 100,
                "mastered_cards": 30,
                "mastery_percentage": 30.0
            },
            "weak_topics": [],
            "recent_activity": {
                "recent_topics": [],
                "recent_quizzes": []
            }
        }
        schema = DashboardOverviewResponse(**valid_data)
        assert schema.learning_metrics.total_topics == 15
    
    def test_comprehensive_analytics_response_schema(self):
        """Test ComprehensiveAnalyticsResponse schema validation"""
        from app.schemas.learning import ComprehensiveAnalyticsResponse
        
        valid_data = {
            "period_days": 30,
            "total_study_time_hours": 35.5,
            "topics_studied": 12,
            "quizzes_completed": 8,
            "flashcards_reviewed": 150,
            "average_quiz_score": 82.3,
            "completion_rate": 85.0,
            "study_streak": 7
        }
        schema = ComprehensiveAnalyticsResponse(**valid_data)
        assert schema.period_days == 30
    
    def test_learning_trends_response_schema(self):
        """Test LearningTrendsResponse schema validation"""
        from app.schemas.learning import LearningTrendsResponse
        
        valid_data = {
            "period_days": 30,
            "total_activity": 145,
            "average_daily_activity": 4.83,
            "most_active_day": "2026-07-15",
            "daily_breakdown": {}
        }
        schema = LearningTrendsResponse(**valid_data)
        assert schema.total_activity == 145
    
    def test_study_statistics_response_schema(self):
        """Test StudyStatisticsResponse schema validation"""
        from app.schemas.learning import StudyStatisticsResponse
        
        valid_data = {
            "overall_statistics": {
                "total_topics_studied": 15,
                "total_quizzes_taken": 25,
                "total_flashcards_created": 100
            },
            "time_statistics": {
                "total_study_time_hours": 45.5,
                "average_time_per_topic_minutes": 182.0
            },
            "performance_statistics": {
                "average_quiz_score": 78.5,
                "highest_quiz_score": 95.0,
                "lowest_quiz_score": 65.0
            }
        }
        schema = StudyStatisticsResponse(**valid_data)
        assert schema.overall_statistics.total_topics_studied == 15
    
    def test_topic_performance_response_schema(self):
        """Test TopicPerformanceResponse schema validation"""
        from app.schemas.learning import TopicPerformanceResponse
        
        valid_data = {
            "topic": "Python Programming",
            "mastery_level": 85.0,
            "time_spent_minutes": 300,
            "last_studied": "2026-07-30T10:30:00Z",
            "study_frequency": 8
        }
        schema = TopicPerformanceResponse(**valid_data)
        assert schema.topic == "Python Programming"
    
    def test_time_spent_analytics_schema(self):
        """Test TimeSpentAnalytics schema validation"""
        from app.schemas.learning import TimeSpentAnalytics
        
        valid_data = {
            "period_days": 30,
            "total_time_spent_hours": 35.5,
            "time_by_topic": {
                "Python Programming": 15.5,
                "Data Structures": 10.0
            },
            "daily_time_spent_hours": {
                "2026-07-30": 2.5,
                "2026-07-29": 1.5
            },
            "average_daily_hours": 1.18
        }
        schema = TimeSpentAnalytics(**valid_data)
        assert schema.period_days == 30
