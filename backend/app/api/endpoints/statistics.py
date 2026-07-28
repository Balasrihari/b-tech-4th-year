from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.document import Document
from app.models.assignment import Assignment
from app.models.quiz import Quiz
from app.models.todo import Todo
from app.models.enrollment import Enrollment
from app.auth.dependencies import get_current_active_user, require_role

router = APIRouter()


@router.get("/system")
def get_system_statistics(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics (admin only)"""
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_faculty = db.query(User).filter(User.role == UserRole.FACULTY).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    total_courses = db.query(Course).count()
    total_documents = db.query(Document).count()
    total_assignments = db.query(Assignment).count()
    total_quizzes = db.query(Quiz).count()
    total_todos = db.query(Todo).count()
    total_enrollments = db.query(Enrollment).count()
    
    return {
        "users": {
            "total": total_users,
            "students": total_students,
            "faculty": total_faculty,
            "admins": total_admins
        },
        "courses": total_courses,
        "documents": total_documents,
        "assignments": total_assignments,
        "quizzes": total_quizzes,
        "todos": total_todos,
        "enrollments": total_enrollments
    }


@router.get("/user")
def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for the current user"""
    user_id = current_user.id
    
    if current_user.role == UserRole.STUDENT:
        enrolled_courses = db.query(Enrollment).filter(Enrollment.student_id == user_id).count()
        user_todos = db.query(Todo).filter(Todo.user_id == user_id).count()
        pending_todos = db.query(Todo).filter(
            Todo.user_id == user_id,
            Todo.status != "completed"
        ).count()
        
        return {
            "enrolled_courses": enrolled_courses,
            "total_todos": user_todos,
            "pending_todos": pending_todos
        }
    
    elif current_user.role == UserRole.FACULTY:
        courses_taught = db.query(Course).filter(Course.faculty_id == user_id).count()
        
        return {
            "courses_taught": courses_taught
        }
    
    elif current_user.role == UserRole.ADMIN:
        return get_system_statistics(current_user, db)
