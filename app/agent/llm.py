"""
LLM integration module for connecting to Groq's language models.
"""
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import settings

def get_llm(model_name: Optional[str] = None) -> BaseChatModel:
    """
    Initialize and return a connection to the Groq LLM.
    
    Args:
        model_name: Optional model name override (defaults to config setting)
        
    Returns:
        An initialized LLM chat model
    """
    model = model_name or settings.KIMI2_MODEL
    
    # Validate and map model names
    valid_models = {
        "kimi2": "moonshotai/kimi-k2-instruct",
        "llama3": "llama3-8b-8192",
        "llama3-70b": "llama3-70b-8192",
        "gemma": "gemma-7b-it"
    }
    
    # If using a shorthand name, map it to the full model name
    if model in valid_models:
        model = valid_models[model]
    
    # Default fallback to a known working model
    if not model or model == "kimi2":
        model = "mixtral-8x7b-32768"
        print(f"Warning: Using fallback model {model}")
    
    try:
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=model,  # Use 'model' not 'model_name' for ChatGroq
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        
        # Test the connection with a simple call
        test_response = llm.invoke([HumanMessage(content="Hello")])
        print(f"LLM initialized successfully with model: {model}")
        
        return llm
        
    except Exception as e:
        print(f"Error initializing LLM with model {model}: {e}")
        print("Falling back to mixtral-8x7b-32768")
        
        # Fallback to a known working model
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model="mixtral-8x7b-32768",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        
        return llm

def create_system_message(content: str) -> SystemMessage:
    """
    Create a system message for the LLM.
    
    Args:
        content: System message content
        
    Returns:
        A SystemMessage object
    """
    return SystemMessage(content=content)

def create_human_message(content: str) -> HumanMessage:
    """
    Create a human message for the LLM.
    
    Args:
        content: Human message content
        
    Returns:
        A HumanMessage object
    """
    return HumanMessage(content=content)

def create_ai_message(content: str) -> AIMessage:
    """
    Create an AI message for the LLM.
    
    Args:
        content: AI message content
        
    Returns:
        An AIMessage object
    """
    return AIMessage(content=content)