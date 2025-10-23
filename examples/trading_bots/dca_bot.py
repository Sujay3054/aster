"""
Aster SDK - DCA (Dollar Cost Averaging) Trading Bot
Automated DCA strategy implementation
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from aster_auth import AsterAuthenticatedClient
from aster_example_utils import format_price, save_data_to_file


class DCABot:
    """Dollar Cost Averaging Trading Bot"""
    
    def __init__(self, api_key: str, secret_key: str, config: Dict[str, Any]):
        """
        Initialize DCA bot
        
        Args:
            api_key: Aster API key
            secret_key: Aster secret key
            config: Bot configuration
        """
        self.client = AsterAuthenticatedClient(api_key, secret_key)
        self.config = config
        self.is_running = False
        self.last_purchase_time = {}
        self.purchase_history = []
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate bot configuration"""
        required_fields = ['symbol', 'amount', 'interval_hours', 'max_purchases']
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required configuration field: {field}")
        
        if self.config['amount'] <= 0:
            raise ValueError("Purchase amount must be positive")
        
        if self.config['interval_hours'] <= 0:
            raise ValueError("Interval must be positive")
        
        if self.config['max_purchases'] <= 0:
            raise ValueError("Max purchases must be positive")
    
    def get_account_balance(self) -> float:
        """Get USDT balance"""
        try:
            balance = self.client.get_balance()
            if balance.get('status') == 'ok':
                balances = balance.get('data', [])
                for bal in balances:
                    if bal.get('asset') == 'USDT':
                        return float(bal.get('free', 0))
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            # This would need to be implemented with the actual API
            # For now, we'll simulate a price
            import random
            base_price = 100.0  # Base price
            variation = random.uniform(-0.05, 0.05)  # 5% variation
            return base_price * (1 + variation)
        except Exception as e:
            print(f"Error getting price: {e}")
            return 0.0
    
    def place_buy_order(self, symbol: str, amount: float) -> Dict[str, Any]:
        """
        Place a buy order
        
        Args:
            symbol: Trading symbol
            amount: Amount in USDT
            
        Returns:
            Order result
        """
        try:
            current_price = self.get_current_price(symbol)
            if current_price <= 0:
                return {'status': 'error', 'message': 'Invalid price'}
            
            # Calculate quantity
            quantity = amount / current_price
            
            print(f"Placing DCA buy order: {amount} USDT for {quantity:.6f} {symbol}")
            
            # Place market buy order
            result = self.client.place_order(
                symbol=symbol,
                side='BUY',
                order_type='MARKET',
                quantity=quantity
            )
            
            if result.get('status') == 'ok':
                # Record purchase
                purchase_record = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'amount_usdt': amount,
                    'quantity': quantity,
                    'price': current_price,
                    'order_id': result.get('response', {}).get('data', {}).get('statuses', [{}])[0].get('resting', {}).get('oid')
                }
                
                self.purchase_history.append(purchase_record)
                self.last_purchase_time[symbol] = datetime.now()
                
                print(f"DCA purchase successful: {quantity:.6f} {symbol} at {format_price(current_price)}")
                
                return {'status': 'success', 'purchase': purchase_record}
            else:
                print(f"DCA purchase failed: {result}")
                return {'status': 'error', 'message': result.get('message', 'Unknown error')}
                
        except Exception as e:
            print(f"Error placing DCA order: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def should_purchase(self, symbol: str) -> bool:
        """
        Check if it's time to make a DCA purchase
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if should purchase
        """
        # Check if we've reached max purchases
        symbol_purchases = [p for p in self.purchase_history if p['symbol'] == symbol]
        if len(symbol_purchases) >= self.config['max_purchases']:
            return False
        
        # Check interval
        if symbol in self.last_purchase_time:
            time_since_last = datetime.now() - self.last_purchase_time[symbol]
            if time_since_last.total_seconds() < (self.config['interval_hours'] * 3600):
                return False
        
        # Check balance
        balance = self.get_account_balance()
        if balance < self.config['amount']:
            print(f"Insufficient balance: {balance} USDT < {self.config['amount']} USDT")
            return False
        
        return True
    
    def run_dca_cycle(self):
        """Run one DCA cycle"""
        symbol = self.config['symbol']
        
        if self.should_purchase(symbol):
            result = self.place_buy_order(symbol, self.config['amount'])
            
            if result['status'] == 'success':
                print(f"DCA cycle completed for {symbol}")
            else:
                print(f"DCA cycle failed for {symbol}: {result.get('message', 'Unknown error')}")
        else:
            print(f"DCA cycle skipped for {symbol} (conditions not met)")
    
    def start_bot(self):
        """Start the DCA bot"""
        print("Starting DCA Bot...")
        print(f"Symbol: {self.config['symbol']}")
        print(f"Amount: {self.config['amount']} USDT")
        print(f"Interval: {self.config['interval_hours']} hours")
        print(f"Max Purchases: {self.config['max_purchases']}")
        print("Press Ctrl+C to stop")
        
        self.is_running = True
        
        try:
            while self.is_running:
                self.run_dca_cycle()
                
                # Wait for next cycle
                wait_time = self.config['interval_hours'] * 3600
                print(f"Waiting {self.config['interval_hours']} hours until next DCA cycle...")
                
                # Check every minute if we should stop
                for _ in range(int(wait_time / 60)):
                    if not self.is_running:
                        break
                    time.sleep(60)
                
        except KeyboardInterrupt:
            print("\nDCA Bot stopped by user")
            self.stop_bot()
    
    def stop_bot(self):
        """Stop the DCA bot"""
        self.is_running = False
        print("DCA Bot stopped")
    
    def get_bot_status(self) -> Dict[str, Any]:
        """Get bot status and statistics"""
        symbol = self.config['symbol']
        symbol_purchases = [p for p in self.purchase_history if p['symbol'] == symbol]
        
        total_invested = sum(p['amount_usdt'] for p in symbol_purchases)
        total_quantity = sum(p['quantity'] for p in symbol_purchases)
        avg_price = total_invested / total_quantity if total_quantity > 0 else 0
        
        current_price = self.get_current_price(symbol)
        current_value = total_quantity * current_price
        unrealized_pnl = current_value - total_invested
        pnl_percentage = (unrealized_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'symbol': symbol,
            'is_running': self.is_running,
            'total_purchases': len(symbol_purchases),
            'max_purchases': self.config['max_purchases'],
            'total_invested': total_invested,
            'total_quantity': total_quantity,
            'average_price': avg_price,
            'current_price': current_price,
            'current_value': current_value,
            'unrealized_pnl': unrealized_pnl,
            'pnl_percentage': pnl_percentage,
            'last_purchase': symbol_purchases[-1] if symbol_purchases else None,
            'next_purchase_time': self._get_next_purchase_time(symbol)
        }
    
    def _get_next_purchase_time(self, symbol: str) -> Optional[str]:
        """Get next purchase time"""
        if symbol not in self.last_purchase_time:
            return datetime.now().isoformat()
        
        next_time = self.last_purchase_time[symbol] + timedelta(hours=self.config['interval_hours'])
        return next_time.isoformat()
    
    def display_status(self):
        """Display bot status"""
        status = self.get_bot_status()
        
        print("\nDCA BOT STATUS")
        print("=" * 50)
        print(f"Symbol: {status['symbol']}")
        print(f"Running: {'Yes' if status['is_running'] else 'No'}")
        print(f"Purchases: {status['total_purchases']}/{status['max_purchases']}")
        print(f"Total Invested: {format_price(status['total_invested'])}")
        print(f"Total Quantity: {status['total_quantity']:.6f}")
        print(f"Average Price: {format_price(status['average_price'])}")
        print(f"Current Price: {format_price(status['current_price'])}")
        print(f"Current Value: {format_price(status['current_value'])}")
        print(f"Unrealized P&L: {format_price(status['unrealized_pnl'])} ({status['pnl_percentage']:+.2f}%)")
        
        if status['last_purchase']:
            print(f"Last Purchase: {status['last_purchase']['timestamp']}")
        
        if status['next_purchase_time']:
            print(f"Next Purchase: {status['next_purchase_time']}")
    
    def export_history(self, filename: Optional[str] = None):
        """Export purchase history"""
        if filename is None:
            filename = f"dca_bot_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'config': self.config,
            'purchase_history': self.purchase_history,
            'export_time': datetime.now().isoformat()
        }
        
        save_data_to_file(data, filename)
        print(f"DCA bot history exported to {filename}")


def main():
    """Main function for DCA bot demo"""
    print("ASTER SDK - DCA TRADING BOT")
    print("=" * 40)
    
    # You would need to provide actual API credentials
    api_key = "your_api_key_here"
    secret_key = "your_secret_key_here"
    
    if api_key == "your_api_key_here":
        print("Please set your actual API credentials to use the DCA bot")
        print("You can edit the main() function with your credentials")
        return
    
    # DCA Bot Configuration
    config = {
        'symbol': 'BTCUSDT',
        'amount': 100.0,  # USDT amount per purchase
        'interval_hours': 24,  # Hours between purchases
        'max_purchases': 10  # Maximum number of purchases
    }
    
    try:
        # Initialize DCA bot
        bot = DCABot(api_key, secret_key, config)
        
        while True:
            print("\nDCA Bot Options:")
            print("1. Start bot")
            print("2. Stop bot")
            print("3. View status")
            print("4. Run single cycle")
            print("5. Export history")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                # Start bot
                bot.start_bot()
                
            elif choice == "2":
                # Stop bot
                bot.stop_bot()
                
            elif choice == "3":
                # View status
                bot.display_status()
                
            elif choice == "4":
                # Run single cycle
                bot.run_dca_cycle()
                
            elif choice == "5":
                # Export history
                bot.export_history()
                
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in DCA bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
