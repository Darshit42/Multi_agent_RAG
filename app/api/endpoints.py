from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from app.core.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()

class ResponseMessage(BaseModel):
    content: str
    type: int
    id: str

class RequestQuery(BaseModel):
    id: str
    content: str

class ResponseQuery(BaseModel):
    id: str
    message: ResponseMessage

class DocumentRequest(BaseModel):
    documents: List[str]

class QueryResponse(BaseModel):
    query_analysis: Dict
    retrieval_results: Dict
    response: Dict
    status: str

class QueryRequest(BaseModel):
    id: str
    content: str

@router.post("/query", response_model=ResponseQuery)
async def answer_query(item: RequestQuery) -> ResponseQuery:
    try:
        result = await orchestrator.process_query(item.content, top_k=3)
        print("Orchestrator result:", result)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        generated_response = result.get("response", {}).get("response")
        if not generated_response:
            generated_response = "No response generated. Please check if documents are ingested and context is available."
        return ResponseQuery(
            id=item.id,
            message=ResponseMessage(
                content=generated_response,
                type=1,
                id=str(uuid.uuid4()),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents")
async def add_documents(request: DocumentRequest):
    try:
        orchestrator.add_documents(request.documents)
        return {
            "status": "success",
            "message": "Documents added successfully",
            "documents_added": len(request.documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents")
async def clear_documents():
    try:
        orchestrator.clear_documents()
        return {
            "status": "success",
            "message": "All documents cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    try:
        status = orchestrator.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def process_query(request: QueryRequest):
    try:
        response = orchestrator.process_query(request.id, request.content)
        return {
            "id": request.id,
            "message": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
