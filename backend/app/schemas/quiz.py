from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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


# PHASE 11: Additional Schemas

class QuestionBankItem(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    points: int = 1
    order: int = 0


class QuestionBankCreate(BaseModel):
    topic: str
    description: Optional[str] = None
    difficulty: QuizDifficulty = QuizDifficulty.MEDIUM
    questions: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Programming",
                "description": "Basic Python concepts",
                "difficulty": "medium",
                "questions": [
                    {
                        "question_text": "What is Python?",
                        "question_type": "multiple_choice",
                        "options": ["A language", "A snake", "A tool", "A framework"],
                        "correct_answer": "0",
                        "points": 1,
                        "order": 0
                    }
                ]
            }
        }


class QuestionBankResponse(QuizResponse):
    pass


class AdaptiveQuizRequest(BaseModel):
    topic: str
    question_count: int = 5
    time_limit: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Programming",
                "question_count": 10,
                "time_limit": 30
            }
        }


class QuizHistoryResponse(BaseModel):
    attempts: List[QuizAttemptResponse]
    total_attempts: int
    average_score: float
    completed_count: int


class TopicPerformance(BaseModel):
    quiz_id: int
    quiz_title: str
    topic: str
    average_score: float
    attempts_count: int


class QuizPerformanceAnalytics(BaseModel):
    period_days: int
    total_attempts: int
    average_score: float
    highest_score: float
    lowest_score: float
    improvement_rate: float
    difficulty_distribution: Dict[str, int]
    topic_performance: List[TopicPerformance]
