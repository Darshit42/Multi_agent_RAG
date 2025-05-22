from typing import Any, Dict, List, Optional
from ..agents.query_agent import QueryUnderstandingAgent
from ..agents.retrieval_agent import RetrievalAgent
from ..agents.response_agent import ResponseGenerationAgent

class AgentOrchestrator:    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        self.query_agent = QueryUnderstandingAgent(
            name="query_understanding",
            config=self.config.get("query_agent", {})
        )
        
        self.retrieval_agent = RetrievalAgent(
            name="retrieval",
            config=self.config.get("retrieval_agent", {})
        )
        
        self.response_agent = ResponseGenerationAgent(
            name="response_generation",
            config=self.config.get("response_agent", {})
        )
    
    async def process_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        try:
            query_analysis = self.query_agent.run(query)
            
            retrieval_results = await self.retrieval_agent.run_async({
                "query": query,
                "top_k": top_k
            })
            
            response = self.response_agent.run({
                "query": query,
                "context": retrieval_results.get("results", [])
            })
            
            return {
                "query_analysis": query_analysis,
                "retrieval_results": retrieval_results,
                "response": response,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def add_documents(self, documents: List[str]) -> None:
        self.retrieval_agent.add_documents(documents)
    
    def clear_index(self) -> None:
        self.retrieval_agent.clear_index()
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "query_agent": self.query_agent.get_status(),
            "retrieval_agent": self.retrieval_agent.get_status(),
            "response_agent": self.response_agent.get_status(),
            "index_stats": self.retrieval_agent.get_index_stats()
        } 