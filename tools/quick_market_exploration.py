"""
Quick Aster Market Data Exploration (Non-interactive)
"""

import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aster_sdk_fixed'))

from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL

def quick_exploration():
    """Run quick market exploration"""
    print("QUICK ASTER MARKET EXPLORATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize Info client
        info = Info(MAINNET_API_URL)
        print("OK Info client initialized")
        
        # Get exchange info
        print("\nLoading exchange data...")
        exchange_info = info.exchange_info()
        symbols = exchange_info.get('symbols', [])
        rate_limits = exchange_info.get('rateLimits', [])
        
        print(f"OK Loaded data for {len(symbols)} symbols")
        print(f"OK Found {len(rate_limits)} rate limits")
        
        # Analyze symbols
        print(f"\nMARKET OVERVIEW")
        print("-" * 30)
        
        # Group by base asset
        base_assets = {}
        for symbol in symbols:
            base = symbol.get('baseAsset', 'Unknown')
            if base not in base_assets:
                base_assets[base] = []
            base_assets[base].append(symbol)
        
        print(f"Total Symbols: {len(symbols)}")
        print(f"Base Assets: {len(base_assets)}")
        
        # Show top base assets
        print(f"\nTop 10 Base Assets:")
        for base, symbol_list in sorted(base_assets.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  {base}: {len(symbol_list)} pairs")
        
        # Show sample symbols
        print(f"\nSAMPLE SYMBOLS (first 10)")
        print("-" * 40)
        for i, symbol in enumerate(symbols[:10]):
            symbol_name = symbol.get('symbol', 'N/A')
            base = symbol.get('baseAsset', 'N/A')
            quote = symbol.get('quoteAsset', 'N/A')
            status = symbol.get('status', 'N/A')
            print(f"{i+1:2d}. {symbol_name:15s} ({base}/{quote}) - {status}")
        
        # Show rate limits
        print(f"\nRATE LIMITS")
        print("-" * 20)
        for limit in rate_limits:
            limit_type = limit.get('rateLimitType', 'N/A')
            interval = limit.get('interval', 'N/A')
            limit_value = limit.get('limit', 'N/A')
            print(f"  {limit_type}: {limit_value} requests per {interval}")
        
        # Export to JSON
        filename = "aster_market_data.json"
        with open(filename, 'w') as f:
            json.dump(exchange_info, f, indent=2)
        print(f"\nOK Data exported to {filename}")
        
        # Show some interesting symbols
        print(f"\nINTERESTING FINDINGS")
        print("-" * 25)
        
        # Find USDT pairs
        usdt_pairs = [s for s in symbols if s.get('quoteAsset') == 'USDT']
        print(f"USDT pairs: {len(usdt_pairs)}")
        
        # Find BTC pairs
        btc_pairs = [s for s in symbols if s.get('quoteAsset') == 'BTC']
        print(f"BTC pairs: {len(btc_pairs)}")
        
        # Find ETH pairs
        eth_pairs = [s for s in symbols if s.get('quoteAsset') == 'ETH']
        print(f"ETH pairs: {len(eth_pairs)}")
        
        # Show some USDT pairs
        if usdt_pairs:
            print(f"\nSample USDT pairs:")
            for pair in usdt_pairs[:5]:
                print(f"  {pair.get('symbol', 'N/A')}")
        
        print(f"\nExploration complete!")
        return True
        
    except Exception as e:
        print(f"Error during exploration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    quick_exploration()
