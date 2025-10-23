"""
Aster SDK - Basic Portfolio Tracker Example
Demonstrates how to track a portfolio using Aster market data
"""

import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_example_utils import setup_info_client, format_price, format_volume, save_data_to_file


class AsterPortfolioTracker:
    """Portfolio tracker for Aster exchange"""
    
    def __init__(self, portfolio_file="portfolio.json"):
        """
        Initialize portfolio tracker
        
        Args:
            portfolio_file: Path to portfolio configuration file
        """
        self.info = setup_info_client()
        self.portfolio_file = portfolio_file
        self.portfolio = self._load_portfolio()
        
    def _load_portfolio(self):
        """Load portfolio from file or create default"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    portfolio = json.load(f)
                print(f"✅ Loaded portfolio from {self.portfolio_file}")
                return portfolio
            except Exception as e:
                print(f"❌ Error loading portfolio: {e}")
        
        # Create default portfolio
        default_portfolio = {
            "holdings": {
                "BTCUSDT": 0.1,
                "ETHUSDT": 1.0,
                "BNBUSDT": 5.0,
                "SOLUSDT": 10.0,
                "ASTERUSDT": 1000.0
            },
            "last_updated": datetime.now().isoformat(),
            "description": "Default portfolio - edit portfolio.json to customize"
        }
        
        self._save_portfolio(default_portfolio)
        print(f"✅ Created default portfolio in {self.portfolio_file}")
        return default_portfolio
    
    def _save_portfolio(self, portfolio):
        """Save portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving portfolio: {e}")
    
    def update_portfolio(self, symbol, amount):
        """
        Update portfolio holdings
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            amount: Amount to hold
        """
        self.portfolio['holdings'][symbol] = amount
        self.portfolio['last_updated'] = datetime.now().isoformat()
        self._save_portfolio(self.portfolio)
        print(f"✅ Updated {symbol} to {amount}")
    
    def add_holding(self, symbol, amount):
        """
        Add to existing holding
        
        Args:
            symbol: Trading symbol
            amount: Amount to add
        """
        current = self.portfolio['holdings'].get(symbol, 0)
        new_amount = current + amount
        self.update_portfolio(symbol, new_amount)
    
    def remove_holding(self, symbol, amount):
        """
        Remove from existing holding
        
        Args:
            symbol: Trading symbol
            amount: Amount to remove
        """
        current = self.portfolio['holdings'].get(symbol, 0)
        new_amount = max(0, current - amount)
        self.update_portfolio(symbol, new_amount)
    
    def get_portfolio_value(self):
        """Calculate current portfolio value"""
        try:
            prices = self.info.ticker_price()
            price_lookup = {p.get('symbol'): float(p.get('price', 0)) for p in prices}
            
            total_value = 0
            holdings_value = {}
            
            for symbol, amount in self.portfolio['holdings'].items():
                if amount > 0:
                    price = price_lookup.get(symbol, 0)
                    value = amount * price
                    holdings_value[symbol] = {
                        'amount': amount,
                        'price': price,
                        'value': value
                    }
                    total_value += value
            
            return {
                'total_value': total_value,
                'holdings': holdings_value,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error calculating portfolio value: {e}")
            return None
    
    def display_portfolio(self):
        """Display current portfolio"""
        print("\n💼 PORTFOLIO OVERVIEW")
        print("=" * 60)
        
        portfolio_value = self.get_portfolio_value()
        if not portfolio_value:
            print("❌ Could not calculate portfolio value")
            return
        
        total_value = portfolio_value['total_value']
        holdings = portfolio_value['holdings']
        
        print(f"Total Portfolio Value: {format_price(total_value)}")
        print(f"Last Updated: {portfolio_value['last_updated']}")
        print()
        
        if not holdings:
            print("No holdings in portfolio")
            return
        
        print(f"{'Symbol':<12} {'Amount':<15} {'Price':<15} {'Value':<15} {'%':<8}")
        print("-" * 70)
        
        for symbol, data in holdings.items():
            amount = data['amount']
            price = data['price']
            value = data['value']
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            
            print(f"{symbol:<12} {amount:<15.6f} {format_price(price):<15} "
                  f"{format_price(value):<15} {percentage:<7.2f}%")
    
    def get_portfolio_performance(self):
        """Get portfolio performance metrics"""
        try:
            stats_24hr = self.info.ticker_24hr()
            stats_lookup = {s.get('symbol'): s for s in stats_24hr}
            
            portfolio_value = self.get_portfolio_value()
            if not portfolio_value:
                return None
            
            total_change_24h = 0
            holdings_performance = {}
            
            for symbol, data in portfolio_value['holdings'].items():
                amount = data['amount']
                current_price = data['price']
                stat_data = stats_lookup.get(symbol, {})
                
                # Calculate 24h change
                change_pct = float(stat_data.get('priceChangePercent', 0))
                change_value = (current_price * change_pct / 100) * amount
                
                holdings_performance[symbol] = {
                    'change_24h_pct': change_pct,
                    'change_24h_value': change_value
                }
                
                total_change_24h += change_value
            
            total_value = portfolio_value['total_value']
            total_change_pct = (total_change_24h / total_value) * 100 if total_value > 0 else 0
            
            return {
                'total_change_24h_value': total_change_24h,
                'total_change_24h_pct': total_change_pct,
                'holdings_performance': holdings_performance
            }
            
        except Exception as e:
            print(f"❌ Error calculating portfolio performance: {e}")
            return None
    
    def display_performance(self):
        """Display portfolio performance"""
        print("\n📈 PORTFOLIO PERFORMANCE (24h)")
        print("=" * 50)
        
        performance = self.get_portfolio_performance()
        if not performance:
            print("❌ Could not calculate performance")
            return
        
        total_change_value = performance['total_change_24h_value']
        total_change_pct = performance['total_change_24h_pct']
        
        # Format change with color coding
        if total_change_value > 0:
            change_str = f"+{format_price(total_change_value)} (+{total_change_pct:.2f}%)"
        elif total_change_value < 0:
            change_str = f"{format_price(total_change_value)} ({total_change_pct:.2f}%)"
        else:
            change_str = f"{format_price(total_change_value)} (0.00%)"
        
        print(f"24h Change: {change_str}")
        print()
        
        print(f"{'Symbol':<12} {'24h Change %':<12} {'24h Change $':<15}")
        print("-" * 40)
        
        for symbol, perf in performance['holdings_performance'].items():
            change_pct = perf['change_24h_pct']
            change_value = perf['change_24h_value']
            
            if change_pct > 0:
                change_pct_str = f"+{change_pct:.2f}%"
            else:
                change_pct_str = f"{change_pct:.2f}%"
            
            print(f"{symbol:<12} {change_pct_str:<12} {format_price(change_value):<15}")
    
    def export_portfolio_report(self):
        """Export comprehensive portfolio report"""
        print("\n💾 EXPORTING PORTFOLIO REPORT")
        print("=" * 35)
        
        try:
            portfolio_value = self.get_portfolio_value()
            performance = self.get_portfolio_performance()
            
            if not portfolio_value or not performance:
                print("❌ Could not generate report")
                return
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio': self.portfolio,
                'current_value': portfolio_value,
                'performance': performance
            }
            
            filename = f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_data_to_file(report, filename)
            
            print(f"✅ Portfolio report exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting portfolio report: {e}")


def main():
    """Main function for portfolio tracking"""
    print("🚀 ASTER SDK - PORTFOLIO TRACKER")
    print("=" * 40)
    
    tracker = AsterPortfolioTracker()
    
    while True:
        print("\nPortfolio Tracker Options:")
        print("1. View portfolio")
        print("2. View performance")
        print("3. Update holding")
        print("4. Add to holding")
        print("5. Remove from holding")
        print("6. Export report")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            tracker.display_portfolio()
        elif choice == "2":
            tracker.display_performance()
        elif choice == "3":
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            try:
                amount = float(input("Enter amount: "))
                tracker.update_portfolio(symbol, amount)
            except ValueError:
                print("❌ Invalid amount")
        elif choice == "4":
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            try:
                amount = float(input("Enter amount to add: "))
                tracker.add_holding(symbol, amount)
            except ValueError:
                print("❌ Invalid amount")
        elif choice == "5":
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            try:
                amount = float(input("Enter amount to remove: "))
                tracker.remove_holding(symbol, amount)
            except ValueError:
                print("❌ Invalid amount")
        elif choice == "6":
            tracker.export_portfolio_report()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
