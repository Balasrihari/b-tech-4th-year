from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.quiz import QuizDifficulty
from app.models.quiz_question import QuestionType


class QuizQuestionCreate(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[str] = None  # JSON string
    correct_answer: str
    points: int = 1
    order: int = 0


class QuizQuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    question_type: QuestionType
    options: Optional[str]
    correct_answer: Optional[str]  # Hidden in responses
    points: int
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: QuizDifficulty = QuizDifficulty.MEDIUM
    time_limit: Optional[int] = None


class QuizCreate(QuizBase):
    course_id: Optional[int] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[QuizDifficulty] = None
    time_limit: Optional[int] = None
    is_active: Optional[bool] = None


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    course_id: Optional[int]
    created_by: int
    difficulty: QuizDifficulty
    time_limit: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    quiz_id: int
    answers: str  # JSON string of answers


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    answers: str
    score: Optional[float]
    total_points: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizWithQuestions(QuizResponse):
    questions: List[QuizQuestionResponse]
