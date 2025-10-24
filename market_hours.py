"""
Market hours utility for VWAP Reversion Trading Bot v1.0.
Handles market hours detection and trading schedule management.

Author: Trevor Hunter
Version: 1.0
"""

import pytz
from datetime import datetime, time
import holidays

class MarketHours:
    """Handles market hours detection and trading schedule."""
    
    def __init__(self):
        """Initialize market hours with US market timezone."""
        self.market_tz = pytz.timezone('US/Eastern')
        self.us_holidays = holidays.US()
        
        # Market hours (Eastern Time)
        self.market_open = time(9, 30)  # 9:30 AM ET
        self.market_close = time(16, 0)  # 4:00 PM ET
        
        # Pre-market and after-hours (optional)
        self.premarket_open = time(4, 0)   # 4:00 AM ET
        self.afterhours_close = time(20, 0)  # 8:00 PM ET
    
    def is_market_open(self, check_time=None):
        """
        Check if the market is currently open.
        
        Args:
            check_time (datetime): Time to check (defaults to now)
            
        Returns:
            bool: True if market is open, False otherwise
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            # Assume UTC if no timezone
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if check_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if it's a US holiday
        if check_time.date() in self.us_holidays:
            return False
        
        # Check if it's within market hours
        current_time = check_time.time()
        return self.market_open <= current_time <= self.market_close
    
    def is_premarket(self, check_time=None):
        """
        Check if it's pre-market hours.
        
        Args:
            check_time (datetime): Time to check (defaults to now)
            
        Returns:
            bool: True if pre-market hours, False otherwise
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        # Check if it's a weekday
        if check_time.weekday() >= 5:
            return False
        
        # Check if it's a US holiday
        if check_time.date() in self.us_holidays:
            return False
        
        current_time = check_time.time()
        return self.premarket_open <= current_time < self.market_open
    
    def is_afterhours(self, check_time=None):
        """
        Check if it's after-hours.
        
        Args:
            check_time (datetime): Time to check (defaults to now)
            
        Returns:
            bool: True if after-hours, False otherwise
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        # Check if it's a weekday
        if check_time.weekday() >= 5:
            return False
        
        # Check if it's a US holiday
        if check_time.date() in self.us_holidays:
            return False
        
        current_time = check_time.time()
        return self.market_close < current_time <= self.afterhours_close
    
    def get_market_status(self, check_time=None):
        """
        Get detailed market status.
        
        Args:
            check_time (datetime): Time to check (defaults to now)
            
        Returns:
            dict: Market status information
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        status = {
            'is_open': self.is_market_open(check_time),
            'is_premarket': self.is_premarket(check_time),
            'is_afterhours': self.is_afterhours(check_time),
            'is_weekend': check_time.weekday() >= 5,
            'is_holiday': check_time.date() in self.us_holidays,
            'current_time': check_time,
            'market_open': check_time.replace(hour=9, minute=30, second=0, microsecond=0),
            'market_close': check_time.replace(hour=16, minute=0, second=0, microsecond=0)
        }
        
        # Determine status text
        if status['is_holiday']:
            status['status_text'] = "Market Closed (Holiday)"
        elif status['is_weekend']:
            status['status_text'] = "Market Closed (Weekend)"
        elif status['is_open']:
            status['status_text'] = "Market Open"
        elif status['is_premarket']:
            status['status_text'] = "Pre-Market"
        elif status['is_afterhours']:
            status['status_text'] = "After-Hours"
        else:
            status['status_text'] = "Market Closed"
        
        return status
    
    def get_next_market_open(self, check_time=None):
        """
        Get the next market open time.
        
        Args:
            check_time (datetime): Time to check from (defaults to now)
            
        Returns:
            datetime: Next market open time
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        # Start from today
        next_open = check_time.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # If market is already open today, or it's past market close, go to next day
        if check_time.time() >= self.market_close or self.is_market_open(check_time):
            next_open = next_open.replace(day=next_open.day + 1)
        
        # Skip weekends and holidays
        while next_open.weekday() >= 5 or next_open.date() in self.us_holidays:
            next_open = next_open.replace(day=next_open.day + 1)
        
        return next_open
    
    def get_time_until_market_open(self, check_time=None):
        """
        Get time remaining until market opens.
        
        Args:
            check_time (datetime): Time to check from (defaults to now)
            
        Returns:
            timedelta: Time until market opens
        """
        if check_time is None:
            check_time = datetime.now(self.market_tz)
        elif check_time.tzinfo is None:
            check_time = pytz.utc.localize(check_time).astimezone(self.market_tz)
        else:
            check_time = check_time.astimezone(self.market_tz)
        
        next_open = self.get_next_market_open(check_time)
        return next_open - check_time

# Global instance
market_hours = MarketHours()

# Convenience functions for direct import
def get_market_status(check_time=None):
    """Get market status using the global instance."""
    return market_hours.get_market_status(check_time)

def get_next_market_open(check_time=None):
    """Get next market open time using the global instance."""
    return market_hours.get_next_market_open(check_time)

def is_market_open(check_time=None):
    """Check if market is open using the global instance."""
    return market_hours.is_market_open(check_time)
