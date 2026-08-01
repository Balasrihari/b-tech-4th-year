from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class LearningProgressBase(BaseModel):
    topic: str
    course_id: Optional[int] = None
    mastery_level: float = 0.0  # 0-100
    time_spent_minutes: int = 0


class LearningProgressCreate(LearningProgressBase):
    pass


class LearningProgressUpdate(BaseModel):
    mastery_level: Optional[float] = None
    time_spent_minutes: Optional[int] = None


class LearningProgressResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    course_id: Optional[int]
    mastery_level: float
    time_spent_minutes: int
    last_accessed: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WeakTopicBase(BaseModel):
    topic: str
    confidence_score: float  # 0-100
    recommended_actions: Optional[str] = None  # JSON string


class WeakTopicCreate(WeakTopicBase):
    pass


class WeakTopicUpdate(BaseModel):
    confidence_score: Optional[float] = None
    recommended_actions: Optional[str] = None


class WeakTopicResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    confidence_score: float
    recommended_actions: Optional[str]
    detected_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# PHASE 13: Additional Analytics Schemas

class LearningMetrics(BaseModel):
    total_topics: int
    average_mastery: float
    total_time_spent_hours: float
    topics_mastered: int


class QuizMetrics(BaseModel):
    total_attempts: int
    average_score: float
    completed_count: int


class FlashcardMetrics(BaseModel):
    total_cards: int
    mastered_cards: int
    mastery_percentage: float


class RecentActivity(BaseModel):
    recent_topics: List[Dict[str, Any]]
    recent_quizzes: List[Dict[str, Any]]


class DashboardOverviewResponse(BaseModel):
    learning_metrics: LearningMetrics
    quiz_metrics: QuizMetrics
    flashcard_metrics: FlashcardMetrics
    weak_topics: List[Dict[str, Any]]
    recent_activity: RecentActivity


class ComprehensiveAnalyticsResponse(BaseModel):
    period_days: int
    total_study_time_hours: float
    topics_studied: int
    quizzes_completed: int
    flashcards_reviewed: int
    average_quiz_score: float
    completion_rate: float
    study_streak: int


class DailyActivityData(BaseModel):
    date: str
    progress_updates: int
    quizzes_completed: int
    flashcards_reviewed: int


class LearningTrendsResponse(BaseModel):
    period_days: int
    total_activity: int
    average_daily_activity: float
    most_active_day: Optional[str]
    daily_breakdown: Dict[str, DailyActivityData]


class OverallStatistics(BaseModel):
    total_topics_studied: int
    total_quizzes_taken: int
    total_flashcards_created: int


class TimeStatistics(BaseModel):
    total_study_time_hours: float
    average_time_per_topic_minutes: float


class PerformanceStatistics(BaseModel):
    average_quiz_score: float
    highest_quiz_score: float
    lowest_quiz_score: float


class StudyStatisticsResponse(BaseModel):
    overall_statistics: OverallStatistics
    time_statistics: TimeStatistics
    performance_statistics: PerformanceStatistics


class TopicPerformanceResponse(BaseModel):
    topic: str
    mastery_level: float
    time_spent_minutes: int
    last_studied: Optional[str]
    study_frequency: int


class TimeSpentAnalytics(BaseModel):
    period_days: int
    total_time_spent_hours: float
    time_by_topic: Dict[str, float]
    daily_time_spent_hours: Dict[str, float]
    average_daily_hours: float
