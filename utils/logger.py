import logging
import os
from pathlib import Path


# 已配置的日志记录器缓存
_configured_loggers: set[str] = set()


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    配置日志记录器。

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if name in _configured_loggers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / "app.log", encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # 文件处理器创建失败时只使用控制台
        pass

    _configured_loggers.add(name)
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器（如果未配置则自动配置）。

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    if name not in _configured_loggers:
        return setup_logger(name)
    return logging.getLogger(name)
