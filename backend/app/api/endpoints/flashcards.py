from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.flashcard import Flashcard, FlashcardStatus
from app.models.flashcard_review import FlashcardReview
from app.schemas.flashcard import (
    FlashcardCreate, FlashcardUpdate, FlashcardResponse, 
    FlashcardReviewCreate, FlashcardReviewResponse,
    FlashcardProgressResponse, DeckStatisticsResponse,
    StudyScheduleResponse
)
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


# PHASE 12: Topic Grouping and Scheduling

@router.get("/decks/statistics", response_model=List[DeckStatisticsResponse])
def get_deck_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for each deck/topic"""
    decks = db.query(Flashcard.deck_name).filter(
        Flashcard.user_id == current_user.id
    ).distinct().all()
    
    statistics = []
    for deck in decks:
        deck_name = deck[0]
        flashcards = db.query(Flashcard).filter(
            Flashcard.user_id == current_user.id,
            Flashcard.deck_name == deck_name
        ).all()
        
        total = len(flashcards)
        new = sum(1 for f in flashcards if f.status == FlashcardStatus.NEW)
        learning = sum(1 for f in flashcards if f.status == FlashcardStatus.LEARNING)
        review = sum(1 for f in flashcards if f.status == FlashcardStatus.REVIEW)
        mastered = sum(1 for f in flashcards if f.status == FlashcardStatus.MASTERED)
        
        # Calculate due for review
        now = datetime.utcnow()
        due_count = 0
        for flashcard in flashcards:
            latest_review = db.query(FlashcardReview).filter(
                FlashcardReview.flashcard_id == flashcard.id,
                FlashcardReview.user_id == current_user.id
            ).order_by(FlashcardReview.created_at.desc()).first()
            
            if latest_review:
                if latest_review.next_review_date and latest_review.next_review_date <= now:
                    due_count += 1
            elif flashcard.status == FlashcardStatus.NEW:
                due_count += 1
        
        statistics.append({
            "deck_name": deck_name,
            "total_cards": total,
            "new_cards": new,
            "learning_cards": learning,
            "review_cards": review,
            "mastered_cards": mastered,
            "due_for_review": due_count
        })
    
    return statistics


@router.get("/progress", response_model=FlashcardProgressResponse)
def get_flashcard_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get overall flashcard learning progress"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all flashcards
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).all()
    
    total_cards = len(flashcards)
    mastered = sum(1 for f in flashcards if f.status == FlashcardStatus.MASTERED)
    learning = sum(1 for f in flashcards if f.status == FlashcardStatus.LEARNING)
    review = sum(1 for f in flashcards if f.status == FlashcardStatus.REVIEW)
    new = sum(1 for f in flashcards if f.status == FlashcardStatus.NEW)
    
    # Get reviews in the period
    reviews = db.query(FlashcardReview).filter(
        FlashcardReview.user_id == current_user.id,
        FlashcardReview.created_at >= start_date
    ).all()
    
    total_reviews = len(reviews)
    avg_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    # Calculate retention rate (reviews with rating >= 3)
    retained = sum(1 for r in reviews if r.rating >= 3)
    retention_rate = (retained / total_reviews * 100) if total_reviews > 0 else 0
    
    return {
        "total_cards": total_cards,
        "mastered_cards": mastered,
        "learning_cards": learning,
        "review_cards": review,
        "new_cards": new,
        "mastery_percentage": round((mastered / total_cards * 100) if total_cards > 0 else 0, 2),
        "total_reviews_period": total_reviews,
        "average_rating": round(avg_rating, 2),
        "retention_rate": round(retention_rate, 2)
    }


@router.get("/schedule", response_model=StudyScheduleResponse)
def get_study_schedule(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=30)
):
    """Get study schedule showing cards due for review in the next N days"""
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)
    
    schedule = {}
    
    for day_offset in range(days):
        target_date = now + timedelta(days=day_offset)
        date_key = target_date.strftime("%Y-%m-%d")
        
        # Find cards due on this specific date
        due_cards = []
        flashcards = db.query(Flashcard).filter(
            Flashcard.user_id == current_user.id
        ).all()
        
        for flashcard in flashcards:
            latest_review = db.query(FlashcardReview).filter(
                FlashcardReview.flashcard_id == flashcard.id,
                FlashcardReview.user_id == current_user.id
            ).order_by(FlashcardReview.created_at.desc()).first()
            
            if latest_review and latest_review.next_review_date:
                # Check if due on this day (same date)
                if latest_review.next_review_date.date() == target_date.date():
                    due_cards.append({
                        "flashcard_id": flashcard.id,
                        "front": flashcard.front,
                        "deck_name": flashcard.deck_name,
                        "status": flashcard.status.value
                    })
            elif flashcard.status == FlashcardStatus.NEW and day_offset == 0:
                # New cards are due today
                due_cards.append({
                    "flashcard_id": flashcard.id,
                    "front": flashcard.front,
                    "deck_name": flashcard.deck_name,
                    "status": flashcard.status.value
                })
        
        schedule[date_key] = {
            "date": date_key,
            "due_count": len(due_cards),
            "cards": due_cards
        }
    
    # Calculate total due cards
    total_due = sum(day_data["due_count"] for day_data in schedule.values())
    
    return {
        "period_days": days,
        "start_date": now.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_due_cards": total_due,
        "daily_schedule": schedule
    }


@router.post("/batch")
def create_flashcard_batch(
    flashcards: List[FlashcardCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create multiple flashcards at once"""
    created_flashcards = []
    
    for flashcard_data in flashcards:
        db_flashcard = Flashcard(
            **flashcard_data.dict(),
            user_id=current_user.id,
            status=FlashcardStatus.NEW
        )
        db.add(db_flashcard)
        db.flush()
        created_flashcards.append(db_flashcard)
    
    db.commit()
    
    return {
        "message": f"Created {len(created_flashcards)} flashcards",
        "flashcards": created_flashcards
    }


@router.put("/decks/{deck_name}")
def update_deck_name(
    deck_name: str,
    new_deck_name: str = Query(..., description="New deck name"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Rename a deck/topic"""
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        Flashcard.deck_name == deck_name
    ).all()
    
    if not flashcards:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    for flashcard in flashcards:
        flashcard.deck_name = new_deck_name
    
    db.commit()
    
    return {"message": f"Renamed deck '{deck_name}' to '{new_deck_name}' with {len(flashcards)} cards"}
