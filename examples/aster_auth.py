"""
Aster SDK Authentication System
Handles authentication for private API endpoints
"""

import hmac
import hashlib
import time
import json
from typing import Dict, Optional, Any
from urllib.parse import urlencode

import requests


class AsterAuth:
    """Authentication handler for Aster API private endpoints"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize authentication
        
        Args:
            api_key: Your Aster API key
            secret_key: Your Aster secret key
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://fapi.asterdex.com"
    
    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC SHA256 signature
        
        Args:
            query_string: Query string to sign
            
        Returns:
            Signature string
        """
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)
    
    def get_headers(self, query_string: str = "") -> Dict[str, str]:
        """
        Get authentication headers
        
        Args:
            query_string: Query string for signature
            
        Returns:
            Headers dictionary
        """
        timestamp = self._get_timestamp()
        
        # Add timestamp to query string
        if query_string:
            query_string += f"&timestamp={timestamp}"
        else:
            query_string = f"timestamp={timestamp}"
        
        # Generate signature
        signature = self._generate_signature(query_string)
        
        return {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get signed parameters for authenticated requests
        
        Args:
            params: Request parameters
            
        Returns:
            Parameters with signature
        """
        # Add timestamp
        params['timestamp'] = self._get_timestamp()
        
        # Create query string
        query_string = urlencode(params)
        
        # Generate signature
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        return params
    
    def make_authenticated_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Aster API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            API response
        """
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == 'GET':
            # For GET requests, add signature to query string
            signed_params = self.get_signed_params(params)
            headers = self.get_headers()
            
            response = requests.get(url, params=signed_params, headers=headers)
        else:
            # For POST requests, add signature to body
            signed_params = self.get_signed_params(params)
            headers = self.get_headers()
            
            response = requests.request(method, url, json=signed_params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")


class AsterAuthenticatedClient:
    """Authenticated client for Aster API private endpoints"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize authenticated client
        
        Args:
            api_key: Your Aster API key
            secret_key: Your Aster secret key
        """
        self.auth = AsterAuth(api_key, secret_key)
        self.base_url = "https://fapi.asterdex.com"
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self.auth.make_authenticated_request('GET', '/fapi/v1/account')
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        return self.auth.make_authenticated_request('GET', '/fapi/v1/balance')
    
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        return self.auth.make_authenticated_request('GET', '/fapi/v1/positionRisk')
    
    def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get open orders
        
        Args:
            symbol: Optional symbol to filter orders
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self.auth.make_authenticated_request('GET', '/fapi/v1/openOrders', params)
    
    def get_all_orders(self, symbol: str, limit: int = 500) -> Dict[str, Any]:
        """
        Get all orders for a symbol
        
        Args:
            symbol: Trading symbol
            limit: Number of orders to retrieve
        """
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        return self.auth.make_authenticated_request('GET', '/fapi/v1/allOrders', params)
    
    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, 
                   price: Optional[float] = None, time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (GTC, IOC, FOK)
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'timeInForce': time_in_force
        }
        
        if order_type == 'LIMIT' and price:
            params['price'] = price
        
        return self.auth.make_authenticated_request('POST', '/fapi/v1/order', params)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
        """
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return self.auth.make_authenticated_request('DELETE', '/fapi/v1/order', params)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        """
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        return self.auth.make_authenticated_request('GET', '/fapi/v1/order', params)
    
    def get_commission_rate(self, symbol: str) -> Dict[str, Any]:
        """
        Get commission rate for a symbol
        
        Args:
            symbol: Trading symbol
        """
        params = {
            'symbol': symbol
        }
        
        return self.auth.make_authenticated_request('GET', '/fapi/v1/commissionRate', params)


def test_authentication():
    """Test authentication system"""
    print("Testing Aster Authentication System...")
    
    # You would need to provide actual API credentials
    api_key = "your_api_key_here"
    secret_key = "your_secret_key_here"
    
    if api_key == "your_api_key_here":
        print("Please set your actual API credentials to test authentication")
        return
    
    try:
        client = AsterAuthenticatedClient(api_key, secret_key)
        
        # Test account info
        print("Testing account info...")
        account_info = client.get_account_info()
        print(f"Account info: {account_info}")
        
        # Test balance
        print("Testing balance...")
        balance = client.get_balance()
        print(f"Balance: {balance}")
        
        print("Authentication test completed successfully!")
        
    except Exception as e:
        print(f"Authentication test failed: {e}")


if __name__ == "__main__":
    test_authentication()
