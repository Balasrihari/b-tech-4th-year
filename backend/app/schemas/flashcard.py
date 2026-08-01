from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from app.models.flashcard import FlashcardStatus


class FlashcardBase(BaseModel):
    front: str
    back: str
    deck_name: Optional[str] = "Default"
    
    class Config:
        json_schema_extra = {
            "example": {
                "front": "What is Python?",
                "back": "Python is a high-level programming language",
                "deck_name": "Programming"
            }
        }


class FlashcardCreate(FlashcardBase):
    pass


class FlashcardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    deck_name: Optional[str] = None
    status: Optional[FlashcardStatus] = None


class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    user_id: int
    deck_name: str
    status: FlashcardStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class FlashcardReviewCreate(BaseModel):
    flashcard_id: int
    rating: float  # 0-5 rating for spaced repetition
    
    class Config:
        json_schema_extra = {
            "example": {
                "flashcard_id": 1,
                "rating": 4.0
            }
        }


class FlashcardReviewResponse(BaseModel):
    id: int
    flashcard_id: int
    user_id: int
    rating: float
    next_review_date: Optional[datetime]
    interval_days: Optional[int]
    ease_factor: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# PHASE 12: Additional Schemas

class FlashcardProgressResponse(BaseModel):
    total_cards: int
    mastered_cards: int
    learning_cards: int
    review_cards: int
    new_cards: int
    mastery_percentage: float
    total_reviews_period: int
    average_rating: float
    retention_rate: float


class DeckStatisticsResponse(BaseModel):
    deck_name: str
    total_cards: int
    new_cards: int
    learning_cards: int
    review_cards: int
    mastered_cards: int
    due_for_review: int


class ScheduledCard(BaseModel):
    flashcard_id: int
    front: str
    deck_name: str
    status: str


class DailySchedule(BaseModel):
    date: str
    due_count: int
    cards: List[ScheduledCard]


class StudyScheduleResponse(BaseModel):
    period_days: int
    start_date: str
    end_date: str
    total_due_cards: int
    daily_schedule: Dict[str, DailySchedule]
