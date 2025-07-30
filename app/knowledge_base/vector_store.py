"""
Vector database integration for storing and retrieving knowledge base content.
"""
from typing import Dict, Any, Optional, List, Union
import os
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import Chroma, Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings
from app.knowledge_base.embeddings import get_embedding_model

# Cache the vector store instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """
    Get or create the vector store instance based on configuration.
    
    Returns:
        An initialized vector store
    """
    global _vector_store_instance
    
    if _vector_store_instance is not None:
        return _vector_store_instance
    
    # Get the embedding model
    embedding_model = get_embedding_model()
    
    # Initialize the appropriate vector store based on configuration
    if settings.VECTOR_DB_TYPE.lower() == "chroma":
        # Create the persist directory if it doesn't exist
        persist_directory = os.path.join(settings.KB_DATA_DIR, "chroma")
        os.makedirs(persist_directory, exist_ok=True)
        
        _vector_store_instance = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            collection_name=settings.VECTOR_DB_COLLECTION
        )
    
    elif settings.VECTOR_DB_TYPE.lower() == "qdrant":
        import qdrant_client
        
        # Connect to Qdrant
        if settings.VECTOR_DB_URL:
            client = qdrant_client.QdrantClient(url=settings.VECTOR_DB_URL, api_key=settings.VECTOR_DB_API_KEY)
        else:
            # Local Qdrant
            local_path = os.path.join(settings.KB_DATA_DIR, "qdrant")
            os.makedirs(local_path, exist_ok=True)
            client = qdrant_client.QdrantClient(path=local_path)
        
        _vector_store_instance = Qdrant(
            client=client,
            collection_name=settings.VECTOR_DB_COLLECTION,
            embedding_function=embedding_model
        )
    
    elif settings.VECTOR_DB_TYPE.lower() == "pinecone":
        from langchain_pinecone import PineconeVectorStore
        import pinecone
        
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.VECTOR_DB_API_KEY,
            environment=settings.VECTOR_DB_URL
        )
        
        _vector_store_instance = PineconeVectorStore(
            index_name=settings.VECTOR_DB_COLLECTION,
            embedding=embedding_model
        )
    
    else:
        raise ValueError(f"Unsupported vector database type: {settings.VECTOR_DB_TYPE}")
    
    return _vector_store_instance

def add_documents(documents: List[Document]) -> None:
    """
    Add documents to the vector store.
    
    Args:
        documents: List of documents to add
    """
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    
    # Persist if using Chroma
    if settings.VECTOR_DB_TYPE.lower() == "chroma":
        vector_store.persist()

def delete_collection() -> None:
    """Delete the entire collection from the vector store."""
    global _vector_store_instance
    
    if settings.VECTOR_DB_TYPE.lower() == "chroma":
        import shutil
        persist_directory = os.path.join(settings.KB_DATA_DIR, "chroma")
        if os.path.exists(persist_directory):
            shutil.rmtree(persist_directory)
    
    elif settings.VECTOR_DB_TYPE.lower() == "qdrant":
        import qdrant_client
        
        # Connect to Qdrant
        if settings.VECTOR_DB_URL:
            client = qdrant_client.QdrantClient(url=settings.VECTOR_DB_URL, api_key=settings.VECTOR_DB_API_KEY)
        else:
            local_path = os.path.join(settings.KB_DATA_DIR, "qdrant")
            client = qdrant_client.QdrantClient(path=local_path)
        
        # Delete the collection
        client.delete_collection(collection_name=settings.VECTOR_DB_COLLECTION)
    
    elif settings.VECTOR_DB_TYPE.lower() == "pinecone":
        import pinecone
        
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.VECTOR_DB_API_KEY,
            environment=settings.VECTOR_DB_URL
        )
        
        # Delete the index
        pinecone.delete_index(settings.VECTOR_DB_COLLECTION)
    
    # Reset the instance
    _vector_store_instance = None