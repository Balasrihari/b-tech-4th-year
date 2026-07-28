from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.quiz import Quiz, QuizDifficulty
from app.models.quiz_question import QuizQuestion, QuestionType
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizWithQuestions,
    QuizQuestionCreate, QuizQuestionResponse,
    QuizAttemptCreate, QuizAttemptResponse
)
from app.auth.dependencies import get_current_active_user, require_role

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
