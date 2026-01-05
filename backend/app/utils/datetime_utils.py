"""日期时间工具函数"""
from datetime import datetime, timezone, timedelta


def get_beijing_time() -> datetime:
    """
    获取北京时间（UTC+8）
    
    Returns:
        datetime: 当前北京时间
    """
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz)


def get_beijing_date_str() -> str:
    """
    获取北京时间的日期字符串（YYYY-MM-DD格式）
    
    Returns:
        str: 格式化的日期字符串
    """
    return get_beijing_time().strftime('%Y-%m-%d')


def get_beijing_datetime_str() -> str:
    """
    获取北京时间的日期时间字符串（YYYY-MM-DD HH:MM:SS格式）
    
    Returns:
        str: 格式化的日期时间字符串
    """
    return get_beijing_time().strftime('%Y-%m-%d %H:%M:%S')
