"""
Pydantic models for API requests and responses.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="The user's message")
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session identifier"
    )

class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="The agent's response")
    status: str = Field(..., description="Response status")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")

class KnowledgeBaseIngestionRequest(BaseModel):
    """Knowledge base ingestion request model."""
    directory: Optional[str] = Field(
        None, 
        description="Directory containing documents to ingest"
    )
    chunk_size: int = Field(
        1000, 
        description="Size of each chunk"
    )
    chunk_overlap: int = Field(
        200, 
        description="Overlap between chunks"
    )
    reset: bool = Field(
        False, 
        description="Whether to reset the knowledge base before ingestion"
    )

class KnowledgeBaseIngestionResponse(BaseModel):
    """Knowledge base ingestion response model."""
    status: str = Field(..., description="Ingestion status")
    message: str = Field(..., description="Status message")