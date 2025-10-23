"""
Aster SDK - Fixed version for Aster's actual API
"""

from .info import Info
from aster_sdk.utils.constants import MAINNET_API_URL, TESTNET_API_URL, LOCAL_API_URL

__version__ = "1.0.0"
__author__ = "Aster SDK Team"

__all__ = [
    "Info",
    "MAINNET_API_URL",
    "TESTNET_API_URL", 
    "LOCAL_API_URL"
]
