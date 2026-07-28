from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.weak_topic import WeakTopic
from app.schemas.learning import (
    LearningProgressCreate, LearningProgressUpdate, LearningProgressResponse,
    WeakTopicCreate, WeakTopicUpdate, WeakTopicResponse
)
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/progress", response_model=LearningProgressResponse)
def create_learning_progress(
    progress: LearningProgressCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if progress already exists for this topic
    existing = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.topic == progress.topic
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Progress for this topic already exists. Use update instead."
        )
    
    db_progress = LearningProgress(
        **progress.dict(),
        user_id=current_user.id,
        last_accessed=datetime.utcnow()
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


@router.get("/progress", response_model=List[LearningProgressResponse])
def get_learning_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    course_id: int = None
):
    query = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    )
    
    if course_id:
        query = query.filter(LearningProgress.course_id == course_id)
    
    progress = query.order_by(LearningProgress.updated_at.desc()).all()
    return progress


@router.put("/progress/{progress_id}", response_model=LearningProgressResponse)
def update_learning_progress(
    progress_id: int,
    progress_update: LearningProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    progress = db.query(LearningProgress).filter(
        LearningProgress.id == progress_id,
        LearningProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Learning progress not found")
    
    update_data = progress_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)
    
    progress.last_accessed = datetime.utcnow()
    db.commit()
    db.refresh(progress)
    return progress


@router.delete("/progress/{progress_id}")
def delete_learning_progress(
    progress_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    progress = db.query(LearningProgress).filter(
        LearningProgress.id == progress_id,
        LearningProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Learning progress not found")
    
    db.delete(progress)
    db.commit()
    return {"message": "Learning progress deleted successfully"}


@router.post("/weak-topics", response_model=WeakTopicResponse)
def create_weak_topic(
    weak_topic: WeakTopicCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if weak topic already exists
    existing = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id,
        WeakTopic.topic == weak_topic.topic
    ).first()
    
    if existing:
        # Update existing
        update_data = weak_topic.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    
    db_weak_topic = WeakTopic(
        **weak_topic.dict(),
        user_id=current_user.id,
        detected_at=datetime.utcnow()
    )
    db.add(db_weak_topic)
    db.commit()
    db.refresh(db_weak_topic)
    return db_weak_topic


@router.get("/weak-topics", response_model=List[WeakTopicResponse])
def get_weak_topics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    weak_topics = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id
    ).order_by(WeakTopic.confidence_score.asc()).all()  # Lowest confidence first
    return weak_topics


@router.put("/weak-topics/{weak_topic_id}", response_model=WeakTopicResponse)
def update_weak_topic(
    weak_topic_id: int,
    weak_topic_update: WeakTopicUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    weak_topic = db.query(WeakTopic).filter(
        WeakTopic.id == weak_topic_id,
        WeakTopic.user_id == current_user.id
    ).first()
    
    if not weak_topic:
        raise HTTPException(status_code=404, detail="Weak topic not found")
    
    update_data = weak_topic_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(weak_topic, field, value)
    
    weak_topic.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(weak_topic)
    return weak_topic


@router.delete("/weak-topics/{weak_topic_id}")
def delete_weak_topic(
    weak_topic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    weak_topic = db.query(WeakTopic).filter(
        WeakTopic.id == weak_topic_id,
        WeakTopic.user_id == current_user.id
    ).first()
    
    if not weak_topic:
        raise HTTPException(status_code=404, detail="Weak topic not found")
    
    db.delete(weak_topic)
    db.commit()
    return {"message": "Weak topic deleted successfully"}


@router.get("/analytics")
def get_learning_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive learning analytics for the user"""
    
    # Get all learning progress
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    # Get all weak topics
    weak_topics = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id
    ).all()
    
    # Calculate analytics
    total_topics = len(progress_list)
    avg_mastery = sum(p.mastery_level for p in progress_list) / total_topics if total_topics > 0 else 0
    total_time_spent = sum(p.time_spent_minutes for p in progress_list)
    weak_topic_count = len(weak_topics)
    avg_confidence = sum(wt.confidence_score for wt in weak_topics) / weak_topic_count if weak_topic_count > 0 else 0
    
    # Mastery distribution
    mastered = sum(1 for p in progress_list if p.mastery_level >= 80)
    learning = sum(1 for p in progress_list if 50 <= p.mastery_level < 80)
    struggling = sum(1 for p in progress_list if p.mastery_level < 50)
    
    return {
        "total_topics": total_topics,
        "average_mastery": round(avg_mastery, 2),
        "total_time_spent_minutes": total_time_spent,
        "total_time_spent_hours": round(total_time_spent / 60, 2),
        "weak_topic_count": weak_topic_count,
        "average_confidence": round(avg_confidence, 2),
        "mastery_distribution": {
            "mastered": mastered,
            "learning": learning,
            "struggling": struggling
        },
        "recent_progress": [
            {
                "topic": p.topic,
                "mastery_level": p.mastery_level,
                "last_accessed": p.last_accessed.isoformat() if p.last_accessed else None
            }
            for p in progress_list[:5]
        ]
    }
