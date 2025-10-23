"""
Aster SDK - Advanced Order Management System
Professional order management with full lifecycle tracking
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_auth import AsterAuthenticatedClient
from aster_example_utils import format_price, save_data_to_file


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(Enum):
    """Order status enumeration"""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimeInForce(Enum):
    """Time in force enumeration"""
    GTC = "GTC"  # Good Till Canceled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class Order:
    """Order representation"""
    
    def __init__(self, symbol: str, side: OrderSide, order_type: OrderType, 
                 quantity: float, price: Optional[float] = None, 
                 time_in_force: TimeInForce = TimeInForce.GTC):
        """
        Initialize order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (for LIMIT orders)
            time_in_force: Time in force
        """
        self.symbol = symbol
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.time_in_force = time_in_force
        self.order_id = None
        self.status = OrderStatus.NEW
        self.filled_quantity = 0.0
        self.remaining_quantity = quantity
        self.avg_price = 0.0
        self.created_time = datetime.now()
        self.updated_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'symbol': self.symbol,
            'side': self.side.value,
            'type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'timeInForce': self.time_in_force.value,
            'orderId': self.order_id,
            'status': self.status.value,
            'filledQuantity': self.filled_quantity,
            'remainingQuantity': self.remaining_quantity,
            'avgPrice': self.avg_price,
            'createdTime': self.created_time.isoformat(),
            'updatedTime': self.updated_time.isoformat()
        }
    
    def update_from_api(self, api_order: Dict[str, Any]):
        """Update order from API response"""
        self.order_id = api_order.get('orderId')
        self.status = OrderStatus(api_order.get('status', 'NEW'))
        self.filled_quantity = float(api_order.get('executedQty', 0))
        self.remaining_quantity = float(api_order.get('origQty', 0)) - self.filled_quantity
        self.avg_price = float(api_order.get('avgPrice', 0))
        self.updated_time = datetime.now()


class OrderManager:
    """Advanced order management system"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize order manager
        
        Args:
            api_key: Aster API key
            secret_key: Aster secret key
        """
        self.client = AsterAuthenticatedClient(api_key, secret_key)
        self.orders: Dict[int, Order] = {}
        self.order_history: List[Order] = []
        self.active_orders: Dict[int, Order] = {}
    
    def place_order(self, order: Order) -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            order: Order to place
            
        Returns:
            API response
        """
        try:
            print(f"Placing {order.side.value} order: {order.quantity} {order.symbol} @ {order.price or 'MARKET'}")
            
            # Prepare order parameters
            params = {
                'symbol': order.symbol,
                'side': order.side.value,
                'type': order.order_type.value,
                'quantity': order.quantity,
                'timeInForce': order.time_in_force.value
            }
            
            if order.order_type == OrderType.LIMIT and order.price:
                params['price'] = order.price
            
            # Place order via API
            response = self.client.place_order(
                symbol=order.symbol,
                side=order.side.value,
                order_type=order.order_type.value,
                quantity=order.quantity,
                price=order.price,
                time_in_force=order.time_in_force.value
            )
            
            if response.get('status') == 'ok':
                # Extract order ID from response
                order_data = response.get('response', {}).get('data', {})
                if 'statuses' in order_data and order_data['statuses']:
                    status_data = order_data['statuses'][0]
                    if 'resting' in status_data:
                        order.order_id = status_data['resting']['oid']
                        order.status = OrderStatus.NEW
                        self.orders[order.order_id] = order
                        self.active_orders[order.order_id] = order
                        print(f"Order placed successfully! Order ID: {order.order_id}")
                    else:
                        print(f"Order filled immediately: {status_data}")
                else:
                    print(f"Order response: {response}")
            else:
                print(f"Order failed: {response}")
            
            return response
            
        except Exception as e:
            print(f"Error placing order: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            API response
        """
        try:
            if order_id not in self.orders:
                return {'status': 'error', 'message': 'Order not found'}
            
            order = self.orders[order_id]
            print(f"Canceling order {order_id}: {order.symbol}")
            
            response = self.client.cancel_order(order.symbol, order_id)
            
            if response.get('status') == 'ok':
                order.status = OrderStatus.CANCELED
                order.updated_time = datetime.now()
                
                # Move from active to history
                if order_id in self.active_orders:
                    del self.active_orders[order_id]
                self.order_history.append(order)
                
                print(f"Order {order_id} canceled successfully")
            else:
                print(f"Cancel failed: {response}")
            
            return response
            
        except Exception as e:
            print(f"Error canceling order: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_order_status(self, order_id: int) -> Optional[Order]:
        """
        Get order status
        
        Args:
            order_id: Order ID
            
        Returns:
            Order object or None
        """
        try:
            if order_id not in self.orders:
                return None
            
            order = self.orders[order_id]
            response = self.client.get_order_status(order.symbol, order_id)
            
            if response.get('status') == 'ok':
                order_data = response.get('data', {})
                order.update_from_api(order_data)
                
                # Update active orders
                if order.status in [OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED]:
                    if order_id in self.active_orders:
                        del self.active_orders[order_id]
                    self.order_history.append(order)
            
            return order
            
        except Exception as e:
            print(f"Error getting order status: {e}")
            return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get open orders
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open orders
        """
        try:
            response = self.client.get_open_orders(symbol)
            
            if response.get('status') == 'ok':
                orders_data = response.get('data', [])
                open_orders = []
                
                for order_data in orders_data:
                    order = Order(
                        symbol=order_data['symbol'],
                        side=OrderSide(order_data['side']),
                        order_type=OrderType(order_data['type']),
                        quantity=float(order_data['origQty']),
                        price=float(order_data.get('price', 0)) if order_data.get('price') else None
                    )
                    order.update_from_api(order_data)
                    open_orders.append(order)
                
                return open_orders
            else:
                print(f"Error getting open orders: {response}")
                return []
                
        except Exception as e:
            print(f"Error getting open orders: {e}")
            return []
    
    def get_order_history(self, symbol: str, limit: int = 100) -> List[Order]:
        """
        Get order history
        
        Args:
            symbol: Trading symbol
            limit: Number of orders to retrieve
            
        Returns:
            List of historical orders
        """
        try:
            response = self.client.get_all_orders(symbol, limit)
            
            if response.get('status') == 'ok':
                orders_data = response.get('data', [])
                history_orders = []
                
                for order_data in orders_data:
                    order = Order(
                        symbol=order_data['symbol'],
                        side=OrderSide(order_data['side']),
                        order_type=OrderType(order_data['type']),
                        quantity=float(order_data['origQty']),
                        price=float(order_data.get('price', 0)) if order_data.get('price') else None
                    )
                    order.update_from_api(order_data)
                    history_orders.append(order)
                
                return history_orders
            else:
                print(f"Error getting order history: {response}")
                return []
                
        except Exception as e:
            print(f"Error getting order history: {e}")
            return []
    
    def display_active_orders(self):
        """Display active orders"""
        print("\nACTIVE ORDERS")
        print("=" * 80)
        
        if not self.active_orders:
            print("No active orders")
            return
        
        print(f"{'ID':<10} {'Symbol':<12} {'Side':<6} {'Type':<8} {'Quantity':<12} {'Price':<12} {'Status':<15}")
        print("-" * 80)
        
        for order_id, order in self.active_orders.items():
            price_str = format_price(order.price) if order.price else "MARKET"
            print(f"{order_id:<10} {order.symbol:<12} {order.side.value:<6} {order.order_type.value:<8} "
                  f"{order.quantity:<12} {price_str:<12} {order.status.value:<15}")
    
    def display_order_history(self, limit: int = 10):
        """Display order history"""
        print(f"\nORDER HISTORY (Last {limit})")
        print("=" * 80)
        
        recent_orders = self.order_history[-limit:] if self.order_history else []
        
        if not recent_orders:
            print("No order history")
            return
        
        print(f"{'ID':<10} {'Symbol':<12} {'Side':<6} {'Type':<8} {'Quantity':<12} {'Price':<12} {'Status':<15}")
        print("-" * 80)
        
        for order in recent_orders:
            price_str = format_price(order.price) if order.price else "MARKET"
            print(f"{order.order_id or 'N/A':<10} {order.symbol:<12} {order.side.value:<6} {order.order_type.value:<8} "
                  f"{order.quantity:<12} {price_str:<12} {order.status.value:<15}")
    
    def export_orders(self, filename: Optional[str] = None):
        """Export orders to JSON"""
        if filename is None:
            filename = f"aster_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        orders_data = {
            'timestamp': datetime.now().isoformat(),
            'active_orders': [order.to_dict() for order in self.active_orders.values()],
            'order_history': [order.to_dict() for order in self.order_history]
        }
        
        save_data_to_file(orders_data, filename)
        print(f"Orders exported to {filename}")


def main():
    """Main function for order management demo"""
    print("ASTER SDK - ADVANCED ORDER MANAGEMENT")
    print("=" * 50)
    
    # You would need to provide actual API credentials
    api_key = "your_api_key_here"
    secret_key = "your_secret_key_here"
    
    if api_key == "your_api_key_here":
        print("Please set your actual API credentials to use order management")
        print("You can edit the main() function with your credentials")
        return
    
    try:
        # Initialize order manager
        order_manager = OrderManager(api_key, secret_key)
        
        while True:
            print("\nOrder Management Options:")
            print("1. Place order")
            print("2. Cancel order")
            print("3. Get order status")
            print("4. View active orders")
            print("5. View order history")
            print("6. Export orders")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                # Place order
                symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
                side = input("Enter side (BUY/SELL): ").strip().upper()
                order_type = input("Enter type (MARKET/LIMIT): ").strip().upper()
                quantity = float(input("Enter quantity: "))
                
                price = None
                if order_type == "LIMIT":
                    price = float(input("Enter price: "))
                
                order = Order(
                    symbol=symbol,
                    side=OrderSide(side),
                    order_type=OrderType(order_type),
                    quantity=quantity,
                    price=price
                )
                
                order_manager.place_order(order)
                
            elif choice == "2":
                # Cancel order
                order_id = int(input("Enter order ID to cancel: "))
                order_manager.cancel_order(order_id)
                
            elif choice == "3":
                # Get order status
                order_id = int(input("Enter order ID: "))
                order = order_manager.get_order_status(order_id)
                if order:
                    print(f"Order status: {order.status.value}")
                    print(f"Filled: {order.filled_quantity}/{order.quantity}")
                else:
                    print("Order not found")
                    
            elif choice == "4":
                # View active orders
                order_manager.display_active_orders()
                
            elif choice == "5":
                # View order history
                symbol = input("Enter symbol (optional): ").strip().upper()
                if symbol:
                    history = order_manager.get_order_history(symbol)
                    print(f"Order history for {symbol}: {len(history)} orders")
                else:
                    order_manager.display_order_history()
                    
            elif choice == "6":
                # Export orders
                order_manager.export_orders()
                
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in order management: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
