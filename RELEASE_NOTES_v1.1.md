# VWAP Reversion Trading Bot v1.1 - Release Notes

## 🎯 **What is the VWAP Reversion Trading Bot?**

The VWAP Reversion Trading Bot is an automated trading system that implements a sophisticated intraday mean reversion strategy. It focuses on identifying overreactions in stock prices relative to the Volume Weighted Average Price (VWAP) and capitalizes on price reversions back to fair value.

## 📊 **What Does It Do?**

### **Core Strategy: VWAP Reversion**
- **Buy Signal**: When price drops below VWAP × 0.99 and then closes above VWAP again (indicating reversion)
- **Sell Signal**: When price exceeds VWAP × 1.01 or RSI > 70 (indicating overextension)
- **Safety Mechanism**: Prevents buying if price is too far below VWAP (more than 5% discount)

### **Key Features:**
- **Intraday Focus**: Optimized for 5-minute timeframes for high-frequency analysis
- **Institutional Benchmark**: Uses VWAP as the fair value reference point
- **Risk Management**: Built-in stop-loss (3%) and take-profit (8%) orders
- **Market Hours Detection**: Only trades during market hours, holidays, and weekends
- **Professional GUI**: Complete graphical interface with real-time monitoring

## 🚀 **New in v1.1**

### **Enhanced User Interface**
- ✅ **Refresh Data Button**: Manual data refresh without starting the bot
- ✅ **Update Current Profile Button**: Save changes to current profile without entering new name
- ✅ **Selection-Based Profile Management**: Click to select profiles instead of typing names
- ✅ **Improved Symbols Management**: Professional listbox display with scrollbar
- ✅ **Dedicated Profiles Tab**: Separate tab for profile management

### **Bug Fixes & Improvements**
- ✅ **Fixed ProfileManager Error**: Added missing `get_profile_data()` method
- ✅ **Fixed .env File Loading**: Resolved Unicode encoding issues with BOM handling
- ✅ **Fixed AlpacaTrader Connection**: Added `connected` property for proper status checking
- ✅ **API Credentials**: Separate trading account from Hybrid-Safe bot
- ✅ **Market Hours Integration**: Proper market status detection and display

### **Technical Improvements**
- ✅ **Better Error Handling**: Comprehensive error handling throughout the application
- ✅ **Unicode Compatibility**: Fixed console encoding issues on Windows
- ✅ **Profile Management**: Enhanced profile system with selection interface
- ✅ **Data Validation**: Improved data quality checks and validation

## 🎨 **User Interface Features**

### **Dashboard Tab**
- Real-time account information (balance, equity, buying power, positions)
- Market status display (open/closed with next open time)
- Bot control buttons (Connect, Start, Stop, Refresh Data)
- Live bot status indicator

### **Trading Settings Tab**
- Position size configuration ($100 default)
- Risk management settings (3% stop-loss, 8% take-profit)
- VWAP strategy parameters (buy/sell thresholds, RSI settings)
- Data refresh intervals (1 minute to 1 hour)

### **Symbols Tab**
- Professional listbox display of current symbols
- Add/Remove individual symbols
- CSV import/export functionality
- Clear all symbols with confirmation
- Real-time symbol list updates

### **Profiles Tab**
- Current profile display
- Save current settings as new profile
- Update current profile (NEW in v1.1)
- Load selected profile (click to select)
- Delete selected profile with confirmation
- Available profiles listbox

### **Logs Tab**
- Real-time trading activity logs
- Market status updates
- Error messages and debugging information
- Clear logs functionality

## 🔧 **Technical Specifications**

### **Strategy Parameters**
- **VWAP Buy Threshold**: 0.99 (buy when price < VWAP × 0.99)
- **VWAP Sell Threshold**: 1.01 (sell when price > VWAP × 1.01)
- **RSI Period**: 14 (standard RSI calculation)
- **RSI Overbought**: 70 (sell when RSI > 70)
- **VWAP Safety Threshold**: 0.95 (don't buy if price < VWAP × 0.95)

### **Trading Parameters**
- **Position Size**: $100 per trade (configurable)
- **Stop Loss**: 3% below entry price
- **Take Profit**: 8% above entry price
- **Timeframe**: 5-minute bars for intraday analysis
- **Default Symbols**: AAPL, NVDA, TSLA, AMZN, META

### **API Integration**
- **Alpaca Paper Trading API**: Safe paper trading environment
- **Separate Account**: Different from Hybrid-Safe bot account
- **Real-time Data**: Live market data and account information
- **Order Management**: Automated bracket orders with stop-loss and take-profit

## 📈 **How It Works**

### **1. Data Collection**
- Fetches 5-minute OHLCV data for configured symbols
- Calculates VWAP (Volume Weighted Average Price)
- Computes RSI (Relative Strength Index)

### **2. Signal Generation**
- **Buy Signal**: Price drops below VWAP threshold AND closes above VWAP again
- **Sell Signal**: Price exceeds VWAP threshold OR RSI becomes overbought
- **Safety Check**: Prevents buying if price is too far below VWAP

### **3. Order Execution**
- Places bracket orders with stop-loss and take-profit
- Manages position sizing automatically
- Logs all trades to SQLite database

### **4. Risk Management**
- Built-in stop-loss protection
- Take-profit targets
- Position size limits
- Market hours validation

## 🎯 **Perfect For**

- **Intraday Traders**: Focus on short-term price reversions
- **Mean Reversion Strategies**: Capitalize on overreactions
- **Institutional Benchmark Trading**: Use VWAP as fair value reference
- **Risk-Conscious Traders**: Built-in risk management features
- **Automated Trading**: Hands-off approach to trading

## 🔄 **Complement to Hybrid-Safe Bot**

The VWAP Reversion Bot is designed to complement the Hybrid-Safe bot:
- **Hybrid-Safe**: Trend-following strategy for longer timeframes
- **VWAP Reversion**: Mean reversion strategy for intraday trading
- **Together**: Cover both trend persistence and mean reversion opportunities

## 📋 **Installation & Setup**

1. **Clone the repository**
2. **Install dependencies**: `pip install -r DEPENDENCIES.txt`
3. **Configure API keys**: Update `.env` file with Alpaca credentials
4. **Run the GUI**: `python gui.py`
5. **Connect to Alpaca**: Click "Connect to Alpaca" button
6. **Configure settings**: Set up symbols, position size, and strategy parameters
7. **Start trading**: Click "Start Bot" when ready

## 🚨 **Important Notes**

- **Paper Trading Only**: Uses Alpaca Paper Trading API for safe testing
- **Market Hours**: Only trades during market hours (9:30 AM - 4:00 PM ET)
- **Risk Management**: Always use stop-losses and position sizing
- **Backtesting**: Test strategies thoroughly before live trading
- **Monitoring**: Keep an eye on bot performance and market conditions

## 📞 **Support**

For questions, issues, or feature requests, please refer to the GitHub repository documentation or create an issue.

---

**Version**: 1.1  
**Release Date**: December 2024  
**Author**: Trevor Hunter  
**License**: MIT
