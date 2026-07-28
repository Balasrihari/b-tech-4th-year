from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentSubmissionCreate, AssignmentSubmissionUpdate,
    AssignmentSubmissionResponse, AssignmentWithSubmissions
)
from app.schemas.audit_log import AuditLogResponse, AuditLogWithUser
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentChunkResponse, DocumentWithChunks
)

__all__ = [
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "AssignmentSubmissionCreate",
    "AssignmentSubmissionUpdate",
    "AssignmentSubmissionResponse",
    "AssignmentWithSubmissions",
    "AuditLogResponse",
    "AuditLogWithUser",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentChunkResponse",
    "DocumentWithChunks",
]
