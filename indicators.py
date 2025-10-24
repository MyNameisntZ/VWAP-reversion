"""
Technical indicators for VWAP Reversion Trading Bot v1.0
VWAP (Volume Weighted Average Price) and RSI calculations for intraday reversion strategy.

Author: Trevor Hunter
Version: 1.0
"""

import pandas as pd
import numpy as np
import ta

def calculate_vwap(df):
    """
    Calculate Volume Weighted Average Price (VWAP).
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        
    Returns:
        pd.Series: VWAP values
    """
    if df.empty or 'volume' not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    
    # VWAP = Sum(Price * Volume) / Sum(Volume)
    # Using typical price: (High + Low + Close) / 3
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    
    # Calculate cumulative VWAP
    cumulative_volume = df['volume'].cumsum()
    cumulative_price_volume = (typical_price * df['volume']).cumsum()
    
    vwap = cumulative_price_volume / cumulative_volume
    
    return vwap

def calculate_rsi(df, period=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        period (int): RSI period (default 14)
        
    Returns:
        pd.Series: RSI values
    """
    if df.empty or 'close' not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    
    return ta.momentum.RSIIndicator(df['close'], window=period).rsi()

def calculate_all_indicators(df, rsi_period=14):
    """
    Calculate all indicators needed for VWAP Reversion strategy.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        rsi_period (int): RSI period (default 14)
        
    Returns:
        pd.DataFrame: DataFrame with calculated indicators
    """
    if df.empty:
        return df
    
    # Calculate VWAP
    df['vwap'] = calculate_vwap(df)
    
    # Calculate RSI
    df['rsi'] = calculate_rsi(df, rsi_period)
    
    return df

def get_latest_signals(df):
    """
    Get the latest indicator values for signal generation.
    
    Args:
        df (pd.DataFrame): DataFrame with calculated indicators
        
    Returns:
        dict: Dictionary containing latest indicator values
    """
    if df.empty:
        return None
    
    latest = df.iloc[-1]
    
    # Check for NaN values and provide fallback
    signals = {
        'close': latest['close'],
        'high': latest['high'],
        'low': latest['low'],
        'vwap': latest['vwap'] if pd.notna(latest['vwap']) else None,
        'rsi': latest['rsi'] if pd.notna(latest['rsi']) else None
    }
    
    return signals

def validate_data_quality(df, min_bars=5):
    """
    Validate that we have sufficient data for VWAP calculation.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        min_bars (int): Minimum number of bars required
        
    Returns:
        bool: True if data is sufficient, False otherwise
    """
    if df.empty:
        return False
    
    if len(df) < min_bars:
        return False
    
    # Check for required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_columns):
        return False
    
    # Check for valid volume data
    if df['volume'].sum() == 0:
        return False
    
    return True

