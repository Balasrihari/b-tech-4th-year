from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.analytics import Analytics
from pydantic import BaseModel

router = APIRouter()


# Schemas
class DocumentStatistics(BaseModel):
    total_documents: int
    documents_by_type: dict
    total_storage_used_bytes: int
    documents_by_user: int
    documents_processed: int
    documents_processing: int
    documents_failed: int
    average_file_size: float
    total_word_count: int
    total_page_count: int


class AIUsageStatistics(BaseModel):
    total_ai_requests: int
    requests_by_type: dict
    total_tokens_used: int
    average_tokens_per_request: float
    requests_last_24h: int
    requests_last_7d: int
    requests_last_30d: int
    error_rate: float
    average_response_time_ms: float


@router.get("/dashboard")
def get_admin_dashboard(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    return {
        "message": "Admin dashboard",
        "user": current_user.email,
        "role": current_user.role.value
    }


@router.get("/statistics/documents", response_model=DocumentStatistics)
def get_document_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get document statistics (Admin only)"""
    # Total documents
    total_documents = db.query(Document).count()
    
    # Documents by type
    documents_by_type = {}
    for doc_type in ['study_material', 'assignment', 'reference', 'notes']:
        count = db.query(Document).filter(Document.document_type == doc_type).count()
        documents_by_type[doc_type] = count
    
    # Total storage used
    total_storage = db.query(func.sum(Document.file_size)).scalar() or 0
    
    # Documents by user (unique users)
    documents_by_user = db.query(func.count(func.distinct(Document.user_id))).scalar() or 0
    
    # Processing status
    documents_processed = db.query(Document).filter(Document.processing_status == 'completed').count()
    documents_processing = db.query(Document).filter(Document.processing_status == 'processing').count()
    documents_failed = db.query(Document).filter(Document.processing_status == 'failed').count()
    
    # Average file size
    avg_file_size = total_storage / total_documents if total_documents > 0 else 0
    
    # Total word count
    total_word_count = db.query(func.sum(Document.word_count)).scalar() or 0
    
    # Total page count
    total_page_count = db.query(func.sum(Document.page_count)).scalar() or 0
    
    return DocumentStatistics(
        total_documents=total_documents,
        documents_by_type=documents_by_type,
        total_storage_used_bytes=total_storage,
        documents_by_user=documents_by_user,
        documents_processed=documents_processed,
        documents_processing=documents_processing,
        documents_failed=documents_failed,
        average_file_size=round(avg_file_size, 2),
        total_word_count=total_word_count,
        total_page_count=total_page_count
    )


@router.get("/statistics/ai-usage", response_model=AIUsageStatistics)
def get_ai_usage_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get AI usage statistics (Admin only)"""
    # Total AI requests
    total_ai_requests = db.query(Analytics).filter(
        Analytics.metric_type == 'ai_request'
    ).count()
    
    # Requests by type
    requests_by_type = {}
    ai_types = ['chat', 'document_qa', 'quiz_generation', 'roadmap_generation', 'recommendations']
    for ai_type in ai_types:
        count = db.query(Analytics).filter(
            Analytics.metric_type == 'ai_request',
            Analytics.metric_name == ai_type
        ).count()
        requests_by_type[ai_type] = count
    
    # Total tokens used
    total_tokens = db.query(func.sum(Analytics.metric_value)).filter(
        Analytics.metric_type == 'token_usage'
    ).scalar() or 0
    
    # Average tokens per request
    avg_tokens = total_tokens / total_ai_requests if total_ai_requests > 0 else 0
    
    # Requests in time periods
    now = datetime.utcnow()
    requests_last_24h = db.query(Analytics).filter(
        Analytics.metric_type == 'ai_request',
        Analytics.created_at >= now - timedelta(hours=24)
    ).count()
    
    requests_last_7d = db.query(Analytics).filter(
        Analytics.metric_type == 'ai_request',
        Analytics.created_at >= now - timedelta(days=7)
    ).count()
    
    requests_last_30d = db.query(Analytics).filter(
        Analytics.metric_type == 'ai_request',
        Analytics.created_at >= now - timedelta(days=30)
    ).count()
    
    # Error rate (assuming error metric exists)
    total_errors = db.query(Analytics).filter(
        Analytics.metric_type == 'ai_error'
    ).count()
    error_rate = (total_errors / total_ai_requests * 100) if total_ai_requests > 0 else 0
    
    # Average response time (assuming response_time metric exists)
    avg_response_time = db.query(func.avg(Analytics.metric_value)).filter(
        Analytics.metric_type == 'response_time'
    ).scalar() or 0
    
    return AIUsageStatistics(
        total_ai_requests=total_ai_requests,
        requests_by_type=requests_by_type,
        total_tokens_used=int(total_tokens),
        average_tokens_per_request=round(avg_tokens, 2),
        requests_last_24h=requests_last_24h,
        requests_last_7d=requests_last_7d,
        requests_last_30d=requests_last_30d,
        error_rate=round(error_rate, 2),
        average_response_time_ms=round(avg_response_time, 2)
    )
