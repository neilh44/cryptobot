#!/usr/bin/env python
"""
Script to ingest knowledge base documents into the vector database.
"""
import argparse
import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

from app.knowledge_base.ingest import ingest_documents
from app.config import settings

def main():
    """Main function to ingest knowledge base documents."""
    parser = argparse.ArgumentParser(description="Ingest documents into the knowledge base.")
    parser.add_argument(
        "--directory", "-d",
        type=str,
        default=settings.KB_DATA_DIR,
        help=f"Directory containing documents to ingest (default: {settings.KB_DATA_DIR})"
    )
    parser.add_argument(
        "--chunk-size", "-c",
        type=int,
        default=1000,
        help="Size of each chunk (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap", "-o",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)"
    )
    parser.add_argument(
        "--reset", "-r",
        action="store_true",
        help="Reset the knowledge base before ingestion"
    )
    
    args = parser.parse_args()
    
    start_time = time.time()
    print(f"Starting ingestion from {args.directory}...")
    
    num_docs = ingest_documents(
        directory=args.directory,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        reset=args.reset
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Ingestion completed in {duration:.2f} seconds.")
    print(f"Ingested {num_docs} documents into the knowledge base.")

if __name__ == "__main__":
    main()