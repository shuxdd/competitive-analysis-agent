"""
配置模块
========

管理全局配置、环境变量和Prompt模板。
"""

from .settings import settings
from .prompts import EXTRACTION_PROMPT, SWOT_PROMPT, REPORT_PROMPT, PLANNING_PROMPT, QA_PROMPT

__all__ = [
    "settings",
    "EXTRACTION_PROMPT",
    "SWOT_PROMPT",
    "REPORT_PROMPT",
    "PLANNING_PROMPT",
    "QA_PROMPT",
]
