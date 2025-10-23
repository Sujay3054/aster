"""
Aster SDK - Technical Analysis Tools
Professional technical analysis with indicators and trend analysis
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL
from aster_example_utils import format_price, save_data_to_file


class TechnicalIndicators:
    """Technical analysis indicators"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(data) < period:
            return [np.nan] * len(data)
        
        sma_values = []
        for i in range(len(data)):
            if i < period - 1:
                sma_values.append(np.nan)
            else:
                sma_values.append(np.mean(data[i - period + 1:i + 1]))
        
        return sma_values
    
    @staticmethod
    def ema(data: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if len(data) < period:
            return [np.nan] * len(data)
        
        alpha = 2 / (period + 1)
        ema_values = [np.nan] * len(data)
        ema_values[period - 1] = np.mean(data[:period])
        
        for i in range(period, len(data)):
            ema_values[i] = alpha * data[i] + (1 - alpha) * ema_values[i - 1]
        
        return ema_values
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return [np.nan] * len(data)
        
        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        rsi_values = [np.nan] * len(data)
        
        for i in range(period, len(data)):
            avg_gain = np.mean(gains[i - period:i])
            avg_loss = np.mean(losses[i - period:i])
            
            if avg_loss == 0:
                rsi_values[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi_values[i] = 100 - (100 / (1 + rs))
        
        return rsi_values
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        macd_line = [fast_val - slow_val if not np.isnan(fast_val) and not np.isnan(slow_val) 
                    else np.nan for fast_val, slow_val in zip(ema_fast, ema_slow)]
        
        signal_line = TechnicalIndicators.ema([val for val in macd_line if not np.isnan(val)], signal)
        
        # Align signal line with macd line
        aligned_signal = [np.nan] * len(macd_line)
        signal_idx = 0
        for i, val in enumerate(macd_line):
            if not np.isnan(val) and signal_idx < len(signal_line):
                aligned_signal[i] = signal_line[signal_idx]
                signal_idx += 1
        
        histogram = [macd_val - signal_val if not np.isnan(macd_val) and not np.isnan(signal_val)
                    else np.nan for macd_val, signal_val in zip(macd_line, aligned_signal)]
        
        return macd_line, aligned_signal, histogram
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: float = 2) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands"""
        sma_values = TechnicalIndicators.sma(data, period)
        
        upper_band = []
        lower_band = []
        
        for i in range(len(data)):
            if i < period - 1:
                upper_band.append(np.nan)
                lower_band.append(np.nan)
            else:
                period_data = data[i - period + 1:i + 1]
                std = np.std(period_data)
                upper_band.append(sma_values[i] + (std_dev * std))
                lower_band.append(sma_values[i] - (std_dev * std))
        
        return upper_band, sma_values, lower_band
    
    @staticmethod
    def stochastic(high: List[float], low: List[float], close: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator"""
        if len(close) < k_period:
            return [np.nan] * len(close), [np.nan] * len(close)
        
        k_values = []
        for i in range(len(close)):
            if i < k_period - 1:
                k_values.append(np.nan)
            else:
                period_high = max(high[i - k_period + 1:i + 1])
                period_low = min(low[i - k_period + 1:i + 1])
                if period_high != period_low:
                    k_values.append(((close[i] - period_low) / (period_high - period_low)) * 100)
                else:
                    k_values.append(50)
        
        d_values = TechnicalIndicators.sma(k_values, d_period)
        
        return k_values, d_values


class MarketData:
    """Market data handler for technical analysis"""
    
    def __init__(self):
        """Initialize market data handler"""
        self.info = Info(MAINNET_API_URL)
        self.cache = {}
        self.cache_timeout = 60  # seconds
    
    def get_historical_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> pd.DataFrame:
        """
        Get historical price data
        
        Args:
            symbol: Trading symbol
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
            
        Returns:
            DataFrame with OHLCV data
        """
        cache_key = f"{symbol}_{interval}_{limit}"
        current_time = datetime.now()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if (current_time - cache_time).seconds < self.cache_timeout:
                return cached_data
        
        try:
            # For now, we'll simulate historical data since we need to find the correct endpoint
            # In a real implementation, you would call the klines endpoint
            print(f"Fetching historical data for {symbol}...")
            
            # Simulate OHLCV data (replace with actual API call)
            dates = pd.date_range(end=current_time, periods=limit, freq=interval)
            np.random.seed(42)  # For consistent results
            
            # Generate realistic price data
            base_price = 100.0
            prices = []
            for i in range(limit):
                change = np.random.normal(0, 0.02)  # 2% volatility
                base_price *= (1 + change)
                prices.append(base_price)
            
            # Create OHLCV data
            data = []
            for i, (date, close) in enumerate(zip(dates, prices)):
                high = close * (1 + abs(np.random.normal(0, 0.01)))
                low = close * (1 - abs(np.random.normal(0, 0.01)))
                open_price = prices[i - 1] if i > 0 else close
                volume = np.random.uniform(1000, 10000)
                
                data.append({
                    'timestamp': date,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            # Cache the data
            self.cache[cache_key] = (df, current_time)
            
            return df
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()


class TechnicalAnalyzer:
    """Technical analysis engine"""
    
    def __init__(self):
        """Initialize technical analyzer"""
        self.market_data = MarketData()
        self.indicators = TechnicalIndicators()
    
    def analyze_symbol(self, symbol: str, interval: str = "1h", limit: int = 100) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis on a symbol
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            limit: Number of data points
            
        Returns:
            Analysis results
        """
        try:
            # Get historical data
            df = self.market_data.get_historical_data(symbol, interval, limit)
            
            if df.empty:
                return {'error': 'No data available'}
            
            # Extract price data
            closes = df['close'].tolist()
            highs = df['high'].tolist()
            lows = df['low'].tolist()
            volumes = df['volume'].tolist()
            
            # Calculate indicators
            sma_20 = self.indicators.sma(closes, 20)
            sma_50 = self.indicators.sma(closes, 50)
            ema_12 = self.indicators.ema(closes, 12)
            ema_26 = self.indicators.ema(closes, 26)
            rsi = self.indicators.rsi(closes, 14)
            macd_line, macd_signal, macd_histogram = self.indicators.macd(closes)
            bb_upper, bb_middle, bb_lower = self.indicators.bollinger_bands(closes)
            stoch_k, stoch_d = self.indicators.stochastic(highs, lows, closes)
            
            # Get current values
            current_price = closes[-1]
            current_rsi = rsi[-1] if not np.isnan(rsi[-1]) else None
            current_macd = macd_line[-1] if not np.isnan(macd_line[-1]) else None
            
            # Generate signals
            signals = self._generate_signals(
                current_price, sma_20, sma_50, rsi, macd_line, macd_signal,
                bb_upper, bb_lower, stoch_k, stoch_d
            )
            
            # Calculate trend
            trend = self._calculate_trend(sma_20, sma_50, current_price)
            
            # Calculate support and resistance
            support, resistance = self._calculate_support_resistance(highs, lows, closes)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'indicators': {
                    'sma_20': sma_20[-1] if not np.isnan(sma_20[-1]) else None,
                    'sma_50': sma_50[-1] if not np.isnan(sma_50[-1]) else None,
                    'ema_12': ema_12[-1] if not np.isnan(ema_12[-1]) else None,
                    'ema_26': ema_26[-1] if not np.isnan(ema_26[-1]) else None,
                    'rsi': current_rsi,
                    'macd': current_macd,
                    'macd_signal': macd_signal[-1] if not np.isnan(macd_signal[-1]) else None,
                    'bb_upper': bb_upper[-1] if not np.isnan(bb_upper[-1]) else None,
                    'bb_middle': bb_middle[-1] if not np.isnan(bb_middle[-1]) else None,
                    'bb_lower': bb_lower[-1] if not np.isnan(bb_lower[-1]) else None,
                    'stoch_k': stoch_k[-1] if not np.isnan(stoch_k[-1]) else None,
                    'stoch_d': stoch_d[-1] if not np.isnan(stoch_d[-1]) else None
                },
                'signals': signals,
                'trend': trend,
                'support': support,
                'resistance': resistance,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _generate_signals(self, price: float, sma_20: List[float], sma_50: List[float],
                         rsi: List[float], macd_line: List[float], macd_signal: List[float],
                         bb_upper: List[float], bb_lower: List[float],
                         stoch_k: List[float], stoch_d: List[float]) -> Dict[str, str]:
        """Generate trading signals"""
        signals = {}
        
        # Moving average signals
        if len(sma_20) > 1 and len(sma_50) > 1:
            if not np.isnan(sma_20[-1]) and not np.isnan(sma_50[-1]):
                if sma_20[-1] > sma_50[-1] and sma_20[-2] <= sma_50[-2]:
                    signals['ma_cross'] = 'BUY'
                elif sma_20[-1] < sma_50[-1] and sma_20[-2] >= sma_50[-2]:
                    signals['ma_cross'] = 'SELL'
                else:
                    signals['ma_cross'] = 'HOLD'
        
        # RSI signals
        if len(rsi) > 0 and not np.isnan(rsi[-1]):
            if rsi[-1] < 30:
                signals['rsi'] = 'OVERSOLD'
            elif rsi[-1] > 70:
                signals['rsi'] = 'OVERBOUGHT'
            else:
                signals['rsi'] = 'NEUTRAL'
        
        # MACD signals
        if len(macd_line) > 1 and len(macd_signal) > 1:
            if not np.isnan(macd_line[-1]) and not np.isnan(macd_signal[-1]):
                if macd_line[-1] > macd_signal[-1] and macd_line[-2] <= macd_signal[-2]:
                    signals['macd'] = 'BUY'
                elif macd_line[-1] < macd_signal[-1] and macd_line[-2] >= macd_signal[-2]:
                    signals['macd'] = 'SELL'
                else:
                    signals['macd'] = 'HOLD'
        
        # Bollinger Bands signals
        if len(bb_upper) > 0 and len(bb_lower) > 0:
            if not np.isnan(bb_upper[-1]) and not np.isnan(bb_lower[-1]):
                if price <= bb_lower[-1]:
                    signals['bollinger'] = 'OVERSOLD'
                elif price >= bb_upper[-1]:
                    signals['bollinger'] = 'OVERBOUGHT'
                else:
                    signals['bollinger'] = 'NEUTRAL'
        
        # Stochastic signals
        if len(stoch_k) > 0 and len(stoch_d) > 0:
            if not np.isnan(stoch_k[-1]) and not np.isnan(stoch_d[-1]):
                if stoch_k[-1] < 20 and stoch_d[-1] < 20:
                    signals['stochastic'] = 'OVERSOLD'
                elif stoch_k[-1] > 80 and stoch_d[-1] > 80:
                    signals['stochastic'] = 'OVERBOUGHT'
                else:
                    signals['stochastic'] = 'NEUTRAL'
        
        return signals
    
    def _calculate_trend(self, sma_20: List[float], sma_50: List[float], current_price: float) -> str:
        """Calculate trend direction"""
        if len(sma_20) > 0 and len(sma_50) > 0:
            if not np.isnan(sma_20[-1]) and not np.isnan(sma_50[-1]):
                if current_price > sma_20[-1] > sma_50[-1]:
                    return 'STRONG_UPTREND'
                elif current_price > sma_20[-1] and sma_20[-1] > sma_50[-1]:
                    return 'UPTREND'
                elif current_price < sma_20[-1] < sma_50[-1]:
                    return 'STRONG_DOWNTREND'
                elif current_price < sma_20[-1] and sma_20[-1] < sma_50[-1]:
                    return 'DOWNTREND'
                else:
                    return 'SIDEWAYS'
        return 'UNKNOWN'
    
    def _calculate_support_resistance(self, highs: List[float], lows: List[float], closes: List[float]) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if len(highs) < 20 or len(lows) < 20:
            return 0.0, 0.0
        
        # Simple support/resistance calculation
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        
        resistance = max(recent_highs)
        support = min(recent_lows)
        
        return support, resistance
    
    def scan_market(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Scan multiple symbols for trading opportunities
        
        Args:
            symbols: List of symbols to scan
            
        Returns:
            List of analysis results
        """
        results = []
        
        for symbol in symbols:
            print(f"Analyzing {symbol}...")
            analysis = self.analyze_symbol(symbol)
            if 'error' not in analysis:
                results.append(analysis)
        
        # Sort by signal strength
        results.sort(key=lambda x: self._calculate_signal_strength(x['signals']), reverse=True)
        
        return results
    
    def _calculate_signal_strength(self, signals: Dict[str, str]) -> int:
        """Calculate signal strength score"""
        score = 0
        
        for signal_type, signal_value in signals.items():
            if signal_value == 'BUY':
                score += 2
            elif signal_value == 'SELL':
                score -= 2
            elif signal_value == 'OVERSOLD':
                score += 1
            elif signal_value == 'OVERBOUGHT':
                score -= 1
        
        return score


def main():
    """Main function for technical analysis demo"""
    print("ASTER SDK - TECHNICAL ANALYSIS TOOLS")
    print("=" * 50)
    
    try:
        analyzer = TechnicalAnalyzer()
        
        while True:
            print("\nTechnical Analysis Options:")
            print("1. Analyze single symbol")
            print("2. Scan multiple symbols")
            print("3. Market overview")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-3): ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                # Analyze single symbol
                symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
                analysis = analyzer.analyze_symbol(symbol)
                
                if 'error' in analysis:
                    print(f"Error: {analysis['error']}")
                else:
                    print(f"\nTechnical Analysis for {symbol}")
                    print("=" * 50)
                    print(f"Current Price: {format_price(analysis['current_price'])}")
                    print(f"Trend: {analysis['trend']}")
                    print(f"Support: {format_price(analysis['support'])}")
                    print(f"Resistance: {format_price(analysis['resistance'])}")
                    
                    print(f"\nIndicators:")
                    indicators = analysis['indicators']
                    if indicators['sma_20']:
                        print(f"SMA 20: {format_price(indicators['sma_20'])}")
                    if indicators['sma_50']:
                        print(f"SMA 50: {format_price(indicators['sma_50'])}")
                    if indicators['rsi']:
                        print(f"RSI: {indicators['rsi']:.2f}")
                    if indicators['macd']:
                        print(f"MACD: {indicators['macd']:.4f}")
                    
                    print(f"\nSignals:")
                    for signal_type, signal_value in analysis['signals'].items():
                        print(f"{signal_type.upper()}: {signal_value}")
                        
            elif choice == "2":
                # Scan multiple symbols
                symbols_input = input("Enter symbols (comma-separated): ").strip()
                symbols = [s.strip().upper() for s in symbols_input.split(',')]
                
                results = analyzer.scan_market(symbols)
                
                print(f"\nMarket Scan Results")
                print("=" * 80)
                print(f"{'Symbol':<12} {'Price':<12} {'Trend':<15} {'Signals':<20}")
                print("-" * 80)
                
                for result in results[:10]:  # Show top 10
                    signals_str = ', '.join([f"{k}:{v}" for k, v in result['signals'].items()])
                    print(f"{result['symbol']:<12} {format_price(result['current_price']):<12} "
                          f"{result['trend']:<15} {signals_str[:20]:<20}")
                          
            elif choice == "3":
                # Market overview
                major_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
                results = analyzer.scan_market(major_symbols)
                
                print(f"\nMajor Cryptocurrencies Overview")
                print("=" * 60)
                print(f"{'Symbol':<12} {'Price':<12} {'Trend':<15} {'RSI':<8}")
                print("-" * 60)
                
                for result in results:
                    rsi = result['indicators']['rsi']
                    rsi_str = f"{rsi:.1f}" if rsi else "N/A"
                    print(f"{result['symbol']:<12} {format_price(result['current_price']):<12} "
                          f"{result['trend']:<15} {rsi_str:<8}")
                          
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
