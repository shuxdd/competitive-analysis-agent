from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    格式化日期时间。

    Args:
        dt: datetime 对象，默认为当前时间
        format_str: 格式字符串

    Returns:
        格式化后的日期字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def get_current_timestamp() -> str:
    """
    获取当前时间戳（ISO 格式）。

    Returns:
        ISO 格式的时间戳字符串
    """
    return datetime.now().isoformat()
