"""
Database module for Hybrid-Safe trading bot.
Handles SQLite database operations for trade logging.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from config import Config

class TradeDatabase:
    """SQLite database handler for trade logging."""
    
    def __init__(self, db_path=None):
        """
        Initialize the database connection.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    price REAL NOT NULL,
                    qty REAL NOT NULL,
                    status TEXT NOT NULL,
                    order_id TEXT,
                    stop_loss REAL,
                    take_profit REAL,
                    reason TEXT
                )
            ''')
            
            # Create account_balance table for tracking balance over time
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_balance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    balance REAL NOT NULL,
                    equity REAL NOT NULL,
                    buying_power REAL NOT NULL
                )
            ''')
            
            conn.commit()
    
    def log_trade(self, symbol, side, price, qty, status, order_id=None, 
                  stop_loss=None, take_profit=None, reason=None):
        """
        Log a trade to the database.
        
        Args:
            symbol (str): Trading symbol
            side (str): 'buy' or 'sell'
            price (float): Trade price
            qty (float): Quantity traded
            status (str): Order status
            order_id (str): Alpaca order ID
            stop_loss (float): Stop loss price
            take_profit (float): Take profit price
            reason (str): Reason for the trade
        """
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, symbol, side, price, qty, status, order_id, stop_loss, take_profit, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, symbol, side, price, qty, status, order_id, 
                  stop_loss, take_profit, reason))
            conn.commit()
    
    def log_account_balance(self, balance, equity, buying_power):
        """
        Log account balance information.
        
        Args:
            balance (float): Account balance
            equity (float): Account equity
            buying_power (float): Available buying power
        """
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO account_balance 
                (timestamp, balance, equity, buying_power)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, balance, equity, buying_power))
            conn.commit()
    
    def get_recent_trades(self, limit=10):
        """
        Get recent trades from the database.
        
        Args:
            limit (int): Number of recent trades to retrieve
            
        Returns:
            pd.DataFrame: Recent trades
        """
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def get_trades_by_symbol(self, symbol, limit=50):
        """
        Get trades for a specific symbol.
        
        Args:
            symbol (str): Trading symbol
            limit (int): Number of trades to retrieve
            
        Returns:
            pd.DataFrame: Trades for the symbol
        """
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM trades 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(symbol, limit))
    
    def get_account_balance_history(self, limit=24):
        """
        Get account balance history.
        
        Args:
            limit (int): Number of balance records to retrieve
            
        Returns:
            pd.DataFrame: Account balance history
        """
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM account_balance 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def get_trade_stats(self):
        """
        Get basic trade statistics.
        
        Returns:
            dict: Trade statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total trades
            cursor.execute('SELECT COUNT(*) FROM trades')
            total_trades = cursor.fetchone()[0]
            
            # Buy vs Sell trades
            cursor.execute('SELECT side, COUNT(*) FROM trades GROUP BY side')
            side_counts = dict(cursor.fetchall())
            
            # Trades by symbol
            cursor.execute('SELECT symbol, COUNT(*) FROM trades GROUP BY symbol ORDER BY COUNT(*) DESC')
            symbol_counts = dict(cursor.fetchall())
            
            # Recent trades (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM trades 
                WHERE timestamp > datetime('now', '-1 day')
            ''')
            recent_trades = cursor.fetchone()[0]
            
            return {
                'total_trades': total_trades,
                'buy_trades': side_counts.get('buy', 0),
                'sell_trades': side_counts.get('sell', 0),
                'symbol_counts': symbol_counts,
                'recent_trades_24h': recent_trades
            }



