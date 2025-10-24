"""
VWAP Reversion Strategy for Trading Bot v1.0
Intraday mean reversion strategy based on VWAP and RSI.

Strategy Rules:
- Buy: Price < VWAP × 0.99 AND candle closes above VWAP again
- Sell: Price > VWAP × 1.01 OR RSI > 70

Author: Trevor Hunter
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

class VWAPReversionStrategy:
    """
    VWAP Reversion Strategy implementation.
    
    This strategy focuses on intraday mean reversion around VWAP,
    perfect for capturing short-term price overreactions.
    """
    
    def __init__(self, vwap_threshold_buy=0.99, vwap_threshold_sell=1.01, 
                 rsi_overbought=70, rsi_period=14):
        """
        Initialize the VWAP Reversion strategy.
        
        Args:
            vwap_threshold_buy (float): Buy threshold (price < VWAP × threshold)
            vwap_threshold_sell (float): Sell threshold (price > VWAP × threshold)
            rsi_overbought (float): RSI overbought level
            rsi_period (int): RSI calculation period
        """
        self.vwap_threshold_buy = vwap_threshold_buy
        self.vwap_threshold_sell = vwap_threshold_sell
        self.rsi_overbought = rsi_overbought
        self.rsi_period = rsi_period
        
        # Track previous candle for "closes above VWAP again" condition
        self.previous_signals = {}
    
    def get_buy_signal(self, signals, symbol):
        """
        Check if buy conditions are met for VWAP Reversion strategy.
        
        Buy conditions:
        1. Price < VWAP × 0.99 (price is below VWAP threshold)
        2. Current candle closes above VWAP (reversion signal)
        
        Args:
            signals (dict): Latest indicator values
            symbol (str): Stock symbol
            
        Returns:
            bool: True if buy signal, False otherwise
        """
        if not signals:
            return False
        
        # Check if we have required data
        if (signals['close'] is None or signals['vwap'] is None or 
            signals['high'] is None or signals['low'] is None):
            return False
        
        current_price = signals['close']
        vwap = signals['vwap']
        
        # Condition 1: Price < VWAP × 0.99 (price is below VWAP threshold)
        price_below_threshold = current_price < (vwap * self.vwap_threshold_buy)
        
        # Condition 2: Current candle closes above VWAP (reversion signal)
        candle_closes_above_vwap = current_price > vwap
        
        # Additional safety: Ensure we're not too far below VWAP (avoid falling knives)
        price_not_too_low = current_price > (vwap * 0.95)  # Within 5% of VWAP
        
        buy_signal = (price_below_threshold and 
                     candle_closes_above_vwap and 
                     price_not_too_low)
        
        # Store signal for next iteration
        self.previous_signals[symbol] = {
            'price': current_price,
            'vwap': vwap,
            'signal': 'buy' if buy_signal else 'hold'
        }
        
        return buy_signal
    
    def get_sell_signal(self, signals, symbol):
        """
        Check if sell conditions are met for VWAP Reversion strategy.
        
        Sell conditions:
        1. Price > VWAP × 1.01 (price is above VWAP threshold)
        2. OR RSI > 70 (overbought condition)
        
        Args:
            signals (dict): Latest indicator values
            symbol (str): Stock symbol
            
        Returns:
            bool: True if sell signal, False otherwise
        """
        if not signals:
            return False
        
        # Check if we have required data
        if (signals['close'] is None or signals['vwap'] is None or 
            signals['rsi'] is None):
            return False
        
        current_price = signals['close']
        vwap = signals['vwap']
        rsi = signals['rsi']
        
        # Condition 1: Price > VWAP × 1.01 (price is above VWAP threshold)
        price_above_threshold = current_price > (vwap * self.vwap_threshold_sell)
        
        # Condition 2: RSI > 70 (overbought condition)
        rsi_overbought = rsi > self.rsi_overbought
        
        sell_signal = price_above_threshold or rsi_overbought
        
        # Store signal for next iteration
        if symbol in self.previous_signals:
            self.previous_signals[symbol]['signal'] = 'sell' if sell_signal else 'hold'
        
        return sell_signal
    
    def get_strategy_info(self):
        """
        Get strategy information and parameters.
        
        Returns:
            dict: Strategy information
        """
        return {
            'name': 'VWAP Reversion Strategy',
            'description': 'Intraday mean reversion around VWAP with RSI confirmation',
            'parameters': {
                'vwap_buy_threshold': self.vwap_threshold_buy,
                'vwap_sell_threshold': self.vwap_threshold_sell,
                'rsi_overbought': self.rsi_overbought,
                'rsi_period': self.rsi_period
            },
            'buy_conditions': [
                f'Price < VWAP × {self.vwap_threshold_buy}',
                'Candle closes above VWAP',
                'Price within 5% of VWAP (safety)'
            ],
            'sell_conditions': [
                f'Price > VWAP × {self.vwap_threshold_sell}',
                f'RSI > {self.rsi_overbought}'
            ]
        }
    
    def update_parameters(self, **kwargs):
        """
        Update strategy parameters.
        
        Args:
            **kwargs: Strategy parameters to update
        """
        if 'vwap_threshold_buy' in kwargs:
            self.vwap_threshold_buy = kwargs['vwap_threshold_buy']
        if 'vwap_threshold_sell' in kwargs:
            self.vwap_threshold_sell = kwargs['vwap_threshold_sell']
        if 'rsi_overbought' in kwargs:
            self.rsi_overbought = kwargs['rsi_overbought']
        if 'rsi_period' in kwargs:
            self.rsi_period = kwargs['rsi_period']
    
    def reset_signals(self):
        """Reset previous signals tracking."""
        self.previous_signals = {}
