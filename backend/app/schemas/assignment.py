from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.assignment import AssignmentStatus
from app.models.assignment_submission import SubmissionStatus


class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: int
    due_date: Optional[datetime] = None
    max_score: Optional[int] = Field(None, ge=0)


class AssignmentCreate(AssignmentBase):
    status: AssignmentStatus = AssignmentStatus.DRAFT


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[int] = None
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    max_score: Optional[int] = Field(None, ge=0)


class AssignmentResponse(AssignmentBase):
    id: int
    faculty_id: int
    status: AssignmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssignmentSubmissionBase(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)


class AssignmentSubmissionCreate(AssignmentSubmissionBase):
    pass


class AssignmentSubmissionUpdate(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    status: Optional[SubmissionStatus] = None
    score: Optional[float] = Field(None, ge=0)
    feedback: Optional[str] = None


class AssignmentSubmissionResponse(AssignmentSubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    status: SubmissionStatus
    score: Optional[float] = None
    feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssignmentWithSubmissions(AssignmentResponse):
    submissions: list[AssignmentSubmissionResponse] = []
