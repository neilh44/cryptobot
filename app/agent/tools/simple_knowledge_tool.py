"""
Simple crypto trading knowledge tool without embeddings.
"""
from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class SimpleKnowledgeInput(BaseModel):
    """Input schema for simple knowledge queries."""
    query: str = Field(description="Crypto trading question")


class SimpleKnowledgeTool(BaseTool):
    """Simple knowledge tool with basic crypto trading info."""
    
    name: str = "crypto_education"
    description: str = """
    Use this tool for basic cryptocurrency trading education and concepts.
    Covers: technical analysis, trading strategies, risk management, market basics.
    """
    args_schema: Type[BaseModel] = SimpleKnowledgeInput
    
    def __init__(self):
        super().__init__()
        self.knowledge = {
            "rsi": "RSI (Relative Strength Index) measures momentum. Values >70 suggest overbought, <30 oversold.",
            "macd": "MACD shows relationship between two moving averages, helps identify trend changes.",
            "support": "Support is a price level where buying interest emerges, acting like a floor.",
            "resistance": "Resistance is where selling pressure emerges, acting like a ceiling.",
            "stop_loss": "Stop-loss automatically sells when price hits a predetermined level to limit losses.",
            "market_cap": "Market cap = current price × total supply. Shows total value of cryptocurrency.",
            "volatility": "Crypto markets are highly volatile - prices can change rapidly.",
            "risk_management": "Key rules: never invest more than you can afford to lose, use stop losses, diversify."
        }
    
    def _run(self, query: str) -> str:
        """Get basic trading information."""
        query_lower = query.lower()
        
        # Check for specific terms
        for term, info in self.knowledge.items():
            if term in query_lower:
                return f"📚 **{term.upper()}**: {info}\n\n⚠️ *Educational content only - not financial advice.*"
        
        # General response
        return """📚 **Crypto Trading Basics:**

🎯 **Key Principles:**
- Start small while learning
- Use stop losses to manage risk  
- Don't trade on emotions
- Study market trends and news

📊 **Popular Indicators:**
- RSI - momentum indicator
- MACD - trend changes
- Support/Resistance levels

⚠️ **Risk Warning:** Crypto trading is risky. Only invest what you can afford to lose."""
    
    async def _arun(self, query: str) -> str:
        return self._run(query)