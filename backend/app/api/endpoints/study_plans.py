from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.learning_progress import LearningProgress
from app.models.weak_topic import WeakTopic
from app.models.todo import Todo
from app.schemas.study_plan import StudyPlanCreate, StudyPlanUpdate, StudyPlanResponse, StudyRecommendation
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=StudyPlanResponse)
def create_study_plan(
    plan: StudyPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Create as a todo item (reusing existing Todo model for study planning)
    db_plan = Todo(
        title=plan.topic,
        description=f"Study plan for {plan.topic}",
        user_id=current_user.id,
        priority=plan.priority.upper(),
        due_date=plan.target_date
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Also create learning progress entry
    progress = LearningProgress(
        user_id=current_user.id,
        topic=plan.topic,
        course_id=plan.course_id,
        mastery_level=0.0,
        time_spent_minutes=0
    )
    db.add(progress)
    db.commit()
    
    return StudyPlanResponse(
        id=db_plan.id,
        user_id=db_plan.user_id,
        topic=db_plan.title,
        course_id=plan.course_id,
        target_date=db_plan.due_date,
        priority=db_plan.priority.lower(),
        estimated_hours=plan.estimated_hours,
        is_completed=db_plan.status == "completed",
        created_at=db_plan.created_at,
        updated_at=db_plan.updated_at
    )


@router.get("/", response_model=List[StudyPlanResponse])
def get_study_plans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    include_completed: bool = False
):
    query = db.query(Todo).filter(Todo.user_id == current_user.id)
    
    if not include_completed:
        query = query.filter(Todo.status != "completed")
    
    plans = query.order_by(Todo.due_date.asc().nullslast()).all()
    
    return [
        StudyPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            topic=plan.title,
            course_id=None,
            target_date=plan.due_date,
            priority=plan.priority.lower(),
            estimated_hours=None,
            is_completed=plan.status == "completed",
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
        for plan in plans
    ]


@router.get("/recommendations", response_model=List[StudyRecommendation])
def get_study_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate personalized study recommendations based on weak topics and progress"""
    recommendations = []
    
    # Get weak topics
    weak_topics = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id
    ).order_by(WeakTopic.confidence_score.asc()).limit(5).all()
    
    for wt in weak_topics:
        recommendations.append(StudyRecommendation(
            topic=wt.topic,
            reason=f"Low confidence score ({wt.confidence_score}%) - needs attention",
            suggested_hours=3,
            priority="high" if wt.confidence_score < 50 else "medium"
        ))
    
    # Get topics with low mastery
    low_mastery = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.mastery_level < 50
    ).order_by(LearningProgress.mastery_level.asc()).limit(3).all()
    
    for lp in low_mastery:
        # Avoid duplicates
        if not any(r.topic == lp.topic for r in recommendations):
            recommendations.append(StudyRecommendation(
                topic=lp.topic,
                reason=f"Low mastery level ({lp.mastery_level}%) - needs review",
                suggested_hours=2,
                priority="high" if lp.mastery_level < 30 else "medium"
            ))
    
    # Get overdue tasks
    overdue = db.query(Todo).filter(
        Todo.user_id == current_user.id,
        Todo.due_date < datetime.utcnow(),
        Todo.status != "completed"
    ).limit(3).all()
    
    for task in overdue:
        if not any(r.topic == task.title for r in recommendations):
            recommendations.append(StudyRecommendation(
                topic=task.title,
                reason=f"Overdue - was due on {task.due_date.strftime('%Y-%m-%d')}",
                suggested_hours=1,
                priority="high"
            ))
    
    return recommendations[:10]  # Return top 10 recommendations


@router.put("/{plan_id}", response_model=StudyPlanResponse)
def update_study_plan(
    plan_id: int,
    plan_update: StudyPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Todo).filter(
        Todo.id == plan_id,
        Todo.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    update_data = plan_update.dict(exclude_unset=True)
    
    if "topic" in update_data:
        plan.title = update_data["topic"]
    if "target_date" in update_data:
        plan.due_date = update_data["target_date"]
    if "priority" in update_data:
        plan.priority = update_data["priority"].upper()
    if "is_completed" in update_data and update_data["is_completed"]:
        plan.status = "completed"
        plan.completed_at = datetime.utcnow()
    elif "is_completed" in update_data and not update_data["is_completed"]:
        plan.status = "pending"
    
    db.commit()
    db.refresh(plan)
    
    return StudyPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        topic=plan.title,
        course_id=None,
        target_date=plan.due_date,
        priority=plan.priority.lower(),
        estimated_hours=None,
        is_completed=plan.status == "completed",
        created_at=plan.created_at,
        updated_at=plan.updated_at
    )


@router.delete("/{plan_id}")
def delete_study_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Todo).filter(
        Todo.id == plan_id,
        Todo.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Study plan deleted successfully"}


@router.get("/roadmap")
def get_study_roadmap(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a personalized study roadmap based on progress and weak topics"""
    
    # Get all learning progress
    progress_list = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    ).all()
    
    # Get weak topics
    weak_topics = db.query(WeakTopic).filter(
        WeakTopic.user_id == current_user.id
    ).all()
    
    # Get pending tasks
    pending_tasks = db.query(Todo).filter(
        Todo.user_id == current_user.id,
        Todo.status != "completed"
    ).order_by(Todo.due_date.asc().nullslast()).all()
    
    # Organize by mastery level
    not_started = [p for p in progress_list if p.mastery_level == 0]
    in_progress = [p for p in progress_list if 0 < p.mastery_level < 80]
    mastered = [p for p in progress_list if p.mastery_level >= 80]
    
    return {
        "not_started": [
            {
                "topic": p.topic,
                "course_id": p.course_id,
                "suggested_action": "Begin studying this topic"
            }
            for p in not_started
        ],
        "in_progress": [
            {
                "topic": p.topic,
                "mastery_level": p.mastery_level,
                "suggested_action": "Continue studying to reach mastery"
            }
            for p in in_progress
        ],
        "mastered": [
            {
                "topic": p.topic,
                "mastery_level": p.mastery_level,
                "suggested_action": "Review periodically to maintain mastery"
            }
            for p in mastered
        ],
        "weak_topics": [
            {
                "topic": wt.topic,
                "confidence_score": wt.confidence_score,
                "recommended_actions": wt.recommended_actions
            }
            for wt in weak_topics
        ],
        "upcoming_deadlines": [
            {
                "topic": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority
            }
            for task in pending_tasks[:5]
        ]
    }
