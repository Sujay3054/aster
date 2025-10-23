# Aster Python SDK

Professional Python SDK for Aster DEX trading platform with 208+ trading pairs support, real-time market data, advanced trading tools, and automated trading strategies.

## 🌟 Features

- **208+ Trading Pairs** - Complete support for all Aster DEX trading pairs
- **Real-time Market Data** - Live prices, 24hr statistics, order book data
- **Professional Trading Tools** - Order management, position tracking, risk analysis
- **Advanced Technical Analysis** - 10+ indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Market Scanner** - Opportunity detection, volume spikes, price breakouts
- **Trading Bots** - DCA (Dollar Cost Averaging) and automated strategies
- **Risk Management** - Position sizing, portfolio optimization
- **Complete Documentation** - Comprehensive guides and examples

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aster-python-sdk.git
cd aster-python-sdk

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from aster_sdk_fixed.info import Info
from aster_sdk.utils.constants import MAINNET_API_URL

# Initialize the SDK
info = Info(MAINNET_API_URL)

# Get current prices
prices = info.ticker_price()
print(f"BTC Price: ${prices[0]['price']}")

# Get 24hr statistics
stats = info.ticker_24hr()
print(f"Market data for {len(stats)} symbols")
```

## 📊 Market Data

```python
# Get major cryptocurrency prices
major_cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ASTERUSDT']
for symbol in major_cryptos:
    price_data = next((p for p in prices if p.get('symbol') == symbol), None)
    if price_data:
        print(f"{symbol}: ${price_data['price']}")
```

## 🛠️ Examples

### Basic Market Data
```bash
python examples/basic_usage.py
```

### Market Analysis
```bash
python examples/basic_market_data.py
```

### Technical Analysis
```bash
python examples/technical_analysis.py
```

### Market Scanner
```bash
python examples/market_scanner.py
```

### Portfolio Tracking
```bash
python examples/basic_portfolio_tracker.py
```

## 🔧 Advanced Features

### Order Management
```python
from examples.aster_auth import AsterAuthenticatedClient

# Initialize with API credentials
client = AsterAuthenticatedClient(api_key, secret_key)

# Place an order
result = client.place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity=0.001
)
```

### Position Tracking
```python
from examples.advanced_position_management import PositionManager

# Track positions and P&L
position_manager = PositionManager(api_key, secret_key)
positions = position_manager.fetch_positions()
position_manager.display_positions()
```

### Technical Analysis
```python
from examples.technical_analysis import TechnicalAnalyzer

# Analyze market trends
analyzer = TechnicalAnalyzer()
analysis = analyzer.analyze_symbol("BTCUSDT")
print(f"Trend: {analysis['trend']}")
print(f"RSI: {analysis['indicators']['rsi']}")
```

### Trading Bots
```python
from examples.trading_bots.dca_bot import DCABot

# DCA Bot configuration
config = {
    'symbol': 'BTCUSDT',
    'amount': 100.0,  # USDT per purchase
    'interval_hours': 24,  # Hours between purchases
    'max_purchases': 10
}

# Start DCA bot
bot = DCABot(api_key, secret_key, config)
bot.start_bot()
```

## 📈 Available Market Data

- **Real-time Prices** - All 208+ trading pairs
- **24hr Statistics** - High, low, volume, price change
- **Order Book Data** - Best bid/ask prices
- **Funding Rates** - Perpetual contract funding
- **Exchange Information** - Rate limits, trading rules

## 🔐 Authentication

For private endpoints (trading, account info), you'll need API credentials:

```python
# Set up authentication
api_key = "your_api_key"
secret_key = "your_secret_key"

# Use authenticated client
client = AsterAuthenticatedClient(api_key, secret_key)
```

## 📚 Documentation

- **[Complete SDK Guide](docs/ASTER_SDK_COMPLETE_GUIDE.md)** - Comprehensive SDK documentation
- **[Examples Guide](docs/ASTER_EXAMPLES_COMPLETE.md)** - All examples explained
- **[Professional Tools](docs/ASTER_PROFESSIONAL_TOOLS_COMPLETE.md)** - Advanced trading tools

## 🧪 Testing

```bash
# Test basic functionality
python test_working_sdk.py

# Test market data
python examples/basic_usage.py

# Test API discovery
python tools/quick_api_discovery.py
```

## 📊 API Endpoints

### Public Endpoints (No Auth Required)
- `/fapi/v1/ping` - Health check
- `/fapi/v1/time` - Server time
- `/fapi/v1/exchangeInfo` - Exchange information
- `/fapi/v1/ticker/24hr` - 24hr price statistics
- `/fapi/v1/ticker/price` - Current prices
- `/fapi/v1/ticker/bookTicker` - Best bid/ask prices
- `/fapi/v1/fundingRate` - Funding rates

### Private Endpoints (Auth Required)
- `/fapi/v1/account` - Account information
- `/fapi/v1/balance` - Account balance
- `/fapi/v1/positionRisk` - Position risk
- `/fapi/v1/order` - Order management
- `/fapi/v1/openOrders` - Open orders
- `/fapi/v1/allOrders` - All orders

## ⚡ Rate Limits

- **REQUEST_WEIGHT**: 2,400 requests per MINUTE
- **ORDERS**: 1,200 requests per MINUTE
- **ORDERS**: 300 requests per SECOND

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/aster-python-sdk/issues)
- **Documentation**: [Complete Guide](docs/ASTER_SDK_COMPLETE_GUIDE.md)
- **Examples**: [Examples Directory](examples/)

## 🎯 What Makes This SDK Special

- **Professional Grade** - Production-ready trading tools
- **Complete Feature Set** - Everything you need for trading
- **Real-time Data** - Live market data from 208+ pairs
- **Advanced Analytics** - Technical analysis and market scanning
- **Automation Ready** - Trading bots and automated strategies
- **Risk Management** - Professional risk assessment tools
- **Comprehensive Documentation** - Complete guides and examples

**Ready for professional trading and development!** 🚀
