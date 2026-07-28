from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment, AssignmentStatus
from app.models.assignment_submission import AssignmentSubmission, SubmissionStatus
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentSubmissionCreate, AssignmentSubmissionUpdate,
    AssignmentSubmissionResponse, AssignmentWithSubmissions
)

router = APIRouter()


# Assignment Endpoints (Faculty only)

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new assignment (Faculty only)"""
    if current_user.role != UserRole.FACULTY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty can create assignments"
        )
    
    db_assignment = Assignment(
        faculty_id=current_user.id,
        title=assignment.title,
        description=assignment.description,
        course_id=assignment.course_id,
        due_date=assignment.due_date,
        max_score=assignment.max_score,
        status=assignment.status
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.get("/", response_model=List[AssignmentResponse])
def get_assignments(
    course_id: int = None,
    status: AssignmentStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignments based on user role"""
    query = db.query(Assignment)
    
    if current_user.role == UserRole.FACULTY:
        # Faculty sees their own assignments
        query = query.filter(Assignment.faculty_id == current_user.id)
    elif current_user.role == UserRole.STUDENT:
        # Students see published assignments from their enrolled courses
        query = query.filter(Assignment.status == AssignmentStatus.PUBLISHED)
    # Admin can see all assignments
    
    if course_id:
        query = query.filter(Assignment.course_id == course_id)
    
    if status:
        query = query.filter(Assignment.status == status)
    
    assignments = query.order_by(Assignment.created_at.desc()).offset(skip).limit(limit).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentWithSubmissions)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific assignment with submissions"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.FACULTY and assignment.faculty_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own assignments"
        )
    
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an assignment (Faculty only)"""
    if current_user.role != UserRole.FACULTY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty can update assignments"
        )
    
    db_assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.faculty_id == current_user.id
    ).first()
    
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    update_data = assignment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assignment, field, value)
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an assignment (Faculty only)"""
    if current_user.role != UserRole.FACULTY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty can delete assignments"
        )
    
    db_assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.faculty_id == current_user.id
    ).first()
    
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    db.delete(db_assignment)
    db.commit()
    return None


# Assignment Submission Endpoints (Students submit, Faculty grade)

@router.post("/{assignment_id}/submissions", response_model=AssignmentSubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    assignment_id: int,
    submission: AssignmentSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an assignment (Student only)"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit assignments"
        )
    
    # Check if assignment exists and is published
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.status == AssignmentStatus.PUBLISHED
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not published"
        )
    
    # Check if already submitted
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this assignment"
        )
    
    db_submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=submission.content,
        file_path=submission.file_path,
        status=SubmissionStatus.SUBMITTED,
        submitted_at=datetime.utcnow()
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionResponse])
def get_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get submissions for an assignment"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    if current_user.role == UserRole.FACULTY:
        # Faculty sees all submissions for their assignment
        if assignment.faculty_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view submissions for your assignments"
            )
        submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id
        ).all()
    elif current_user.role == UserRole.STUDENT:
        # Students see only their own submission
        submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        ).all()
    else:
        # Admin sees all
        submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id
        ).all()
    
    return submissions


@router.put("/submissions/{submission_id}", response_model=AssignmentSubmissionResponse)
def grade_submission(
    submission_id: int,
    submission_update: AssignmentSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Grade a submission (Faculty only)"""
    if current_user.role != UserRole.FACULTY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty can grade submissions"
        )
    
    db_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not db_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check if faculty owns the assignment
    assignment = db.query(Assignment).filter(
        Assignment.id == db_submission.assignment_id
    ).first()
    
    if assignment.faculty_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only grade submissions for your assignments"
        )
    
    update_data = submission_update.model_dump(exclude_unset=True)
    
    # If grading, set status to graded and graded_at
    if 'score' in update_data or 'feedback' in update_data:
        update_data['status'] = SubmissionStatus.GRADED
        update_data['graded_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_submission, field, value)
    
    db.commit()
    db.refresh(db_submission)
    return db_submission


@router.get("/my/submissions", response_model=List[AssignmentSubmissionResponse])
def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's submissions (Student only)"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their submissions"
        )
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == current_user.id
    ).order_by(AssignmentSubmission.created_at.desc()).all()
    
    return submissions
