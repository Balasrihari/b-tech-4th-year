from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType
from app.models.document_chunk import DocumentChunk
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentChunkResponse, DocumentWithChunks
)
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.ocr_service import ocr_service
from app.services.web_scraping_service import web_scraping_service

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str,
    document_type: DocumentType,
    description: str = None,
    course_id: int = None,
    file: UploadFile = File(...),
    url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document (file or URL)"""
    
    # Handle URL upload
    if url:
        if not web_scraping_service.is_valid_url(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format"
            )
        
        try:
            # Extract content from URL
            content_data = web_scraping_service.extract_content_from_url(url)
            
            # Create document from URL content
            document = Document(
                title=title or content_data['title'],
                description=description or content_data.get('metadata', {}).get('description', ''),
                file_type='url',
                file_size=len(content_data['content'].encode()),
                word_count=content_data['word_count'],
                page_count=1,
                processing_status="processing",
                uploaded_by_id=current_user.id,
                course_id=course_id,
                source_url=url
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Process content
            text = content_data['content']
            chunks = document_processor.chunk_text(text)
            
            # Create chunks
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk_text,
                    token_count=len(chunk_text.split())
                )
                db.add(chunk)
            
            # Generate embeddings
            embedding_service.generate_embeddings_for_document(document.id, db)
            
            # Update document status
            document.processing_status = "completed"
            document.page_count = len(chunks)
            db.commit()
            db.refresh(document)
            
            return document
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process URL: {str(e)}"
            )
    
    # Handle file upload
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file or URL must be provided"
        )
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    valid_extensions = ['pdf', 'docx', 'pptx', 'xlsx', 'txt', 'md', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']
    
    if file_extension not in valid_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Supported types: {', '.join(valid_extensions)}"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Process document (handle images with OCR)
    try:
        # Check if file is an image (OCR required)
        if file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
            # Preprocess image for better OCR
            preprocessed_contents = ocr_service.preprocess_image(contents)
            
            # Extract text using OCR
            text = ocr_service.extract_text_from_image(preprocessed_contents)
            
            processed = {
                'text': text,
                'chunks': document_processor.chunk_text(text),
                'metadata': {
                    'page_count': 1,
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'ocr_used': True
                }
            }
        else:
            # Process regular document
            processed = document_processor.process_document(str(file_path), file_extension)
    except Exception as e:
        # Clean up file if processing fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )
    
    # Create document record
    db_document = Document(
        title=title,
        description=description,
        file_type=file_extension,
        file_path=str(file_path),
        file_size=len(contents),
        page_count=processed['metadata'].get('page_count'),
        word_count=processed['metadata'].get('word_count'),
        char_count=processed['metadata'].get('char_count'),
        processing_status="completed",
        uploaded_by_id=current_user.id,
        course_id=course_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Create document chunks
    chunks = []
    for idx, chunk_text in enumerate(processed['chunks']):
        db_chunk = DocumentChunk(
            document_id=db_document.id,
            chunk_index=idx,
            content=chunk_text,
            token_count=len(chunk_text.split())
        )
        db.add(db_chunk)
        chunks.append(db_chunk)
    
    db.commit()
    
    # Generate and store embeddings
    try:
        embedding_service.generate_embeddings_for_document(db_document.id, db)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to generate embeddings: {str(e)}")
    
    return db_document


@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    document_type: DocumentType = None,
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get documents based on user role"""
    query = db.query(Document)
    
    if current_user.role.value == "student":
        # Students see their own documents
        query = query.filter(Document.user_id == current_user.id)
    elif current_user.role.value == "faculty":
        # Faculty see their own documents
        query = query.filter(Document.user_id == current_user.id)
    # Admin can see all documents
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if course_id:
        query = query.filter(Document.course_id == course_id)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentWithChunks)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document with chunks"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if current_user.role.value == "student" and document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own documents"
        )
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if db_document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own documents"
        )
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if db_document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own documents"
        )
    
    # Delete file from filesystem
    try:
        if os.path.exists(db_document.file_path):
            os.unlink(db_document.file_path)
    except Exception:
        pass
    
    # Delete from database (chunks will be cascade deleted)
    db.delete(db_document)
    db.commit()
    
    return None


@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chunks for a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check permissions
    if current_user.role.value == "student" and document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own documents"
        )
    
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()
    
    return chunks
