"""
LLM工厂
=======

创建和管理LLM实例。
"""

import httpx
from langchain_openai import ChatOpenAI
from config.settings import settings


def create_llm(temperature: float = 0.7, max_tokens: int = 4096) -> ChatOpenAI:
    """
    创建LLM实例

    Args:
        temperature: 温度参数
        max_tokens: 最大token数

    Returns:
        ChatOpenAI实例
    """
    # 自定义 httpx 客户端，避免 latin-1 编码错误
    http_client = httpx.Client(
        timeout=120,
        follow_redirects=True,
        limits=httpx.Limits(max_keepalive_connections=5),
    )

    return ChatOpenAI(
        model=settings.default_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=temperature,
        max_tokens=max_tokens,
        http_client=http_client,
    )
