"""
Trader module for Hybrid-Safe trading bot.
Handles order management and Alpaca API interactions.
"""

import time
import logging
import pandas as pd
from alpaca_trade_api import REST, TimeFrame
from alpaca_trade_api.rest import APIError
from config import Config
from database import TradeDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlpacaTrader:
    """Handles trading operations with Alpaca API."""
    
    def __init__(self):
        """Initialize the trader with Alpaca API connection."""
        self.api = REST(
            key_id=Config.ALPACA_API_KEY,
            secret_key=Config.ALPACA_SECRET_KEY,
            base_url=Config.BASE_URL,
            api_version='v2'
        )
        self.db = TradeDatabase()
        self.position_size = Config.POSITION_SIZE
        self.stop_loss_pct = Config.STOP_LOSS_PCT
        self.take_profit_pct = Config.TAKE_PROFIT_PCT
        
        # Test connection
        try:
            account = self.api.get_account()
            logger.info(f"✓ Connected to Alpaca. Account: {account.account_number}")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            raise
    
    def get_account_info(self):
        """
        Get current account information.
        
        Returns:
            dict: Account information
        """
        try:
            account = self.api.get_account()
            return {
                'balance': float(account.cash),
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_positions(self):
        """
        Get current positions.
        
        Returns:
            list: List of current positions
        """
        try:
            positions = self.api.list_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': 'long' if float(pos.qty) > 0 else 'short',
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_historical_data(self, symbol, timeframe='1Hour', limit=200):
        """
        Get historical OHLCV data for a symbol.
        
        Args:
            symbol (str): Trading symbol
            timeframe (str): Timeframe for data
            limit (int): Number of bars to retrieve
            
        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        try:
            # Convert timeframe string to TimeFrame object
            tf_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, 'minute'),
                '15Min': TimeFrame(15, 'minute'),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day
            }
            
            tf = tf_map.get(timeframe, TimeFrame.Hour)
            
            # Get historical data
            bars = self.api.get_bars(
                symbol,
                tf,
                limit=limit
            )
            
            # Convert to DataFrame
            data = []
            for bar in bars:
                # Access the raw data from the _raw attribute
                raw_data = bar._raw
                
                data.append({
                    'timestamp': raw_data['t'],  # timestamp
                    'open': float(raw_data['o']),  # open
                    'high': float(raw_data['h']),  # high
                    'low': float(raw_data['l']),   # low
                    'close': float(raw_data['c']), # close
                    'volume': int(raw_data['v'])   # volume
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_position_size(self, price):
        """
        Calculate position size based on current price and position size setting.
        
        Args:
            price (float): Current price of the asset
            
        Returns:
            float: Number of shares to buy/sell
        """
        return round(self.position_size / price, 2)
    
    def update_trading_settings(self, position_size=None, stop_loss_pct=None, take_profit_pct=None):
        """
        Update trading settings dynamically.
        
        Args:
            position_size (float): New position size in dollars
            stop_loss_pct (float): New stop loss percentage (as decimal, e.g., 0.03 for 3%)
            take_profit_pct (float): New take profit percentage (as decimal, e.g., 0.08 for 8%)
        """
        if position_size is not None:
            self.position_size = position_size
        if stop_loss_pct is not None:
            self.stop_loss_pct = stop_loss_pct
        if take_profit_pct is not None:
            self.take_profit_pct = take_profit_pct
        
        logger.info(f"Trading settings updated: Position=${self.position_size}, Stop Loss={self.stop_loss_pct*100:.1f}%, Take Profit={self.take_profit_pct*100:.1f}%")
    
    def place_bracket_order(self, symbol, side, qty, current_price, reason=None):
        """
        Place a bracket order with stop loss and take profit.
        
        Args:
            symbol (str): Trading symbol
            side (str): 'buy' or 'sell'
            qty (float): Quantity to trade
            current_price (float): Current market price
            reason (str): Reason for the trade
            
        Returns:
            dict: Order information
        """
        try:
            # Calculate stop loss and take profit prices
            if side.lower() == 'buy':
                stop_loss_price = current_price * (1 - self.stop_loss_pct)
                take_profit_price = current_price * (1 + self.take_profit_pct)
            else:  # sell
                stop_loss_price = current_price * (1 + self.stop_loss_pct)
                take_profit_price = current_price * (1 - self.take_profit_pct)
            
            # Place bracket order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day',
                order_class='bracket',
                stop_loss={'stop_price': stop_loss_price},
                take_profit={'limit_price': take_profit_price}
            )
            
            # Log the trade
            self.db.log_trade(
                symbol=symbol,
                side=side,
                price=current_price,
                qty=qty,
                status='submitted',
                order_id=order.id,
                stop_loss=stop_loss_price,
                take_profit=take_profit_price,
                reason=reason
            )
            
            logger.info(f"✓ {side.upper()} order placed for {symbol}: {qty} shares @ ${current_price:.2f}")
            logger.info(f"  Stop Loss: ${stop_loss_price:.2f}, Take Profit: ${take_profit_price:.2f}")
            
            return {
                'order_id': order.id,
                'status': 'submitted',
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price
            }
            
        except APIError as e:
            logger.error(f"API Error placing {side} order for {symbol}: {e}")
            self.db.log_trade(
                symbol=symbol,
                side=side,
                price=current_price,
                qty=qty,
                status='failed',
                reason=f"API Error: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error placing {side} order for {symbol}: {e}")
            self.db.log_trade(
                symbol=symbol,
                side=side,
                price=current_price,
                qty=qty,
                status='failed',
                reason=f"Error: {e}"
            )
            return None
    
    def close_position(self, symbol, reason=None):
        """
        Close an existing position for a symbol.
        
        Args:
            symbol (str): Trading symbol
            reason (str): Reason for closing
            
        Returns:
            bool: True if position was closed successfully
        """
        try:
            positions = self.get_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                logger.info(f"No position found for {symbol}")
                return False
            
            # Determine side to close position
            side = 'sell' if position['side'] == 'long' else 'buy'
            qty = abs(position['qty'])
            
            # Get current price
            current_price = self.get_current_price(symbol)
            if not current_price:
                logger.error(f"Could not get current price for {symbol}")
                return False
            
            # Place market order to close
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            # Log the trade
            self.db.log_trade(
                symbol=symbol,
                side=side,
                price=current_price,
                qty=qty,
                status='submitted',
                order_id=order.id,
                reason=f"Close position: {reason}"
            )
            
            logger.info(f"✓ Position closed for {symbol}: {qty} shares @ ${current_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return False
    
    def get_current_price(self, symbol):
        """
        Get current price for a symbol.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            float: Current price or None if error
        """
        try:
            quote = self.api.get_latest_quote(symbol)
            return float(quote.ask_price)
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def execute_trade(self, symbol, signal, current_price, reason=None):
        """
        Execute a trade based on signal.
        
        Args:
            symbol (str): Trading symbol
            signal (str): 'BUY', 'SELL', or 'HOLD'
            current_price (float): Current market price
            reason (str): Reason for the trade
            
        Returns:
            bool: True if trade was executed successfully
        """
        if signal == 'HOLD':
            return True
        
        # Check if we already have a position
        positions = self.get_positions()
        has_position = any(p['symbol'] == symbol for p in positions)
        
        if signal == 'BUY' and not has_position:
            # Calculate position size
            qty = self.calculate_position_size(current_price)
            if qty > 0:
                return self.place_bracket_order(symbol, 'buy', qty, current_price, reason) is not None
        
        elif signal == 'SELL' and has_position:
            return self.close_position(symbol, reason)
        
        return True
