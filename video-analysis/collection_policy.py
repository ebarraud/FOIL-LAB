"""Provider stop policy shared by collection entry points; no paid fallback."""
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

def stop_status(code):
    return code in (401,403,429) or code>=500

def next_allowed(value, now=None):
    now=now or datetime.now(timezone.utc)
    try:
        seconds=int(value)
        if seconds>=0:return now+timedelta(seconds=seconds)
    except (ValueError,TypeError):pass
    try:
        date=parsedate_to_datetime(value)
        if date.tzinfo is None:date=date.replace(tzinfo=timezone.utc)
        return max(date,now)
    except (ValueError,TypeError,OverflowError):
        return now+timedelta(hours=1)
