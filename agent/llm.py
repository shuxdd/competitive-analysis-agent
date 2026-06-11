"""
LLM工厂
=======

创建和管理LLM实例。
"""

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
    return ChatOpenAI(
        model=settings.default_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=temperature,
        max_tokens=max_tokens,
    )
