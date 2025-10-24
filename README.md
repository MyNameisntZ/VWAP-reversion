# VWAP Reversion Trading Bot v1.0

A professional Python trading bot that implements a VWAP (Volume Weighted Average Price) Reversion strategy for intraday mean reversion trading. This bot connects to the Alpaca Paper Trading API and provides both command-line and GUI interfaces.

## 🎯 Strategy Overview

**VWAP Reversion Strategy** - Perfect for intraday mean reversion trading:

### Buy Conditions:
- Price < VWAP × 0.99 (price drops below VWAP threshold)
- Candle closes above VWAP again (reversion signal)
- Price within 5% of VWAP (safety filter)

### Sell Conditions:
- Price > VWAP × 1.01 (price exceeds VWAP threshold)
- OR RSI > 70 (overbought condition)

## ✨ Key Features

### 🚀 **Professional GUI Interface**
- Clean, modern design with blue accent colors
- Real-time market status display
- Account information dashboard
- Customizable trading parameters
- Symbol management with CSV import/export
- Profile management system
- Comprehensive logging

### 📊 **Advanced Trading Features**
- VWAP-based mean reversion strategy
- RSI confirmation for overbought conditions
- Bracket orders with stop-loss and take-profit
- Market hours detection
- Real-time data updates
- SQLite trade logging

### ⚙️ **Customizable Settings**
- Position size per trade
- Stop-loss and take-profit percentages
- VWAP buy/sell thresholds
- RSI overbought levels
- Data refresh intervals
- Multiple timeframe support

### 🛡️ **Safety Features**
- Paper trading only (no real money risk)
- Market hours detection
- Data quality validation
- Error handling and logging
- Profile-based settings management

## 🚀 Quick Start

### 1. **Download and Setup**
```bash
# Clone or download the repository
# Navigate to the vwap_reversion_bot folder
cd vwap_reversion_bot
```

### 2. **Install Dependencies**
```bash
# Install all required packages
python -m pip install alpaca-trade-api pandas numpy ta schedule python-dotenv requests Pillow pytz holidays
```

### 3. **Configure API Keys**
Create a `.env` file in the bot directory:
```env
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
BASE_URL=https://paper-api.alpaca.markets
```

### 4. **Run the Bot**
```bash
# Start the GUI (recommended)
start_gui.bat

# Or run from command line
python gui.py
```

## 📁 File Structure

```
vwap_reversion_bot/
├── gui.py                 # Main GUI application
├── vwap_bot.py           # Command-line bot
├── config.py             # Configuration and API keys
├── strategy.py           # VWAP Reversion strategy logic
├── indicators.py         # VWAP and RSI calculations
├── trader.py             # Alpaca API integration
├── database.py           # SQLite trade logging
├── market_hours.py       # Market hours detection
├── profile_manager.py    # Profile management
├── start_gui.bat         # Windows launcher
├── vwap-trader-logo.png  # Bot logo
├── sample_symbols.csv    # Sample ticker list
├── DEPENDENCIES.txt      # Installation requirements
└── README.md            # This file
```

## 🎮 Usage

### **GUI Mode (Recommended)**
1. Run `start_gui.bat` or `python gui.py`
2. Click "Connect to Alpaca" to establish connection
3. Configure your trading settings in the "Trading Settings" tab
4. Add symbols in the "Symbols" tab
5. Click "Start Bot" to begin trading
6. Monitor activity in the "Logs" tab

### **Command Line Mode**
```bash
# Run with default symbols
python vwap_bot.py

# Run with custom symbols
python vwap_bot.py --symbols AAPL NVDA TSLA
```

## ⚙️ Configuration

### **Trading Parameters**
- **Position Size**: $100 per trade (default)
- **Stop Loss**: 3% below entry price
- **Take Profit**: 8% above entry price
- **Timeframe**: 5-minute bars (optimal for VWAP)

### **Strategy Parameters**
- **VWAP Buy Threshold**: 0.99 (buy when price < VWAP × 0.99)
- **VWAP Sell Threshold**: 1.01 (sell when price > VWAP × 1.01)
- **RSI Overbought**: 70 (sell when RSI > 70)
- **RSI Period**: 14 (RSI calculation period)

### **Data Refresh**
- **Auto Refresh**: Enabled by default
- **Refresh Interval**: 5 minutes (configurable)
- **Market Hours**: Only trades during market hours

## 📊 Strategy Logic

### **Why VWAP Reversion?**
- **Institutional Benchmark**: VWAP is used by institutions as fair value
- **Mean Reversion**: Prices tend to revert to VWAP after overreactions
- **Intraday Focus**: Perfect for short-term trading opportunities
- **Volume Weighted**: More accurate than simple moving averages

### **Entry Logic**
1. Price drops below VWAP threshold (0.99)
2. Candle closes above VWAP (reversion signal)
3. Price not too far below VWAP (safety filter)
4. RSI not overbought (confirmation)

### **Exit Logic**
1. Price exceeds VWAP threshold (1.01) - profit taking
2. RSI becomes overbought (>70) - momentum reversal
3. Stop-loss triggered (3% below entry)
4. Take-profit reached (8% above entry)

## 🔧 Advanced Features

### **Profile Management**
- Save multiple trading configurations
- Quick switching between strategies
- Export/import settings
- Persistent storage

### **Symbol Management**
- Add/remove individual symbols
- CSV import/export for bulk operations
- Real-time symbol validation
- Custom symbol lists

### **Market Hours Detection**
- Automatic market status detection
- Pre-market and after-hours awareness
- Holiday calendar integration
- Timezone handling (Eastern Time)

### **Data Quality Validation**
- Minimum data requirements
- Volume validation
- Price data integrity checks
- Error handling for missing data

## 📈 Performance Monitoring

### **Real-time Dashboard**
- Account value and buying power
- Open positions display
- Market status indicator
- Bot status monitoring

### **Comprehensive Logging**
- All trading decisions logged
- Error tracking and debugging
- Performance metrics
- Exportable log files

### **Trade Database**
- SQLite database for all trades
- Timestamp, symbol, side, price, quantity
- Strategy used and status
- Historical performance tracking

## 🛠️ Troubleshooting

### **Common Issues**

**1. Connection Errors**
- Verify API keys in `.env` file
- Check internet connection
- Ensure Alpaca account is active

**2. Data Issues**
- Some symbols may have insufficient data
- Check market hours
- Verify symbol format (uppercase)

**3. GUI Issues**
- Ensure all dependencies are installed
- Check Python version (3.7+)
- Try running from command line

### **Error Messages**
- **"Insufficient data"**: Symbol needs more historical data
- **"Market closed"**: Bot only trades during market hours
- **"Connection failed"**: Check API keys and internet

## 📚 Dependencies

See `DEPENDENCIES.txt` for complete installation instructions.

**Core Requirements:**
- Python 3.7+
- alpaca-trade-api
- pandas, numpy
- ta (technical analysis)
- tkinter (GUI)
- Pillow (image handling)

## ⚠️ Important Notes

### **Paper Trading Only**
- This bot connects to Alpaca Paper Trading API
- No real money is at risk
- Perfect for testing and learning

### **Market Hours**
- Bot only trades during market hours
- Pre-market and after-hours are detected
- Weekend and holiday awareness

### **Data Limitations**
- Alpaca Paper API has limited historical data
- Strategy optimized for available data
- Works best with liquid, high-volume stocks

## 🤝 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify all dependencies are installed
4. Ensure API keys are correct

## 📄 License

This project is for educational and testing purposes. Use at your own risk.

---

**Author**: Trevor Hunter  
**Version**: 1.0  
**Strategy**: VWAP Reversion for Intraday Mean Reversion Trading
