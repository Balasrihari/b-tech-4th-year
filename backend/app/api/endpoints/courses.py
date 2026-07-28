from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.auth.dependencies import get_current_active_user, require_role

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
def get_courses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all courses (accessible by all authenticated users)"""
    courses = db.query(Course).filter(Course.is_active == True).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific course by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db)
):
    """Create a new course (faculty only)"""
    # Verify faculty_id matches current user
    if course.faculty_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You can only create courses for yourself"
        )
    
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db)
):
    """Update a course (faculty only - only own courses)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Faculty can only update their own courses (admin can update any)
    if current_user.role != UserRole.ADMIN and course.faculty_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own courses"
        )
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    current_user: User = Depends(require_role(UserRole.FACULTY)),
    db: Session = Depends(get_db)
):
    """Delete a course (faculty only - only own courses)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Faculty can only delete their own courses (admin can delete any)
    if current_user.role != UserRole.ADMIN and course.faculty_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own courses"
        )
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
