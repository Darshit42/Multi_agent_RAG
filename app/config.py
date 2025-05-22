import os
from typing import Dict, Any
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(f"GOOGLE_API_KEY loaded: {'Yes' if GOOGLE_API_KEY else 'No'}")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

AGENT_CONFIG: Dict[str, Any] = {
    "query_agent": {
        "model": os.getenv("QUERY_AGENT_MODEL", "gemini-2.0-flash"),
        "max_tokens": int(os.getenv("QUERY_AGENT_MAX_TOKENS", "150")),
        "temperature": float(os.getenv("QUERY_AGENT_TEMPERATURE", "0.7"))
    },
    "retrieval_agent": {
        "model_name": os.getenv("RETRIEVAL_AGENT_MODEL", "all-MiniLM-L6-v2"),
        "top_k": int(os.getenv("RETRIEVAL_AGENT_TOP_K", "3"))
    },
    "response_agent": {
        "model": os.getenv("RESPONSE_AGENT_MODEL", "gemini-2.0-flash"),
        "max_tokens": int(os.getenv("RESPONSE_AGENT_MAX_TOKENS", "500")),
        "temperature": float(os.getenv("RESPONSE_AGENT_TEMPERATURE", "0.7")),
        "system_prompt": """You are an expert FAQ response generator. 
        Generate clear, concise, and accurate responses based on the provided context.
        Focus on being helpful, accurate, and maintaining a professional tone."""
    }
}