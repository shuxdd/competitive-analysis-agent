import logging
import os
import tempfile
from utils.logger import setup_logger, get_logger


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
