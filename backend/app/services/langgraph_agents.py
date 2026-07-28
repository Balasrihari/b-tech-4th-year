"""
LangGraph Agents System
Implements a multi-agent system using LangGraph with specialized AI agents
"""
from typing import Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.services.gemini_service import GeminiService
from app.services.rag_pipeline import RAGPipeline
import operator


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    current_agent: str
    context: Dict
    next_action: str


class LangGraphAgentSystem:
    """Multi-agent system using LangGraph"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=settings.GEMINI_API_KEY
        )
        self.gemini_service = GeminiService()
        self.rag_pipeline = RAGPipeline()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph with all agents"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", self.supervisor_agent)
        workflow.add_node("academic", self.academic_agent)
        workflow.add_node("rag", self.rag_agent)
        workflow.add_node("coding", self.coding_agent)
        workflow.add_node("quiz", self.quiz_agent)
        workflow.add_node("study_planner", self.study_planner_agent)
        workflow.add_node("analytics", self.analytics_agent)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.route_to_agent,
            {
                "academic": "academic",
                "rag": "rag",
                "coding": "coding",
                "quiz": "quiz",
                "study_planner": "study_planner",
                "analytics": "analytics",
                "end": END
            }
        )
        
        # All agents return to supervisor
        workflow.add_edge("academic", "supervisor")
        workflow.add_edge("rag", "supervisor")
        workflow.add_edge("coding", "supervisor")
        workflow.add_edge("quiz", "supervisor")
        workflow.add_edge("study_planner", "supervisor")
        workflow.add_edge("analytics", "supervisor")
        
        return workflow.compile()
    
    def route_to_agent(self, state: AgentState) -> str:
        """Route to appropriate agent based on supervisor decision"""
        return state.get("next_action", "end")
    
    def supervisor_agent(self, state: AgentState) -> AgentState:
        """Supervisor agent that routes requests to appropriate specialized agents"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        # Analyze the request and determine which agent should handle it
        prompt = f"""
        You are a supervisor agent. Analyze the following user request and determine which specialized agent should handle it.
        
        Available agents:
        - academic: For academic questions, concept explanations, study help
        - rag: For questions that require document retrieval and context
        - coding: For code-related questions, debugging, programming help
        - quiz: For quiz generation, test preparation
        - study_planner: For creating study plans, scheduling
        - analytics: For performance analysis, learning analytics
        
        User request: {last_message}
        
        Respond with only the agent name (one of: academic, rag, coding, quiz, study_planner, analytics, end)
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            agent_name = response.content.strip().lower()
            
            # Validate agent name
            valid_agents = ["academic", "rag", "coding", "quiz", "study_planner", "analytics", "end"]
            if agent_name not in valid_agents:
                agent_name = "academic"  # Default to academic
            
            state["current_agent"] = "supervisor"
            state["next_action"] = agent_name
            state["messages"].append(AIMessage(content=f"Routed to {agent_name} agent"))
            
        except Exception as e:
            state["next_action"] = "academic"
            state["messages"].append(AIMessage(content=f"Error in routing: {str(e)}"))
        
        return state
    
    def academic_agent(self, state: AgentState) -> AgentState:
        """Academic agent for general academic questions and concept explanations"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # Use Gemini service for academic responses
            response = self.gemini_service.generate_response(
                f"Provide a detailed academic explanation for: {last_message}",
                temperature=0.7
            )
            
            state["current_agent"] = "academic"
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Academic agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def rag_agent(self, state: AgentState) -> AgentState:
        """RAG agent for document-based question answering"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # Use RAG pipeline to retrieve context
            rag_results = self.rag_pipeline.retrieve(
                query=str(last_message),
                top_k=3,
                use_hybrid=True,
                rerank=True,
                compress=True
            )
            
            # Use Gemini to answer with context
            response = self.gemini_service.answer_with_context(
                question=str(last_message),
                context=rag_results['context']
            )
            
            state["current_agent"] = "rag"
            state["context"] = rag_results
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"RAG agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def coding_agent(self, state: AgentState) -> AgentState:
        """Coding agent for programming and code-related questions"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # Detect if code is in the message
            message_str = str(last_message).lower()
            
            if "```" in message_str or "def " in message_str or "function" in message_str:
                # Extract code and explain it
                response = self.gemini_service.generate_code_explanation(
                    code=str(last_message),
                    language="python" if "python" in message_str else "general"
                )
            else:
                # General coding help
                response = self.gemini_service.generate_response(
                    f"Provide coding help for: {last_message}",
                    temperature=0.6
                )
            
            state["current_agent"] = "coding"
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Coding agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def quiz_agent(self, state: AgentState) -> AgentState:
        """Quiz agent for generating quizzes and test preparation"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # Extract topic from message
            message_str = str(last_message).lower()
            
            # Simple topic extraction (in production, use NLP)
            topic = message_str.replace("quiz", "").replace("test", "").replace("generate", "").strip()
            if not topic:
                topic = "general knowledge"
            
            # Generate quiz questions
            questions = self.gemini_service.generate_quiz_questions(
                topic=topic,
                num_questions=5,
                difficulty="medium"
            )
            
            response = f"Generated quiz on {topic}:\n\n"
            for i, q in enumerate(questions, 1):
                response += f"Q{i}: {q['question']}\n"
                response += f"Options: {', '.join(q['options'])}\n"
                response += f"Correct: {q['options'][q['correct_answer']]}\n\n"
            
            state["current_agent"] = "quiz"
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Quiz agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def study_planner_agent(self, state: AgentState) -> AgentState:
        """Study planner agent for creating personalized study plans"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # Extract subject and parameters from message
            message_str = str(last_message).lower()
            
            # Simple extraction (in production, use NLP)
            subject = message_str.replace("study plan", "").replace("schedule", "").strip()
            if not subject:
                subject = "general studies"
            
            # Generate study plan
            plan = self.gemini_service.generate_study_plan(
                subject=subject,
                duration_weeks=4,
                hours_per_week=10
            )
            
            response = f"Study Plan for {subject}:\n\n"
            response += f"Weekly Goals: {', '.join(plan['weekly_goals'])}\n"
            response += f"Daily Schedule: {plan['daily_schedule']}\n"
            response += f"Topics to Cover: {', '.join(plan['topics'])}\n"
            response += f"Resources: {', '.join(plan['resources'])}\n"
            
            state["current_agent"] = "study_planner"
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Study planner agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def analytics_agent(self, state: AgentState) -> AgentState:
        """Analytics agent for performance analysis and learning insights"""
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            # In a real implementation, this would query the database for user performance data
            # For now, provide a template response
            response = """
            Learning Analytics Summary:
            
            Performance Metrics:
            - Overall Progress: 65%
            - Quiz Average: 78%
            - Study Time: 12 hours this week
            - Assignments Completed: 8/10
            
            Strengths:
            - Strong performance in Mathematics
            - Consistent study habits
            - Good quiz completion rate
            
            Areas for Improvement:
            - Focus on Physics concepts
            - Increase practice problem solving
            - Review past quiz mistakes
            
            Recommendations:
            - Spend 2 more hours on Physics weekly
            - Complete 5 additional practice problems
            - Review weak topics from analytics dashboard
            """
            
            state["current_agent"] = "analytics"
            state["messages"].append(AIMessage(content=response))
            state["next_action"] = "end"
            
        except Exception as e:
            state["messages"].append(AIMessage(content=f"Analytics agent error: {str(e)}"))
            state["next_action"] = "end"
        
        return state
    
    def run(self, user_message: str) -> Dict:
        """Run the agent system with a user message"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_message)],
            "current_agent": "",
            "context": {},
            "next_action": ""
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            
            return {
                "response": final_state["messages"][-1].content if final_state["messages"] else "No response",
                "agent_used": final_state.get("current_agent", "unknown"),
                "context": final_state.get("context", {}),
                "all_messages": [msg.content for msg in final_state["messages"]]
            }
        except Exception as e:
            return {
                "response": f"Agent system error: {str(e)}",
                "agent_used": "error",
                "context": {},
                "all_messages": []
            }
