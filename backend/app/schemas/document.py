from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentType


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: DocumentType
    course_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: Optional[int] = None


class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    file_path: str
    file_size: int
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    processing_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_text: str
    chunk_index: int
    metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithChunks(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []
