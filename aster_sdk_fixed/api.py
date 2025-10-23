"""
Aster SDK - Base API client (fixed version)
"""

import json
import logging
from json import JSONDecodeError
from typing import Any, Optional

import requests

from aster_sdk.utils.constants import MAINNET_API_URL
from aster_sdk.utils.error import ClientError, ServerError


class API:
    """Base API client for Aster DEX"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL for the API (defaults to mainnet)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or MAINNET_API_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._logger = logging.getLogger(__name__)
        self.timeout = timeout

    def post(self, url_path: str, payload: Any = None) -> Any:
        """
        Make a POST request to the API
        
        Args:
            url_path: API endpoint path
            payload: Request payload
            
        Returns:
            API response data
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
        """
        payload = payload or {}
        url = self.base_url + url_path
        
        self._logger.debug(f"POST {url} with payload: {payload}")
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            self._handle_exception(response)
            
            try:
                return response.json()
            except ValueError:
                return {"error": f"Could not parse JSON: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Request failed: {e}")
            raise ClientError(0, "REQUEST_FAILED", str(e))

    def get(self, url_path: str, params: Optional[dict] = None) -> Any:
        """
        Make a GET request to the API
        
        Args:
            url_path: API endpoint path
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
        """
        params = params or {}
        url = self.base_url + url_path
        
        self._logger.debug(f"GET {url} with params: {params}")
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            self._handle_exception(response)
            
            try:
                return response.json()
            except ValueError:
                return {"error": f"Could not parse JSON: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Request failed: {e}")
            raise ClientError(0, "REQUEST_FAILED", str(e))

    def _handle_exception(self, response: requests.Response) -> None:
        """
        Handle HTTP response exceptions
        
        Args:
            response: HTTP response object
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
        """
        status_code = response.status_code
        
        if status_code < 400:
            return
            
        if 400 <= status_code < 500:
            try:
                err = json.loads(response.text)
            except JSONDecodeError:
                raise ClientError(status_code, None, response.text, None, response.headers)
                
            if err is None:
                raise ClientError(status_code, None, response.text, None, response.headers)
                
            error_data = err.get("data")
            raise ClientError(status_code, err.get("code"), err.get("msg", "Unknown error"), response.headers, error_data)
            
        raise ServerError(status_code, response.text)

    def set_api_key(self, api_key: str) -> None:
        """
        Set API key for authenticated requests
        
        Args:
            api_key: API key string
        """
        self.session.headers.update({"X-MBX-APIKEY": api_key})

    def set_timeout(self, timeout: float) -> None:
        """
        Set request timeout
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
