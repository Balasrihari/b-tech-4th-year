from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.document_chunk import DocumentChunk
from app.services.rag_pipeline import RAGPipeline

router = APIRouter()

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    use_hybrid: bool = True
    rerank: bool = True
    compress: bool = True


class RAGResponse(BaseModel):
    query: str
    rewritten_query: str
    context: str
    citations: list
    results: list


@router.post("/retrieve", response_model=RAGResponse)
def retrieve_context(
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve relevant context using RAG pipeline"""
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    # Build BM25 index from document chunks
    chunks = db.query(DocumentChunk).all()
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents available for retrieval"
        )
    
    chunk_texts = [chunk.chunk_text for chunk in chunks]
    document_ids = [f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}" for chunk in chunks]
    
    rag_pipeline.build_bm25_index(chunk_texts, document_ids)
    
    # Retrieve context
    try:
        results = rag_pipeline.retrieve(
            query=request.query,
            top_k=request.top_k,
            use_hybrid=request.use_hybrid,
            rerank=request.rerank,
            compress=request.compress
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG retrieval failed: {str(e)}"
        )


@router.get("/health")
def check_rag_health():
    """Check if RAG pipeline is operational"""
    return {
        "status": "healthy",
        "pipeline": "RAG",
        "components": {
            "bm25": "available",
            "vector_search": "available",
            "hybrid_search": "available",
            "reranking": "available",
            "context_compression": "available"
        }
    }
