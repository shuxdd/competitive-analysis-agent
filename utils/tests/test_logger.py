import logging
from unittest.mock import patch

import pytest

from utils.logger import setup_logger, get_logger, _configured_loggers


@pytest.fixture(autouse=True)
def reset_configured_loggers():
    """在每个测试前重置 _configured_loggers，防止测试间干扰。"""
    _configured_loggers.clear()
    yield
    _configured_loggers.clear()


class TestSetupLogger:
    """setup_logger 函数测试"""

    def test_setup_logger_returns_logger(self):
        """测试返回正确的 Logger 实例"""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logger_with_level(self):
        """测试设置日志级别"""
        logger = setup_logger("test_debug", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_setup_logger_has_handlers(self):
        """测试日志记录器有处理器"""
        logger = setup_logger("test_handlers")
        assert len(logger.handlers) > 0

    def test_setup_logger_format(self):
        """测试日志格式"""
        logger = setup_logger("test_format")
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_setup_logger_no_duplicate_handlers(self):
        """测试重复调用不会添加重复处理器"""
        logger = setup_logger("test_no_dup")
        handler_count = len(logger.handlers)
        assert handler_count > 0

        # 再次调用，处理器数量不应增加
        logger2 = setup_logger("test_no_dup")
        assert logger2 is logger
        assert len(logger.handlers) == handler_count

    def test_setup_logger_file_handler_failure(self):
        """测试文件处理器创建失败时回退到仅控制台"""
        with patch("utils.logger.Path.mkdir", side_effect=OSError("权限不足")):
            logger = setup_logger("test_file_fail")
            # 应该仍然有控制台处理器
            assert len(logger.handlers) >= 1
            # 确认没有 FileHandler
            file_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) == 0


class TestGetLogger:
    """get_logger 函数测试"""

    def test_get_logger_returns_logger(self):
        """测试返回正确的 Logger 实例"""
        logger = get_logger("test_get")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_same_instance(self):
        """测试相同名称返回相同实例"""
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        assert logger1 is logger2

    def test_get_logger_auto_setup(self):
        """测试自动配置"""
        logger = get_logger("test_auto")
        assert len(logger.handlers) > 0
