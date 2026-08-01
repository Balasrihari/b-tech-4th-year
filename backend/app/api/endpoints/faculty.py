from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.learning_progress import LearningProgress
from app.models.assignment import Assignment
from app.models.assignment_submission import AssignmentSubmission, SubmissionStatus
from app.models.quiz_attempt import QuizAttempt
from pydantic import BaseModel

router = APIRouter()


# Schemas
class StudentInfo(BaseModel):
    id: int
    email: str
    full_name: str
    enrollment_status: str
    enrolled_at: datetime


class StudentPerformance(BaseModel):
    student_id: int
    student_name: str
    student_email: str
    course_id: int
    course_name: str
    average_quiz_score: float
    total_quizzes_taken: int
    average_assignment_score: float
    total_assignments_submitted: int
    total_mastery_level: float
    total_time_spent_minutes: int
    last_activity: Optional[datetime]


class CourseProgressSummary(BaseModel):
    course_id: int
    course_name: str
    total_students: int
    active_students: int
    average_mastery: float
    total_time_spent_hours: float
    average_quiz_score: float
    average_assignment_score: float


@router.get("/dashboard")
def get_faculty_dashboard(
    current_user: User = Depends(require_role(UserRole.FACULTY))
):
    return {
        "message": "Faculty dashboard",
        "user": current_user.email,
        "role": current_user.role.value
    }


@router.get("/students", response_model=List[StudentInfo])
def get_faculty_students(
    course_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FACULTY))
):
    """Get students enrolled in faculty's courses"""
    # Get faculty's courses
    courses_query = db.query(Course).filter(Course.faculty_id == current_user.id)
    
    if course_id:
        courses_query = courses_query.filter(Course.id == course_id)
    
    courses = courses_query.all()
    course_ids = [course.id for course in courses]
    
    if not course_ids:
        return []
    
    # Get enrollments for these courses
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id.in_(course_ids)
    ).offset(skip).limit(limit).all()
    
    students = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        if student:
            students.append(StudentInfo(
                id=student.id,
                email=student.email,
                full_name=student.full_name,
                enrollment_status=enrollment.status.value,
                enrolled_at=enrollment.enrolled_at
            ))
    
    return students


@router.get("/students/performance", response_model=List[StudentPerformance])
def get_students_performance(
    course_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FACULTY))
):
    """Get performance analytics for students in faculty's courses"""
    # Get faculty's courses
    courses_query = db.query(Course).filter(Course.faculty_id == current_user.id)
    
    if course_id:
        courses_query = courses_query.filter(Course.id == course_id)
    
    courses = courses_query.all()
    course_ids = [course.id for course in courses]
    
    if not course_ids:
        return []
    
    # Get enrollments
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id.in_(course_ids)
    ).all()
    
    performances = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        
        if not student or not course:
            continue
        
        # Calculate quiz performance
        quiz_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == student.id
        ).all()
        
        avg_quiz_score = 0.0
        if quiz_attempts:
            avg_quiz_score = sum(attempt.score for attempt in quiz_attempts) / len(quiz_attempts)
        
        # Calculate assignment performance
        submissions = db.query(AssignmentSubmission).join(Assignment).filter(
            AssignmentSubmission.student_id == student.id,
            Assignment.course_id == course.id,
            AssignmentSubmission.status == SubmissionStatus.GRADED
        ).all()
        
        avg_assignment_score = 0.0
        if submissions:
            avg_assignment_score = sum(sub.score for sub in submissions if sub.score) / len(submissions)
        
        # Calculate learning progress
        learning_progress = db.query(func.avg(LearningProgress.mastery_level)).filter(
            LearningProgress.user_id == student.id,
            LearningProgress.course_id == course.id
        ).scalar()
        
        total_mastery = learning_progress if learning_progress else 0.0
        
        # Calculate total time spent
        total_time = db.query(func.sum(LearningProgress.time_spent_minutes)).filter(
            LearningProgress.user_id == student.id,
            LearningProgress.course_id == course.id
        ).scalar()
        
        total_time_spent = total_time if total_time else 0
        
        # Get last activity
        last_progress = db.query(LearningProgress).filter(
            LearningProgress.user_id == student.id,
            LearningProgress.course_id == course.id
        ).order_by(LearningProgress.last_accessed.desc()).first()
        
        last_activity = last_progress.last_accessed if last_progress else None
        
        performances.append(StudentPerformance(
            student_id=student.id,
            student_name=student.full_name,
            student_email=student.email,
            course_id=course.id,
            course_name=course.name,
            average_quiz_score=round(avg_quiz_score, 2),
            total_quizzes_taken=len(quiz_attempts),
            average_assignment_score=round(avg_assignment_score, 2),
            total_assignments_submitted=len(submissions),
            total_mastery_level=round(total_mastery, 2),
            total_time_spent_minutes=total_time_spent,
            last_activity=last_activity
        ))
    
    return performances[skip:skip + limit]


@router.get("/courses/progress", response_model=List[CourseProgressSummary])
def get_courses_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FACULTY))
):
    """Get progress summary for all faculty's courses"""
    courses = db.query(Course).filter(Course.faculty_id == current_user.id).all()
    
    summaries = []
    for course in courses:
        # Total students
        total_students = db.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()
        
        # Active students
        active_students = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.status == EnrollmentStatus.ACTIVE
        ).count()
        
        # Average mastery
        avg_mastery = db.query(func.avg(LearningProgress.mastery_level)).filter(
            LearningProgress.course_id == course.id
        ).scalar()
        
        # Total time spent
        total_time = db.query(func.sum(LearningProgress.time_spent_minutes)).filter(
            LearningProgress.course_id == course.id
        ).scalar()
        
        total_time_hours = (total_time / 60) if total_time else 0.0
        
        # Average quiz score
        quiz_attempts = db.query(QuizAttempt).join(LearningProgress).filter(
            LearningProgress.course_id == course.id,
            QuizAttempt.user_id == LearningProgress.user_id
        ).all()
        
        avg_quiz_score = 0.0
        if quiz_attempts:
            avg_quiz_score = sum(attempt.score for attempt in quiz_attempts) / len(quiz_attempts)
        
        # Average assignment score
        submissions = db.query(AssignmentSubmission).join(Assignment).filter(
            Assignment.course_id == course.id,
            AssignmentSubmission.status == SubmissionStatus.GRADED
        ).all()
        
        avg_assignment_score = 0.0
        if submissions:
            avg_assignment_score = sum(sub.score for sub in submissions if sub.score) / len(submissions)
        
        summaries.append(CourseProgressSummary(
            course_id=course.id,
            course_name=course.name,
            total_students=total_students,
            active_students=active_students,
            average_mastery=round(avg_mastery, 2) if avg_mastery else 0.0,
            total_time_spent_hours=round(total_time_hours, 2),
            average_quiz_score=round(avg_quiz_score, 2),
            average_assignment_score=round(avg_assignment_score, 2)
        ))
    
    return summaries


@router.get("/students/{student_id}/progress")
def get_student_progress(
    student_id: int,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FACULTY))
):
    """Get detailed progress for a specific student"""
    # Verify student is enrolled in faculty's course
    courses_query = db.query(Course).filter(Course.faculty_id == current_user.id)
    
    if course_id:
        courses_query = courses_query.filter(Course.id == course_id)
    
    courses = courses_query.all()
    course_ids = [course.id for course in courses]
    
    if not course_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No courses found for this faculty"
        )
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.course_id.in_(course_ids)
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not enrolled in any of your courses"
        )
    
    student = db.query(User).filter(User.id == student_id).first()
    
    # Get learning progress
    progress_query = db.query(LearningProgress).filter(
        LearningProgress.user_id == student_id
    )
    
    if course_id:
        progress_query = progress_query.filter(LearningProgress.course_id == course_id)
    
    progress_records = progress_query.all()
    
    # Get quiz attempts
    quiz_query = db.query(QuizAttempt).filter(QuizAttempt.user_id == student_id)
    
    if course_id:
        quiz_query = quiz_query.join(LearningProgress).filter(
            LearningProgress.course_id == course_id,
            QuizAttempt.user_id == LearningProgress.user_id
        )
    
    quiz_attempts = quiz_query.all()
    
    # Get assignment submissions
    submission_query = db.query(AssignmentSubmission).join(Assignment).filter(
        AssignmentSubmission.student_id == student_id
    )
    
    if course_id:
        submission_query = submission_query.filter(Assignment.course_id == course_id)
    
    submissions = submission_query.all()
    
    return {
        "student": {
            "id": student.id,
            "name": student.full_name,
            "email": student.email
        },
        "enrollment": {
            "course_id": enrollment.course_id,
            "status": enrollment.status.value,
            "enrolled_at": enrollment.enrolled_at
        },
        "learning_progress": [
            {
                "topic": p.topic,
                "mastery_level": p.mastery_level,
                "time_spent_minutes": p.time_spent_minutes,
                "last_accessed": p.last_accessed
            }
            for p in progress_records
        ],
        "quiz_performance": {
            "total_attempts": len(quiz_attempts),
            "average_score": round(sum(attempt.score for attempt in quiz_attempts) / len(quiz_attempts), 2) if quiz_attempts else 0.0,
            "recent_attempts": [
                {
                    "quiz_id": attempt.quiz_id,
                    "score": attempt.score,
                    "completed_at": attempt.completed_at
                }
                for attempt in quiz_attempts[-5:]
            ]
        },
        "assignment_performance": {
            "total_submissions": len(submissions),
            "graded_submissions": len([s for s in submissions if s.status == SubmissionStatus.GRADED]),
            "average_score": round(sum(sub.score for sub in submissions if sub.score) / len([s for s in submissions if s.score]), 2) if submissions and any(s.score for s in submissions) else 0.0,
            "recent_submissions": [
                {
                    "assignment_id": sub.assignment_id,
                    "score": sub.score,
                    "status": sub.status.value,
                    "submitted_at": sub.submitted_at
                }
                for sub in submissions[-5:]
            ]
        }
    }
