"""
Aster SDK - Constants and Configuration
"""

# =============================================================================
# API ENDPOINTS
# =============================================================================

# Aster DEX API endpoints (verified working)
MAINNET_API_URL = "https://fapi.asterdex.com"  # Aster mainnet API - WORKING
TESTNET_API_URL = "https://fapi.asterdex.com"  # Using mainnet for development (testnet not available)
LOCAL_API_URL = "http://localhost:3001"  # For local development

# WebSocket endpoints
MAINNET_WS_URL = "wss://fstream.asterdex.com/ws"  # Aster mainnet WebSocket
TESTNET_WS_URL = "wss://fstream.asterdex.com/ws"  # Using mainnet for now

# =============================================================================
# CHAIN CONFIGURATION
# =============================================================================

# Aster blockchain configuration
ASTER_CHAIN_ID = 592  # Astar network chain ID
ASTER_DOMAIN_NAME = "AsterDEX"  # Aster DEX domain name
ASTER_VERSION = "1"

# =============================================================================
# API ENDPOINTS
# =============================================================================

# Specific API endpoints for Aster DEX
PING_ENDPOINT = "/fapi/v1/ping"
SERVER_TIME_ENDPOINT = "/fapi/v1/time"
EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"
ORDER_ENDPOINT = "/fapi/v1/order"
ACCOUNT_INFO_ENDPOINT = "/fapi/v1/account"
POSITION_INFO_ENDPOINT = "/fapi/v1/positionRisk"

# =============================================================================
# TRANSACTION TYPES
# =============================================================================

# Aster DEX transaction types
TRANSACTION_TYPES = {
    "ORDER": "AsterTransaction:Order",
    "TRANSFER": "AsterTransaction:Transfer", 
    "WITHDRAW": "AsterTransaction:Withdraw",
    "CANCEL": "AsterTransaction:Cancel",
    "MODIFY": "AsterTransaction:Modify",
}

# =============================================================================
# ORDER TYPES
# =============================================================================

# Update these based on Aster's order system
ORDER_TYPES = {
    "LIMIT": "limit",
    "MARKET": "market",
    "STOP": "stop",
    "STOP_LIMIT": "stop_limit",
}

TIME_IN_FORCE = {
    "GTC": "Gtc",  # Good Till Cancelled
    "IOC": "Ioc",  # Immediate or Cancel
    "ALO": "Alo",  # Add Liquidity Only
}

# =============================================================================
# DEFAULT VALUES
# =============================================================================

DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_SLIPPAGE = 0.05  # 5%
DEFAULT_ORDER_SIZE = 1.0
DEFAULT_RETRY_ATTEMPTS = 3

# =============================================================================
# ERROR CODES
# =============================================================================

# Update these based on Aster's error codes
ERROR_CODES = {
    "INSUFFICIENT_BALANCE": 1001,
    "INVALID_ORDER": 1002,
    "ORDER_NOT_FOUND": 1003,
    "MARKET_CLOSED": 1004,
    "RATE_LIMIT": 1005,
}

# =============================================================================
# ASSET CONFIGURATION
# =============================================================================

# Update these based on Aster's supported assets
SUPPORTED_ASSETS = {
    "ASTER": {"id": 1, "decimals": 8, "type": "native"},
    "USDC": {"id": 2, "decimals": 6, "type": "stablecoin"},
    "ETH": {"id": 3, "decimals": 8, "type": "crypto"},
    "BTC": {"id": 4, "decimals": 8, "type": "crypto"},
}

# =============================================================================
# WEBSOCKET CONFIGURATION
# =============================================================================

# WebSocket stream endpoints
DEPTH_STREAM = "{symbol}@depth"
TRADE_STREAM = "{symbol}@trade"
TICKER_STREAM = "{symbol}@ticker"
KLINE_STREAM = "{symbol}@kline_{interval}"
USER_DATA_STREAM = "user_data"

# WebSocket connection settings
WS_PING_INTERVAL = 50  # seconds
WS_PONG_TIMEOUT = 10   # seconds
WS_RECONNECT_DELAY = 5  # seconds
WS_MAX_RECONNECT_ATTEMPTS = 10

# =============================================================================
# RATE LIMITS
# =============================================================================

# Update these based on Aster's rate limits
RATE_LIMITS = {
    "ORDERS_PER_SECOND": 10,
    "REQUESTS_PER_MINUTE": 100,
    "REQUESTS_PER_HOUR": 1000,
}

# =============================================================================
# API AUTHENTICATION
# =============================================================================

# API headers
API_HEADERS = {
    "Content-Type": "application/json",
    "X-MBX-APIKEY": "",  # Will be set dynamically
}

# Signature requirements
SIGNATURE_REQUIRED = True
TIMESTAMP_REQUIRED = True

# =============================================================================
# DEVELOPMENT CONFIGURATION
# =============================================================================

DEBUG_MODE = False
LOG_LEVEL = "INFO"
ENABLE_WEBSOCKET_LOGGING = False
