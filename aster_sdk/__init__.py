"""
Aster SDK - Python SDK for Aster DEX Trading
"""

from .api import API
from .info import Info
from .exchange import Exchange
from .utils.constants import MAINNET_API_URL, TESTNET_API_URL, LOCAL_API_URL

__version__ = "1.0.0"
__author__ = "Aster SDK Team"

__all__ = [
    "API",
    "Info", 
    "Exchange",
    "MAINNET_API_URL",
    "TESTNET_API_URL", 
    "LOCAL_API_URL"
]
