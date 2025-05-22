from typing import Any, Dict, List, Optional
import google.generativeai as genai
from .base_agent import BaseAgent
import json
import os

class ResponseGenerationAgent(BaseAgent):    
    def _initialize(self) -> None:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.config.get("model", "gemini-2.0-flash"))
        self.max_tokens = self.config.get("max_tokens", 500)
        self.temperature = self.config.get("temperature", 0.7)
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are an expert FAQ response generator. Generate clear, concise and accurate responses based on the provided context."
        )
    
    async def validate(self, input_data: Dict[str, Any]) -> bool:
        required_keys = ["query", "context"]
        return all(key in input_data for key in required_keys) and isinstance(input_data["context"], list)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data["query"]
        context = input_data["context"]

        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc['document']}"
            for i, doc in enumerate(context)
        ])

        prompt = f"""
        {self.system_prompt}
        
        Based on the following context, please provide a clear and accurate answer to the query.
        
        Query: {query}
        
        Context:
        {context_text}
        
        Please provide a response that:
        1. Directly answers the query
        2. Uses information from the context
        3. Is clear and concise
        4. Maintains a professional tone
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )
        
        generated_response = response.text.strip()
        
        quality_metrics = self._analyze_response_quality(
            query=query,
            context=context,
            response=generated_response
        )
        
        return {
            "query": query,
            "response": generated_response,
            "quality_metrics": quality_metrics,
            "context_used": len(context)
        }
    
    def _analyze_response_quality(self, query: str, context: List[Dict[str, Any]], response: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following FAQ response and return a JSON object with:
        1. relevance_score (1-5, where 5 is highest)
        2. accuracy_score (1-5, where 5 is highest)
        3. clarity_score (1-5, where 5 is highest)
        4. context_usage_score (1-5, where 5 is highest)
        5. suggested_improvements (list of specific improvements)
        
        Query: {query}
        
        Response: {response}
        """
        
        analysis = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=200,
            )
        )
        
        try:
            return json.loads(analysis.text)
        except json.JSONDecodeError:
            return {
                "relevance_score": 3,
                "accuracy_score": 3,
                "clarity_score": 3,
                "context_usage_score": 3,
                "suggested_improvements": ["Unable to analyze response quality"]
            } 