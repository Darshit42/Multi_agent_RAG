from typing import Any, Dict, List, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .base_agent import BaseAgent

class RetrievalAgent(BaseAgent):    
    def _initialize(self) -> None:
        self.model_name = self.config.get("model_name", "all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(self.model_name)
        self.index = None
        self.documents = []
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
    
    async def validate(self, input_data: Dict[str, Any]) -> bool:
        required_keys = ["query", "top_k"]
        return all(key in input_data for key in required_keys) and isinstance(input_data["top_k"], int)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data["query"]
        top_k = input_data["top_k"]
        
        query_embedding = self.embedding_model.encode([query])[0]
        
        if self.index is None:
            return {"error": "Index not initialized", "results": []}
        
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'),
            top_k
        )
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx != -1: 
                results.append({
                    "document": self.documents[idx],
                    "score": float(1 / (1 + distance)),
                    "index": int(idx)
                })
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    
    def add_documents(self, documents: List[str]) -> None:
        if not documents:
            return
        
        embeddings = self.embedding_model.encode(documents)
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(documents)
    
    def clear_index(self) -> None:
        self.index = None
        self.documents = []
    
    def get_index_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "index_type": "FAISS FlatL2" if self.index else "Not initialized"
        } 