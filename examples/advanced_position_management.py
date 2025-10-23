"""
Aster SDK - Advanced Position Management System
Professional position tracking with P&L calculation and risk management
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_auth import AsterAuthenticatedClient
from aster_example_utils import format_price, save_data_to_file


@dataclass
class Position:
    """Position representation"""
    symbol: str
    size: float  # Position size (positive for long, negative for short)
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin: float
    leverage: float
    liquidation_price: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary"""
        return {
            'symbol': self.symbol,
            'size': self.size,
            'entry_price': self.entry_price,
            'mark_price': self.mark_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'margin': self.margin,
            'leverage': self.leverage,
            'liquidation_price': self.liquidation_price,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PositionMetrics:
    """Position metrics and statistics"""
    total_unrealized_pnl: float
    total_realized_pnl: float
    total_margin: float
    total_exposure: float
    portfolio_value: float
    margin_ratio: float
    risk_score: float
    largest_position: Optional[Position]
    most_profitable: Optional[Position]
    most_losing: Optional[Position]


class PositionManager:
    """Advanced position management system"""
    
    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize position manager
        
        Args:
            api_key: Aster API key
            secret_key: Aster secret key
        """
        self.client = AsterAuthenticatedClient(api_key, secret_key)
        self.positions: Dict[str, Position] = {}
        self.position_history: List[Position] = []
        self.pnl_history: List[Dict[str, Any]] = []
    
    def fetch_positions(self) -> List[Position]:
        """
        Fetch current positions from API
        
        Returns:
            List of current positions
        """
        try:
            response = self.client.get_positions()
            
            if response.get('status') == 'ok':
                positions_data = response.get('data', [])
                positions = []
                
                for pos_data in positions_data:
                    position = Position(
                        symbol=pos_data.get('symbol', ''),
                        size=float(pos_data.get('positionAmt', 0)),
                        entry_price=float(pos_data.get('entryPrice', 0)),
                        mark_price=float(pos_data.get('markPrice', 0)),
                        unrealized_pnl=float(pos_data.get('unrealizedPnl', 0)),
                        realized_pnl=float(pos_data.get('realizedPnl', 0)),
                        margin=float(pos_data.get('isolatedMargin', 0)),
                        leverage=float(pos_data.get('leverage', 1)),
                        liquidation_price=float(pos_data.get('liquidationPrice', 0)),
                        timestamp=datetime.now()
                    )
                    
                    # Only include positions with non-zero size
                    if position.size != 0:
                        positions.append(position)
                        self.positions[position.symbol] = position
                
                return positions
            else:
                print(f"Error fetching positions: {response}")
                return []
                
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def calculate_position_metrics(self) -> PositionMetrics:
        """
        Calculate position metrics and statistics
        
        Returns:
            Position metrics
        """
        if not self.positions:
            return PositionMetrics(
                total_unrealized_pnl=0.0,
                total_realized_pnl=0.0,
                total_margin=0.0,
                total_exposure=0.0,
                portfolio_value=0.0,
                margin_ratio=0.0,
                risk_score=0.0,
                largest_position=None,
                most_profitable=None,
                most_losing=None
            )
        
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        total_margin = sum(pos.margin for pos in self.positions.values())
        total_exposure = sum(abs(pos.size * pos.mark_price) for pos in self.positions.values())
        
        # Calculate portfolio value (simplified)
        portfolio_value = total_margin + total_unrealized_pnl
        
        # Calculate margin ratio
        margin_ratio = (total_margin / total_exposure * 100) if total_exposure > 0 else 0
        
        # Calculate risk score (simplified)
        risk_score = min(100, (total_exposure / portfolio_value * 100)) if portfolio_value > 0 else 0
        
        # Find extreme positions
        largest_position = max(self.positions.values(), key=lambda p: abs(p.size * p.mark_price)) if self.positions else None
        most_profitable = max(self.positions.values(), key=lambda p: p.unrealized_pnl) if self.positions else None
        most_losing = min(self.positions.values(), key=lambda p: p.unrealized_pnl) if self.positions else None
        
        return PositionMetrics(
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=total_realized_pnl,
            total_margin=total_margin,
            total_exposure=total_exposure,
            portfolio_value=portfolio_value,
            margin_ratio=margin_ratio,
            risk_score=risk_score,
            largest_position=largest_position,
            most_profitable=most_profitable,
            most_losing=most_losing
        )
    
    def display_positions(self):
        """Display current positions"""
        print("\nCURRENT POSITIONS")
        print("=" * 100)
        
        if not self.positions:
            print("No open positions")
            return
        
        print(f"{'Symbol':<12} {'Size':<15} {'Entry':<12} {'Mark':<12} {'Unrealized P&L':<15} {'Margin':<12} {'Leverage':<10}")
        print("-" * 100)
        
        for position in self.positions.values():
            pnl_str = f"{position.unrealized_pnl:+.2f}"
            if position.unrealized_pnl > 0:
                pnl_str = f"+{position.unrealized_pnl:.2f}"
            elif position.unrealized_pnl < 0:
                pnl_str = f"{position.unrealized_pnl:.2f}"
            else:
                pnl_str = "0.00"
            
            print(f"{position.symbol:<12} {position.size:<15.6f} {format_price(position.entry_price):<12} "
                  f"{format_price(position.mark_price):<12} {pnl_str:<15} {format_price(position.margin):<12} "
                  f"{position.leverage:<10.1f}x")
    
    def display_position_metrics(self):
        """Display position metrics and statistics"""
        metrics = self.calculate_position_metrics()
        
        print("\nPOSITION METRICS")
        print("=" * 50)
        print(f"Total Unrealized P&L: {format_price(metrics.total_unrealized_pnl)}")
        print(f"Total Realized P&L: {format_price(metrics.total_realized_pnl)}")
        print(f"Total Margin: {format_price(metrics.total_margin)}")
        print(f"Total Exposure: {format_price(metrics.total_exposure)}")
        print(f"Portfolio Value: {format_price(metrics.portfolio_value)}")
        print(f"Margin Ratio: {metrics.margin_ratio:.2f}%")
        print(f"Risk Score: {metrics.risk_score:.2f}%")
        
        if metrics.largest_position:
            print(f"\nLargest Position: {metrics.largest_position.symbol} "
                  f"({format_price(abs(metrics.largest_position.size * metrics.largest_position.mark_price))})")
        
        if metrics.most_profitable:
            print(f"Most Profitable: {metrics.most_profitable.symbol} "
                  f"({format_price(metrics.most_profitable.unrealized_pnl)})")
        
        if metrics.most_losing:
            print(f"Most Losing: {metrics.most_losing.symbol} "
                  f"({format_price(metrics.most_losing.unrealized_pnl)})")
    
    def analyze_position_risk(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze risk for a specific position
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Risk analysis
        """
        if symbol not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[symbol]
        
        # Calculate risk metrics
        exposure = abs(position.size * position.mark_price)
        margin_ratio = (position.margin / exposure * 100) if exposure > 0 else 0
        
        # Calculate distance to liquidation
        if position.liquidation_price > 0:
            if position.size > 0:  # Long position
                liquidation_distance = ((position.mark_price - position.liquidation_price) / position.mark_price * 100)
            else:  # Short position
                liquidation_distance = ((position.liquidation_price - position.mark_price) / position.mark_price * 100)
        else:
            liquidation_distance = 0
        
        # Risk assessment
        risk_level = "LOW"
        if margin_ratio < 20 or liquidation_distance < 10:
            risk_level = "HIGH"
        elif margin_ratio < 40 or liquidation_distance < 20:
            risk_level = "MEDIUM"
        
        return {
            'symbol': symbol,
            'exposure': exposure,
            'margin_ratio': margin_ratio,
            'liquidation_distance': liquidation_distance,
            'risk_level': risk_level,
            'recommendation': self._get_risk_recommendation(risk_level, margin_ratio, liquidation_distance)
        }
    
    def _get_risk_recommendation(self, risk_level: str, margin_ratio: float, liquidation_distance: float) -> str:
        """Get risk management recommendation"""
        if risk_level == "HIGH":
            if margin_ratio < 20:
                return "Consider reducing position size or adding margin"
            elif liquidation_distance < 10:
                return "URGENT: Position at high liquidation risk"
            else:
                return "Monitor position closely"
        elif risk_level == "MEDIUM":
            return "Consider risk management strategies"
        else:
            return "Position risk is acceptable"
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive portfolio summary
        
        Returns:
            Portfolio summary
        """
        metrics = self.calculate_position_metrics()
        
        # Get account info
        try:
            account_info = self.client.get_account_info()
            account_data = account_info.get('data', {}) if account_info.get('status') == 'ok' else {}
        except:
            account_data = {}
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_positions': len(self.positions),
            'metrics': {
                'total_unrealized_pnl': metrics.total_unrealized_pnl,
                'total_realized_pnl': metrics.total_realized_pnl,
                'total_margin': metrics.total_margin,
                'total_exposure': metrics.total_exposure,
                'portfolio_value': metrics.portfolio_value,
                'margin_ratio': metrics.margin_ratio,
                'risk_score': metrics.risk_score
            },
            'positions': [pos.to_dict() for pos in self.positions.values()],
            'account_info': account_data
        }
        
        return summary
    
    def export_positions(self, filename: Optional[str] = None):
        """Export positions to JSON"""
        if filename is None:
            filename = f"aster_positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = self.get_portfolio_summary()
        save_data_to_file(summary, filename)
        print(f"Positions exported to {filename}")
    
    def monitor_positions(self, interval: int = 30):
        """
        Monitor positions in real-time
        
        Args:
            interval: Monitoring interval in seconds
        """
        print(f"Starting position monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("ASTER POSITION MONITOR")
                print("=" * 50)
                print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Fetch and display positions
                self.fetch_positions()
                self.display_positions()
                self.display_position_metrics()
                
                print(f"\nNext update in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nPosition monitoring stopped")


def main():
    """Main function for position management demo"""
    print("ASTER SDK - ADVANCED POSITION MANAGEMENT")
    print("=" * 50)
    
    # You would need to provide actual API credentials
    api_key = "your_api_key_here"
    secret_key = "your_secret_key_here"
    
    if api_key == "your_api_key_here":
        print("Please set your actual API credentials to use position management")
        print("You can edit the main() function with your credentials")
        return
    
    try:
        # Initialize position manager
        position_manager = PositionManager(api_key, secret_key)
        
        while True:
            print("\nPosition Management Options:")
            print("1. View current positions")
            print("2. View position metrics")
            print("3. Analyze position risk")
            print("4. Get portfolio summary")
            print("5. Export positions")
            print("6. Monitor positions (real-time)")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                # View positions
                position_manager.fetch_positions()
                position_manager.display_positions()
                
            elif choice == "2":
                # View metrics
                position_manager.fetch_positions()
                position_manager.display_position_metrics()
                
            elif choice == "3":
                # Analyze risk
                symbol = input("Enter symbol to analyze: ").strip().upper()
                position_manager.fetch_positions()
                risk_analysis = position_manager.analyze_position_risk(symbol)
                
                if 'error' in risk_analysis:
                    print(f"Error: {risk_analysis['error']}")
                else:
                    print(f"\nRisk Analysis for {symbol}:")
                    print(f"Exposure: {format_price(risk_analysis['exposure'])}")
                    print(f"Margin Ratio: {risk_analysis['margin_ratio']:.2f}%")
                    print(f"Liquidation Distance: {risk_analysis['liquidation_distance']:.2f}%")
                    print(f"Risk Level: {risk_analysis['risk_level']}")
                    print(f"Recommendation: {risk_analysis['recommendation']}")
                    
            elif choice == "4":
                # Portfolio summary
                position_manager.fetch_positions()
                summary = position_manager.get_portfolio_summary()
                print(f"\nPortfolio Summary:")
                print(f"Total Positions: {summary['total_positions']}")
                print(f"Portfolio Value: {format_price(summary['metrics']['portfolio_value'])}")
                print(f"Total P&L: {format_price(summary['metrics']['total_unrealized_pnl'])}")
                print(f"Risk Score: {summary['metrics']['risk_score']:.2f}%")
                
            elif choice == "5":
                # Export positions
                position_manager.fetch_positions()
                position_manager.export_positions()
                
            elif choice == "6":
                # Monitor positions
                interval = input("Enter monitoring interval in seconds (default 30): ").strip()
                interval = int(interval) if interval.isdigit() else 30
                position_manager.monitor_positions(interval)
                
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in position management: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
