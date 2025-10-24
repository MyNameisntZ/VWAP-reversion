"""
Configuration module for VWAP Reversion Trading Bot v1.0
Loads API credentials and settings from environment variables.

Author: Trevor Hunter
Version: 1.0
"""

import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv is not available, read .env file manually
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

class Config:
    """Configuration class for the trading bot."""
    
    # Alpaca API credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = os.getenv('BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Trading parameters
    POSITION_SIZE = 100  # $100 per trade
    STOP_LOSS_PCT = 0.03  # 3% stop loss
    TAKE_PROFIT_PCT = 0.08  # 8% take profit
    
    # VWAP Reversion Strategy parameters
    VWAP_BUY_THRESHOLD = 0.99    # Buy when price < VWAP × 0.99
    VWAP_SELL_THRESHOLD = 1.01   # Sell when price > VWAP × 1.01
    RSI_PERIOD = 14              # RSI calculation period
    RSI_OVERBOUGHT = 70          # RSI overbought level
    VWAP_SAFETY_THRESHOLD = 0.95 # Safety: don't buy if price < VWAP × 0.95
    
    # Default symbols to trade
    DEFAULT_SYMBOLS = ["AAPL", "NVDA", "TSLA", "AMZN", "META"]
    
    # Timeframe for data (VWAP works best with shorter timeframes)
    TIMEFRAME = "5Min"  # 5-minute bars for intraday VWAP strategy
    
    # Database
    DATABASE_PATH = "trades.db"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        if not cls.ALPACA_API_KEY:
            raise ValueError("ALPACA_API_KEY not found in environment variables")
        if not cls.ALPACA_SECRET_KEY:
            raise ValueError("ALPACA_SECRET_KEY not found in environment variables")
        if not cls.BASE_URL:
            raise ValueError("BASE_URL not found in environment variables")
        
        print("✓ Configuration validated successfully")
        return True
