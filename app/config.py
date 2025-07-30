"""
Configuration settings for the Crypto AI Agent application.
"""
import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # LLM Settings
    GROQ_API_KEY: Optional[str] = None
    KIMI2_MODEL: str = "moonshotai/kimi-k2-instruct"
    
    # Binance API Settings
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    
    # Vector Database Settings
    VECTOR_DB_TYPE: str = "chroma"  # Options: chroma, qdrant, pinecone
    VECTOR_DB_URL: Optional[str] = None
    VECTOR_DB_API_KEY: Optional[str] = None
    VECTOR_DB_COLLECTION: str = "crypto_knowledge"
    
    # Embedding Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Knowledge Base Settings
    KB_DATA_DIR: str = "./data/knowledge_base"
    
    # Memory Settings
    MEMORY_WINDOW: int = 10
    
    # Additional settings that might be needed by your application
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: Optional[int] = None
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    LOG_LEVEL: str = "INFO"
    
    # Chroma Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # Properties for backward compatibility with other parts of your code
    @property
    def LLM_MODEL_NAME(self) -> str:
        """Alias for KIMI2_MODEL for backward compatibility."""
        return self.KIMI2_MODEL
    
    @property
    def VECTOR_STORE_TYPE(self) -> str:
        """Alias for VECTOR_DB_TYPE for backward compatibility."""
        return self.VECTOR_DB_TYPE
    
    @property
    def EMBEDDING_MODEL_NAME(self) -> str:
        """Alias for EMBEDDING_MODEL for backward compatibility."""
        return self.EMBEDDING_MODEL
    
    @property
    def QDRANT_COLLECTION_NAME(self) -> str:
        """Alias for VECTOR_DB_COLLECTION for backward compatibility."""
        return self.VECTOR_DB_COLLECTION
    
    @property
    def KNOWLEDGE_BASE_PATH(self) -> str:
        """Alias for KB_DATA_DIR for backward compatibility."""
        return self.KB_DATA_DIR
    
    @property
    def QDRANT_URL(self) -> Optional[str]:
        """Alias for VECTOR_DB_URL when using Qdrant."""
        return self.VECTOR_DB_URL if self.VECTOR_DB_TYPE.lower() == "qdrant" else None
    
    @property
    def PINECONE_API_KEY(self) -> Optional[str]:
        """Alias for VECTOR_DB_API_KEY when using Pinecone."""
        return self.VECTOR_DB_API_KEY if self.VECTOR_DB_TYPE.lower() == "pinecone" else None
    
    class Config:
        # Look for .env file in the project root
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create a global settings instance
settings = Settings()