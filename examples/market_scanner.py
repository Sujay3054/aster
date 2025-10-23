"""
Aster SDK - Market Scanner
Advanced market scanning for trading opportunities
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL
from aster_example_utils import format_price, format_volume, format_percentage, save_data_to_file


class MarketScanner:
    """Advanced market scanner for trading opportunities"""
    
    def __init__(self):
        """Initialize market scanner"""
        self.info = Info(MAINNET_API_URL)
        self.scan_results = []
        self.alert_history = []
    
    def scan_volume_spikes(self, min_volume_increase: float = 2.0, min_volume: float = 1000000) -> List[Dict[str, Any]]:
        """
        Scan for volume spikes
        
        Args:
            min_volume_increase: Minimum volume increase multiplier
            min_volume: Minimum volume threshold
            
        Returns:
            List of symbols with volume spikes
        """
        try:
            print("Scanning for volume spikes...")
            
            # Get 24hr statistics
            stats_24hr = self.info.ticker_24hr()
            
            volume_spikes = []
            for ticker in stats_24hr:
                symbol = ticker.get('symbol', '')
                volume = float(ticker.get('volume', 0))
                price = float(ticker.get('lastPrice', 0))
                change_pct = float(ticker.get('priceChangePercent', 0))
                
                # Calculate volume value
                volume_value = volume * price
                
                if volume_value >= min_volume:
                    # For now, we'll use a simple heuristic for volume spikes
                    # In a real implementation, you'd compare with historical averages
                    if abs(change_pct) > 5:  # Significant price movement
                        volume_spikes.append({
                            'symbol': symbol,
                            'volume': volume,
                            'volume_value': volume_value,
                            'price': price,
                            'change_pct': change_pct,
                            'type': 'VOLUME_SPIKE',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Sort by volume value
            volume_spikes.sort(key=lambda x: x['volume_value'], reverse=True)
            
            return volume_spikes[:20]  # Top 20
            
        except Exception as e:
            print(f"Error scanning volume spikes: {e}")
            return []
    
    def scan_price_breakouts(self, min_change: float = 10.0) -> List[Dict[str, Any]]:
        """
        Scan for price breakouts
        
        Args:
            min_change: Minimum price change percentage
            
        Returns:
            List of symbols with price breakouts
        """
        try:
            print("Scanning for price breakouts...")
            
            stats_24hr = self.info.ticker_24hr()
            
            breakouts = []
            for ticker in stats_24hr:
                symbol = ticker.get('symbol', '')
                change_pct = float(ticker.get('priceChangePercent', 0))
                price = float(ticker.get('lastPrice', 0))
                volume = float(ticker.get('volume', 0))
                high = float(ticker.get('highPrice', 0))
                low = float(ticker.get('lowPrice', 0))
                
                if abs(change_pct) >= min_change:
                    # Calculate volatility
                    volatility = ((high - low) / low * 100) if low > 0 else 0
                    
                    breakouts.append({
                        'symbol': symbol,
                        'price': price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'volatility': volatility,
                        'high': high,
                        'low': low,
                        'type': 'PRICE_BREAKOUT',
                        'direction': 'UP' if change_pct > 0 else 'DOWN',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sort by absolute change
            breakouts.sort(key=lambda x: abs(x['change_pct']), reverse=True)
            
            return breakouts[:20]  # Top 20
            
        except Exception as e:
            print(f"Error scanning price breakouts: {e}")
            return []
    
    def scan_oversold_overbought(self, rsi_threshold: float = 30.0, overbought_threshold: float = 70.0) -> List[Dict[str, Any]]:
        """
        Scan for oversold/overbought conditions
        
        Args:
            rsi_threshold: RSI threshold for oversold
            overbought_threshold: RSI threshold for overbought
            
        Returns:
            List of symbols with oversold/overbought conditions
        """
        try:
            print("Scanning for oversold/overbought conditions...")
            
            stats_24hr = self.info.ticker_24hr()
            
            conditions = []
            for ticker in stats_24hr:
                symbol = ticker.get('symbol', '')
                change_pct = float(ticker.get('priceChangePercent', 0))
                price = float(ticker.get('lastPrice', 0))
                volume = float(ticker.get('volume', 0))
                
                # Simple RSI approximation using price change
                # In a real implementation, you'd calculate actual RSI
                rsi_approx = 50 + (change_pct * 2)  # Rough approximation
                rsi_approx = max(0, min(100, rsi_approx))
                
                if rsi_approx <= rsi_threshold:
                    conditions.append({
                        'symbol': symbol,
                        'price': price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'rsi_approx': rsi_approx,
                        'type': 'OVERSOLD',
                        'timestamp': datetime.now().isoformat()
                    })
                elif rsi_approx >= overbought_threshold:
                    conditions.append({
                        'symbol': symbol,
                        'price': price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'rsi_approx': rsi_approx,
                        'type': 'OVERBOUGHT',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sort by RSI value
            conditions.sort(key=lambda x: abs(x['rsi_approx'] - 50), reverse=True)
            
            return conditions[:20]  # Top 20
            
        except Exception as e:
            print(f"Error scanning oversold/overbought: {e}")
            return []
    
    def scan_momentum(self, min_momentum: float = 5.0) -> List[Dict[str, Any]]:
        """
        Scan for momentum opportunities
        
        Args:
            min_momentum: Minimum momentum threshold
            
        Returns:
            List of symbols with momentum
        """
        try:
            print("Scanning for momentum opportunities...")
            
            stats_24hr = self.info.ticker_24hr()
            
            momentum_list = []
            for ticker in stats_24hr:
                symbol = ticker.get('symbol', '')
                change_pct = float(ticker.get('priceChangePercent', 0))
                price = float(ticker.get('lastPrice', 0))
                volume = float(ticker.get('volume', 0))
                
                if abs(change_pct) >= min_momentum:
                    # Calculate momentum score
                    volume_score = min(10, volume / 1000000)  # Volume score
                    price_score = abs(change_pct) / 10  # Price change score
                    momentum_score = volume_score + price_score
                    
                    momentum_list.append({
                        'symbol': symbol,
                        'price': price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'momentum_score': momentum_score,
                        'type': 'MOMENTUM',
                        'direction': 'UP' if change_pct > 0 else 'DOWN',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Sort by momentum score
            momentum_list.sort(key=lambda x: x['momentum_score'], reverse=True)
            
            return momentum_list[:20]  # Top 20
            
        except Exception as e:
            print(f"Error scanning momentum: {e}")
            return []
    
    def scan_arbitrage_opportunities(self, min_spread: float = 0.5) -> List[Dict[str, Any]]:
        """
        Scan for arbitrage opportunities
        
        Args:
            min_spread: Minimum spread percentage
            
        Returns:
            List of arbitrage opportunities
        """
        try:
            print("Scanning for arbitrage opportunities...")
            
            # Get best bid/ask prices
            best_prices = self.info.ticker_book_ticker()
            
            arbitrage_ops = []
            for price_data in best_prices:
                symbol = price_data.get('symbol', '')
                bid_price = float(price_data.get('bidPrice', 0))
                ask_price = float(price_data.get('askPrice', 0))
                bid_qty = float(price_data.get('bidQty', 0))
                ask_qty = float(price_data.get('askQty', 0))
                
                if bid_price > 0 and ask_price > 0:
                    spread = ((ask_price - bid_price) / bid_price) * 100
                    
                    if spread >= min_spread:
                        arbitrage_ops.append({
                            'symbol': symbol,
                            'bid_price': bid_price,
                            'ask_price': ask_price,
                            'bid_qty': bid_qty,
                            'ask_qty': ask_qty,
                            'spread_pct': spread,
                            'type': 'ARBITRAGE',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Sort by spread
            arbitrage_ops.sort(key=lambda x: x['spread_pct'], reverse=True)
            
            return arbitrage_ops[:10]  # Top 10
            
        except Exception as e:
            print(f"Error scanning arbitrage opportunities: {e}")
            return []
    
    def comprehensive_scan(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform comprehensive market scan
        
        Returns:
            Dictionary with all scan results
        """
        print("Performing comprehensive market scan...")
        
        results = {
            'volume_spikes': self.scan_volume_spikes(),
            'price_breakouts': self.scan_price_breakouts(),
            'oversold_overbought': self.scan_oversold_overbought(),
            'momentum': self.scan_momentum(),
            'arbitrage': self.scan_arbitrage_opportunities(),
            'scan_time': datetime.now().isoformat()
        }
        
        self.scan_results = results
        return results
    
    def display_scan_results(self, results: Dict[str, List[Dict[str, Any]]]):
        """Display scan results in formatted output"""
        print("\nMARKET SCAN RESULTS")
        print("=" * 80)
        print(f"Scan Time: {results['scan_time']}")
        
        # Volume Spikes
        if results['volume_spikes']:
            print(f"\nVOLUME SPIKES (Top {len(results['volume_spikes'])})")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Price':<12} {'Volume':<15} {'Change %':<10}")
            for item in results['volume_spikes'][:10]:
                print(f"{item['symbol']:<12} {format_price(item['price']):<12} "
                      f"{format_volume(item['volume_value']):<15} {format_percentage(str(item['change_pct'])):<10}")
        
        # Price Breakouts
        if results['price_breakouts']:
            print(f"\nPRICE BREAKOUTS (Top {len(results['price_breakouts'])})")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Price':<12} {'Change %':<10} {'Direction':<10} {'Volatility':<12}")
            for item in results['price_breakouts'][:10]:
                print(f"{item['symbol']:<12} {format_price(item['price']):<12} "
                      f"{format_percentage(str(item['change_pct'])):<10} {item['direction']:<10} {item['volatility']:<11.2f}%")
        
        # Oversold/Overbought
        if results['oversold_overbought']:
            print(f"\nOVERSOLD/OVERBOUGHT (Top {len(results['oversold_overbought'])})")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Price':<12} {'RSI':<8} {'Type':<12} {'Change %':<10}")
            for item in results['oversold_overbought'][:10]:
                print(f"{item['symbol']:<12} {format_price(item['price']):<12} "
                      f"{item['rsi_approx']:<7.1f} {item['type']:<12} {format_percentage(str(item['change_pct'])):<10}")
        
        # Momentum
        if results['momentum']:
            print(f"\nMOMENTUM OPPORTUNITIES (Top {len(results['momentum'])})")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Price':<12} {'Momentum':<10} {'Direction':<10} {'Change %':<10}")
            for item in results['momentum'][:10]:
                print(f"{item['symbol']:<12} {format_price(item['price']):<12} "
                      f"{item['momentum_score']:<9.2f} {item['direction']:<10} {format_percentage(str(item['change_pct'])):<10}")
        
        # Arbitrage
        if results['arbitrage']:
            print(f"\nARBITRAGE OPPORTUNITIES (Top {len(results['arbitrage'])})")
            print("-" * 60)
            print(f"{'Symbol':<12} {'Bid':<12} {'Ask':<12} {'Spread %':<10}")
            for item in results['arbitrage'][:10]:
                print(f"{item['symbol']:<12} {format_price(item['bid_price']):<12} "
                      f"{format_price(item['ask_price']):<12} {item['spread_pct']:<9.2f}%")
    
    def create_alerts(self, results: Dict[str, List[Dict[str, Any]]], alert_thresholds: Dict[str, float]):
        """
        Create alerts based on scan results
        
        Args:
            results: Scan results
            alert_thresholds: Alert thresholds
        """
        alerts = []
        
        # Volume spike alerts
        for item in results.get('volume_spikes', []):
            if item['change_pct'] >= alert_thresholds.get('volume_spike_change', 10):
                alerts.append({
                    'type': 'VOLUME_SPIKE',
                    'symbol': item['symbol'],
                    'message': f"Volume spike detected: {item['symbol']} +{item['change_pct']:.1f}%",
                    'priority': 'HIGH' if item['change_pct'] > 20 else 'MEDIUM',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Price breakout alerts
        for item in results.get('price_breakouts', []):
            if abs(item['change_pct']) >= alert_thresholds.get('breakout_change', 15):
                alerts.append({
                    'type': 'PRICE_BREAKOUT',
                    'symbol': item['symbol'],
                    'message': f"Price breakout: {item['symbol']} {item['change_pct']:+.1f}%",
                    'priority': 'HIGH' if abs(item['change_pct']) > 25 else 'MEDIUM',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Oversold/Overbought alerts
        for item in results.get('oversold_overbought', []):
            if item['type'] == 'OVERSOLD' and item['rsi_approx'] <= alert_thresholds.get('oversold_rsi', 25):
                alerts.append({
                    'type': 'OVERSOLD',
                    'symbol': item['symbol'],
                    'message': f"Oversold condition: {item['symbol']} RSI {item['rsi_approx']:.1f}",
                    'priority': 'MEDIUM',
                    'timestamp': datetime.now().isoformat()
                })
            elif item['type'] == 'OVERBOUGHT' and item['rsi_approx'] >= alert_thresholds.get('overbought_rsi', 75):
                alerts.append({
                    'type': 'OVERBOUGHT',
                    'symbol': item['symbol'],
                    'message': f"Overbought condition: {item['symbol']} RSI {item['rsi_approx']:.1f}",
                    'priority': 'MEDIUM',
                    'timestamp': datetime.now().isoformat()
                })
        
        self.alert_history.extend(alerts)
        return alerts
    
    def export_scan_results(self, results: Dict[str, List[Dict[str, Any]]], filename: Optional[str] = None):
        """Export scan results to JSON"""
        if filename is None:
            filename = f"aster_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        save_data_to_file(results, filename)
        print(f"Scan results exported to {filename}")
    
    def monitor_market(self, interval: int = 300, alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Monitor market continuously
        
        Args:
            interval: Monitoring interval in seconds
            alert_thresholds: Alert thresholds
        """
        if alert_thresholds is None:
            alert_thresholds = {
                'volume_spike_change': 10,
                'breakout_change': 15,
                'oversold_rsi': 25,
                'overbought_rsi': 75
            }
        
        print(f"Starting market monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("ASTER MARKET MONITOR")
                print("=" * 50)
                print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Perform scan
                results = self.comprehensive_scan()
                
                # Create alerts
                alerts = self.create_alerts(results, alert_thresholds)
                
                # Display results
                self.display_scan_results(results)
                
                # Display alerts
                if alerts:
                    print(f"\nALERTS ({len(alerts)})")
                    print("-" * 40)
                    for alert in alerts[-5:]:  # Show last 5 alerts
                        priority_icon = "🔴" if alert['priority'] == 'HIGH' else "🟡"
                        print(f"{priority_icon} {alert['message']}")
                
                print(f"\nNext scan in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMarket monitoring stopped")


def main():
    """Main function for market scanner demo"""
    print("ASTER SDK - MARKET SCANNER")
    print("=" * 40)
    
    try:
        scanner = MarketScanner()
        
        while True:
            print("\nMarket Scanner Options:")
            print("1. Scan volume spikes")
            print("2. Scan price breakouts")
            print("3. Scan oversold/overbought")
            print("4. Scan momentum")
            print("5. Scan arbitrage opportunities")
            print("6. Comprehensive scan")
            print("7. Monitor market (continuous)")
            print("8. Export last scan results")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                # Volume spikes
                results = scanner.scan_volume_spikes()
                scanner.display_scan_results({'volume_spikes': results, 'scan_time': datetime.now().isoformat()})
                
            elif choice == "2":
                # Price breakouts
                results = scanner.scan_price_breakouts()
                scanner.display_scan_results({'price_breakouts': results, 'scan_time': datetime.now().isoformat()})
                
            elif choice == "3":
                # Oversold/overbought
                results = scanner.scan_oversold_overbought()
                scanner.display_scan_results({'oversold_overbought': results, 'scan_time': datetime.now().isoformat()})
                
            elif choice == "4":
                # Momentum
                results = scanner.scan_momentum()
                scanner.display_scan_results({'momentum': results, 'scan_time': datetime.now().isoformat()})
                
            elif choice == "5":
                # Arbitrage
                results = scanner.scan_arbitrage_opportunities()
                scanner.display_scan_results({'arbitrage': results, 'scan_time': datetime.now().isoformat()})
                
            elif choice == "6":
                # Comprehensive scan
                results = scanner.comprehensive_scan()
                scanner.display_scan_results(results)
                
            elif choice == "7":
                # Monitor market
                interval = input("Enter monitoring interval in seconds (default 300): ").strip()
                interval = int(interval) if interval.isdigit() else 300
                scanner.monitor_market(interval)
                
            elif choice == "8":
                # Export results
                if scanner.scan_results:
                    scanner.export_scan_results(scanner.scan_results)
                else:
                    print("No scan results to export. Run a scan first.")
                    
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in market scanner: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
