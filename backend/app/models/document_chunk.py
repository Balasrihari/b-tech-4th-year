from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_vector = Column(Text)  # JSON string of vector
    chunk_metadata = Column(Text)  # JSON string of metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
