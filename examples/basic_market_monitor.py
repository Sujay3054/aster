"""
Aster SDK - Basic Market Monitor Example
Demonstrates real-time market monitoring capabilities
"""

import sys
import os
import time
import threading
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_example_utils import setup_info_client, format_price, format_volume, format_percentage


class AsterMarketMonitor:
    """Real-time market monitor for Aster exchange"""
    
    def __init__(self, symbols=None, refresh_interval=5):
        """
        Initialize the market monitor
        
        Args:
            symbols: List of symbols to monitor (defaults to major cryptos)
            refresh_interval: Refresh interval in seconds
        """
        self.info = setup_info_client()
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 
                                  'DOGEUSDT', 'ADAUSDT', 'DOTUSDT', 'ASTERUSDT']
        self.refresh_interval = refresh_interval
        self.running = False
        self.monitor_thread = None
        
        # Data storage
        self.last_prices = {}
        self.price_changes = {}
        
    def start_monitoring(self):
        """Start the market monitoring"""
        print(f"🚀 Starting Aster Market Monitor")
        print(f"📊 Monitoring {len(self.symbols)} symbols")
        print(f"⏱️  Refresh interval: {self.refresh_interval} seconds")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the market monitoring"""
        print("\n\n🛑 Stopping market monitor...")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("✅ Market monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._update_prices()
                self._display_prices()
                time.sleep(self.refresh_interval)
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(self.refresh_interval)
    
    def _update_prices(self):
        """Update current prices"""
        try:
            prices = self.info.ticker_price()
            stats_24hr = self.info.ticker_24hr()
            
            # Create lookup for 24hr stats
            stats_lookup = {s.get('symbol'): s for s in stats_24hr}
            
            for symbol in self.symbols:
                price_data = next((p for p in prices if p.get('symbol') == symbol), None)
                if price_data:
                    current_price = float(price_data.get('price', 0))
                    stat_data = stats_lookup.get(symbol, {})
                    
                    # Calculate price change from last update
                    if symbol in self.last_prices:
                        price_change = current_price - self.last_prices[symbol]
                        self.price_changes[symbol] = price_change
                    
                    self.last_prices[symbol] = current_price
                    
        except Exception as e:
            print(f"Error updating prices: {e}")
    
    def _display_prices(self):
        """Display current prices with changes"""
        # Clear screen (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🚀 ASTER MARKET MONITOR")
        print("=" * 60)
        print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Display prices
        print(f"{'Symbol':<12} {'Price':<15} {'24h Change':<12} {'Volume':<15} {'Live Change':<12}")
        print("-" * 70)
        
        try:
            stats_24hr = self.info.ticker_24hr()
            stats_lookup = {s.get('symbol'): s for s in stats_24hr}
            
            for symbol in self.symbols:
                if symbol in self.last_prices:
                    price = self.last_prices[symbol]
                    stat_data = stats_lookup.get(symbol, {})
                    
                    # 24hr change
                    change_24h = stat_data.get('priceChangePercent', '0')
                    volume = float(stat_data.get('volume', 0))
                    
                    # Live change
                    live_change = self.price_changes.get(symbol, 0)
                    live_change_pct = (live_change / (price - live_change)) * 100 if live_change != 0 else 0
                    
                    # Format live change with color coding
                    if live_change > 0:
                        live_change_str = f"+{live_change_pct:.2f}%"
                    elif live_change < 0:
                        live_change_str = f"{live_change_pct:.2f}%"
                    else:
                        live_change_str = "0.00%"
                    
                    print(f"{symbol:<12} {format_price(price):<15} {format_percentage(change_24h):<12} "
                          f"{format_volume(volume):<15} {live_change_str:<12}")
        
        except Exception as e:
            print(f"Error displaying prices: {e}")
        
        print(f"\nNext update in {self.refresh_interval} seconds...")


def monitor_specific_symbols():
    """Monitor specific symbols with custom settings"""
    print("🔍 CUSTOM SYMBOL MONITOR")
    print("=" * 40)
    
    # Get user input for symbols
    symbols_input = input("Enter symbols to monitor (comma-separated, e.g., BTCUSDT,ETHUSDT): ").strip()
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
    else:
        symbols = ['BTCUSDT', 'ETHUSDT', 'ASTERUSDT']
    
    # Get refresh interval
    interval_input = input("Enter refresh interval in seconds (default 5): ").strip()
    try:
        interval = int(interval_input) if interval_input else 5
    except ValueError:
        interval = 5
    
    # Start monitoring
    monitor = AsterMarketMonitor(symbols, interval)
    monitor.start_monitoring()


def monitor_top_movers():
    """Monitor top movers dynamically"""
    print("📈 TOP MOVERS MONITOR")
    print("=" * 30)
    
    try:
        info = setup_info_client()
        stats_24hr = info.ticker_24hr()
        
        # Get top 10 gainers and losers
        gainers = sorted(stats_24hr, 
                        key=lambda x: float(x.get('priceChangePercent', 0)), 
                        reverse=True)[:5]
        
        losers = sorted(stats_24hr, 
                       key=lambda x: float(x.get('priceChangePercent', 0)))[:5]
        
        # Combine and get unique symbols
        top_movers = list(set([g.get('symbol') for g in gainers] + [l.get('symbol') for l in losers]))
        
        print(f"Monitoring top movers: {', '.join(top_movers)}")
        
        # Start monitoring
        monitor = AsterMarketMonitor(top_movers, 10)
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"Error setting up top movers monitor: {e}")


def main():
    """Main function for market monitoring examples"""
    print("🚀 ASTER SDK - MARKET MONITORING EXAMPLES")
    print("=" * 50)
    
    while True:
        print("\nChoose monitoring option:")
        print("1. Monitor major cryptocurrencies")
        print("2. Monitor custom symbols")
        print("3. Monitor top movers")
        print("4. Quick price check")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            # Monitor major cryptos
            monitor = AsterMarketMonitor()
            monitor.start_monitoring()
        elif choice == "2":
            monitor_specific_symbols()
        elif choice == "3":
            monitor_top_movers()
        elif choice == "4":
            # Quick price check
            try:
                info = setup_info_client()
                prices = info.ticker_price()
                
                print("\n💰 QUICK PRICE CHECK")
                print("-" * 30)
                
                major_cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ASTERUSDT']
                for symbol in major_cryptos:
                    price_data = next((p for p in prices if p.get('symbol') == symbol), None)
                    if price_data:
                        price = float(price_data.get('price', 0))
                        print(f"{symbol}: {format_price(price)}")
                
            except Exception as e:
                print(f"Error in quick price check: {e}")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
