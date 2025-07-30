"""
Utilities for ingesting knowledge base content into the vector database.
"""
import os
import glob
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, 
    CSVLoader, 
    UnstructuredMarkdownLoader,
    JSONLoader
)
from app.config import settings
from app.knowledge_base.vector_store import add_documents, delete_collection

def load_documents(directory: str) -> List[Document]:
    """
    Load documents from a directory.
    
    Args:
        directory: Directory path containing documents
        
    Returns:
        List of loaded documents
    """
    documents = []
    
    # Process text files
    for file_path in glob.glob(os.path.join(directory, "**/*.txt"), recursive=True):
        loader = TextLoader(file_path, encoding="utf-8")
        documents.extend(loader.load())
    
    # Process Markdown files
    for file_path in glob.glob(os.path.join(directory, "**/*.md"), recursive=True):
        loader = UnstructuredMarkdownLoader(file_path, encoding="utf-8")
        documents.extend(loader.load())
    
    # Process CSV files
    for file_path in glob.glob(os.path.join(directory, "**/*.csv"), recursive=True):
        loader = CSVLoader(file_path)
        documents.extend(loader.load())
    
    # Process JSON files
    for file_path in glob.glob(os.path.join(directory, "**/*.json"), recursive=True):
        # The jq_schema specifies how to extract content from JSON
        loader = JSONLoader(
            file_path,
            jq_schema='.[]',  # Modify this based on your JSON structure
            text_content=False
        )
        documents.extend(loader.load())
    
    return documents

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks for better embedding.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of split documents
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    return text_splitter.split_documents(documents)

def ingest_documents(directory: str = None, chunk_size: int = 1000, chunk_overlap: int = 200, reset: bool = False) -> int:
    """
    Ingest documents into the vector store.
    
    Args:
        directory: Directory containing documents (defaults to KB_DATA_DIR)
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        reset: Whether to reset the vector store before ingestion
        
    Returns:
        Number of documents ingested
    """
    directory = directory or settings.KB_DATA_DIR
    
    # Reset the vector store if requested
    if reset:
        delete_collection()
    
    # Load documents
    documents = load_documents(directory)
    
    if not documents:
        print(f"No documents found in {directory}")
        return 0
    
    # Split documents
    split_docs = split_documents(documents, chunk_size, chunk_overlap)
    
    # Add documents to vector store
    add_documents(split_docs)
    
    return len(split_docs)