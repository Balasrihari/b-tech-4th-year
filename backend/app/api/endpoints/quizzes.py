from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.quiz import Quiz, QuizDifficulty
from app.models.quiz_question import QuizQuestion, QuestionType
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizWithQuestions,
    QuizQuestionCreate, QuizQuestionResponse,
    QuizAttemptCreate, QuizAttemptResponse, QuestionBankCreate,
    QuestionBankResponse, AdaptiveQuizRequest, QuizHistoryResponse,
    QuizPerformanceAnalytics
)
from app.auth.dependencies import get_current_active_user, require_role
from app.services.gemini_service import generate_quiz_questions

router = APIRouter()


@router.post("/", response_model=QuizResponse)
def create_quiz(
    quiz: QuizCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_quiz = Quiz(
        **quiz.dict(),
        created_by=current_user.id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


@router.get("/", response_model=List[QuizResponse])
def get_quizzes (
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    course_id: int = None
):
    query = db.query(Quiz).filter(Quiz.is_active == True)
    
    if course_id:
        query = query.filter(Quiz.course_id == course_id)
    
    # Students can only see quizzes from their enrolled courses
    if current_user.role == UserRole.STUDENT:
        # For now, return all active quizzes (simplified)
        pass
    
    quizzes = query.order_by(Quiz.created_at.desc()).all()
    return quizzes


@router.get("/{quiz_id}", response_model=QuizWithQuestions)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.order).all()
    
    return QuizWithQuestions(
        **quiz.__dict__,
        questions=questions
    )


@router.post("/{quiz_id}/questions", response_model=QuizQuestionResponse)
def add_question(
    quiz_id: int,
    question: QuizQuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Only creator can add questions (or admin)
    if current_user.role != UserRole.ADMIN and quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only add questions to your own quizzes")
    
    db_question = QuizQuestion(
        **question.dict(),
        quiz_id=quiz_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.post("/{quiz_id}/attempt", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    quiz_id: int,
    attempt: QuizAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get all questions for the quiz
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    
    # Calculate score
    answers = json.loads(attempt.answers)
    total_points = sum(q.points for q in questions)
    correct_points = 0
    
    for question in questions:
        question_id = str(question.id)
        if question_id in answers:
            if answers[question_id] == question.correct_answer:
                correct_points += question.points
    
    score = (correct_points / total_points * 100) if total_points > 0 else 0
    
    db_attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=current_user.id,
        answers=attempt.answers,
        score=score,
        total_points=total_points,
        completed_at=datetime.utcnow()
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    return db_attempt


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Students can only see their own attempts
    if current_user.role == UserRole.STUDENT:
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == current_user.id
        ).order_by(QuizAttempt.created_at.desc()).all()
    else:
        # Faculty and admin can see all attempts for their quizzes
        if current_user.role != UserRole.ADMIN and quiz.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view attempts for your own quizzes")
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id
        ).order_by(QuizAttempt.created_at.desc()).all()
    
    return attempts


@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Only creator can update (or admin)
    if current_user.role != UserRole.ADMIN and quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own quizzes")
    
    update_data = quiz_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    db.commit()
    db.refresh(quiz)
    return quiz


@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Only creator can delete (or admin)
    if current_user.role != UserRole.ADMIN and quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own quizzes")
    
    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}


# PHASE 11: Question Generation and Question Bank

@router.post("/generate-questions")
async def generate_questions(
    topic: str = Query(..., description="Topic to generate questions for"),
    difficulty: QuizDifficulty = Query(QuizDifficulty.MEDIUM, description="Question difficulty"),
    question_count: int = Query(5, ge=1, le=20, description="Number of questions to generate"),
    question_type: QuestionType = Query(QuestionType.MULTIPLE_CHOICE, description="Type of questions"),
    current_user: User = Depends(get_current_active_user)
):
    """AI-powered question generation using Gemini API"""
    try:
        questions = await generate_quiz_questions(
            topic=topic,
            difficulty=difficulty.value,
            question_count=question_count,
            question_type=question_type.value
        )
        return {
            "topic": topic,
            "difficulty": difficulty,
            "question_type": question_type,
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


@router.post("/question-bank", response_model=QuestionBankResponse)
def create_question_bank(
    question_bank: QuestionBankCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a reusable question bank"""
    # Create a quiz to serve as question bank
    db_quiz = Quiz(
        title=f"Question Bank: {question_bank.topic}",
        description=question_bank.description,
        difficulty=question_bank.difficulty,
        created_by=current_user.id,
        is_active=True
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Add questions to the bank
    for question_data in question_bank.questions:
        db_question = QuizQuestion(
            quiz_id=db_quiz.id,
            question_text=question_data["question_text"],
            question_type=question_data["question_type"],
            options=json.dumps(question_data.get("options", [])),
            correct_answer=question_data["correct_answer"],
            points=question_data.get("points", 1),
            order=question_data.get("order", 0)
        )
        db.add(db_question)
    
    db.commit()
    return db_quiz


@router.get("/question-bank", response_model=List[QuestionBankResponse])
def get_question_banks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    topic: Optional[str] = None
):
    """Get all question banks"""
    query = db.query(Quiz).filter(
        Quiz.created_by == current_user.id,
        Quiz.title.like("Question Bank:%")
    )
    
    if topic:
        query = query.filter(Quiz.title.contains(topic))
    
    return query.order_by(Quiz.created_at.desc()).all()


@router.get("/question-bank/{bank_id}/questions")
def get_question_bank_questions(
    bank_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get questions from a question bank"""
    bank = db.query(Quiz).filter(
        Quiz.id == bank_id,
        Quiz.created_by == current_user.id
    ).first()
    
    if not bank:
        raise HTTPException(status_code=404, detail="Question bank not found")
    
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == bank_id
    ).order_by(QuizQuestion.order).all()
    
    return {
        "bank_id": bank_id,
        "bank_title": bank.title,
        "questions": questions
    }


# PHASE 11: Adaptive Learning

@router.post("/adaptive", response_model=QuizWithQuestions)
async def generate_adaptive_quiz(
    request: AdaptiveQuizRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate adaptive quiz based on student performance"""
    # Get student's previous attempts to determine appropriate difficulty
    previous_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).all()
    
    # Calculate average score to determine starting difficulty
    if previous_attempts:
        avg_score = sum(attempt.score or 0 for attempt in previous_attempts) / len(previous_attempts)
        if avg_score >= 80:
            difficulty = QuizDifficulty.HARD
        elif avg_score >= 50:
            difficulty = QuizDifficulty.MEDIUM
        else:
            difficulty = QuizDifficulty.EASY
    else:
        difficulty = QuizDifficulty.MEDIUM
    
    # Create adaptive quiz
    db_quiz = Quiz(
        title=f"Adaptive Quiz: {request.topic}",
        description=f"Adaptive quiz for {request.topic} based on your performance",
        difficulty=difficulty,
        created_by=current_user.id,
        time_limit=request.time_limit,
        is_active=True
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Generate or select questions based on difficulty
    # For now, use existing question bank or generate AI questions
    questions = db.query(QuizQuestion).join(Quiz).filter(
        Quiz.title.like(f"%Question Bank:%{request.topic}%"),
        Quiz.difficulty == difficulty
    ).limit(request.question_count).all()
    
    if not questions:
        # Fallback to AI generation
        try:
            generated_questions = await generate_quiz_questions(
                topic=request.topic,
                difficulty=difficulty.value,
                question_count=request.question_count,
                question_type=QuestionType.MULTIPLE_CHOICE.value
            )
            
            for idx, q_data in enumerate(generated_questions):
                db_question = QuizQuestion(
                    quiz_id=db_quiz.id,
                    question_text=q_data["question_text"],
                    question_type=q_data["question_type"],
                    options=json.dumps(q_data.get("options", [])),
                    correct_answer=q_data["correct_answer"],
                    points=1,
                    order=idx
                )
                db.add(db_question)
        except:
            raise HTTPException(status_code=500, detail="Failed to generate adaptive questions")
    else:
        # Use existing questions
        for idx, question in enumerate(questions):
            new_question = QuizQuestion(
                quiz_id=db_quiz.id,
                question_text=question.question_text,
                question_type=question.question_type,
                options=question.options,
                correct_answer=question.correct_answer,
                points=question.points,
                order=idx
            )
            db.add(new_question)
    
    db.commit()
    db.refresh(db_quiz)
    
    # Return quiz with questions
    quiz_questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == db_quiz.id
    ).order_by(QuizQuestion.order).all()
    
    return QuizWithQuestions(
        **db_quiz.__dict__,
        questions=quiz_questions
    )


# PHASE 11: Quiz History and Analytics

@router.get("/history", response_model=QuizHistoryResponse)
def get_quiz_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get student's quiz attempt history"""
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).offset(offset).limit(limit).all()
    
    total_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).count()
    
    # Calculate statistics
    completed_attempts = [a for a in attempts if a.completed_at]
    avg_score = sum(a.score or 0 for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
    
    return {
        "attempts": attempts,
        "total_attempts": total_attempts,
        "average_score": round(avg_score, 2),
        "completed_count": len(completed_attempts)
    }


@router.get("/performance-analytics", response_model=QuizPerformanceAnalytics)
def get_quiz_performance_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get detailed quiz performance analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.completed_at >= start_date
    ).all()
    
    # Calculate performance metrics
    total_attempts = len(attempts)
    completed_attempts = [a for a in attempts if a.completed_at]
    
    if not completed_attempts:
        return {
            "period_days": days,
            "total_attempts": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "improvement_rate": 0,
            "difficulty_distribution": {},
            "topic_performance": []
        }
    
    scores = [a.score or 0 for a in completed_attempts]
    avg_score = sum(scores) / len(scores)
    highest_score = max(scores)
    lowest_score = min(scores)
    
    # Calculate improvement rate (compare first half vs second half)
    mid_point = len(completed_attempts) // 2
    if mid_point > 0:
        first_half_avg = sum(scores[:mid_point]) / mid_point
        second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
        improvement_rate = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
    else:
        improvement_rate = 0
    
    # Difficulty distribution
    difficulty_dist = {"easy": 0, "medium": 0, "hard": 0}
    for attempt in completed_attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz:
            difficulty_dist[quiz.difficulty.value] += 1
    
    # Topic performance
    topic_performance = []
    quiz_ids = list(set(a.quiz_id for a in completed_attempts))
    for quiz_id in quiz_ids:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quiz:
            quiz_attempts = [a for a in completed_attempts if a.quiz_id == quiz_id]
            quiz_avg = sum(a.score or 0 for a in quiz_attempts) / len(quiz_attempts)
            topic_performance.append({
                "quiz_id": quiz_id,
                "quiz_title": quiz.title,
                "topic": quiz.title,
                "average_score": round(quiz_avg, 2),
                "attempts_count": len(quiz_attempts)
            })
    
    return {
        "period_days": days,
        "total_attempts": total_attempts,
        "average_score": round(avg_score, 2),
        "highest_score": round(highest_score, 2),
        "lowest_score": round(lowest_score, 2),
        "improvement_rate": round(improvement_rate, 2),
        "difficulty_distribution": difficulty_dist,
        "topic_performance": topic_performance
    }
