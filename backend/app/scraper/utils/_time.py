from datetime import datetime
from datetime import timedelta

def parse_date(date_str):
    """
    given a string date mm-dd HH:MM, turn it into a 
    datetime object
    """
    try:
        date_obj = datetime.strptime(date_str, "%m-%d %H:%M")
        return date_obj.replace(year=datetime.now().year)
    except ValueError:
        print(f"Invalid datetime '{date_str}'; expected format: mm-dd hh:mm")
        return None

def is_within_range(dt, delta=timedelta(3)):
    """
    check if a date (dt) is within a certain range (delta)
    which is 3 days by default
    """
    now = datetime.now()
    return dt >= now - delta

def fmt_date(date: str):
    """
    extract "mm-dd hh:mm" str date format from Xueqiu 
    dates provided
    """
    def fmt_day(time: datetime):
        return f"{str(time.month).rjust(2, '0')}-{str(time.day).rjust(2, '0')}"
    
    def fmt_time(time: datetime):
        return f"{str(time.hour).rjust(2, '0')}:{str(time.minute).rjust(2, '0')}"

    if date.startswith("修改于"):
        date = date[3:]
    
    if date.endswith("小时前"):
        hours_ago = int(date[:len(date)-3])
        time = datetime.now() - timedelta(hours=hours_ago)
        date = f"{fmt_day(time)} {fmt_time(time)}"
    elif date.endswith("分钟前"):
        minutes_ago = int(date[:len(date)-3])
        time = datetime.now() - timedelta(minutes=minutes_ago)
        date = f"{fmt_day(time)} {fmt_time(time)}"
    else:
        time = datetime.now()
        yesterday = time - timedelta(1)
        date = date.replace("昨天", fmt_day(yesterday))

    return date
