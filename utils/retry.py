"""
重试工具
========

为LLM调用和网络请求提供统一的重试逻辑。
使用tenacity实现指数退避策略。
"""

import logging
from typing import Any, Callable, Awaitable

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    AsyncRetrying,
)

logger = logging.getLogger(__name__)

# 可重试的LLM错误
_LLM_RETRYABLE_ERRORS = []

# 可重试的网络错误
_NETWORK_RETRYABLE_ERRORS = []

try:
    import openai
    _LLM_RETRYABLE_ERRORS.extend([
        openai.APITimeoutError,
        openai.APIConnectionError,
        openai.RateLimitError,
    ])
    # 5xx 状态码的 API 错误需要特殊处理
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

try:
    import httpx
    _NETWORK_RETRYABLE_ERRORS.extend([
        httpx.TimeoutException,
        httpx.ConnectError,
    ])
except ImportError:
    pass

try:
    import requests.exceptions
    _NETWORK_RETRYABLE_ERRORS.extend([
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ])
except ImportError:
    pass

# 所有可重试的错误类型
ALL_RETRYABLE_ERRORS = tuple(_LLM_RETRYABLE_ERRORS + _NETWORK_RETRYABLE_ERRORS)


def _is_retryable_status_error(exc: Exception) -> bool:
    """判断是否为可重试的HTTP状态错误（5xx）"""
    if _HAS_OPENAI and isinstance(exc, openai.APIStatusError):
        return exc.status_code >= 500
    return False


def _should_retry(exc: Exception) -> bool:
    """判断异常是否应该重试"""
    if isinstance(exc, ALL_RETRYABLE_ERRORS):
        return True
    return _is_retryable_status_error(exc)


def retry_llm(func: Callable) -> Callable:
    """
    LLM调用重试装饰器

    最多重试3次，指数退避（2-30秒）。
    重试：超时、连接错误、限流、5xx错误。
    """
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=_should_retry,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)


def retry_network(func: Callable) -> Callable:
    """
    网络请求重试装饰器

    最多重试3次，指数退避（2-30秒）。
    重试：超时、连接错误。
    """
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(tuple(_NETWORK_RETRYABLE_ERRORS)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )(func)


async def retry_async(
    coro_factory: Callable[[], Awaitable[Any]],
    max_attempts: int = 3,
) -> Any:
    """
    异步调用重试包装器

    用于在节点内部对单个异步调用添加重试逻辑。
    每次重试会重新创建协程（通过 coro_factory）。

    Args:
        coro_factory: 返回协程的工厂函数
        max_attempts: 最大尝试次数

    Returns:
        异步调用的返回值
    """
    retrying = AsyncRetrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=_should_retry,
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )

    async for attempt in retrying:
        with attempt:
            return await coro_factory()
