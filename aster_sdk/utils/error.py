"""
Aster SDK - Error handling
"""

from typing import Any, Dict, Optional


class AsterError(Exception):
    """Base exception for Aster SDK errors"""
    
    def __init__(self, message: str, code: Optional[str] = None, data: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data


class ClientError(AsterError):
    """Client-side error (4xx status codes)"""
    
    def __init__(
        self, 
        status_code: int, 
        code: Optional[str], 
        message: str, 
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None
    ):
        super().__init__(message, code, data)
        self.status_code = status_code
        self.headers = headers or {}


class ServerError(AsterError):
    """Server-side error (5xx status codes)"""
    
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(ClientError):
    """Authentication/authorization error"""
    pass


class RateLimitError(ClientError):
    """Rate limit exceeded error"""
    pass


class InsufficientBalanceError(ClientError):
    """Insufficient balance error"""
    pass


class InvalidOrderError(ClientError):
    """Invalid order error"""
    pass


class OrderNotFoundError(ClientError):
    """Order not found error"""
    pass


class MarketClosedError(ClientError):
    """Market closed error"""
    pass
