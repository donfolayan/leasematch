from datetime import datetime, timedelta

def default_scheduled_time(days=7):
    return datetime.now() + timedelta(days=days)