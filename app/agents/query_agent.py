from typing import Any, Dict, List, Optional
import google.generativeai as genai
from .base_agent import BaseAgent
import json
import os

class QueryUnderstandingAgent(BaseAgent):
    def _initialize(self) -> None:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.config.get("model", "gemini-2.0-flash"))
        self.max_tokens = self.config.get("max_tokens", 150)
        self.temperature = self.config.get("temperature", 0.7)
    
    async def validate(self, input_data: str) -> bool:
        return isinstance(input_data, str) and len(input_data.strip()) > 0
    
    def process(self, input_data: str) -> Dict[str, Any]:
        concepts = self._extract_concepts(input_data)
        
        reformulations = self._generate_reformulations(input_data, concepts)
        
        query_metadata = self._analyze_query(input_data)
        
        return {
            "original_query": input_data,
            "concepts": concepts,
            "reformulations": reformulations,
            "metadata": query_metadata
        }
    
    def _extract_concepts(self, query: str) -> List[str]:
        prompt = f"""
        Extract the key concepts from the following query. Return only the concepts as a comma-separated list:
        
        Query: {query}
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )
        
        concepts = response.text.strip().split(",")
        return [concept.strip() for concept in concepts]
    
    async def _generate_reformulations(self, query: str, concepts: List[str]) -> List[str]:
        prompt = f"""
        Generate 3 alternative formulations of the following query, focusing on these key concepts: {', '.join(concepts)}
        
        Original query: {query}
        
        Return only the reformulations as a comma-separated list.
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )
        
        reformulations = response.text.strip().split(",")
        return [reform.strip() for reform in reformulations]
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following query and return a JSON object with:
        1. query_type (e.g., 'factual', 'procedural', 'conceptual')
        2. priority (1-5, where 5 is highest)
        3. complexity (1-5, where 5 is highest)
        4. required_context (list of context types needed)
        
        Query: {query}
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "query_type": "unknown",
                "priority": 3,
                "complexity": 3,
                "required_context": []
            } 