from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.todo import TodoPriority, TodoStatus


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TodoPriority = TodoPriority.MEDIUM
    due_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TodoPriority] = None
    status: Optional[TodoStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    user_id: int
    priority: TodoPriority
    status: TodoStatus
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
