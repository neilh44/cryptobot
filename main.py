"""
Crypto AI Agent - Main Application Entry Point
This module initializes and runs the FastAPI application.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.config import settings

app = FastAPI(
    title="Crypto AI Agent",
    description="An AI agent for cryptocurrency information powered by Groq Kimi2",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    # Use PORT environment variable provided by Render
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Required for Render - bind to all interfaces
        port=port,       # Use dynamic port from Render
        reload=settings.DEBUG
    )