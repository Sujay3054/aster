"""
Aster SDK - Basic Usage Example
Demonstrates basic functionality of the Aster SDK
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_example_utils import setup_info_client, print_market_summary, print_symbol_info


def main():
    """Main function demonstrating basic Aster SDK usage"""
    print("ASTER SDK - BASIC USAGE EXAMPLE")
    print("=" * 50)
    
    try:
        # Set up the Info client
        info = setup_info_client()
        
        # Print market summary
        print_market_summary(info)
        
        # Get server time
        print("\nSERVER TIME")
        print("-" * 30)
        server_time = info.server_time()
        print(f"Server Time: {server_time}")
        
        # Get exchange information
        print("\nEXCHANGE INFO")
        print("-" * 30)
        exchange_info = info.exchange_info()
        symbols = exchange_info.get('symbols', [])
        rate_limits = exchange_info.get('rateLimits', [])
        
        print(f"Total Symbols: {len(symbols)}")
        print(f"Rate Limits: {len(rate_limits)}")
        
        # Show rate limits
        for limit in rate_limits:
            limit_type = limit.get('rateLimitType', 'N/A')
            interval = limit.get('interval', 'N/A')
            limit_value = limit.get('limit', 'N/A')
            print(f"  {limit_type}: {limit_value} requests per {interval}")
        
        # Get current prices for major cryptocurrencies
        print("\nMAJOR CRYPTOCURRENCY PRICES")
        print("-" * 40)
        prices = info.ticker_price()
        
        major_cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 
                        'DOGEUSDT', 'ADAUSDT', 'DOTUSDT', 'ASTERUSDT']
        
        for symbol in major_cryptos:
            price_data = next((p for p in prices if p.get('symbol') == symbol), None)
            if price_data:
                price = float(price_data.get('price', 0))
                print(f"{symbol:<12}: ${price:>12,.4f}")
        
        # Get 24hr statistics
        print("\n24HR STATISTICS (Top 10 by Volume)")
        print("-" * 50)
        stats_24hr = info.ticker_24hr()
        
        # Sort by volume and show top 10
        top_volume = sorted(stats_24hr, 
                          key=lambda x: float(x.get('volume', 0)), 
                          reverse=True)[:10]
        
        print(f"{'Symbol':<12} {'Price':<12} {'Change':<10} {'Volume':<15}")
        print("-" * 50)
        
        for ticker in top_volume:
            symbol = ticker.get('symbol', 'N/A')
            price = float(ticker.get('lastPrice', 0))
            change = ticker.get('priceChangePercent', '0')
            volume = float(ticker.get('volume', 0))
            
            print(f"{symbol:<12} ${price:<11,.4f} {change:<9}% ${volume:<14,.0f}")
        
        # Get best bid/ask prices
        print("\nBEST BID/ASK PRICES (Sample)")
        print("-" * 40)
        best_prices = info.ticker_book_ticker()
        
        # Show first 5 symbols
        for i, best in enumerate(best_prices[:5]):
            symbol = best.get('symbol', 'N/A')
            bid = float(best.get('bidPrice', 0))
            ask = float(best.get('askPrice', 0))
            spread = ask - bid
            
            print(f"{symbol:<12}: Bid ${bid:<10,.4f} Ask ${ask:<10,.4f} Spread ${spread:.4f}")
        
        # Get funding rates
        print("\nFUNDING RATES (Sample)")
        print("-" * 30)
        funding_rates = info.funding_rate()
        
        # Show first 5 funding rates
        for i, rate in enumerate(funding_rates[:5]):
            symbol = rate.get('symbol', 'N/A')
            funding_rate = float(rate.get('fundingRate', 0))
            funding_time = rate.get('fundingTime', 0)
            
            print(f"{symbol:<12}: {funding_rate:>8.6f} (Time: {funding_time})")
        
        print("\nOK Basic usage example completed successfully!")
        
    except Exception as e:
        print(f"Error in basic usage example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()