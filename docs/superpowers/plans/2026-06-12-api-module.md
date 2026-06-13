# API 模块实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为竞品分析 Agent 开发 FastAPI 后端接口层，支持竞品 CRUD、异步分析任务、报告管理和智能问答。

**Architecture:** 模块化路由结构，4个独立 router 文件 + database/schemas 支撑层。SQLite + async SQLAlchemy 持久化，异步任务用 asyncio.create_task 启动、内存字典追踪。

**Tech Stack:** FastAPI, SQLAlchemy (async), aiosqlite, Pydantic V2, httpx (测试)

---

## 文件结构

```
api/
├── app.py              # FastAPI 应用入口、中间件、异常处理、生命周期事件
├── database.py         # 异步引擎、Session 工厂、ORM 模型、依赖注入
├── schemas.py          # API 请求/响应 Schema
├── routers/
│   ├── __init__.py     # 路由注册
│   ├── competitors.py  # 竞品 CRUD
│   ├── analysis.py     # 分析任务（提交/查询/取消）
│   ├── reports.py      # 报告管理
│   └── qa.py           # 智能问答
tests/
└── test_api.py         # API 集成测试
```

---

### Task 1: 安装依赖

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: 添加 aiosqlite 依赖**

在 `requirements.txt` 的 `# 后端框架` 区块添加 `aiosqlite`:

```
# 后端框架
fastapi>=0.136.3
uvicorn[standard]>=0.30.0
pydantic>=2.8.0
pydantic-settings>=2.5.0
aiosqlite>=0.20.0
```

- [ ] **Step 2: 安装依赖**

Run: `pip install aiosqlite`
Expected: Successfully installed aiosqlite

- [ ] **Step 3: 验证安装**

Run: `python -c "import aiosqlite; print('aiosqlite OK')"`
Expected: `aiosqlite OK`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "feat: 添加 aiosqlite 异步 SQLite 驱动依赖"
```

---

### Task 2: 数据库模块 (`api/database.py`)

**Files:**
- Create: `api/database.py`
- Test: `tests/test_api.py` (database 部分)

- [ ] **Step 1: 编写数据库模块测试**

创建 `tests/test_api.py`，先写数据库相关测试：

```python
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestDatabase -v`
Expected: FAIL (ModuleNotFoundError: No module named 'api.database')

- [ ] **Step 3: 实现数据库模块**

创建 `api/database.py`：

```python
"""
数据库模块
==========

异步 SQLAlchemy 引擎、Session 和 ORM 模型定义。
"""

import uuid
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


# 异步引擎（默认使用 SQLite）
DATABASE_URL = f"sqlite+aiosqlite:///{settings.chroma_persist_dir}/../app.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


class CompetitorORM(Base):
    """竞品 ORM 模型"""
    __tablename__ = "competitors"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AnalysisTaskORM(Base):
    """分析任务 ORM 模型"""
    __tablename__ = "analysis_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    competitors = Column(JSON, nullable=False)
    analysis_type = Column(String, default="standard")
    dimensions = Column(JSON, default=list)
    my_product = Column(String, nullable=True)
    status = Column(String, default="pending")
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)


class ReportORM(Base):
    """报告 ORM 模型"""
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    report_type = Column(String, default="standard")
    format = Column(String, default="markdown")
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


async def init_db():
    """初始化数据库（创建表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入：获取数据库 session"""
    async with async_session() as session:
        yield session
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestDatabase -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add api/database.py tests/test_api.py
git commit -m "feat: 添加数据库模块 - 异步 SQLAlchemy ORM 模型定义"
```

---

### Task 3: API Schema 模块 (`api/schemas.py`)

**Files:**
- Create: `api/schemas.py`
- Modify: `tests/test_api.py` (添加 schema 测试)

- [ ] **Step 1: 编写 Schema 测试**

在 `tests/test_api.py` 中追加：

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestSchemas -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: 实现 Schema 模块**

创建 `api/schemas.py`：

```python
"""
API Schema
==========

定义 API 请求/响应的 Pydantic 模型。
复用 models/ 中已有模型，添加 API 专用的包装模型。
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 通用响应 ====================

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = 200
    data: Any = None
    message: str = "success"


class PaginatedResponse(BaseModel):
    """分页响应"""
    code: int = 200
    data: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    message: str = "success"


# ==================== 竞品 ====================

class CompetitorCreateRequest(BaseModel):
    """创建竞品请求"""
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None


class CompetitorUpdateRequest(BaseModel):
    """更新竞品请求"""
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CompetitorResponse(BaseModel):
    """竞品响应"""
    id: str
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ==================== 分析任务 ====================

class AnalysisSubmitRequest(BaseModel):
    """提交分析任务请求"""
    competitors: List[str]
    analysis_type: str = "standard"
    dimensions: List[str] = ["features", "pricing", "swot"]
    my_product: Optional[str] = None


class AnalysisSubmitResponse(BaseModel):
    """分析任务提交响应"""
    task_id: str
    status: str
    message: str


class AnalysisTaskResponse(BaseModel):
    """分析任务详情响应"""
    id: str
    competitors: List[str]
    analysis_type: str
    dimensions: List[str]
    my_product: Optional[str] = None
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


# ==================== 报告 ====================

class ReportResponse(BaseModel):
    """报告响应"""
    id: str
    analysis_id: str
    title: str
    report_type: str
    format: str
    content: str
    file_path: Optional[str] = None
    created_at: Optional[str] = None


# ==================== 智能问答 ====================

class QARequest(BaseModel):
    """问答请求"""
    question: str
    competitors: Optional[List[str]] = None


class QAResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: List[str] = []
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestSchemas -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add api/schemas.py tests/test_api.py
git commit -m "feat: 添加 API Schema 模块 - 请求/响应模型定义"
```

---

### Task 4: 竞品管理路由 (`api/routers/competitors.py`)

**Files:**
- Create: `api/routers/__init__.py`
- Create: `api/routers/competitors.py`
- Modify: `tests/test_api.py` (添加竞品 CRUD 测试)

- [ ] **Step 1: 编写竞品 CRUD 测试**

在 `tests/test_api.py` 中追加：

```python
# ==================== 竞品路由测试 ====================

@pytest_asyncio.fixture
async def test_app():
    """创建测试用 FastAPI 应用"""
    from api.app import create_app
    app = create_app()
    return app


@pytest_asyncio.fixture
async def client(test_app):
    """创建测试客户端"""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestCompetitorRoutes:
    """竞品路由测试"""

    @pytest.mark.asyncio
    async def test_create_competitor(self, client):
        """测试创建竞品"""
        resp = await client.post("/api/competitors", json={
            "name": "Notion",
            "website": "https://notion.so",
            "industry": "SaaS",
            "tags": ["笔记", "协作"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "Notion"

    @pytest.mark.asyncio
    async def test_list_competitors(self, client):
        """测试获取竞品列表"""
        # 先创建一个
        await client.post("/api/competitors", json={"name": "TestComp"})
        # 查询列表
        resp = await client.get("/api/competitors")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_competitor(self, client):
        """测试获取竞品详情"""
        create_resp = await client.post("/api/competitors", json={"name": "DetailComp"})
        comp_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/competitors/{comp_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "DetailComp"

    @pytest.mark.asyncio
    async def test_get_competitor_not_found(self, client):
        """测试获取不存在的竞品"""
        resp = await client.get("/api/competitors/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_competitor(self, client):
        """测试更新竞品"""
        create_resp = await client.post("/api/competitors", json={"name": "OldName"})
        comp_id = create_resp.json()["data"]["id"]

        resp = await client.put(f"/api/competitors/{comp_id}", json={"name": "NewName"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "NewName"

    @pytest.mark.asyncio
    async def test_delete_competitor(self, client):
        """测试删除竞品"""
        create_resp = await client.post("/api/competitors", json={"name": "ToDelete"})
        comp_id = create_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/competitors/{comp_id}")
        assert resp.status_code == 200

        # 确认已删除
        resp = await client.get(f"/api/competitors/{comp_id}")
        assert resp.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestCompetitorRoutes -v`
Expected: FAIL (import errors)

- [ ] **Step 3: 创建路由包初始化文件**

创建 `api/routers/__init__.py`：

```python
"""
路由注册
========

注册所有路由到 FastAPI 应用。
"""

from fastapi import APIRouter

from .competitors import router as competitors_router
from .analysis import router as analysis_router
from .reports import router as reports_router
from .qa import router as qa_router


def register_routers(app):
    """注册所有路由"""
    app.include_router(competitors_router, prefix="/api/competitors", tags=["竞品管理"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["分析任务"])
    app.include_router(reports_router, prefix="/api/reports", tags=["报告管理"])
    app.include_router(qa_router, prefix="/api/qa", tags=["智能问答"])
```

- [ ] **Step 4: 实现竞品路由**

创建 `api/routers/competitors.py`：

```python
"""
竞品管理路由
============

提供竞品的 CRUD 接口。
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import CompetitorORM, get_session
from api.schemas import (
    ApiResponse,
    CompetitorCreateRequest,
    CompetitorUpdateRequest,
    CompetitorResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _orm_to_response(orm: CompetitorORM) -> dict:
    """ORM 对象转响应字典"""
    return {
        "id": orm.id,
        "name": orm.name,
        "website": orm.website,
        "industry": orm.industry,
        "tags": orm.tags or [],
        "notes": orm.notes,
        "created_at": orm.created_at.isoformat() if orm.created_at else None,
        "updated_at": orm.updated_at.isoformat() if orm.updated_at else None,
    }


@router.get("")
async def list_competitors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    keyword: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取竞品列表"""
    query = select(CompetitorORM)

    if industry:
        query = query.where(CompetitorORM.industry == industry)
    if keyword:
        query = query.where(CompetitorORM.name.contains(keyword))

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    competitors = result.scalars().all()

    return {
        "code": 200,
        "data": [_orm_to_response(c) for c in competitors],
        "total": total,
        "page": page,
        "page_size": page_size,
        "message": "success",
    }


@router.post("")
async def create_competitor(
    req: CompetitorCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """创建竞品"""
    orm = CompetitorORM(
        name=req.name,
        website=req.website,
        industry=req.industry,
        tags=req.tags,
        notes=req.notes,
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)

    logger.info(f"创建竞品: {orm.name} (id={orm.id})")
    return {"code": 200, "data": _orm_to_response(orm), "message": "创建成功"}


@router.get("/{competitor_id}")
async def get_competitor(
    competitor_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取竞品详情"""
    result = await session.execute(
        select(CompetitorORM).where(CompetitorORM.id == competitor_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="竞品不存在")

    return {"code": 200, "data": _orm_to_response(orm), "message": "success"}


@router.put("/{competitor_id}")
async def update_competitor(
    competitor_id: str,
    req: CompetitorUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    """更新竞品"""
    result = await session.execute(
        select(CompetitorORM).where(CompetitorORM.id == competitor_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="竞品不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(orm, key, value)
    orm.updated_at = datetime.now()

    await session.commit()
    await session.refresh(orm)

    logger.info(f"更新竞品: {orm.id}")
    return {"code": 200, "data": _orm_to_response(orm), "message": "更新成功"}


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除竞品"""
    result = await session.execute(
        select(CompetitorORM).where(CompetitorORM.id == competitor_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="竞品不存在")

    await session.delete(orm)
    await session.commit()

    logger.info(f"删除竞品: {competitor_id}")
    return {"code": 200, "data": None, "message": "删除成功"}
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestCompetitorRoutes -v`
Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add api/routers/__init__.py api/routers/competitors.py tests/test_api.py
git commit -m "feat: 添加竞品管理路由 - CRUD 接口"
```

---

### Task 5: 分析任务路由 (`api/routers/analysis.py`)

**Files:**
- Create: `api/routers/analysis.py`
- Modify: `tests/test_api.py` (添加分析任务测试)

- [ ] **Step 1: 编写分析任务测试**

在 `tests/test_api.py` 中追加：

```python
# ==================== 分析任务路由测试 ====================

class TestAnalysisRoutes:
    """分析任务路由测试"""

    @pytest.mark.asyncio
    async def test_submit_analysis(self, client):
        """测试提交分析任务"""
        resp = await client.post("/api/analysis", json={
            "competitors": ["Notion", "Obsidian"],
            "analysis_type": "quick",
            "dimensions": ["features"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 200
        assert data["data"]["task_id"] is not None
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_tasks(self, client):
        """测试获取任务列表"""
        # 先提交一个
        await client.post("/api/analysis", json={
            "competitors": ["Test"],
        })
        resp = await client.get("/api/analysis")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_task(self, client):
        """测试获取任务详情"""
        submit_resp = await client.post("/api/analysis", json={
            "competitors": ["Notion"],
        })
        task_id = submit_resp.json()["data"]["task_id"]

        resp = await client.get(f"/api/analysis/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == task_id

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client):
        """测试获取不存在的任务"""
        resp = await client.get("/api/analysis/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task(self, client):
        """测试删除任务"""
        submit_resp = await client.post("/api/analysis", json={
            "competitors": ["Notion"],
        })
        task_id = submit_resp.json()["data"]["task_id"]

        resp = await client.delete(f"/api/analysis/{task_id}")
        assert resp.status_code == 200
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestAnalysisRoutes -v`
Expected: FAIL

- [ ] **Step 3: 实现分析任务路由**

创建 `api/routers/analysis.py`：

```python
"""
分析任务路由
============

提供分析任务的提交、查询、取消接口。
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import AnalysisTaskORM, ReportORM, get_session
from api.schemas import AnalysisSubmitRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# 运行中的任务追踪
_running_tasks: dict[str, asyncio.Task] = {}


def _orm_to_response(orm: AnalysisTaskORM) -> dict:
    """ORM 对象转响应字典"""
    return {
        "id": orm.id,
        "competitors": orm.competitors or [],
        "analysis_type": orm.analysis_type,
        "dimensions": orm.dimensions or [],
        "my_product": orm.my_product,
        "status": orm.status,
        "result": orm.result,
        "error_message": orm.error_message,
        "created_at": orm.created_at.isoformat() if orm.created_at else None,
        "completed_at": orm.completed_at.isoformat() if orm.completed_at else None,
    }


async def _run_analysis(task_id: str):
    """后台执行分析任务"""
    from api.database import async_session
    from agent.graph import create_analysis_graph

    async with async_session() as session:
        try:
            # 更新状态为 planning
            result = await session.execute(
                select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                return

            task.status = "planning"
            await session.commit()

            # 执行分析图
            graph = create_analysis_graph()
            task.status = "collecting"
            await session.commit()

            graph_result = await graph.ainvoke({
                "competitors": task.competitors,
                "analysis_type": task.analysis_type,
                "dimensions": task.dimensions or ["features", "pricing", "swot"],
                "my_product": task.my_product,
                "collection_plan": {},
                "raw_data": [],
                "extracted_info": [],
                "analysis_results": {},
                "report": "",
                "status": "collecting",
                "errors": [],
            })

            # 更新结果
            task.status = "completed"
            task.result = {
                "report": graph_result.get("report", ""),
                "analysis_results": graph_result.get("analysis_results", {}),
                "errors": graph_result.get("errors", []),
            }
            task.completed_at = datetime.now()
            await session.commit()

            # 自动保存报告
            if graph_result.get("report"):
                report_orm = ReportORM(
                    analysis_id=task_id,
                    title=f"竞品分析报告 - {', '.join(task.competitors)}",
                    report_type=task.analysis_type,
                    format="markdown",
                    content=graph_result["report"],
                )
                session.add(report_orm)
                await session.commit()

            logger.info(f"分析任务完成: {task_id}")

        except Exception as e:
            logger.error(f"分析任务失败: {task_id}, 错误: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            await session.commit()

        finally:
            _running_tasks.pop(task_id, None)


@router.post("")
async def submit_analysis(
    req: AnalysisSubmitRequest,
    session: AsyncSession = Depends(get_session),
):
    """提交分析任务"""
    orm = AnalysisTaskORM(
        competitors=req.competitors,
        analysis_type=req.analysis_type,
        dimensions=req.dimensions,
        my_product=req.my_product,
        status="pending",
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)

    # 启动后台任务
    task = asyncio.create_task(_run_analysis(orm.id))
    _running_tasks[orm.id] = task

    logger.info(f"提交分析任务: {orm.id}, 竞品: {req.competitors}")
    return {
        "code": 200,
        "data": {"task_id": orm.id, "status": "pending", "message": "分析任务已提交"},
        "message": "success",
    }


@router.get("")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取任务列表"""
    query = select(AnalysisTaskORM)

    if status:
        query = query.where(AnalysisTaskORM.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(AnalysisTaskORM.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    tasks = result.scalars().all()

    return {
        "code": 200,
        "data": [_orm_to_response(t) for t in tasks],
        "total": total,
        "page": page,
        "page_size": page_size,
        "message": "success",
    }


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取任务详情"""
    result = await session.execute(
        select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {"code": 200, "data": _orm_to_response(orm), "message": "success"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    """取消/删除任务"""
    result = await session.execute(
        select(AnalysisTaskORM).where(AnalysisTaskORM.id == task_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果任务正在运行，取消它
    if task_id in _running_tasks:
        _running_tasks[task_id].cancel()
        _running_tasks.pop(task_id, None)

    await session.delete(orm)
    await session.commit()

    logger.info(f"删除任务: {task_id}")
    return {"code": 200, "data": None, "message": "删除成功"}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestAnalysisRoutes -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add api/routers/analysis.py tests/test_api.py
git commit -m "feat: 添加分析任务路由 - 提交/查询/删除接口"
```

---

### Task 6: 报告管理路由 (`api/routers/reports.py`)

**Files:**
- Create: `api/routers/reports.py`
- Modify: `tests/test_api.py` (添加报告测试)

- [ ] **Step 1: 编写报告管理测试**

在 `tests/test_api.py` 中追加：

```python
# ==================== 报告路由测试 ====================

class TestReportRoutes:
    """报告路由测试"""

    @pytest.mark.asyncio
    async def test_list_reports_empty(self, client):
        """测试获取空报告列表"""
        resp = await client.get("/api/reports")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, client):
        """测试获取不存在的报告"""
        resp = await client.get("/api/reports/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_report_not_found(self, client):
        """测试删除不存在的报告"""
        resp = await client.delete("/api/reports/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_reports_with_data(self, client):
        """测试获取报告列表（有数据）"""
        # 直接通过数据库插入测试数据
        from api.database import async_session, ReportORM
        async with async_session() as session:
            report = ReportORM(
                analysis_id="test-analysis",
                title="测试报告",
                report_type="standard",
                format="markdown",
                content="# 测试报告内容",
            )
            session.add(report)
            await session.commit()

        resp = await client.get("/api/reports")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    @pytest.mark.asyncio
    async def test_export_report_not_found(self, client):
        """测试导出不存在的报告"""
        resp = await client.get("/api/reports/nonexistent/export")
        assert resp.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestReportRoutes -v`
Expected: FAIL

- [ ] **Step 3: 实现报告管理路由**

创建 `api/routers/reports.py`：

```python
"""
报告管理路由
============

提供报告的查询、导出、删除接口。
"""

import logging
from typing import Optional
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import ReportORM, get_session

logger = logging.getLogger(__name__)
router = APIRouter()


def _orm_to_response(orm: ReportORM) -> dict:
    """ORM 对象转响应字典"""
    return {
        "id": orm.id,
        "analysis_id": orm.analysis_id,
        "title": orm.title,
        "report_type": orm.report_type,
        "format": orm.format,
        "content": orm.content,
        "file_path": orm.file_path,
        "created_at": orm.created_at.isoformat() if orm.created_at else None,
    }


@router.get("")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    analysis_id: Optional[str] = None,
    report_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """获取报告列表"""
    query = select(ReportORM)

    if analysis_id:
        query = query.where(ReportORM.analysis_id == analysis_id)
    if report_type:
        query = query.where(ReportORM.report_type == report_type)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(ReportORM.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    reports = result.scalars().all()

    return {
        "code": 200,
        "data": [_orm_to_response(r) for r in reports],
        "total": total,
        "page": page,
        "page_size": page_size,
        "message": "success",
    }


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取报告详情"""
    result = await session.execute(
        select(ReportORM).where(ReportORM.id == report_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="报告不存在")

    return {"code": 200, "data": _orm_to_response(orm), "message": "success"}


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query("markdown", regex="^(markdown|html)$"),
    session: AsyncSession = Depends(get_session),
):
    """导出报告文件"""
    result = await session.execute(
        select(ReportORM).where(ReportORM.id == report_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="报告不存在")

    content = orm.content
    filename = f"{orm.title}"

    if format == "html":
        from report.generator import ReportGenerator
        generator = ReportGenerator()
        html_content = generator._markdown_to_html(content)
        buffer = BytesIO(html_content.encode("utf-8"))
        media_type = "text/html"
        filename = f"{filename}.html"
    else:
        buffer = BytesIO(content.encode("utf-8"))
        media_type = "text/markdown"
        filename = f"{filename}.md"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除报告"""
    result = await session.execute(
        select(ReportORM).where(ReportORM.id == report_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        raise HTTPException(status_code=404, detail="报告不存在")

    await session.delete(orm)
    await session.commit()

    logger.info(f"删除报告: {report_id}")
    return {"code": 200, "data": None, "message": "删除成功"}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestReportRoutes -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add api/routers/reports.py tests/test_api.py
git commit -m "feat: 添加报告管理路由 - 查询/导出/删除接口"
```

---

### Task 7: 智能问答路由 (`api/routers/qa.py`)

**Files:**
- Create: `api/routers/qa.py`
- Modify: `tests/test_api.py` (添加问答测试)

- [ ] **Step 1: 编写智能问答测试**

在 `tests/test_api.py` 中追加：

```python
# ==================== 智能问答路由测试 ====================

class TestQARoutes:
    """智能问答路由测试"""

    @pytest.mark.asyncio
    async def test_qa_submit(self, client):
        """测试提交问答"""
        with patch("api.routers.qa._get_knowledge_context") as mock_ctx, \
             patch("api.routers.qa._ask_llm") as mock_llm:
            mock_ctx.return_value = "Notion 是一款笔记协作工具"
            mock_llm.return_value = "Notion 是一款全能型笔记和协作工具，支持文档、数据库、看板等功能。"

            resp = await client.post("/api/qa", json={
                "question": "Notion 是什么？",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["code"] == 200
            assert len(data["data"]["answer"]) > 0

    @pytest.mark.asyncio
    async def test_qa_with_competitors(self, client):
        """测试指定竞品的问答"""
        with patch("api.routers.qa._get_knowledge_context") as mock_ctx, \
             patch("api.routers.qa._ask_llm") as mock_llm:
            mock_ctx.return_value = "Notion 定价信息"
            mock_llm.return_value = "Notion 提供免费版、Plus 版 $8/月、Business 版 $15/月。"

            resp = await client.post("/api/qa", json={
                "question": "Notion 的定价是什么？",
                "competitors": ["Notion"],
            })
            assert resp.status_code == 200
            assert "Notion" in resp.json()["data"]["answer"]

    @pytest.mark.asyncio
    async def test_qa_empty_question(self, client):
        """测试空问题"""
        resp = await client.post("/api/qa", json={"question": ""})
        assert resp.status_code == 422  # Pydantic 验证失败
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestQARoutes -v`
Expected: FAIL

- [ ] **Step 3: 实现智能问答路由**

创建 `api/routers/qa.py`：

```python
"""
智能问答路由
============

基于知识库的智能问答接口。
"""

import logging
from typing import List, Optional

from fastapi import APIRouter
from sqlalchemy import select

from api.database import async_session, CompetitorORM
from api.schemas import QARequest
from agent.llm import create_llm
from knowledge.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_knowledge_context(question: str, competitors: Optional[List[str]] = None) -> str:
    """从知识库获取上下文"""
    try:
        kb = KnowledgeBase()

        if competitors:
            # 按竞品名称搜索
            all_context = []
            for name in competitors:
                results = kb.search_competitors(query=question, top_k=3)
                for r in results:
                    all_context.append(r.get("document", ""))
            return "\n\n".join(all_context[:5])
        else:
            results = kb.search_competitors(query=question, top_k=5)
            return "\n\n".join(r.get("document", "") for r in results)
    except Exception as e:
        logger.warning(f"知识库查询失败: {e}")
        return ""


async def _ask_llm(question: str, context: str) -> str:
    """调用 LLM 回答问题"""
    prompt = f"""基于以下竞品知识库信息，回答用户的问题。如果知识库中没有相关信息，请说明。

知识库信息：
{context if context else "暂无相关信息"}

用户问题：{question}

请用中文回答，简洁准确："""

    llm = create_llm(temperature=0.3, max_tokens=2048)
    response = await llm.ainvoke(prompt)
    return response.content


@router.post("")
async def ask_question(req: QARequest):
    """提交智能问答"""
    # 获取知识库上下文
    context = _get_knowledge_context(req.question, req.competitors)

    # 调用 LLM
    answer = await _ask_llm(req.question, context)

    sources = []
    if context:
        sources.append("竞品知识库")
    if not context:
        sources.append("LLM 通用知识")

    logger.info(f"问答完成: {req.question[:50]}...")
    return {
        "code": 200,
        "data": {"answer": answer, "sources": sources},
        "message": "success",
    }
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestQARoutes -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add api/routers/qa.py tests/test_api.py
git commit -m "feat: 添加智能问答路由 - 基于知识库的问答接口"
```

---

### Task 8: FastAPI 应用入口 (`api/app.py`)

**Files:**
- Create: `api/app.py`
- Modify: `tests/test_api.py` (添加应用级测试)

- [ ] **Step 1: 编写应用级测试**

在 `tests/test_api.py` 中追加：

```python
# ==================== 应用级测试 ====================

class TestApp:
    """应用级测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查端点"""
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_root(self, client):
        """测试根路径"""
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "竞品分析" in resp.json()["message"]

    @pytest.mark.asyncio
    async def test_404_handler(self, client):
        """测试 404 处理"""
        resp = await client.get("/nonexistent-path")
        assert resp.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py::TestApp -v`
Expected: FAIL

- [ ] **Step 3: 实现 FastAPI 应用**

创建 `api/app.py`：

```python
"""
FastAPI 应用入口
================

创建和配置 FastAPI 应用实例。
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.database import init_db
from api.routers import register_routers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    yield
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title="智能竞品分析 Agent API",
        description="基于 LLM 的自动化竞品分析系统后端接口",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS 中间件（前后端分离需要）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    register_routers(app)

    # 健康检查
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # 根路径
    @app.get("/")
    async def root():
        return {"message": "智能竞品分析 Agent API", "version": "0.1.0"}

    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"code": 500, "data": None, "message": f"服务器内部错误: {str(exc)}"},
        )

    return app


# 应用实例（uvicorn 入口）
app = create_app()
```

- [ ] **Step 4: 更新路由注册**

更新 `api/routers/__init__.py`，确保路由注册正确（如果 Task 4 已创建，检查内容是否完整）：

```python
"""
路由注册
========

注册所有路由到 FastAPI 应用。
"""

from fastapi import APIRouter

from .competitors import router as competitors_router
from .analysis import router as analysis_router
from .reports import router as reports_router
from .qa import router as qa_router


def register_routers(app):
    """注册所有路由"""
    app.include_router(competitors_router, prefix="/api/competitors", tags=["竞品管理"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["分析任务"])
    app.include_router(reports_router, prefix="/api/reports", tags=["报告管理"])
    app.include_router(qa_router, prefix="/api/qa", tags=["智能问答"])
```

- [ ] **Step 5: 运行全部测试确认通过**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_api.py -v`
Expected: All passed

- [ ] **Step 6: Commit**

```bash
git add api/app.py api/routers/__init__.py tests/test_api.py
git commit -m "feat: 添加 FastAPI 应用入口 - 生命周期、CORS、异常处理"
```

---

### Task 9: 更新 `api/__init__.py` 和文档

**Files:**
- Modify: `api/__init__.py`
- Modify: `CLAUDE.md`
- Modify: `DEVELOPMENT_PROGRESS.md`

- [ ] **Step 1: 更新 api 模块导出**

更新 `api/__init__.py`：

```python
"""
FastAPI 接口层
==============

提供竞品分析系统的 REST API 接口。
"""

from .app import create_app

__all__ = ["create_app"]
```

- [ ] **Step 2: 更新 CLAUDE.md**

将模块状态表中的 `api/` 从 `⏳ 待开发` 改为 `✅ 完成`，并添加 API 相关命令：

```markdown
## 常用命令

```bash
# 启动API服务
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```
```

- [ ] **Step 3: 更新 DEVELOPMENT_PROGRESS.md**

在末尾添加 API 模块开发记录：

```markdown
### 7. API接口模块 (api/) ✅

**完成时间**: 2026-06-12

**主要功能**:
- FastAPI应用 (app.py) - 生命周期管理、CORS、全局异常处理
- 数据库模块 (database.py) - 异步 SQLAlchemy ORM、3张表（竞品/任务/报告）
- Schema模块 (schemas.py) - 请求/响应 Pydantic 模型
- 竞品管理路由 (routers/competitors.py) - CRUD 接口
- 分析任务路由 (routers/analysis.py) - 提交/查询/删除接口
- 报告管理路由 (routers/reports.py) - 查询/导出/删除接口
- 智能问答路由 (routers/qa.py) - 基于知识库的问答接口

**文件**:
- `api/app.py` - FastAPI应用入口
- `api/database.py` - 数据库模块
- `api/schemas.py` - API Schema
- `api/routers/__init__.py` - 路由注册
- `api/routers/competitors.py` - 竞品管理路由
- `api/routers/analysis.py` - 分析任务路由
- `api/routers/reports.py` - 报告管理路由
- `api/routers/qa.py` - 智能问答路由
- `tests/test_api.py` - 单元测试

**测试结果**: ✅ 全部通过
```

- [ ] **Step 4: 运行全量测试确认没有破坏已有功能**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && python -m pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py -v`
Expected: All passed

- [ ] **Step 5: Commit**

```bash
git add api/__init__.py CLAUDE.md DEVELOPMENT_PROGRESS.md
git commit -m "docs: 更新文档 - API模块完成状态"
```

---

### Task 10: 验证服务启动

- [ ] **Step 1: 启动 API 服务**

Run: `cd "D:/Desktop/新建文件夹/competitive-analysis-agent" && timeout 10 uvicorn api.app:app --host 0.0.0.0 --port 8000 || true`
Expected: 服务启动成功，显示 "Uvicorn running on http://0.0.0.0:8000"

- [ ] **Step 2: 测试健康检查**

Run: `curl http://localhost:8000/health 2>/dev/null || echo "服务未运行（预期中）"`
Expected: `{"status": "ok"}` 或提示服务未运行

- [ ] **Step 3: 测试 API 文档**

服务运行时访问 `http://localhost:8000/docs` 可看到 Swagger UI。

- [ ] **Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: 完成 API 模块开发 - 14个端点、异步任务、完整测试"
```
