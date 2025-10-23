# Aster SDK Examples

This directory contains comprehensive examples demonstrating how to use the Aster SDK for various trading and market analysis tasks.

## 📁 Example Files

### Basic Examples

- **`basic_usage.py`** - Basic SDK functionality demonstration
- **`basic_market_data.py`** - Market data analysis and exploration
- **`basic_market_monitor.py`** - Real-time market monitoring
- **`basic_portfolio_tracker.py`** - Portfolio tracking and management

### Utility Files

- **`aster_example_utils.py`** - Helper functions and utilities
- **`config.json.example`** - Configuration file template

## 🚀 Quick Start

### 1. Setup

```bash
# Navigate to the examples directory
cd examples

# Copy the configuration template
cp config.json.example config.json

# Edit config.json with your settings (optional for public endpoints)
```

### 2. Run Examples

```bash
# Basic usage example
python basic_usage.py

# Market data analysis
python basic_market_data.py

# Real-time market monitoring
python basic_market_monitor.py

# Portfolio tracking
python basic_portfolio_tracker.py
```

## 📊 Example Descriptions

### Basic Usage (`basic_usage.py`)

Demonstrates fundamental SDK operations:
- Connecting to Aster API
- Getting server time and exchange info
- Retrieving current prices
- Viewing 24hr statistics
- Accessing best bid/ask prices
- Getting funding rates

**Key Features:**
- Market summary display
- Major cryptocurrency prices
- Volume leaders
- Rate limit information

### Market Data Analysis (`basic_market_data.py`)

Advanced market data analysis:
- Top gainers and losers analysis
- Volume leaders identification
- Price range and volatility analysis
- Symbol search functionality
- Data export capabilities

**Key Features:**
- Comprehensive market analysis
- Custom symbol searches
- JSON data export
- Formatted output display

### Market Monitor (`basic_market_monitor.py`)

Real-time market monitoring:
- Live price updates
- Custom symbol monitoring
- Top movers tracking
- Price change alerts
- Configurable refresh intervals

**Key Features:**
- Real-time price updates
- Multiple monitoring modes
- Live change tracking
- Interactive interface

### Portfolio Tracker (`basic_portfolio_tracker.py`)

Portfolio management and tracking:
- Portfolio value calculation
- Performance tracking
- Holdings management
- 24hr performance analysis
- Report generation

**Key Features:**
- Portfolio value tracking
- Performance metrics
- Holdings management
- Export capabilities

## ⚙️ Configuration

### Configuration File (`config.json`)

```json
{
  "api_key": "your_api_key_here",
  "secret_key": "your_secret_key_here",
  "account_address": "your_account_address",
  "base_url": "https://fapi.asterdex.com",
  "testnet": false
}
```

**Note:** For public endpoints (market data), no API credentials are required. Credentials are only needed for private endpoints (trading, account info).

### Environment Variables

You can also set configuration via environment variables:

```bash
export ASTER_API_KEY="your_api_key"
export ASTER_SECRET_KEY="your_secret_key"
export ASTER_BASE_URL="https://fapi.asterdex.com"
```

## 🔧 Dependencies

The examples require the following packages:

```bash
pip install requests
```

## 📈 Available Market Data

The Aster API provides access to:

- **208+ trading pairs** (all USDT pairs)
- **Real-time prices** for all symbols
- **24hr statistics** (high, low, volume, change)
- **Best bid/ask prices** (order book data)
- **Funding rates** for perpetual contracts
- **Exchange information** and rate limits

## 🎯 Use Cases

### Market Analysis
- Track price movements and trends
- Identify top performers and losers
- Analyze trading volumes
- Monitor market volatility

### Portfolio Management
- Track portfolio value in real-time
- Monitor performance metrics
- Manage holdings
- Generate reports

### Trading Research
- Research market conditions
- Identify trading opportunities
- Monitor specific symbols
- Analyze market sentiment

### Data Collection
- Export market data for analysis
- Build custom datasets
- Historical data collection
- Market research

## 🚨 Rate Limits

Aster API rate limits:
- **2,400 requests per minute** (general)
- **1,200 orders per minute** (trading)
- **300 orders per second** (trading)

The examples include proper rate limiting and error handling.

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for production
- Keep your secret keys secure
- Test with small amounts first

## 📞 Support

For issues or questions:
1. Check the main SDK documentation
2. Review the example code
3. Test with the basic examples first
4. Ensure proper configuration

## 🎉 Getting Started

1. **Start with `basic_usage.py`** to understand the SDK
2. **Try `basic_market_data.py`** for market analysis
3. **Use `basic_market_monitor.py`** for real-time monitoring
4. **Explore `basic_portfolio_tracker.py`** for portfolio management

Each example is self-contained and includes comprehensive error handling and documentation.
