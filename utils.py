from datetime import datetime
import pytz

# Get current time in IST
def get_ist_now():
    """Get current time in Indian Standard Time (IST)"""
    utc_now = datetime.utcnow()
    ist_timezone = pytz.timezone('Asia/Kolkata')
    return utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

# Format IST timestamp (if needed for presentation)
def format_ist_timestamp(timestamp):
    """Format a timezone-aware timestamp to IST string format"""
    if not timestamp.tzinfo:
        # If the timestamp doesn't have timezone info, assume UTC
        timestamp = timestamp.replace(tzinfo=pytz.utc)
    
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = timestamp.astimezone(ist_timezone)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S %Z") 