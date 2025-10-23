"""
Aster SDK - Basic Market Data Example
Demonstrates how to retrieve and analyze market data
"""

import sys
import os
import time
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_example_utils import setup_info_client, save_data_to_file, format_price, format_volume, format_percentage


def analyze_top_movers(info):
    """Analyze and display top gainers and losers"""
    print("\n📈 TOP MOVERS ANALYSIS")
    print("=" * 50)
    
    try:
        stats_24hr = info.ticker_24hr()
        
        # Sort by price change percentage
        gainers = sorted(stats_24hr, 
                        key=lambda x: float(x.get('priceChangePercent', 0)), 
                        reverse=True)[:10]
        
        losers = sorted(stats_24hr, 
                       key=lambda x: float(x.get('priceChangePercent', 0)))[:10]
        
        print("TOP 10 GAINERS:")
        print(f"{'Symbol':<12} {'Price':<12} {'Change':<10} {'Volume':<15}")
        print("-" * 50)
        
        for ticker in gainers:
            symbol = ticker.get('symbol', 'N/A')
            price = float(ticker.get('lastPrice', 0))
            change = ticker.get('priceChangePercent', '0')
            volume = float(ticker.get('volume', 0))
            
            print(f"{symbol:<12} {format_price(price):<12} {format_percentage(change):<10} {format_volume(volume):<15}")
        
        print("\nTOP 10 LOSERS:")
        print(f"{'Symbol':<12} {'Price':<12} {'Change':<10} {'Volume':<15}")
        print("-" * 50)
        
        for ticker in losers:
            symbol = ticker.get('symbol', 'N/A')
            price = float(ticker.get('lastPrice', 0))
            change = ticker.get('priceChangePercent', '0')
            volume = float(ticker.get('volume', 0))
            
            print(f"{symbol:<12} {format_price(price):<12} {format_percentage(change):<10} {format_volume(volume):<15}")
        
    except Exception as e:
        print(f"Error analyzing top movers: {e}")


def analyze_volume_leaders(info):
    """Analyze and display volume leaders"""
    print("\n📊 VOLUME LEADERS")
    print("=" * 50)
    
    try:
        stats_24hr = info.ticker_24hr()
        
        # Sort by volume
        volume_leaders = sorted(stats_24hr, 
                              key=lambda x: float(x.get('volume', 0)), 
                              reverse=True)[:15]
        
        print(f"{'Symbol':<12} {'Price':<12} {'Volume':<15} {'Change':<10}")
        print("-" * 50)
        
        for ticker in volume_leaders:
            symbol = ticker.get('symbol', 'N/A')
            price = float(ticker.get('lastPrice', 0))
            volume = float(ticker.get('volume', 0))
            change = ticker.get('priceChangePercent', '0')
            
            print(f"{symbol:<12} {format_price(price):<12} {format_volume(volume):<15} {format_percentage(change):<10}")
        
    except Exception as e:
        print(f"Error analyzing volume leaders: {e}")


def analyze_price_ranges(info):
    """Analyze price ranges and volatility"""
    print("\n📏 PRICE RANGE ANALYSIS")
    print("=" * 50)
    
    try:
        stats_24hr = info.ticker_24hr()
        
        # Calculate price ranges
        ranges = []
        for ticker in stats_24hr:
            symbol = ticker.get('symbol', 'N/A')
            high = float(ticker.get('highPrice', 0))
            low = float(ticker.get('lowPrice', 0))
            current = float(ticker.get('lastPrice', 0))
            
            if high > 0 and low > 0:
                range_pct = ((high - low) / low) * 100
                ranges.append({
                    'symbol': symbol,
                    'high': high,
                    'low': low,
                    'current': current,
                    'range_pct': range_pct
                })
        
        # Sort by range percentage
        ranges.sort(key=lambda x: x['range_pct'], reverse=True)
        
        print("TOP 10 MOST VOLATILE (24hr range):")
        print(f"{'Symbol':<12} {'Current':<12} {'High':<12} {'Low':<12} {'Range %':<10}")
        print("-" * 60)
        
        for item in ranges[:10]:
            symbol = item['symbol']
            current = item['current']
            high = item['high']
            low = item['low']
            range_pct = item['range_pct']
            
            print(f"{symbol:<12} {format_price(current):<12} {format_price(high):<12} {format_price(low):<12} {range_pct:<9.2f}%")
        
    except Exception as e:
        print(f"Error analyzing price ranges: {e}")


def search_symbols(info, query):
    """Search for symbols containing the query"""
    print(f"\n🔍 SEARCH RESULTS for '{query}'")
    print("=" * 50)
    
    try:
        prices = info.ticker_price()
        stats_24hr = info.ticker_24hr()
        
        # Create a lookup for 24hr stats
        stats_lookup = {s.get('symbol'): s for s in stats_24hr}
        
        matches = []
        for price_data in prices:
            symbol = price_data.get('symbol', '')
            if query.upper() in symbol.upper():
                price = float(price_data.get('price', 0))
                stat_data = stats_lookup.get(symbol, {})
                change = stat_data.get('priceChangePercent', '0')
                volume = float(stat_data.get('volume', 0))
                
                matches.append({
                    'symbol': symbol,
                    'price': price,
                    'change': change,
                    'volume': volume
                })
        
        if matches:
            print(f"Found {len(matches)} matches:")
            print(f"{'Symbol':<12} {'Price':<12} {'Change':<10} {'Volume':<15}")
            print("-" * 50)
            
            for match in matches:
                symbol = match['symbol']
                price = match['price']
                change = match['change']
                volume = match['volume']
                
                print(f"{symbol:<12} {format_price(price):<12} {format_percentage(change):<10} {format_volume(volume):<15}")
        else:
            print(f"No symbols found matching '{query}'")
        
    except Exception as e:
        print(f"Error searching symbols: {e}")


def export_market_data(info):
    """Export comprehensive market data to JSON"""
    print("\n💾 EXPORTING MARKET DATA")
    print("=" * 30)
    
    try:
        # Collect all market data
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'server_time': info.server_time(),
            'exchange_info': info.exchange_info(),
            'prices': info.ticker_price(),
            'stats_24hr': info.ticker_24hr(),
            'best_prices': info.ticker_book_ticker(),
            'funding_rates': info.funding_rate()
        }
        
        # Save to file
        filename = f"aster_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_data_to_file(market_data, filename)
        
        print(f"Market data exported to {filename}")
        print(f"Total records: {len(market_data['prices'])} prices, {len(market_data['stats_24hr'])} 24hr stats")
        
    except Exception as e:
        print(f"Error exporting market data: {e}")


def main():
    """Main function demonstrating market data analysis"""
    print("🚀 ASTER SDK - MARKET DATA ANALYSIS")
    print("=" * 50)
    
    try:
        # Set up the Info client
        info = setup_info_client()
        
        # Run various analyses
        analyze_top_movers(info)
        analyze_volume_leaders(info)
        analyze_price_ranges(info)
        
        # Search for specific symbols
        search_symbols(info, "BTC")
        search_symbols(info, "ETH")
        
        # Export data
        export_market_data(info)
        
        print("\n✅ Market data analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in market data analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
