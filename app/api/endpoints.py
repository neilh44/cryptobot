"""
API endpoints for the Crypto AI Agent.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import asyncio

from app.agent.agent import CryptoAgent
from app.api.models import (
    ChatRequest, 
    ChatResponse, 
    HealthResponse,
    KnowledgeBaseIngestionRequest,
    KnowledgeBaseIngestionResponse
)
from app.knowledge_base.ingest import ingest_documents

router = APIRouter()

# Store chat sessions
chat_sessions = {}

def get_agent(session_id: str) -> CryptoAgent:
    """
    Get or create a chat agent for the given session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        A CryptoAgent instance
    """
    if session_id not in chat_sessions:
        chat_sessions[session_id] = CryptoAgent()
    
    return chat_sessions[session_id]

@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Check the health of the API."""
    return {"status": "ok", "version": "1.0.0"}

@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return the agent's response.
    
    Args:
        request: Chat request containing the message and session ID
        
    Returns:
        The agent's response
    """
    try:
        # Get or create agent for the session
        agent = get_agent(request.session_id)
        
        # Process the message
        response = await agent.process_message(request.message)
        
        return {
            "session_id": request.session_id,
            "response": response,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.post("/knowledge-base/ingest", response_model=KnowledgeBaseIngestionResponse, tags=["knowledge-base"])
async def ingest_knowledge_base(request: KnowledgeBaseIngestionRequest, background_tasks: BackgroundTasks) -> KnowledgeBaseIngestionResponse:
    """
    Ingest documents into the knowledge base.
    
    Args:
        request: Knowledge base ingestion request
        background_tasks: FastAPI background tasks
        
    Returns:
        Status response
    """
    try:
        # Define background task for ingestion
        def ingest_in_background():
            num_docs = ingest_documents(
                directory=request.directory,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
                reset=request.reset
            )
            print(f"Ingested {num_docs} documents into the knowledge base")
        
        # Add task to background queue
        background_tasks.add_task(ingest_in_background)
        
        return {
            "status": "ingestion_started",
            "message": "Knowledge base ingestion has been started in the background"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting ingestion: {str(e)}"
        )