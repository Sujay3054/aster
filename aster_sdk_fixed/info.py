"""
Aster SDK - Info module adapted for Aster's actual API endpoints
"""

from typing import Any, Dict, List, Optional, Union, Callable
from .api import API
from aster_sdk.utils.constants import MAINNET_API_URL


class Info(API):
    """Info module for retrieving market data from Aster DEX"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        skip_ws: Optional[bool] = False,
        timeout: Optional[float] = None,
    ):
        """
        Initialize Info client
        
        Args:
            base_url: Base URL for the API
            skip_ws: Skip WebSocket initialization
            timeout: Request timeout
        """
        super().__init__(base_url, timeout)
        
        # Initialize metadata mappings
        self.coin_to_asset = {}
        self.name_to_coin = {}
        self.asset_to_sz_decimals = {}

    def ping(self) -> Any:
        """
        Test connectivity to the API
        
        Returns:
            Empty dict if successful
        """
        return self.get("/fapi/v1/ping")

    def server_time(self) -> Any:
        """
        Get server time
        
        Returns:
            Server time in milliseconds
        """
        return self.get("/fapi/v1/time")

    def exchange_info(self) -> Any:
        """
        Get exchange information
        
        Returns:
            Exchange information including symbols and rate limits
        """
        return self.get("/fapi/v1/exchangeInfo")
    
    def ticker_24hr(self) -> Any:
        """
        Get 24hr ticker price change statistics
        
        Returns:
            List of 24hr ticker statistics
        """
        return self.get("/fapi/v1/ticker/24hr")
    
    def ticker_price(self) -> Any:
        """
        Get current price for all symbols
        
        Returns:
            List of current prices
        """
        return self.get("/fapi/v1/ticker/price")
    
    def ticker_book_ticker(self) -> Any:
        """
        Get best price/qty on the order book for all symbols
        
        Returns:
            List of best bid/ask prices
        """
        return self.get("/fapi/v1/ticker/bookTicker")
    
    def funding_rate(self) -> Any:
        """
        Get funding rate information
        
        Returns:
            List of funding rate data
        """
        return self.get("/fapi/v1/fundingRate")

    def all_mids(self) -> Any:
        """
        Get all mid prices (placeholder - need to find correct endpoint)
        
        Returns:
            Dictionary of coin names to mid prices
        """
        # This endpoint needs to be discovered
        # For now, return empty dict
        return {}

    def user_state(self, address: str) -> Any:
        """
        Get user state (placeholder - need to find correct endpoint)
        
        Args:
            address: User address
            
        Returns:
            User state information
        """
        # This endpoint needs to be discovered
        # For now, return empty dict
        return {}

    def open_orders(self, address: str) -> Any:
        """
        Get open orders (placeholder - need to find correct endpoint)
        
        Args:
            address: User address
            
        Returns:
            List of open orders
        """
        # This endpoint needs to be discovered
        # For now, return empty list
        return []

    def l2_snapshot(self, symbol: str) -> Any:
        """
        Get L2 order book snapshot (placeholder - need to find correct endpoint)
        
        Args:
            symbol: Trading symbol
            
        Returns:
            L2 order book snapshot
        """
        # This endpoint needs to be discovered
        # For now, return empty dict
        return {}

    def candles_snapshot(self, symbol: str, interval: str, start_time: int, end_time: int) -> Any:
        """
        Get candlestick data (placeholder - need to find correct endpoint)
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of candlestick data
        """
        # This endpoint needs to be discovered
        # For now, return empty list
        return []

    def name_to_asset(self, name: str) -> int:
        """
        Convert coin name to asset ID (placeholder)
        
        Args:
            name: Coin name
            
        Returns:
            Asset ID
        """
        # This needs to be implemented based on actual API response
        return 0
