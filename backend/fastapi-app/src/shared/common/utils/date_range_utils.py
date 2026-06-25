from datetime import date, datetime, timedelta
import calendar

def get_current_month_date_range():
    """Returns the start and end dates for the current month."""
    today = date.today()
    start_date = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day)
    return start_date, end_date

def get_date_range(date_from: date = None, date_to: date = None):
    """Returns a validated date range."""
    if not date_from and not date_to:
        return get_current_month_date_range()
    
    if date_from and not date_to:
        date_to = date.today()
        
    if not date_from and date_to:
        date_from = date_to.replace(day=1)
        
    return date_from, date_to
