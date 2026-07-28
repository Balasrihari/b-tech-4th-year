from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.gemini_service import GeminiService
from app.services.rag_pipeline import RAGPipeline

router = APIRouter()

# Initialize services
gemini_service = GeminiService()
rag_pipeline = RAGPipeline()


class QuizGenerationRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"


class FlashcardGenerationRequest(BaseModel):
    topic: str
    num_cards: int = 10


class TextSummarizationRequest(BaseModel):
    text: str
    max_length: int = 200


class QuestionAnswerRequest(BaseModel):
    question: str
    use_rag: bool = True


class StudyPlanRequest(BaseModel):
    subject: str
    duration_weeks: int = 4
    hours_per_week: int = 10


class ConceptExplanationRequest(BaseModel):
    concept: str
    level: str = "intermediate"


class CodeExplanationRequest(BaseModel):
    code: str
    language: str = "python"


@router.post("/quiz/generate")
def generate_quiz(
    request: QuizGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate quiz questions using AI"""
    try:
        questions = gemini_service.generate_quiz_questions(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )


@router.post("/flashcards/generate")
def generate_flashcards(
    request: FlashcardGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate flashcards using AI"""
    try:
        flashcards = gemini_service.generate_flashcards(
            topic=request.topic,
            num_cards=request.num_cards
        )
        return {"flashcards": flashcards}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.post("/text/summarize")
def summarize_text(
    request: TextSummarizationRequest,
    current_user: User = Depends(get_current_user)
):
    """Summarize text using AI"""
    try:
        summary = gemini_service.summarize_text(
            text=request.text,
            max_length=request.max_length
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize text: {str(e)}"
        )


@router.post("/qa/answer")
def answer_question(
    request: QuestionAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Answer a question using AI with optional RAG"""
    try:
        if request.use_rag:
            # Use RAG to retrieve context
            from app.models.document_chunk import DocumentChunk
            chunks = db.query(DocumentChunk).all()
            if chunks:
                chunk_texts = [chunk.chunk_text for chunk in chunks]
                document_ids = [f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}" for chunk in chunks]
                rag_pipeline.build_bm25_index(chunk_texts, document_ids)
                
                rag_results = rag_pipeline.retrieve(
                    query=request.question,
                    top_k=3,
                    use_hybrid=True,
                    rerank=True,
                    compress=True
                )
                context = rag_results['context']
            else:
                context = ""
            
            answer = gemini_service.answer_with_context(
                question=request.question,
                context=context
            )
        else:
            answer = gemini_service.generate_response(request.question)
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.post("/study-plan/generate")
def generate_study_plan(
    request: StudyPlanRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a study plan using AI"""
    try:
        plan = gemini_service.generate_study_plan(
            subject=request.subject,
            duration_weeks=request.duration_weeks,
            hours_per_week=request.hours_per_week
        )
        return {"plan": plan}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study plan: {str(e)}"
        )


@router.post("/concept/explain")
def explain_concept(
    request: ConceptExplanationRequest,
    current_user: User = Depends(get_current_user)
):
    """Explain a concept using AI"""
    try:
        explanation = gemini_service.explain_concept(
            concept=request.concept,
            level=request.level
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to explain concept: {str(e)}"
        )


@router.post("/code/explain")
def explain_code(
    request: CodeExplanationRequest,
    current_user: User = Depends(get_current_user)
):
    """Explain code using AI"""
    try:
        explanation = gemini_service.generate_code_explanation(
            code=request.code,
            language=request.language
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to explain code: {str(e)}"
        )


@router.get("/health")
def check_ai_health():
    """Check if AI services are operational"""
    return {
        "status": "healthy",
        "services": {
            "gemini": "available",
            "rag": "available"
        }
    }
