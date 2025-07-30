"""
Knowledge Base tool for retrieving information from vector databases.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json
from langchain_core.tools import BaseTool

# Safe imports for vector stores
try:
    from langchain_community.vectorstores import Chroma, Qdrant
except ImportError as e:
    print(f"Warning: Could not import some vector stores: {e}")
    Chroma = None
    Qdrant = None

# Try multiple import paths for Pinecone
PineconeVectorStore = None
try:
    from langchain_pinecone import PineconeVectorStore
except ImportError:
    try:
        from langchain_community.vectorstores import Pinecone as PineconeVectorStore
    except ImportError:
        print("Warning: PineconeVectorStore not available. Install with: pip install langchain-pinecone")

# Import other necessary modules
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

class KnowledgeBaseRequest(BaseModel):
    """Schema for knowledge base query parameters."""
    query: str = Field(..., description="The search query for the knowledge base")
    k: Optional[int] = Field(5, description="Number of results to return")

class KnowledgeBaseTool(BaseTool):
    """Tool for querying the knowledge base."""
    
    # Add proper type annotations
    name: str = "knowledge_base"
    description: str = """
    Use this tool to search for information in the knowledge base.
    Input should be a search query string.
    This tool can help answer questions about cryptocurrency concepts, trading strategies, and market analysis.
    """
    args_schema: type[KnowledgeBaseRequest] = KnowledgeBaseRequest
    
    def __init__(self):
        """Initialize the Knowledge Base tool."""
        super().__init__()
        self.vector_store = self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store based on configuration."""
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
            
            if settings.VECTOR_STORE_TYPE.lower() == "chroma" and Chroma:
                return Chroma(
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                    embedding_function=embeddings
                )
            elif settings.VECTOR_STORE_TYPE.lower() == "qdrant" and Qdrant:
                return Qdrant(
                    url=settings.QDRANT_URL,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    embeddings=embeddings
                )
            elif settings.VECTOR_STORE_TYPE.lower() == "pinecone" and PineconeVectorStore:
                return PineconeVectorStore(
                    index_name=settings.PINECONE_INDEX_NAME,
                    embedding=embeddings
                )
            else:
                print(f"Warning: Vector store type '{settings.VECTOR_STORE_TYPE}' not available or not supported")
                return None
                
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return None
    
    def _run(self, query: str, k: Optional[int] = 5) -> str:
        """
        Run the tool to search the knowledge base.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            Formatted search results as a string
        """
        if not self.vector_store:
            return "Knowledge base is not available. Please check the configuration."
        
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search(query, k=k)
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(results, 1):
                formatted_results.append({
                    "result": i,
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return json.dumps({
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results)
            }, indent=2)
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"