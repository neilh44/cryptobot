"""
Rejection tool for handling non-crypto trading queries.
Provides polite rejection responses and redirects to automatealgos.in
"""
from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class RejectionInput(BaseModel):
    """Input schema for the rejection tool."""
    query: str = Field(description="The user's non-trading query that should be rejected")


class RejectionTool(BaseTool):
    """
    Tool for handling non-crypto trading queries with polite rejection.
    """
    
    name: str = "rejection_handler"
    description: str = """
    Use this tool IMMEDIATELY when users ask about topics NOT related to cryptocurrency trading:
    
    NON-CRYPTO TOPICS (use this tool):
    - Weather, sports, politics, cooking, travel
    - General knowledge, history, science
    - Personal advice unrelated to trading  
    - Technical support for non-crypto platforms
    - Entertainment, movies, books
    - Health, fitness, relationships
    
    CRYPTO TRADING TOPICS (don't use this tool):
    - Cryptocurrency prices, market data
    - Trading strategies, technical analysis
    - Blockchain and crypto education
    - Risk management in trading
    """
    
    args_schema: Type[BaseModel] = RejectionInput
    
    def _run(self, query: str) -> str:
        """
        Generate a polite, chat-friendly rejection response.
        
        Args:
            query: The user's non-trading query
            
        Returns:
            Formatted rejection message with redirect
        """
        # Extract topic for personalization
        topic = self._extract_topic(query)
        
        responses = [
            f"🤖 I'm specialized in cryptocurrency trading only!\n\nFor **{topic}** questions, check out:\n🌐 **https://automatealgos.in**\n\nI can help with:\n📈 Crypto prices & market data\n📊 Trading strategies\n📚 Crypto education\n\nWhat crypto trading topic can I assist with? 🚀",
            
            f"🎯 I focus exclusively on crypto trading assistance!\n\nFor **{topic}** related queries, visit:\n🌐 **https://automatealgos.in**\n\nI'm your go-to for:\n💰 Live crypto prices\n📉 Technical analysis\n⚖️ Risk management\n\nAny crypto trading questions? 📊",
            
            f"🤖 My expertise is cryptocurrency trading only!\n\nFor **{topic}** information, please see:\n🌐 **https://automatealgos.in**\n\nI can help you with:\n🚀 Market insights\n📈 Trading education  \n💡 Strategy guidance\n\nWhat's your crypto trading question? 💰"
        ]
        
        # Select response based on query characteristics
        selection = hash(query) % len(responses)
        return responses[selection]
    
    def _extract_topic(self, query: str) -> str:
        """Extract the main topic from the query for personalization."""
        query_lower = query.lower()
        
        topic_keywords = {
            "weather": "weather",
            "sport": "sports", 
            "politic": "politics",
            "cook": "cooking",
            "travel": "travel",
            "health": "health",
            "movie": "entertainment",
            "book": "books",
            "music": "music",
            "news": "general news",
            "science": "science",
            "history": "history"
        }
        
        for keyword, topic in topic_keywords.items():
            if keyword in query_lower:
                return topic
        
        return "general topics"
    
    async def _arun(self, query: str) -> str:
        """Async version of the rejection tool."""
        return self._run(query)