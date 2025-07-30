"""
Binance API integration tool for retrieving cryptocurrency price and market data.
"""
import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import json
from langchain_core.tools import BaseTool
from app.config import settings

class BinancePriceRequest(BaseModel):
    """Schema for Binance price request parameters."""
    symbol: str = Field(..., description="The cryptocurrency symbol, e.g., BTCUSDT")
    interval: Optional[str] = Field(None, description="Time interval for klines/candlesticks")

class BinancePriceTool(BaseTool):
    """Tool for retrieving cryptocurrency price data from Binance."""
    
    # Add proper type annotations for overridden fields
    name: str = "binance_price"
    description: str = """
    Use this tool to get current price and market information for cryptocurrencies from Binance.
    Input should be a cryptocurrency symbol like 'BTCUSDT', 'ETHUSDT', etc.
    You can also specify additional parameters for more detailed information.
    """
    args_schema: type[BinancePriceRequest] = BinancePriceRequest
    
    def __init__(self):
        """Initialize the Binance tool with API credentials."""
        super().__init__()
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.base_url = "https://api.binance.com"
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for authenticated Binance API requests.
        
        Args:
            params: Request parameters
            
        Returns:
            Signature string
        """
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, signed: bool = False) -> Dict[str, Any]:
        """
        Make a request to the Binance API.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            signed: Whether the request requires authentication
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        
        # For signed requests, add timestamp and signature
        if signed and self.api_secret:
            params = params or {}
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            
        Returns:
            Current price information
        """
        endpoint = "/api/v3/ticker/price"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            
        Returns:
            24-hour price statistics
        """
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_klines(self, symbol: str, interval: str, limit: int = 10) -> List[List[Union[int, str, float]]]:
        """
        Get candlestick data for a symbol.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            interval: Kline/candlestick interval (1m, 5m, 15m, 30m, 1h, etc.)
            limit: Number of data points to return
            
        Returns:
            Candlestick data
        """
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def _run(self, symbol: str, interval: Optional[str] = None) -> str:
        """
        Run the tool to get cryptocurrency price information.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            interval: Optional time interval for historical data
            
        Returns:
            Formatted price information as a string
        """
        try:
            # Get current price
            price_data = self.get_ticker_price(symbol)
            
            # Get 24hr statistics
            stats_data = self.get_ticker_24hr(symbol)
            
            # Format the response
            response = {
                "symbol": symbol,
                "current_price": float(price_data.get("price", 0)),
                "price_change_24h": float(stats_data.get("priceChange", 0)),
                "price_change_percent_24h": stats_data.get("priceChangePercent", "0") + "%",
                "high_24h": float(stats_data.get("highPrice", 0)),
                "low_24h": float(stats_data.get("lowPrice", 0)),
                "volume_24h": float(stats_data.get("volume", 0)),
                "timestamp": stats_data.get("closeTime", 0),
            }
            
            # If interval is provided, add historical data
            if interval:
                klines = self.get_klines(symbol, interval)
                historical_data = []
                
                for k in klines:
                    historical_data.append({
                        "open_time": k[0],
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": float(k[5]),
                        "close_time": k[6],
                    })
                
                response["historical_data"] = historical_data
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return f"Error retrieving price data: {str(e)}"