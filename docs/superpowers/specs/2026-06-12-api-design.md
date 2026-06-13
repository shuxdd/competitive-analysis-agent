# API 模块设计文档

**日期**: 2026-06-12
**状态**: 已批准

## 概述

为竞品分析 Agent 开发 FastAPI 后端接口层，采用前后端分离架构，API 供 Streamlit 前端调用。

## 设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 架构方案 | 模块化路由 | 与项目现有风格一致，易扩展 |
| 数据库 | SQLite + async SQLAlchemy | 轻量，ORM 解耦便于后续迁移 |
| 任务模型 | 异步任务 | 分析耗时长，避免请求超时 |
| 认证 | 无 | 内部系统，先快速开发 |

## 数据库层 (`api/database.py`)

### ORM 模型

**competitors 表**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | String (UUID) | 主键 |
| name | String | 竞品名称 |
| website | String (nullable) | 官网 |
| industry | String (nullable) | 行业 |
| tags | JSON | 标签列表 |
| notes | Text (nullable) | 备注 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**analysis_tasks 表**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | String (UUID) | 主键 |
| competitors | JSON | 竞品名称列表 |
| analysis_type | String | quick/standard/deep |
| dimensions | JSON | 分析维度列表 |
| my_product | String (nullable) | 自家产品 |
| status | String | pending/planning/collecting/analyzing/completed/failed |
| result | JSON (nullable) | 分析结果 |
| error_message | Text (nullable) | 失败原因 |
| created_at | DateTime | 创建时间 |
| completed_at | DateTime (nullable) | 完成时间 |

**reports 表**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | String (UUID) | 主键 |
| analysis_id | String (FK) | 关联分析任务 |
| title | String | 报告标题 |
| report_type | String | quick/standard/deep |
| format | String | markdown/html |
| content | Text | 报告内容 |
| file_path | String (nullable) | 导出文件路径 |
| created_at | DateTime | 创建时间 |

### 技术细节

- 使用 `create_async_engine` + `aiosqlite`
- `async_sessionmaker` 管理会话
- 每个请求通过依赖注入获取 session

## API 端点

### 竞品管理 (`/api/competitors`)

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/api/competitors` | 列表查询 | ?page=&page_size=&industry=&keyword= | 分页列表 |
| POST | `/api/competitors` | 创建竞品 | CompetitorCreate | 竞品详情 |
| GET | `/api/competitors/{id}` | 获取详情 | - | 竞品详情 |
| PUT | `/api/competitors/{id}` | 更新竞品 | CompetitorUpdateRequest | 竞品详情 |
| DELETE | `/api/competitors/{id}` | 删除竞品 | - | 成功/失败 |

### 分析任务 (`/api/analysis`)

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/api/analysis` | 提交任务 | AnalysisRequest | task_id + status |
| GET | `/api/analysis` | 任务列表 | ?page=&page_size=&status= | 分页列表 |
| GET | `/api/analysis/{id}` | 查询状态 | - | 任务详情+结果 |
| DELETE | `/api/analysis/{id}` | 取消/删除 | - | 成功/失败 |

### 报告管理 (`/api/reports`)

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/api/reports` | 报告列表 | ?page=&page_size=&analysis_id=&report_type= | 分页列表 |
| GET | `/api/reports/{id}` | 获取报告 | - | 报告详情 |
| GET | `/api/reports/{id}/export` | 导出文件 | ?format=markdown/html | 文件下载 |
| DELETE | `/api/reports/{id}` | 删除报告 | - | 成功/失败 |

### 智能问答 (`/api/qa`)

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/api/qa` | 提交问题 | {"question": str, "competitors": list?} | 答案 + 引用来源 |

## 异步任务模型

### 执行流程

1. `POST /api/analysis` → 创建任务记录（status=pending），返回 task_id
2. `asyncio.create_task()` 启动后台分析
3. 状态流转：pending → planning → collecting → analyzing → completed/failed
4. 前端轮询 `GET /api/analysis/{id}` 查询进度
5. 分析完成后结果写入 `analysis_tasks.result` JSON 字段

### 任务状态管理

- 使用内存字典 `{task_id: asyncio.Task}` 追踪运行中的任务
- 服务重启后，数据库中 pending/planning/collecting/analyzing 状态的任务标记为 failed

## 错误处理

### 统一响应格式

```json
{
  "code": 200,
  "data": { ... },
  "message": "success"
}
```

错误响应：
```json
{
  "code": 404,
  "data": null,
  "message": "竞品不存在"
}
```

### 异常处理

- 全局异常处理器捕获未处理异常
- HTTP 异常（404/422/500）统一格式
- 任务失败记录 error_message

## 文件结构

```
api/
├── app.py              # FastAPI应用入口、中间件、异常处理、启动/关闭事件
├── database.py         # 异步引擎、Session工厂、ORM模型、依赖注入
├── schemas.py          # API请求/响应Schema（复用models/中的Pydantic模型）
├── routers/
│   ├── __init__.py
│   ├── competitors.py  # 竞品CRUD路由
│   ├── analysis.py     # 分析任务路由
│   ├── reports.py      # 报告管理路由
│   └── qa.py           # 智能问答路由
tests/
└── test_api.py         # API集成测试
```

## 依赖

新增：
- `aiosqlite` — SQLite 异步驱动

已有（无需新增）：
- `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pydantic-settings`

## 测试策略

- 使用 `httpx.AsyncClient` 测试所有端点
- Mock LLM 调用（与现有测试一致）
- 测试覆盖：CRUD 操作、异步任务生命周期、错误场景

## 与其他模块的集成

- `models/` — 复用 Pydantic 模型做请求验证和响应序列化
- `agent/` — 调用 `create_analysis_graph()` 执行分析
- `report/` — 调用 `ReportGenerator` 生成报告
- `knowledge/` — 调用 `KnowledgeBase` 进行智能问答
- `config/` — 使用 `settings` 获取配置
