"""
VWAP Reversion Trading Bot v1.0
A complete Python trading bot that connects to the Alpaca Paper Trading API
and implements the VWAP Reversion strategy for intraday mean reversion trading.

Strategy: Buy when price < VWAP × 0.99 and candle closes above VWAP again.
          Sell when price > VWAP × 1.01 or RSI > 70.

Author: Trevor Hunter
Version: 1.0
"""

import time
import schedule
import logging
from datetime import datetime
from typing import List, Dict, Any

from config import Config
from trader import AlpacaTrader
from strategy import VWAPReversionStrategy
from indicators import calculate_all_indicators, get_latest_signals, validate_data_quality
from database import TradeDatabase
from market_hours import get_market_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vwap_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VWAPReversionBot:
    """
    VWAP Reversion Trading Bot for intraday mean reversion trading.
    
    This bot implements a VWAP-based reversion strategy that:
    - Buys when price drops below VWAP threshold and shows reversion
    - Sells when price exceeds VWAP threshold or RSI becomes overbought
    - Works best with 5-15 minute timeframes for high-frequency testing
    """
    
    def __init__(self, symbols: List[str] = None):
        """
        Initialize the VWAP Reversion bot.
        
        Args:
            symbols (List[str]): List of symbols to trade
        """
        self.symbols = symbols or Config.DEFAULT_SYMBOLS
        self.trader = AlpacaTrader()
        self.strategy = VWAPReversionStrategy(
            vwap_threshold_buy=Config.VWAP_BUY_THRESHOLD,
            vwap_threshold_sell=Config.VWAP_SELL_THRESHOLD,
            rsi_overbought=Config.RSI_OVERBOUGHT,
            rsi_period=Config.RSI_PERIOD
        )
        self.database = TradeDatabase()
        
        logger.info("VWAP Reversion Bot initialized")
        logger.info(f"Strategy: {self.strategy.get_strategy_info()['name']}")
        logger.info(f"Symbols: {self.symbols}")
        logger.info(f"Timeframe: {Config.TIMEFRAME}")
    
    def run_strategy(self):
        """
        Run the VWAP Reversion strategy on all symbols.
        """
        logger.info("=" * 50)
        logger.info("Running VWAP Reversion Strategy")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check market status
        market_status = get_market_status()
        if not market_status['is_open']:
            logger.info(f"Market is {market_status['status']} - skipping strategy")
            return
        
        logger.info("Market is open - running strategy analysis")
        
        for symbol in self.symbols:
            try:
                self.analyze_symbol(symbol)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        logger.info("Strategy analysis complete")
    
    def analyze_symbol(self, symbol: str):
        """
        Analyze a single symbol for VWAP Reversion signals.
        
        Args:
            symbol (str): Stock symbol to analyze
        """
        try:
            # Get historical data
            df = self.trader.get_historical_data(symbol, Config.TIMEFRAME)
            
            if not validate_data_quality(df, min_bars=5):
                logger.warning(f"Insufficient data for {symbol} - skipping")
                return
            
            # Calculate indicators
            df = calculate_all_indicators(df, Config.RSI_PERIOD)
            
            # Get latest signals
            signals = get_latest_signals(df)
            if not signals:
                logger.warning(f"No signals available for {symbol}")
                return
            
            # Check for buy signal
            if self.strategy.get_buy_signal(signals, symbol):
                self.execute_buy_order(symbol, signals)
            
            # Check for sell signal
            elif self.strategy.get_sell_signal(signals, symbol):
                self.execute_sell_order(symbol, signals)
            
            else:
                logger.info(f"{symbol} → HOLD (no signal)")
                self.log_signal(symbol, "HOLD", signals)
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
    
    def execute_buy_order(self, symbol: str, signals: Dict[str, Any]):
        """
        Execute a buy order for VWAP Reversion strategy.
        
        Args:
            symbol (str): Stock symbol
            signals (dict): Latest indicator values
        """
        try:
            current_price = signals['close']
            vwap = signals['vwap']
            rsi = signals['rsi']
            
            # Calculate position size
            qty = Config.POSITION_SIZE / current_price
            
            # Submit bracket order
            order = self.trader.submit_bracket_order(
                symbol=symbol,
                side='buy',
                qty=qty,
                stop_loss_pct=Config.STOP_LOSS_PCT,
                take_profit_pct=Config.TAKE_PROFIT_PCT
            )
            
            if order:
                logger.info(f"{symbol} → BUY triggered @ ${current_price:.2f} (Qty: {qty:.2f})")
                logger.info(f"  VWAP: ${vwap:.2f}, RSI: {rsi:.1f}")
                
                # Log to database
                self.database.log_trade(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    side='buy',
                    price=current_price,
                    qty=qty,
                    status='submitted',
                    strategy='VWAP_Reversion'
                )
                
                self.log_signal(symbol, "BUY", signals)
            else:
                logger.error(f"Failed to submit buy order for {symbol}")
        
        except Exception as e:
            logger.error(f"Error executing buy order for {symbol}: {e}")
    
    def execute_sell_order(self, symbol: str, signals: Dict[str, Any]):
        """
        Execute a sell order for VWAP Reversion strategy.
        
        Args:
            symbol (str): Stock symbol
            signals (dict): Latest indicator values
        """
        try:
            current_price = signals['close']
            vwap = signals['vwap']
            rsi = signals['rsi']
            
            # Get current position
            position = self.trader.get_position(symbol)
            if not position or position.qty <= 0:
                logger.info(f"{symbol} → No position to sell")
                return
            
            # Submit sell order
            order = self.trader.submit_market_order(
                symbol=symbol,
                side='sell',
                qty=position.qty
            )
            
            if order:
                logger.info(f"{symbol} → SELL triggered @ ${current_price:.2f} (Qty: {position.qty:.2f})")
                logger.info(f"  VWAP: ${vwap:.2f}, RSI: {rsi:.1f}")
                
                # Log to database
                self.database.log_trade(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    side='sell',
                    price=current_price,
                    qty=position.qty,
                    status='submitted',
                    strategy='VWAP_Reversion'
                )
                
                self.log_signal(symbol, "SELL", signals)
            else:
                logger.error(f"Failed to submit sell order for {symbol}")
        
        except Exception as e:
            logger.error(f"Error executing sell order for {symbol}: {e}")
    
    def log_signal(self, symbol: str, action: str, signals: Dict[str, Any]):
        """
        Log signal information for analysis.
        
        Args:
            symbol (str): Stock symbol
            action (str): Signal action (BUY/SELL/HOLD)
            signals (dict): Latest indicator values
        """
        try:
            logger.info(f"  Signal Details for {symbol}:")
            logger.info(f"    Action: {action}")
            logger.info(f"    Price: ${signals['close']:.2f}")
            logger.info(f"    VWAP: ${signals['vwap']:.2f}" if signals['vwap'] else "    VWAP: N/A")
            logger.info(f"    RSI: {signals['rsi']:.1f}" if signals['rsi'] else "    RSI: N/A")
            
            # Calculate VWAP ratios
            if signals['vwap']:
                vwap_ratio = signals['close'] / signals['vwap']
                logger.info(f"    Price/VWAP: {vwap_ratio:.3f}")
        
        except Exception as e:
            logger.error(f"Error logging signal for {symbol}: {e}")
    
    def print_account_summary(self):
        """Print current account balance and positions."""
        try:
            account = self.trader.get_account()
            positions = self.trader.get_positions()
            
            logger.info("=" * 50)
            logger.info("ACCOUNT SUMMARY")
            logger.info(f"Account Value: ${float(account.equity):,.2f}")
            logger.info(f"Buying Power: ${float(account.buying_power):,.2f}")
            logger.info(f"Cash: ${float(account.cash):,.2f}")
            logger.info(f"Open Positions: {len(positions)}")
            
            if positions:
                logger.info("Current Positions:")
                for pos in positions:
                    logger.info(f"  {pos.symbol}: {pos.qty} @ ${pos.avg_entry_price}")
            
            logger.info("=" * 50)
        
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
    
    def run(self):
        """Start the VWAP Reversion bot."""
        logger.info("Starting VWAP Reversion Trading Bot")
        logger.info(f"Strategy: {self.strategy.get_strategy_info()['name']}")
        logger.info(f"Symbols: {self.symbols}")
        logger.info(f"Timeframe: {Config.TIMEFRAME}")
        
        # Validate configuration
        Config.validate_config()
        
        # Connect to Alpaca
        if not self.trader.connect():
            logger.error("Failed to connect to Alpaca API")
            return
        
        # Print initial account summary
        self.print_account_summary()
        
        # Schedule strategy runs
        schedule.every(5).minutes.do(self.run_strategy)  # Run every 5 minutes for intraday
        schedule.every().hour.do(self.print_account_summary)
        
        logger.info("Bot scheduled to run every 5 minutes")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")

def main():
    """Main function to run the VWAP Reversion bot."""
    import argparse
    
    parser = argparse.ArgumentParser(description='VWAP Reversion Trading Bot')
    parser.add_argument('--symbols', nargs='+', help='Symbols to trade')
    args = parser.parse_args()
    
    bot = VWAPReversionBot(symbols=args.symbols)
    bot.run()

if __name__ == "__main__":
    main()

