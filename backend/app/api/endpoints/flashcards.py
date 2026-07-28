from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.flashcard import Flashcard, FlashcardStatus
from app.models.flashcard_review import FlashcardReview
from app.schemas.flashcard import FlashcardCreate, FlashcardUpdate, FlashcardResponse, FlashcardReviewCreate, FlashcardReviewResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=FlashcardResponse)
def create_flashcard(
    flashcard: FlashcardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_flashcard = Flashcard(
        **flashcard.dict(),
        user_id=current_user.id,
        status=FlashcardStatus.NEW
    )
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


@router.get("/", response_model=List[FlashcardResponse])
def get_flashcards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    deck_name: str = None
):
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    if deck_name:
        query = query.filter(Flashcard.deck_name == deck_name)
    flashcards = query.order_by(Flashcard.created_at.desc()).all()
    return flashcards


@router.get("/decks")
def get_decks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    decks = db.query(Flashcard.deck_name).filter(
        Flashcard.user_id == current_user.id
    ).distinct().all()
    return {"decks": [deck[0] for deck in decks]}


@router.get("/review")
def get_flashcards_for_review(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    deck_name: str = None
):
    """Get flashcards due for review based on spaced repetition"""
    now = datetime.utcnow()
    
    query = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    )
    
    if deck_name:
        query = query.filter(Flashcard.deck_name == deck_name)
    
    # Get flashcards that are due for review
    flashcards = query.all()
    due_flashcards = []
    
    for flashcard in flashcards:
        latest_review = db.query(FlashcardReview).filter(
            FlashcardReview.flashcard_id == flashcard.id,
            FlashcardReview.user_id == current_user.id
        ).order_by(FlashcardReview.created_at.desc()).first()
        
        if latest_review:
            if latest_review.next_review_date and latest_review.next_review_date <= now:
                due_flashcards.append(flashcard)
        else:
            # New flashcards are always due
            if flashcard.status == FlashcardStatus.NEW:
                due_flashcards.append(flashcard)
    
    return due_flashcards


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return flashcard


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: int,
    flashcard_update: FlashcardUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    update_data = flashcard_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flashcard, field, value)
    
    db.commit()
    db.refresh(flashcard)
    return flashcard


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    db.delete(flashcard)
    db.commit()
    return {"message": "Flashcard deleted successfully"}


@router.post("/review", response_model=FlashcardReviewResponse)
def submit_flashcard_review(
    review: FlashcardReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Verify flashcard belongs to user
    flashcard = db.query(Flashcard).filter(
        Flashcard.id == review.flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Calculate spaced repetition parameters using SM-2 algorithm
    latest_review = db.query(FlashcardReview).filter(
        FlashcardReview.flashcard_id == review.flashcard_id,
        FlashcardReview.user_id == current_user.id
    ).order_by(FlashcardReview.created_at.desc()).first()
    
    if latest_review:
        ease_factor = latest_review.ease_factor
        interval_days = latest_review.interval_days
    else:
        ease_factor = 2.5
        interval_days = 1
    
    # SM-2 algorithm
    if review.rating >= 3:
        if interval_days == 1:
            interval_days = 6
        elif interval_days == 6:
            interval_days = 10
        else:
            interval_days = int(interval_days * ease_factor)
        
        ease_factor = ease_factor + (0.1 - (5 - review.rating) * (0.08 + (5 - review.rating) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3
    else:
        interval_days = 1
        ease_factor = ease_factor - 0.8
        if ease_factor < 1.3:
            ease_factor = 1.3
    
    next_review_date = datetime.utcnow() + timedelta(days=interval_days)
    
    # Update flashcard status
    if review.rating >= 4:
        flashcard.status = FlashcardStatus.MASTERED
    elif review.rating >= 3:
        flashcard.status = FlashcardStatus.REVIEW
    else:
        flashcard.status = FlashcardStatus.LEARNING
    
    # Create review record
    db_review = FlashcardReview(
        flashcard_id=review.flashcard_id,
        user_id=current_user.id,
        rating=review.rating,
        next_review_date=next_review_date,
        interval_days=interval_days,
        ease_factor=ease_factor
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review
