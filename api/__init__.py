"""
FastAPI 接口层
==============

提供竞品分析系统的 REST API 接口。
"""

from .app import create_app

__all__ = ["create_app"]
