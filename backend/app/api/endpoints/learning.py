from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.weak_topic import WeakTopic
from app.models.quiz_attempt import QuizAttempt
from app.models.flashcard_review import FlashcardReview
from app.models.flashcard import Flashcard
from app.schemas.learning import (
    LearningProgressCreate, LearningProgressUpdate, LearningProgressResponse,
    WeakTopicCreate, WeakTopicUpdate, WeakTopicResponse,
    ComprehensiveAnalyticsResponse, LearningTrendsResponse,
    StudyStatisticsResponse, DashboardOverviewResponse,
    TopicPerformanceResponse, TimeSpentAnalytics
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


# PHASE 13: Comprehensive Analytics Dashboard

@router.get("/dashboard", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview with all key metrics"""
    
    # Learning progress metrics
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    total_topics = len(progress_list)
    avg_mastery = sum(p.mastery_level for p in progress_list) / total_topics if total_topics > 0 else 0
    total_time_spent = sum(p.time_spent_minutes for p in progress_list)
    
    # Quiz metrics
    quiz_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).all()
    
    total_quizzes = len(quiz_attempts)
    completed_quizzes = [q for q in quiz_attempts if q.completed_at]
    avg_quiz_score = sum(q.score or 0 for q in completed_quizzes) / len(completed_quizzes) if completed_quizzes else 0
    
    # Flashcard metrics
    flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).all()
    
    total_flashcards = len(flashcards)
    mastered_flashcards = sum(1 for f in flashcards if f.status.value == "mastered")
    
    # Recent activity
    recent_progress = progress_list[:5] if progress_list else []
    recent_quizzes = quiz_attempts[:3] if quiz_attempts else []
    
    # Weak topics
    weak_topics = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id
    ).order_by(WeakTopic.confidence_score.asc()).limit(5).all()
    
    return {
        "learning_metrics": {
            "total_topics": total_topics,
            "average_mastery": round(avg_mastery, 2),
            "total_time_spent_hours": round(total_time_spent / 60, 2),
            "topics_mastered": sum(1 for p in progress_list if p.mastery_level >= 80)
        },
        "quiz_metrics": {
            "total_attempts": total_quizzes,
            "average_score": round(avg_quiz_score, 2),
            "completed_count": len(completed_quizzes)
        },
        "flashcard_metrics": {
            "total_cards": total_flashcards,
            "mastered_cards": mastered_flashcards,
            "mastery_percentage": round((mastered_flashcards / total_flashcards * 100) if total_flashcards > 0 else 0, 2)
        },
        "weak_topics": [
            {"topic": wt.topic, "confidence_score": wt.confidence_score}
            for wt in weak_topics
        ],
        "recent_activity": {
            "recent_topics": [{"topic": p.topic, "mastery": p.mastery_level} for p in recent_progress],
            "recent_quizzes": [{"quiz_id": q.quiz_id, "score": q.score} for q in recent_quizzes]
        }
    }


@router.get("/comprehensive", response_model=ComprehensiveAnalyticsResponse)
def get_comprehensive_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get comprehensive analytics for a specified time period"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Learning progress
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.updated_at >= start_date
    ).all()
    
    # Quiz performance
    quiz_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.completed_at >= start_date
    ).all()
    
    # Flashcard activity
    flashcard_reviews = db.query(FlashcardReview).filter(
        FlashcardReview.user_id == current_user.id,
        FlashcardReview.created_at >= start_date
    ).all()
    
    # Calculate metrics
    total_study_time = sum(p.time_spent_minutes for p in progress_list)
    topics_studied = len(set(p.topic for p in progress_list))
    quizzes_completed = len([q for q in quiz_attempts if q.completed_at])
    flashcards_reviewed = len(flashcard_reviews)
    
    # Performance trends
    quiz_scores = [q.score for q in quiz_attempts if q.score]
    avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    
    # Completion rate
    completion_rate = (quizzes_completed / len(quiz_attempts) * 100) if quiz_attempts else 0
    
    return {
        "period_days": days,
        "total_study_time_hours": round(total_study_time / 60, 2),
        "topics_studied": topics_studied,
        "quizzes_completed": quizzes_completed,
        "flashcards_reviewed": flashcards_reviewed,
        "average_quiz_score": round(avg_quiz_score, 2),
        "completion_rate": round(completion_rate, 2),
        "study_streak": calculate_study_streak(current_user.id, db)
    }


@router.get("/trends", response_model=LearningTrendsResponse)
def get_learning_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=7, le=365)
):
    """Get learning trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily activity
    daily_data = {}
    for day_offset in range(days):
        target_date = start_date + timedelta(days=day_offset)
        date_key = target_date.strftime("%Y-%m-%d")
        
        # Progress updates on this day
        progress_count = db.query(LearningProgress).filter(
            LearningProgress.user_id == current_user.id,
            func.date(LearningProgress.updated_at) == target_date.date()
        ).count()
        
        # Quiz completions on this day
        quiz_count = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == current_user.id,
            func.date(QuizAttempt.completed_at) == target_date.date()
        ).count()
        
        # Flashcard reviews on this day
        review_count = db.query(FlashcardReview).filter(
            FlashcardReview.user_id == current_user.id,
            func.date(FlashcardReview.created_at) == target_date.date()
        ).count()
        
        daily_data[date_key] = {
            "date": date_key,
            "progress_updates": progress_count,
            "quizzes_completed": quiz_count,
            "flashcards_reviewed": review_count
        }
    
    # Calculate overall trends
    total_activity = sum(
        day_data["progress_updates"] + day_data["quizzes_completed"] + day_data["flashcards_reviewed"]
        for day_data in daily_data.values()
    )
    
    avg_daily_activity = total_activity / days if days > 0 else 0
    
    # Identify most active day
    most_active_day = max(daily_data.items(), key=lambda x: sum(x[1].values())) if daily_data else None
    
    return {
        "period_days": days,
        "total_activity": total_activity,
        "average_daily_activity": round(avg_daily_activity, 2),
        "most_active_day": most_active_day[0] if most_active_day else None,
        "daily_breakdown": daily_data
    }


@router.get("/statistics", response_model=StudyStatisticsResponse)
def get_study_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed study statistics"""
    
    # Overall statistics
    total_progress = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).count()
    
    total_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).count()
    
    total_flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).count()
    
    # Time statistics
    total_time_minutes = db.query(func.sum(LearningProgress.time_spent_minutes)).filter(
        LearningProgress.user_id == current_user.id
    ).scalar() or 0
    
    avg_time_per_topic = total_time_minutes / total_progress if total_progress > 0 else 0
    
    # Performance statistics
    quiz_scores = db.query(QuizAttempt.score).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.score.isnot(None)
    ).all()
    
    avg_score = sum(q[0] for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
    highest_score = max(q[0] for q in quiz_scores) if quiz_scores else 0
    lowest_score = min(q[0] for q in quiz_scores) if quiz_scores else 0
    
    return {
        "overall_statistics": {
            "total_topics_studied": total_progress,
            "total_quizzes_taken": total_quizzes,
            "total_flashcards_created": total_flashcards
        },
        "time_statistics": {
            "total_study_time_hours": round(total_time_minutes / 60, 2),
            "average_time_per_topic_minutes": round(avg_time_per_topic, 2)
        },
        "performance_statistics": {
            "average_quiz_score": round(avg_score, 2),
            "highest_quiz_score": round(highest_score, 2),
            "lowest_quiz_score": round(lowest_score, 2)
        }
    }


@router.get("/topic-performance", response_model=List[TopicPerformanceResponse])
def get_topic_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance breakdown by topic"""
    
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    topic_performance = []
    for progress in progress_list:
        # Get quiz attempts related to this topic
        # This is a simplified version - in production, you'd have better topic-quiz relationships
        topic_performance.append({
            "topic": progress.topic,
            "mastery_level": progress.mastery_level,
            "time_spent_minutes": progress.time_spent_minutes,
            "last_studied": progress.last_accessed.isoformat() if progress.last_accessed else None,
            "study_frequency": calculate_study_frequency(progress.id, db)
        })
    
    return topic_performance


@router.get("/time-analytics", response_model=TimeSpentAnalytics)
def get_time_spent_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get detailed time spent analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get progress updates in the period
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.updated_at >= start_date
    ).all()
    
    # Calculate time by topic
    time_by_topic = {}
    for progress in progress_list:
        if progress.topic not in time_by_topic:
            time_by_topic[progress.topic] = 0
        time_by_topic[progress.topic] += progress.time_spent_minutes
    
    # Calculate daily time spent
    daily_time = {}
    for day_offset in range(days):
        target_date = start_date + timedelta(days=day_offset)
        date_key = target_date.strftime("%Y-%m-%d")
        
        day_progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == current_user.id,
            func.date(LearningProgress.updated_at) == target_date.date()
        ).all()
        
        daily_time[date_key] = sum(p.time_spent_minutes for p in day_progress)
    
    total_time = sum(time_by_topic.values())
    
    return {
        "period_days": days,
        "total_time_spent_hours": round(total_time / 60, 2),
        "time_by_topic": {topic: round(minutes / 60, 2) for topic, minutes in time_by_topic.items()},
        "daily_time_spent_hours": {date: round(minutes / 60, 2) for date, minutes in daily_time.items()},
        "average_daily_hours": round((total_time / days / 60), 2) if days > 0 else 0
    }


# Helper functions

def calculate_study_streak(user_id: int, db: Session) -> int:
    """Calculate current study streak in days"""
    streak = 0
    current_date = datetime.utcnow().date()
    
    while True:
        # Check if there was any activity on this day
        activity_count = db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            func.date(LearningProgress.updated_at) == current_date
        ).count()
        
        quiz_activity = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == user_id,
            func.date(QuizAttempt.completed_at) == current_date
        ).count()
        
        if activity_count > 0 or quiz_activity > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def calculate_study_frequency(progress_id: int, db: Session) -> int:
    """Calculate how many times a topic has been studied"""
    # This is a simplified version - in production, track actual study sessions
    progress = db.query(LearningProgress).filter(
        LearningProgress.id == progress_id
    ).first()
    
    if progress:
        # Use time_spent_minutes as a proxy for frequency
        return min(progress.time_spent_minutes // 10, 10)  # Cap at 10
    return 0
