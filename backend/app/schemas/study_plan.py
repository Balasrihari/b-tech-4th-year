from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StudyPlanBase(BaseModel):
    topic: str
    course_id: Optional[int] = None
    target_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    estimated_hours: Optional[int] = None


class StudyPlanCreate(StudyPlanBase):
    pass


class StudyPlanUpdate(BaseModel):
    topic: Optional[str] = None
    target_date: Optional[datetime] = None
    priority: Optional[str] = None
    estimated_hours: Optional[int] = None
    is_completed: Optional[bool] = None


class StudyPlanResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    course_id: Optional[int]
    target_date: Optional[datetime]
    priority: str
    estimated_hours: Optional[int]
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StudyRecommendation(BaseModel):
    topic: str
    reason: str
    suggested_hours: int
    priority: str
