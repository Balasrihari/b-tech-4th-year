from pydantic import BaseModel
from typing import Optional
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
