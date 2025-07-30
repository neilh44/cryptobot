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
    symbol: str = Field(..., description="Trading pair symbol like BTCUSDT, ETHUSDT")


class BinancePriceTool(BaseTool):
    """Tool for retrieving cryptocurrency price data from Binance."""
    
    name: str = "binance_price"
    description: str = """
    Use this tool to get current live price and market information for cryptocurrencies from Binance.
    Input should be a cryptocurrency symbol like 'BTCUSDT', 'ETHUSDT', etc.
    This tool fetches REAL-TIME data from Binance API.
    Examples: BTCUSDT, ETHUSDT, ADAUSDT, BNBUSDT
    """
    args_schema: type[BinancePriceRequest] = BinancePriceRequest
    
    def __init__(self):
        """Initialize the Binance tool."""
        super().__init__()
        # Use private attributes to avoid Pydantic field conflicts
        self._api_key = getattr(settings, 'BINANCE_API_KEY', None)
        self._api_secret = getattr(settings, 'BINANCE_API_SECRET', None)
        self._base_url = "https://api.binance.com"
        print(f"🔧 BinancePriceTool initialized")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for authenticated Binance API requests.
        
        Args:
            params: Request parameters
            
        Returns:
            Signature string
        """
        if not self._api_secret:
            raise Exception("API secret required for signed requests")
            
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self._api_secret.encode('utf-8'),
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
        url = f"{self._base_url}{endpoint}"
        headers = {}
        
        # Add API key to headers if available
        if self._api_key:
            headers["X-MBX-APIKEY"] = self._api_key
        
        # For signed requests, add timestamp and signature
        if signed and self._api_secret:
            params = params or {}
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            print(f"🌐 Making request to: {url}")
            print(f"📝 Parameters: {params}")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ API Response received successfully")
            return data
            
        except requests.exceptions.Timeout:
            raise Exception("Request timed out - Binance API might be slow")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                raise Exception(f"Invalid symbol or parameters: {response.text}")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded - too many requests")
            else:
                raise Exception(f"HTTP error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            
        Returns:
            Current price information
        """
        endpoint = "/api/v3/ticker/price"
        params = {"symbol": symbol.upper()}
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
        params = {"symbol": symbol.upper()}
        return self._make_request(endpoint, params)
    
    def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information.
        
        Args:
            symbol: Optional specific symbol to get info for
            
        Returns:
            Exchange information
        """
        endpoint = "/api/v3/exchangeInfo"
        params = {"symbol": symbol.upper()} if symbol else {}
        return self._make_request(endpoint, params)
    
    def _run(self, symbol: str) -> str:
        """
        Run the tool to get cryptocurrency price information from Binance API.
        
        Args:
            symbol: Cryptocurrency trading pair (e.g., BTCUSDT)
            
        Returns:
            Formatted price information as a JSON string
        """
        try:
            print(f"🔍 Fetching LIVE data for {symbol} from Binance API...")
            
            # Ensure symbol is uppercase and clean
            symbol = symbol.upper().strip()
            
            # Validate symbol format (basic check)
            if not symbol or len(symbol) < 6:
                raise Exception(f"Invalid symbol format: {symbol}. Use format like BTCUSDT")
            
            # Get current price
            print(f"📊 Getting current price for {symbol}...")
            price_data = self.get_ticker_price(symbol)
            
            # Get 24hr statistics
            print(f"📈 Getting 24h statistics for {symbol}...")
            stats_data = self.get_ticker_24hr(symbol)
            
            # Calculate price change percentage as float
            price_change_percent = float(stats_data.get("priceChangePercent", 0))
            
            # Determine trend
            trend_emoji = "📈" if price_change_percent > 0 else "📉" if price_change_percent < 0 else "➡️"
            
            # Format the response
            response = {
                "symbol": symbol,
                "current_price": float(price_data.get("price", 0)),
                "price_change_24h": float(stats_data.get("priceChange", 0)),
                "price_change_percent_24h": round(float(stats_data.get("priceChangePercent", 0)), 2),
                "high_24h": float(stats_data.get("highPrice", 0)),
                "low_24h": float(stats_data.get("lowPrice", 0)),
                "volume_24h": float(stats_data.get("volume", 0)),
                "quote_volume_24h": float(stats_data.get("quoteVolume", 0)),
                "open_price": float(stats_data.get("openPrice", 0)),
                "close_price": float(stats_data.get("prevClosePrice", 0)),
                "bid_price": float(stats_data.get("bidPrice", 0)),
                "ask_price": float(stats_data.get("askPrice", 0)),
                "timestamp": stats_data.get("closeTime", int(time.time() * 1000)),
                "trend": trend_emoji,
                "data_source": "Binance API",
                "status": "LIVE",
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
            
            print(f"✅ Successfully retrieved LIVE data for {symbol}")
            print(f"💰 Current Price: ${response['current_price']}")
            print(f"📊 24h Change: {response['price_change_percent_24h']}% {trend_emoji}")
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            error_msg = f"Failed to retrieve live price data for {symbol}: {str(e)}"
            print(f"❌ {error_msg}")
            
            error_response = {
                "error": True,
                "message": error_msg,
                "symbol": symbol,
                "data_source": "Binance API",
                "status": "ERROR",
                "timestamp": int(time.time() * 1000)
            }
            
            return json.dumps(error_response, indent=2)
    
    async def _arun(self, symbol: str) -> str:
        """
        Async version of the tool.
        
        Args:
            symbol: Cryptocurrency trading pair
            
        Returns:
            Formatted price information
        """
        return self._run(symbol)


# Utility function to test the tool directly
def test_binance_tool():
    """Test function to verify the tool works correctly."""
    print("🧪 Testing BinancePriceTool...")
    
    try:
        tool = BinancePriceTool()
        
        # Test cases
        test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        
        for symbol in test_symbols:
            print(f"\n🔬 Testing {symbol}...")
            result = tool._run(symbol)
            print(f"Result preview: {result[:200]}...")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_binance_tool()