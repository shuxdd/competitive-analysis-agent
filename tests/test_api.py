"""
API 模块测试
============

测试 FastAPI 接口功能。
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch


# ==================== 数据库层测试 ====================

class TestDatabase:
    """数据库模块测试"""

    def test_orm_models_exist(self):
        """测试 ORM 模型定义存在"""
        from api.database import CompetitorORM, AnalysisTaskORM, ReportORM

        assert CompetitorORM.__tablename__ == "competitors"
        assert AnalysisTaskORM.__tablename__ == "analysis_tasks"
        assert ReportORM.__tablename__ == "reports"

    def test_competitor_orm_columns(self):
        """测试竞品表字段"""
        from api.database import CompetitorORM

        columns = {c.name for c in CompetitorORM.__table__.columns}
        expected = {"id", "name", "website", "industry", "tags", "notes", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_analysis_task_orm_columns(self):
        """测试分析任务表字段"""
        from api.database import AnalysisTaskORM

        columns = {c.name for c in AnalysisTaskORM.__table__.columns}
        expected = {"id", "competitors", "analysis_type", "dimensions", "my_product",
                    "status", "result", "error_message", "created_at", "completed_at"}
        assert expected.issubset(columns)

    def test_report_orm_columns(self):
        """测试报告表字段"""
        from api.database import ReportORM

        columns = {c.name for c in ReportORM.__table__.columns}
        expected = {"id", "analysis_id", "title", "report_type", "format", "content", "file_path", "created_at"}
        assert expected.issubset(columns)


# ==================== Schema 测试 ====================

class TestSchemas:
    """API Schema 测试"""

    def test_competitor_response_schema(self):
        """测试竞品响应 Schema"""
        from api.schemas import CompetitorResponse

        data = {
            "id": "test-id",
            "name": "竞品A",
            "website": "https://example.com",
            "industry": "SaaS",
            "tags": ["AI"],
            "notes": None,
            "created_at": "2026-06-12T00:00:00",
            "updated_at": "2026-06-12T00:00:00",
        }
        resp = CompetitorResponse(**data)
        assert resp.id == "test-id"
        assert resp.name == "竞品A"

    def test_analysis_submit_response(self):
        """测试分析提交响应 Schema"""
        from api.schemas import AnalysisSubmitResponse

        resp = AnalysisSubmitResponse(
            task_id="task-123",
            status="pending",
            message="分析任务已提交",
        )
        assert resp.task_id == "task-123"
        assert resp.status == "pending"

    def test_api_response_wrapper(self):
        """测试统一响应包装"""
        from api.schemas import ApiResponse

        resp = ApiResponse(code=200, data={"key": "value"}, message="success")
        assert resp.code == 200
        assert resp.data["key"] == "value"

    def test_qa_request_schema(self):
        """测试问答请求 Schema"""
        from api.schemas import QARequest

        req = QARequest(question="Notion 的定价是什么？")
        assert req.question == "Notion 的定价是什么？"
        assert req.competitors is None

    def test_qa_response_schema(self):
        """测试问答响应 Schema"""
        from api.schemas import QAResponse

        resp = QAResponse(
            answer="Notion 提供免费版和付费版",
            sources=["竞品知识库"],
        )
        assert "Notion" in resp.answer
        assert len(resp.sources) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
