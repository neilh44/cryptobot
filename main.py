"""
Crypto AI Agent - Main Application Entry Point
This module initializes and runs the FastAPI application.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Add this import
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
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )