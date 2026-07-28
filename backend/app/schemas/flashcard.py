from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.flashcard import FlashcardStatus


class FlashcardBase(BaseModel):
    front: str
    back: str
    deck_name: Optional[str] = "Default"


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
