"""
路由注册
========

注册所有路由到 FastAPI 应用。
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .competitors import router as competitors_router
from .analysis import router as analysis_router
from .reports import router as reports_router
from .qa import router as qa_router


def register_routers(app):
    """注册所有路由"""
    app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
    app.include_router(competitors_router, prefix="/api/competitors", tags=["竞品管理"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["分析任务"])
    app.include_router(reports_router, prefix="/api/reports", tags=["报告管理"])
    app.include_router(qa_router, prefix="/api/qa", tags=["智能问答"])
