"""Multi-Agent System using LangGraph"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from loguru import logger
import operator


class AgentState(TypedDict):
    """State for the multi-agent system"""
    messages: Annotated[List, operator.add]
    current_agent: str
    context: Dict[str, Any]
    query: str
    results: Dict[str, Any]


class MultiAgentSystem:
    """Multi-agent system using LangGraph for coordinated AI responses"""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.agents = {
            "supervisor": self._supervisor_agent,
            "academic": self._academic_agent,
            "rag": self._rag_agent,
            "coding": self._coding_agent,
            "quiz": self._quiz_agent,
            "planner": self._planner_agent,
            "analytics": self._analytics_agent
        }
        
        logger.info("Multi-agent system initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for the multi-agent system"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("academic", self._academic_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("coding", self._coding_node)
        workflow.add_node("quiz", self._quiz_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("analytics", self._analytics_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {
                "academic": "academic",
                "rag": "rag",
                "coding": "coding",
                "quiz": "quiz",
                "planner": "planner",
                "analytics": "analytics",
                "end": END
            }
        )
        
        # All agents return to supervisor
        for agent in ["academic", "rag", "coding", "quiz", "planner", "analytics"]:
            workflow.add_edge(agent, "supervisor")
        
        return workflow.compile()
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Route query to appropriate agent based on query type"""
        query = state["query"].lower()
        
        # Simple routing logic
        if any(keyword in query for keyword in ["code", "programming", "function", "debug", "python", "javascript"]):
            return "coding"
        elif any(keyword in query for keyword in ["quiz", "test", "question", "practice"]):
            return "quiz"
        elif any(keyword in query for keyword in ["plan", "schedule", "roadmap", "study"]):
            return "planner"
        elif any(keyword in query for keyword in ["analytics", "progress", "performance", "statistics"]):
            return "analytics"
        elif any(keyword in query for keyword in ["document", "search", "find", "what is"]):
            return "rag"
        else:
            return "academic"
    
    async def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor agent that coordinates other agents"""
        logger.info(f"Supervisor processing query: {state['query']}")
        
        # Determine if we need to route to another agent
        if not state.get("results"):
            # First pass - route to appropriate agent
            return state
        else:
            # Results collected - prepare final response
            state["messages"].append(
                AIMessage(content=self._compile_results(state["results"]))
            )
            return state
    
    async def _academic_node(self, state: AgentState) -> AgentState:
        """Academic agent for general academic queries"""
        logger.info("Academic agent processing")
        
        from app.services.gemini_service import gemini_service
        
        response = await gemini_service.generate_response(
            f"Answer this academic question: {state['query']}"
        )
        
        state["results"]["academic"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def _rag_node(self, state: AgentState) -> AgentState:
        """RAG agent for document-based queries"""
        logger.info("RAG agent processing")
        
        from app.services.rag_service import rag_service
        
        response = await rag_service.query_documents(state["query"])
        
        state["results"]["rag"] = response
        state["messages"].append(AIMessage(content=response["answer"]))
        
        return state
    
    async def _coding_node(self, state: AgentState) -> AgentState:
        """Coding agent for programming queries"""
        logger.info("Coding agent processing")
        
        from app.services.gemini_service import gemini_service
        
        response = await gemini_service.generate_response(
            f"Help with this coding question: {state['query']}. Provide code examples."
        )
        
        state["results"]["coding"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def _quiz_node(self, state: AgentState) -> AgentState:
        """Quiz agent for quiz generation"""
        logger.info("Quiz agent processing")
        
        from app.services.gemini_service import gemini_service
        
        response = await gemini_service.generate_response(
            f"Generate a quiz question based on: {state['query']}"
        )
        
        state["results"]["quiz"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def _planner_node(self, state: AgentState) -> AgentState:
        """Study planner agent"""
        logger.info("Study planner agent processing")
        
        from app.services.gemini_service import gemini_service
        
        response = await gemini_service.generate_response(
            f"Create a study plan for: {state['query']}"
        )
        
        state["results"]["planner"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    async def _analytics_node(self, state: AgentState) -> AgentState:
        """Analytics agent for learning analytics"""
        logger.info("Analytics agent processing")
        
        from app.services.gemini_service import gemini_service
        
        response = await gemini_service.generate_response(
            f"Analyze learning progress for: {state['query']}"
        )
        
        state["results"]["analytics"] = response
        state["messages"].append(AIMessage(content=response))
        
        return state
    
    def _compile_results(self, results: Dict[str, Any]) -> str:
        """Compile results from multiple agents into final response"""
        if not results:
            return "I couldn't find a specific answer to your question."
        
        # If only one agent responded, return its result
        if len(results) == 1:
            return list(results.values())[0]
        
        # Multiple agents responded - combine results
        combined = []
        for agent, result in results.items():
            combined.append(f"**{agent.title()} Agent:** {result}")
        
        return "\n\n".join(combined)
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system
        
        Args:
            query: User query
            context: Optional context for the query
            
        Returns:
            Response from the agent system
        """
        try:
            initial_state: AgentState = {
                "messages": [HumanMessage(content=query)],
                "current_agent": "supervisor",
                "context": context or {},
                "query": query,
                "results": {}
            }
            
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract final response
            final_message = final_state["messages"][-1]
            
            return {
                "answer": final_message.content,
                "agent_used": final_state.get("current_agent", "supervisor"),
                "results": final_state.get("results", {})
            }
            
        except Exception as e:
            logger.error(f"Multi-agent processing failed: {e}")
            return {
                "answer": "I encountered an error processing your request.",
                "agent_used": "error",
                "results": {}
            }
    
    def _supervisor_agent(self, state: AgentState) -> str:
        """Supervisor agent logic"""
        query = state["query"].lower()
        
        # Determine which agent should handle the query
        if "code" in query or "programming" in query:
            return "coding"
        elif "quiz" in query or "test" in query:
            return "quiz"
        elif "plan" in query or "schedule" in query:
            return "planner"
        elif "analytics" in query or "progress" in query:
            return "analytics"
        elif "document" in query or "search" in query:
            return "rag"
        else:
            return "academic"
    
    def _academic_agent(self, query: str) -> str:
        """Academic agent logic"""
        return f"Academic response to: {query}"
    
    def _rag_agent(self, query: str) -> str:
        """RAG agent logic"""
        return f"RAG response to: {query}"
    
    def _coding_agent(self, query: str) -> str:
        """Coding agent logic"""
        return f"Coding response to: {query}"
    
    def _quiz_agent(self, query: str) -> str:
        """Quiz agent logic"""
        return f"Quiz response to: {query}"
    
    def _planner_agent(self, query: str) -> str:
        """Study planner agent logic"""
        return f"Planner response to: {query}"
    
    def _analytics_agent(self, query: str) -> str:
        """Analytics agent logic"""
        return f"Analytics response to: {query}"


# Global multi-agent system instance
multi_agent_system = MultiAgentSystem()
