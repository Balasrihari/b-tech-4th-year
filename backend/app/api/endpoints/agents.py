from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.models.user import User
from app.services.langgraph_agents import LangGraphAgentSystem

router = APIRouter()

# Initialize agent system
agent_system = LangGraphAgentSystem()


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str
    agent_used: str
    context: dict
    all_messages: list


@router.post("/chat", response_model=AgentResponse)
def chat_with_agents(
    request: AgentRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with the multi-agent system"""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    try:
        result = agent_system.run(request.message)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent system error: {str(e)}"
        )


@router.get("/health")
def check_agents_health():
    """Check if agent system is operational"""
    return {
        "status": "healthy",
        "system": "LangGraph Multi-Agent",
        "agents": [
            "supervisor",
            "academic",
            "rag",
            "coding",
            "quiz",
            "study_planner",
            "analytics"
        ]
    }
