"""
Aster SDK - Advanced Trading Example
"""

import json
import time
from typing import Optional

from aster_sdk import Info, Exchange
from aster_sdk.utils.constants import MAINNET_API_URL
from aster_sdk.utils.types import Cloid
from eth_account import Account


class AsterTrader:
    """Example trading class for Aster DEX"""
    
    def __init__(self, private_key: str, base_url: Optional[str] = None):
        """
        Initialize trader
        
        Args:
            private_key: Private key for wallet
            base_url: Base URL for API (defaults to mainnet)
        """
        self.wallet = Account.from_key(private_key)
        self.exchange = Exchange(self.wallet, base_url or MAINNET_API_URL)
        self.info = Info(base_url or MAINNET_API_URL, skip_ws=True)
        
        print(f"Trader initialized with address: {self.wallet.address}")
    
    def get_account_info(self) -> dict:
        """Get account information"""
        return self.info.user_state(self.wallet.address)
    
    def get_open_orders(self) -> list:
        """Get open orders"""
        return self.info.open_orders(self.wallet.address)
    
    def get_positions(self) -> list:
        """Get current positions"""
        account_info = self.get_account_info()
        return account_info.get("assetPositions", [])
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        client_order_id: Optional[str] = None
    ) -> dict:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            side: "buy" or "sell"
            size: Order size
            price: Limit price
            client_order_id: Optional client order ID
            
        Returns:
            Order response
        """
        is_buy = side.lower() == "buy"
        cloid = Cloid(client_order_id) if client_order_id else None
        
        order_response = self.exchange.order(
            name=symbol,
            is_buy=is_buy,
            sz=size,
            limit_px=price,
            order_type={"limit": {"tif": "Gtc"}},
            reduce_only=False,
            cloid=cloid
        )
        
        print(f"Placed {side} order for {size} {symbol} at {price}")
        return order_response
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        slippage: float = 0.05
    ) -> dict:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            size: Order size
            slippage: Slippage tolerance (default 5%)
            
        Returns:
            Order response
        """
        is_buy = side.lower() == "buy"
        
        order_response = self.exchange.market_open(
            name=symbol,
            is_buy=is_buy,
            sz=size,
            slippage=slippage
        )
        
        print(f"Placed market {side} order for {size} {symbol}")
        return order_response
    
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """
        Cancel an order by order ID
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancel response
        """
        cancel_response = self.exchange.cancel(symbol, order_id)
        print(f"Cancelled order {order_id} for {symbol}")
        return cancel_response
    
    def cancel_order_by_cloid(self, symbol: str, client_order_id: str) -> dict:
        """
        Cancel an order by client order ID
        
        Args:
            symbol: Trading symbol
            client_order_id: Client order ID to cancel
            
        Returns:
            Cancel response
        """
        cloid = Cloid(client_order_id)
        cancel_response = self.exchange.cancel_by_cloid(symbol, cloid)
        print(f"Cancelled order with client ID {client_order_id} for {symbol}")
        return cancel_response
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> dict:
        """
        Cancel all orders for a symbol or all symbols
        
        Args:
            symbol: Optional symbol to cancel orders for
            
        Returns:
            Cancel response
        """
        open_orders = self.get_open_orders()
        
        if symbol:
            # Cancel orders for specific symbol
            orders_to_cancel = [order for order in open_orders if order["coin"] == symbol]
        else:
            # Cancel all orders
            orders_to_cancel = open_orders
        
        if not orders_to_cancel:
            print("No orders to cancel")
            return {}
        
        cancel_requests = [
            {"coin": order["coin"], "oid": order["oid"]}
            for order in orders_to_cancel
        ]
        
        cancel_response = self.exchange.bulk_cancel(cancel_requests)
        print(f"Cancelled {len(cancel_requests)} orders")
        return cancel_response
    
    def close_position(self, symbol: str, slippage: float = 0.05) -> dict:
        """
        Close a position for a symbol
        
        Args:
            symbol: Trading symbol
            slippage: Slippage tolerance
            
        Returns:
            Close position response
        """
        close_response = self.exchange.market_close(symbol, slippage=slippage)
        print(f"Closed position for {symbol}")
        return close_response
    
    def update_leverage(self, symbol: str, leverage: int, is_cross: bool = True) -> dict:
        """
        Update leverage for a position
        
        Args:
            symbol: Trading symbol
            leverage: New leverage value
            is_cross: Whether to use cross margin
            
        Returns:
            Update leverage response
        """
        leverage_response = self.exchange.update_leverage(symbol, leverage, is_cross)
        print(f"Updated leverage for {symbol} to {leverage}x")
        return leverage_response
    
    def get_portfolio_summary(self) -> dict:
        """Get portfolio summary"""
        account_info = self.get_account_info()
        
        summary = {
            "account_value": float(account_info.get("marginSummary", {}).get("accountValue", 0)),
            "total_margin_used": float(account_info.get("marginSummary", {}).get("totalMarginUsed", 0)),
            "withdrawable": float(account_info.get("withdrawable", 0)),
            "positions": []
        }
        
        for position in account_info.get("assetPositions", []):
            pos = position["position"]
            summary["positions"].append({
                "coin": pos["coin"],
                "size": float(pos["szi"]),
                "entry_price": float(pos.get("entryPx", 0)) if pos.get("entryPx") else None,
                "unrealized_pnl": float(pos["unrealizedPnl"]),
                "position_value": float(pos["positionValue"]),
                "margin_used": float(pos["marginUsed"])
            })
        
        return summary
    
    def print_portfolio(self):
        """Print portfolio summary"""
        summary = self.get_portfolio_summary()
        
        print("\n=== Portfolio Summary ===")
        print(f"Account Value: ${summary['account_value']:,.2f}")
        print(f"Total Margin Used: ${summary['total_margin_used']:,.2f}")
        print(f"Withdrawable: ${summary['withdrawable']:,.2f}")
        
        if summary["positions"]:
            print("\nPositions:")
            for pos in summary["positions"]:
                print(f"  {pos['coin']}: {pos['size']:,.4f} @ ${pos['entry_price'] or 'N/A'}")
                print(f"    PnL: ${pos['unrealized_pnl']:,.2f} | Value: ${pos['position_value']:,.2f}")
        else:
            print("\nNo open positions")


def main():
    """Main trading example"""
    print("Aster SDK - Advanced Trading Example")
    print("=" * 50)
    
    # Note: This is a demonstration. In practice, you would load a real wallet
    print("WARNING: This example requires a real wallet with funds!")
    print("For demonstration purposes, we'll show the structure")
    
    # Example usage (commented out for safety)
    # private_key = "your_private_key_here"
    # trader = AsterTrader(private_key)
    
    # # Get portfolio information
    # trader.print_portfolio()
    
    # # Place a limit order
    # order_response = trader.place_limit_order(
    #     symbol="BTC",
    #     side="buy",
    #     size=0.001,
    #     price=45000.0,
    #     client_order_id="my_order_1"
    # )
    
    # # Get open orders
    # open_orders = trader.get_open_orders()
    # print(f"Open orders: {len(open_orders)}")
    
    # # Cancel order by client ID
    # trader.cancel_order_by_cloid("BTC", "my_order_1")
    
    print("Trading example structure shown (requires real wallet)")


if __name__ == "__main__":
    main()
