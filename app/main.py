from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.config import HOST, PORT, DEBUG, GOOGLE_API_KEY
import google.generativeai as genai

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(
    title="AIFAQ Multi-Agent RAG System",
    description="A sophisticated multi-agent system for enhancing AI-generated FAQ responses",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AIFAQ Multi-Agent RAG System",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 