"""
Embedding model setup for the knowledge base vector database.
"""
from typing import Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

# Cache the embedding model instance
_embedding_model_instance = None

def get_embedding_model() -> Any:
    """
    Get or create the embedding model instance based on configuration.
    
    Returns:
        An initialized embedding model
    """
    global _embedding_model_instance
    
    if _embedding_model_instance is not None:
        return _embedding_model_instance
    
    # Initialize the embedding model
    _embedding_model_instance = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},  # Use GPU if available by changing to "cuda"
        encode_kwargs={"normalize_embeddings": True}
    )
    
    return _embedding_model_instance