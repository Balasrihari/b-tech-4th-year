from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/dashboard")
def get_student_dashboard(
    current_user: User = Depends(require_role(UserRole.STUDENT))
):
    return {
        "message": "Student dashboard",
        "user": current_user.email,
        "role": current_user.role.value
    }
