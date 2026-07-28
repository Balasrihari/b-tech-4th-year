from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class FlashcardReview(Base):
    __tablename__ = "flashcard_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float)  # Spaced repetition rating (0-5)
    next_review_date = Column(DateTime(timezone=True))
    interval_days = Column(Integer)
    ease_factor = Column(Float, default=2.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flashcard = relationship("Flashcard", back_populates="reviews")
    user = relationship("User", back_populates="flashcard_reviews")
