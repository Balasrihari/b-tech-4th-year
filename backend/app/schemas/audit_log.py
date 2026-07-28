from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AuditLogBase(BaseModel):
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    details: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogWithUser(AuditLogResponse):
    user_email: Optional[str] = None
    user_name: Optional[str] = None
