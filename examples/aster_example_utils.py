"""
Aster SDK Example Utilities
Helper functions for Aster SDK examples
"""

import json
import os
import getpass
from typing import Optional, Tuple

from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL, TESTNET_API_URL


def setup_info_client(base_url: Optional[str] = None, skip_ws: bool = False) -> Info:
    """
    Set up an Aster Info client
    
    Args:
        base_url: Base URL for the API (defaults to mainnet)
        skip_ws: Skip WebSocket initialization
        
    Returns:
        Configured Info client
    """
    if base_url is None:
        base_url = MAINNET_API_URL
    
    print(f"Setting up Aster Info client with URL: {base_url}")
    info = Info(base_url, skip_ws)
    
    # Test connection
    try:
        ping_result = info.ping()
        print("OK Successfully connected to Aster API")
        return info
    except Exception as e:
        print(f"Error: Failed to connect to Aster API: {e}")
        raise


def load_config(config_path: Optional[str] = None) -> dict:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to config file (defaults to config.json in examples directory)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    if not os.path.exists(config_path):
        # Create default config if it doesn't exist
        default_config = {
            "api_key": "",
            "secret_key": "",
            "account_address": "",
            "base_url": MAINNET_API_URL,
            "testnet": False
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default config file at {config_path}")
        print("Please edit the config file with your API credentials")
        return default_config
    
    with open(config_path) as f:
        config = json.load(f)
    
    return config


def setup_with_config(config_path: Optional[str] = None) -> Tuple[Info, dict]:
    """
    Set up Info client with configuration
    
    Args:
        config_path: Path to config file
        
    Returns:
        Tuple of (Info client, config dict)
    """
    config = load_config(config_path)
    
    # Determine base URL
    if config.get("testnet", False):
        base_url = TESTNET_API_URL
    else:
        base_url = config.get("base_url", MAINNET_API_URL)
    
    info = setup_info_client(base_url)
    
    return info, config


def get_secret_key(config: dict) -> str:
    """
    Get secret key from config or prompt user
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Secret key string
    """
    if config.get("secret_key"):
        return config["secret_key"]
    else:
        return getpass.getpass("Enter your secret key: ")


def print_market_summary(info: Info) -> None:
    """
    Print a summary of the current market
    
    Args:
        info: Info client instance
    """
    try:
        print("\n📊 MARKET SUMMARY")
        print("=" * 50)
        
        # Get exchange info
        exchange_info = info.exchange_info()
        symbols = exchange_info.get('symbols', [])
        print(f"Total Symbols: {len(symbols)}")
        
        # Get current prices
        prices = info.ticker_price()
        print(f"Price Data Available: {len(prices)} symbols")
        
        # Get 24hr stats
        stats_24hr = info.ticker_24hr()
        print(f"24hr Stats Available: {len(stats_24hr)} symbols")
        
        # Show top symbols by volume
        if stats_24hr:
            top_volume = sorted(stats_24hr, 
                              key=lambda x: float(x.get('volume', 0)), 
                              reverse=True)[:5]
            
            print(f"\nTop 5 by Volume:")
            for i, ticker in enumerate(top_volume, 1):
                symbol = ticker.get('symbol', 'N/A')
                volume = float(ticker.get('volume', 0))
                price = float(ticker.get('lastPrice', 0))
                change = ticker.get('priceChangePercent', '0')
                print(f"  {i}. {symbol}: ${price:.4f} (Vol: ${volume:,.0f}, Change: {change}%)")
        
    except Exception as e:
        print(f"Error getting market summary: {e}")


def print_symbol_info(info: Info, symbol: str) -> None:
    """
    Print detailed information about a specific symbol
    
    Args:
        info: Info client instance
        symbol: Symbol to get info for (e.g., 'BTCUSDT')
    """
    try:
        print(f"\n🔍 SYMBOL INFO: {symbol}")
        print("=" * 50)
        
        # Get current price
        prices = info.ticker_price()
        price_data = next((p for p in prices if p.get('symbol') == symbol), None)
        
        if price_data:
            print(f"Current Price: ${price_data.get('price', 'N/A')}")
        else:
            print("Price data not available")
        
        # Get 24hr stats
        stats_24hr = info.ticker_24hr()
        stat_data = next((s for s in stats_24hr if s.get('symbol') == symbol), None)
        
        if stat_data:
            print(f"24hr High: ${stat_data.get('highPrice', 'N/A')}")
            print(f"24hr Low: ${stat_data.get('lowPrice', 'N/A')}")
            print(f"24hr Volume: ${float(stat_data.get('volume', 0)):,.0f}")
            print(f"24hr Change: {stat_data.get('priceChangePercent', 'N/A')}%")
        
        # Get best bid/ask
        best_prices = info.ticker_book_ticker()
        best_data = next((b for b in best_prices if b.get('symbol') == symbol), None)
        
        if best_data:
            print(f"Best Bid: ${best_data.get('bidPrice', 'N/A')}")
            print(f"Best Ask: ${best_data.get('askPrice', 'N/A')}")
            print(f"Spread: ${float(best_data.get('askPrice', 0)) - float(best_data.get('bidPrice', 0)):.4f}")
        
    except Exception as e:
        print(f"Error getting symbol info: {e}")


def save_data_to_file(data: dict, filename: str) -> None:
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        filename: Filename to save to
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Data saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")


def load_data_from_file(filename: str) -> dict:
    """
    Load data from a JSON file
    
    Args:
        filename: Filename to load from
        
    Returns:
        Loaded data dictionary
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        print(f"✅ Data loaded from {filename}")
        return data
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return {}


def format_price(price: float, decimals: int = 4) -> str:
    """
    Format price with appropriate decimal places
    
    Args:
        price: Price to format
        decimals: Number of decimal places
        
    Returns:
        Formatted price string
    """
    return f"${price:.{decimals}f}"


def format_volume(volume: float) -> str:
    """
    Format volume with appropriate units
    
    Args:
        volume: Volume to format
        
    Returns:
        Formatted volume string
    """
    if volume >= 1_000_000:
        return f"${volume/1_000_000:.1f}M"
    elif volume >= 1_000:
        return f"${volume/1_000:.1f}K"
    else:
        return f"${volume:.0f}"


def format_percentage(percentage: str) -> str:
    """
    Format percentage with color coding
    
    Args:
        percentage: Percentage string
        
    Returns:
        Formatted percentage string
    """
    try:
        pct = float(percentage)
        if pct > 0:
            return f"+{percentage}%"
        else:
            return f"{percentage}%"
    except:
        return f"{percentage}%"
