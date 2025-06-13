import hashlib
from datetime import datetime, timedelta
import re

def generate_article_id(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

def parse_relative_time(time_str):
    now = datetime.now()
    time_str = time_str.lower()

    if "minute" in time_str:
        match = re.search(r'(\d+)\s+minute', time_str)
        if match:
            minutes = int(match.group(1))
            return now - timedelta(minutes=minutes)
    elif "hour" in time_str:
        match = re.search(r'(\d+)\s+hour', time_str)
        if match:
            hours = int(match.group(1))
            return now - timedelta(hours=hours)
    elif "day" in time_str:
        match = re.search(r'(\d+)\s+day', time_str)
        if match:
            days = int(match.group(1))
            return now - timedelta(days=days)
    elif "week" in time_str:
        match = re.search(r'(\d+)\s+week', time_str)
        if match:
            weeks = int(match.group(1))
            return now - timedelta(weeks=weeks)
    elif "month" in time_str:
        match = re.search(r'(\d+)\s+month', time_str)
        if match:
            months = int(match.group(1))
           
            return now - timedelta(days=months * 30)
    elif "year" in time_str:
        match = re.search(r'(\d+)\s+year', time_str)
        if match:
            years = int(match.group(1))
          
            return now - timedelta(days=years * 365)
    elif "just now" in time_str or "ago" not in time_str:
        return now 
    
    return None 

def format_relative_time(dt_object):
   
    now = datetime.now()
    diff = now - dt_object

    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = minutes // 24
    weeks = days // 7
    months = days // 30 
    years = days // 365

    if seconds < 60:
        return "just now"
    elif minutes < 60:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif hours < 24:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif days < 7:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif weeks < 4:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif months < 12:
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        return f"{years} year{'s' if years > 1 else ''} ago"
