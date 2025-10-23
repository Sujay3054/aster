"""
Aster Market Data Explorer
Explore available trading pairs, market data, and API capabilities
"""

import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aster_sdk_fixed'))

from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL

class AsterMarketExplorer:
    def __init__(self):
        self.info = Info(MAINNET_API_URL)
        self.exchange_data = None
        
    def load_exchange_data(self):
        """Load and cache exchange information"""
        print("Loading exchange data...")
        self.exchange_data = self.info.exchange_info()
        print(f"✅ Loaded data for {len(self.exchange_data.get('symbols', []))} symbols")
        return self.exchange_data
    
    def explore_symbols(self):
        """Explore available trading symbols"""
        if not self.exchange_data:
            self.load_exchange_data()
            
        symbols = self.exchange_data.get('symbols', [])
        print(f"\n📊 MARKET OVERVIEW")
        print("=" * 50)
        print(f"Total Symbols: {len(symbols)}")
        
        # Group by base asset
        base_assets = {}
        for symbol in symbols:
            base = symbol.get('baseAsset', 'Unknown')
            if base not in base_assets:
                base_assets[base] = []
            base_assets[base].append(symbol)
        
        print(f"Base Assets: {len(base_assets)}")
        print("\nTop Base Assets:")
        for base, symbol_list in sorted(base_assets.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  {base}: {len(symbol_list)} pairs")
        
        return symbols, base_assets
    
    def show_symbol_details(self, limit=10):
        """Show detailed information about symbols"""
        if not self.exchange_data:
            self.load_exchange_data()
            
        symbols = self.exchange_data.get('symbols', [])
        print(f"\n🔍 SYMBOL DETAILS (showing first {limit})")
        print("=" * 80)
        
        for i, symbol in enumerate(symbols[:limit]):
            print(f"\n{i+1}. {symbol.get('symbol', 'N/A')}")
            print(f"   Base: {symbol.get('baseAsset', 'N/A')}")
            print(f"   Quote: {symbol.get('quoteAsset', 'N/A')}")
            print(f"   Status: {symbol.get('status', 'N/A')}")
            print(f"   Type: {symbol.get('contractType', 'N/A')}")
            
            # Show filters if available
            filters = symbol.get('filters', [])
            for filter_info in filters:
                if filter_info.get('filterType') == 'PRICE_FILTER':
                    print(f"   Min Price: {filter_info.get('minPrice', 'N/A')}")
                    print(f"   Max Price: {filter_info.get('maxPrice', 'N/A')}")
                    print(f"   Tick Size: {filter_info.get('tickSize', 'N/A')}")
                elif filter_info.get('filterType') == 'LOT_SIZE':
                    print(f"   Min Qty: {filter_info.get('minQty', 'N/A')}")
                    print(f"   Max Qty: {filter_info.get('maxQty', 'N/A')}")
                    print(f"   Step Size: {filter_info.get('stepSize', 'N/A')}")
    
    def show_rate_limits(self):
        """Show API rate limits"""
        if not self.exchange_data:
            self.load_exchange_data()
            
        rate_limits = self.exchange_data.get('rateLimits', [])
        print(f"\n⏱️  RATE LIMITS")
        print("=" * 50)
        
        for limit in rate_limits:
            print(f"Type: {limit.get('rateLimitType', 'N/A')}")
            print(f"Interval: {limit.get('interval', 'N/A')}")
            print(f"Limit: {limit.get('limit', 'N/A')}")
            print()
    
    def search_symbols(self, query):
        """Search for symbols containing the query"""
        if not self.exchange_data:
            self.load_exchange_data()
            
        symbols = self.exchange_data.get('symbols', [])
        matches = []
        
        for symbol in symbols:
            symbol_name = symbol.get('symbol', '').upper()
            base_asset = symbol.get('baseAsset', '').upper()
            quote_asset = symbol.get('quoteAsset', '').upper()
            
            if (query.upper() in symbol_name or 
                query.upper() in base_asset or 
                query.upper() in quote_asset):
                matches.append(symbol)
        
        print(f"\n🔍 SEARCH RESULTS for '{query}'")
        print("=" * 50)
        print(f"Found {len(matches)} matches:")
        
        for symbol in matches:
            print(f"  {symbol.get('symbol', 'N/A')} ({symbol.get('baseAsset', 'N/A')}/{symbol.get('quoteAsset', 'N/A')})")
        
        return matches
    
    def export_symbols_to_json(self, filename="aster_symbols.json"):
        """Export all symbol data to JSON file"""
        if not self.exchange_data:
            self.load_exchange_data()
            
        with open(filename, 'w') as f:
            json.dump(self.exchange_data, f, indent=2)
        print(f"✅ Exported symbol data to {filename}")
    
    def run_full_exploration(self):
        """Run complete market exploration"""
        print("🚀 ASTER MARKET DATA EXPLORER")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Load data
            self.load_exchange_data()
            
            # Explore symbols
            symbols, base_assets = self.explore_symbols()
            
            # Show details
            self.show_symbol_details(limit=5)
            
            # Show rate limits
            self.show_rate_limits()
            
            # Export data
            self.export_symbols_to_json()
            
            print(f"\n✅ Exploration complete!")
            print(f"📁 Data exported to aster_symbols.json")
            
        except Exception as e:
            print(f"❌ Error during exploration: {e}")

def main():
    explorer = AsterMarketExplorer()
    
    while True:
        print("\n" + "="*60)
        print("ASTER MARKET DATA EXPLORER")
        print("="*60)
        print("1. Full exploration")
        print("2. Show symbol overview")
        print("3. Show symbol details")
        print("4. Search symbols")
        print("5. Show rate limits")
        print("6. Export to JSON")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            explorer.run_full_exploration()
        elif choice == "2":
            explorer.explore_symbols()
        elif choice == "3":
            limit = input("How many symbols to show? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            explorer.show_symbol_details(limit)
        elif choice == "4":
            query = input("Enter search query: ").strip()
            if query:
                explorer.search_symbols(query)
        elif choice == "5":
            explorer.show_rate_limits()
        elif choice == "6":
            filename = input("Enter filename (default: aster_symbols.json): ").strip()
            filename = filename if filename else "aster_symbols.json"
            explorer.export_symbols_to_json(filename)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
