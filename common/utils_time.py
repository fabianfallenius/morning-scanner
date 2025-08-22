"""
Time utilities for the Morning Scanner application.

This module provides:
- Stockholm timezone handling
- Date parsing and formatting
- Trading day detection for Swedish markets
- Business day calculations
"""

import pytz
from datetime import datetime, date, timedelta
from typing import Optional, Union
from dateutil import parser


# Stockholm timezone constant
STOCKHOLM_TZ = pytz.timezone('Europe/Stockholm')


def now_se() -> datetime:
    """
    Get current time in Stockholm timezone.
    
    Returns:
        datetime: Current time in Stockholm timezone
    """
    return datetime.now(STOCKHOLM_TZ)


def today_date_se() -> date:
    """
    Get today's date in Stockholm timezone.
    
    Returns:
        date: Today's date in Stockholm timezone
    """
    return now_se().date()


def parse_iso_guess_tz(time_string: str) -> datetime:
    """
    Parse ISO format time string and guess timezone if not specified.
    
    Args:
        time_string (str): ISO format time string
        
    Returns:
        datetime: Parsed datetime in Stockholm timezone
        
    Raises:
        ValueError: If string cannot be parsed as datetime
    """
    try:
        # Parse the time string
        dt = parser.parse(time_string)
        
        # If datetime is naive (no timezone), assume it's in Stockholm timezone
        if dt.tzinfo is None:
            dt = STOCKHOLM_TZ.localize(dt)
        else:
            # Convert to Stockholm timezone
            dt = dt.astimezone(STOCKHOLM_TZ)
        
        return dt
        
    except Exception as e:
        raise ValueError(f"Could not parse time string '{time_string}': {str(e)}")


def is_trading_day_sweden(check_date: Optional[Union[date, datetime]] = None) -> bool:
    """
    Check if a given date is a trading day in Sweden.
    
    Currently only skips weekends (Saturday and Sunday).
    TODO: Add Swedish holiday list for more accurate trading day detection.
    
    Args:
        check_date (date or datetime, optional): Date to check. If None, uses today.
        
    Returns:
        bool: True if trading day, False otherwise
    """
    if check_date is None:
        check_date = today_date_se()
    elif isinstance(check_date, datetime):
        check_date = check_date.date()
    
    # Skip weekends (Saturday = 5, Sunday = 6)
    if check_date.weekday() >= 5:
        return False
    
    # TODO: Add Swedish holiday list
    # Swedish holidays to skip:
    # - New Year's Day (January 1)
    # - Epiphany (January 6)
    # - Good Friday (varies)
    # - Easter Monday (varies)
    # - May Day (May 1)
    # - Ascension Day (varies)
    # - National Day (June 6)
    # - Midsummer Eve (Friday before June 21)
    # - All Saints' Day (Saturday between October 31 and November 6)
    # - Christmas Eve (December 24)
    # - Christmas Day (December 25)
    # - Boxing Day (December 26)
    # - New Year's Eve (December 31)
    
    return True


def get_next_trading_day(start_date: Optional[Union[date, datetime]] = None) -> date:
    """
    Get the next trading day from a given date.
    
    Args:
        start_date (date or datetime, optional): Starting date. If None, uses today.
        
    Returns:
        date: Next trading day
    """
    if start_date is None:
        start_date = today_date_se()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    
    current_date = start_date
    while True:
        current_date += timedelta(days=1)
        if is_trading_day_sweden(current_date):
            return current_date


def get_previous_trading_day(start_date: Optional[Union[date, datetime]] = None) -> date:
    """
    Get the previous trading day from a given date.
    
    Args:
        start_date (date or datetime, optional): Starting date. If None, uses today.
        
    Returns:
        date: Previous trading day
    """
    if start_date is None:
        start_date = today_date_se()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    
    current_date = start_date
    while True:
        current_date -= timedelta(days=1)
        if is_trading_day_sweden(current_date):
            return current_date


def is_market_hours(check_time: Optional[datetime] = None) -> bool:
    """
    Check if current time is during Swedish market hours (9:00-17:30 Stockholm time).
    
    Args:
        check_time (datetime, optional): Time to check. If None, uses current time.
        
    Returns:
        bool: True if during market hours, False otherwise
    """
    if check_time is None:
        check_time = now_se()
    
    stockholm_time = check_time.astimezone(STOCKHOLM_TZ)
    
    # Check if it's a trading day
    if not is_trading_day_sweden(stockholm_time):
        return False
    
    # Market hours: 9:00-17:30
    market_start = stockholm_time.replace(hour=9, minute=0, second=0, microsecond=0)
    market_end = stockholm_time.replace(hour=17, minute=30, second=0, microsecond=0)
    
    return market_start <= stockholm_time <= market_end


def get_market_open_time(check_date: Optional[Union[date, datetime]] = None) -> datetime:
    """
    Get market open time for a given date.
    
    Args:
        check_date (date or datetime, optional): Date to check. If None, uses today.
        
    Returns:
        datetime: Market open time in Stockholm timezone
    """
    if check_date is None:
        check_date = today_date_se()
    elif isinstance(check_date, date):
        check_date = datetime.combine(check_date, datetime.min.time())
    
    stockholm_date = check_date.astimezone(STOCKHOLM_TZ)
    return stockholm_date.replace(hour=9, minute=0, second=0, microsecond=0)


def get_market_close_time(check_date: Optional[Union[date, datetime]] = None) -> datetime:
    """
    Get market close time for a given date.
    
    Args:
        check_date (date or datetime, optional): Date to check. If None, uses today.
        
    Returns:
        datetime: Market close time in Stockholm timezone
    """
    if check_date is None:
        check_date = today_date_se()
    elif isinstance(check_date, date):
        check_date = datetime.combine(check_date, datetime.min.time())
    
    stockholm_date = check_date.astimezone(STOCKHOLM_TZ)
    return stockholm_date.replace(hour=17, minute=30, second=0, microsecond=0)


def time_until_market_open(check_time: Optional[datetime] = None) -> Optional[timedelta]:
    """
    Calculate time until market opens.
    
    Args:
        check_time (datetime, optional): Current time. If None, uses current time.
        
    Returns:
        timedelta or None: Time until market opens, or None if market is already open
    """
    if check_time is None:
        check_time = now_se()
    
    stockholm_time = check_time.astimezone(STOCKHOLM_TZ)
    
    # If market is already open, return None
    if is_market_hours(stockholm_time):
        return None
    
    # Get next market open time
    next_open = get_market_open_time(stockholm_time)
    
    # If today's market is closed, get tomorrow's
    if stockholm_time > next_open:
        next_open = get_market_open_time(get_next_trading_day(stockholm_time))
    
    return next_open - stockholm_time


def time_since_market_close(check_time: Optional[datetime] = None) -> Optional[timedelta]:
    """
    Calculate time since market closed.
    
    Args:
        check_time (datetime, optional): Current time. If None, uses current time.
        
    Returns:
        timedelta or None: Time since market closed, or None if market is still open
    """
    if check_time is None:
        check_time = now_se()
    
    stockholm_time = check_time.astimezone(STOCKHOLM_TZ)
    
    # If market is still open, return None
    if is_market_hours(stockholm_time):
        return None
    
    # Get today's market close time
    today_close = get_market_close_time(stockholm_time)
    
    # If market hasn't opened today, get yesterday's close
    if stockholm_time < today_close:
        yesterday = get_previous_trading_day(stockholm_time)
        today_close = get_market_close_time(yesterday)
    
    return stockholm_time - today_close


def format_stockholm_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """
    Format a datetime in Stockholm timezone.
    
    Args:
        dt (datetime): Datetime to format
        format_str (str): Format string for output
        
    Returns:
        str: Formatted datetime string
    """
    stockholm_dt = dt.astimezone(STOCKHOLM_TZ)
    return stockholm_dt.strftime(format_str)


def format_duration(duration: timedelta) -> str:
    """
    Format a timedelta into a human-readable string.
    
    Args:
        duration (timedelta): Duration to format
        
    Returns:
        str: Formatted duration string
    """
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h"


def get_swedish_holidays(year: int) -> list[date]:
    """
    Get Swedish holidays for a specific year.
    
    TODO: Implement proper Swedish holiday calculation including:
    - Easter and related holidays (varies by year)
    - Midsummer Eve (Friday before June 21)
    - All Saints' Day (Saturday between October 31 and November 6)
    
    Args:
        year (int): Year to get holidays for
        
    Returns:
        list[date]: List of holiday dates
    """
    holidays = [
        # Fixed holidays
        date(year, 1, 1),   # New Year's Day
        date(year, 1, 6),   # Epiphany
        date(year, 5, 1),   # May Day
        date(year, 6, 6),   # National Day
        date(year, 12, 24), # Christmas Eve
        date(year, 12, 25), # Christmas Day
        date(year, 12, 26), # Boxing Day
        date(year, 12, 31), # New Year's Eve
    ]
    
    # TODO: Add variable holidays like Easter, Midsummer, etc.
    
    return sorted(holidays) 