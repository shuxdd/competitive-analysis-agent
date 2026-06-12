from datetime import datetime
from unittest.mock import patch
from utils.date_utils import format_datetime, get_current_timestamp


class TestFormatDatetime:
    """format_datetime 函数测试"""

    def test_format_default(self):
        """测试默认格式"""
        dt = datetime(2026, 6, 12, 14, 30)
        result = format_datetime(dt)
        assert result == "2026-06-12 14:30"

    def test_format_custom(self):
        """测试自定义格式"""
        dt = datetime(2026, 6, 12, 14, 30, 0)
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2026/06/12"

    def test_format_none_uses_current(self):
        """测试 None 使用当前时间"""
        with patch("utils.date_utils.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 0, 0)
            mock_dt.strftime = datetime.strftime
            result = format_datetime()
            assert "2026-01-01" in result


class TestGetCurrentTimestamp:
    """get_current_timestamp 函数测试"""

    def test_iso_format(self):
        """测试 ISO 格式"""
        result = get_current_timestamp()
        assert isinstance(result, str)
        # 验证结果可被 datetime.fromisoformat 解析
        parsed = datetime.fromisoformat(result)
        assert isinstance(parsed, datetime)
