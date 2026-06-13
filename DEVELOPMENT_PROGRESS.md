# 开发进度

## 已完成模块

### 1. 数据模型模块 (models/) ✅

**完成时间**: 2026-06-11

**主要功能**:
- 竞品信息模型 (CompetitorInfo)
- 产品信息模型 (Product)
- 定价模型 (PricingModel, ProductTier)
- 公司信息模型 (CompanyInfo)
- 分析请求模型 (AnalysisRequest)
- 分析结果模型 (AnalysisResult)
- 报告模型 (Report, QuickReport, StandardReport, DeepReport)
- 枚举类型 (ReportType, AnalysisDimension, AnalysisStatus, ReportFormat)

**文件**:
- `models/competitor.py` - 竞品相关模型
- `models/analysis.py` - 分析相关模型
- `models/report.py` - 报告相关模型
- `models/__init__.py` - 模块导出
- `tests/test_models.py` - 单元测试 (15个测试用例)

**测试结果**: ✅ 全部通过

### 2. 知识库模块 (knowledge/) ✅

**完成时间**: 2026-06-11

**主要功能**:
- 向量数据库管理 (VectorStore)
  - 集合管理（创建、删除、清空）
  - 文档管理（添加、更新、删除）
  - 语义检索（支持元数据过滤）
- Embedding服务 (EmbeddingService, LocalEmbeddingService)
  - OpenAI Embedding支持
  - 本地Embedding支持（sentence-transformers）
  - 批量处理
- 知识库管理 (KnowledgeBase)
  - 竞品信息管理
  - 网页内容存储
  - 用户评价管理
  - 语义检索
  - 上下文获取（用于RAG）

**文件**:
- `knowledge/vector_store.py` - 向量数据库管理
- `knowledge/embeddings.py` - Embedding服务
- `knowledge/knowledge_base.py` - 知识库管理
- `knowledge/__init__.py` - 模块导出
- `knowledge/README.md` - 模块文档
- `tests/test_knowledge.py` - 完整测试（需要真实数据库）
- `tests/test_knowledge_simple.py` - 简单测试（使用mock）

**测试结果**: ✅ 全部通过（简单测试）

### 3. 配置模块 (config/) ✅

**完成时间**: 2026-06-11

**主要功能**:
- 全局配置管理 (Settings)
- Prompt模板 (EXTRACTION_PROMPT, SWOT_PROMPT, REPORT_PROMPT等)

**文件**:
- `config/settings.py` - 配置设置
- `config/prompts.py` - Prompt模板

### 4. 数据采集模块 (collector/) ✅

**完成时间**: 2026-06-11（最后更新: 2026-06-13）

**主要功能**:
- 基础采集器 (BaseCollector) - 采集器基类和结果封装
- 网页搜索采集器 (WebSearchCollector) - 通过SerpAPI搜索
- 网页爬取采集器 (WebScraperCollector) - 使用Selenium爬取网页（带本地文件缓存，TTL 7天）
- 数据清洗工具 (DataCleaner) - 文本清理、价格提取、功能提取等
- GitHub 采集器 (GitHubCollector) - 采集仓库 star/fork/issue 等数据
- **Apify 应用商店采集器 (ApifyCollector) [新增]** - 通过 Apify 平台采集 Google Play 和 App Store 评论，默认 3 条

**文件**:
- `collector/base.py` - 基础采集器
- `collector/web_search.py` - 网页搜索采集器
- `collector/web_scraper.py` - 网页爬取采集器
- `collector/cleaner.py` - 数据清洗工具
- `collector/github_collector.py` - GitHub 数据采集器
- `collector/apify_collector.py` - Apify 应用商店采集器
- `collector/__init__.py` - 模块导出
- `tests/test_collector.py` - 单元测试 (28个测试用例)
- `examples/collector_demo.py` - 使用示例

**测试结果**: ✅ 全部通过

### 5. Agent核心模块 (agent/) ✅

**完成时间**: 2026-06-11（最后更新: 2026-06-13）

**主要功能**:
- LangGraph状态图 (create_analysis_graph)
- 任务规划节点 (plan_analysis) - 使用LLM生成采集计划
- 搜索节点 (search_competitors) - 并行采集多数据源（网页搜索、GitHub、Google Play、App Store）
- 爬取节点 (scrape_data) - 使用WebScraperCollector爬取网页
- 信息提取节点 (extract_info) - 按竞品合并网页文本后批量LLM提取，减少调用次数
- 分析节点 (analyze_competitors) - 功能矩阵、定价对比、SWOT分析、**用户评价分析**
- 报告生成节点 (generate_report) - 使用LLM生成Markdown报告
- LLM工厂 (create_llm) - 基于MIMO的ChatOpenAI实例
- Agent工具 (SearchTool, ScraperTool, VectorSearchTool) - LangChain BaseTool封装

**文件**:
- `agent/graph_state.py` - AgentState状态定义
- `agent/graph.py` - 状态图组装
- `agent/llm.py` - LLM工厂
- `agent/nodes/planner.py` - 任务规划节点
- `agent/nodes/searcher.py` - 搜索节点（含Apify应用商店集成）
- `agent/nodes/scraper.py` - 爬取节点
- `agent/nodes/extractor.py` - 信息提取节点（改为按竞品合并提取）
- `agent/nodes/analyzer.py` - 分析对比节点（新增应用商店评价分析）
- `agent/nodes/reporter.py` - 报告生成节点
- `agent/tools/search_tool.py` - 搜索工具
- `agent/tools/scraper_tool.py` - 爬取工具
- `agent/tools/vector_tool.py` - 向量检索工具
- `agent/__init__.py` - 模块导出
- `tests/test_agent.py` - 单元测试 (11个测试用例)
- `examples/agent_demo.py` - 使用示例

**测试结果**: ✅ 全部通过

### 6. 报告生成模块 (report/) ✅

**完成时间**: 2026-06-11

**主要功能**:
- 报告生成器 (ReportGenerator) - 支持quick/standard/deep三种报告类型
- 报告模板管理 (ReportTemplates) - 模板列表、章节管理、Prompt管理
- Markdown文件导出
- HTML文件导出（带CSS样式）
- 降级报告生成（LLM失败时自动降级）

**文件**:
- `report/generator.py` - 报告生成器
- `report/templates.py` - 报告模板管理
- `report/__init__.py` - 模块导出
- `tests/test_report.py` - 单元测试 (12个测试用例)
- `examples/report_demo.py` - 使用示例

**测试结果**: ✅ 全部通过

### 7. API接口模块 (api/) ✅

**完成时间**: 2026-06-12

**主要功能**:
- FastAPI应用 (app.py) - 生命周期管理、CORS、全局异常处理
- 数据库模块 (database.py) - 异步 SQLAlchemy ORM、3张表（竞品/任务/报告）
- Schema模块 (schemas.py) - 请求/响应 Pydantic 模型
- 竞品管理路由 (routers/competitors.py) - CRUD 接口（5个端点）
- 分析任务路由 (routers/analysis.py) - 提交/查询/删除接口（4个端点）
- 报告管理路由 (routers/reports.py) - 查询/导出/删除接口（4个端点）
- 智能问答路由 (routers/qa.py) - 基于知识库的问答接口（1个端点）

**文件**:
- `api/app.py` - FastAPI应用入口
- `api/database.py` - 数据库模块
- `api/schemas.py` - API Schema
- `api/routers/__init__.py` - 路由注册
- `api/routers/competitors.py` - 竞品管理路由
- `api/routers/analysis.py` - 分析任务路由
- `api/routers/reports.py` - 报告管理路由
- `api/routers/qa.py` - 智能问答路由
- `tests/test_api.py` - 单元测试 (28个测试用例)

**测试结果**: ✅ 全部通过

### 8. 前端模块 (frontend/) ✅

**完成时间**: 2026-06-12

**技术栈**: React 18 + TypeScript + Vite 8 + Tailwind CSS 4 + shadcn/ui + Recharts

**主要功能**:
- 项目基础架构（Vite + TypeScript + Tailwind CSS + shadcn/ui）
- axios 封装（响应拦截器、自动解包 data 字段）
- React Query 数据管理
- React Router 路由配置
- 主题切换（亮/暗模式，localStorage 持久化）
- 仪表盘页面（数据概览卡片、最近任务、最近报告）
- 竞品管理页面（列表、搜索、新建/编辑/删除）
- 分析任务页面（任务列表、新建分析、状态轮询）
- 报告中心页面（卡片网格视图、搜索）
- 智能问答页面（ChatGPT 风格对话、打字机效果）

**UI 组件**:
- Button、Input、Card、Dialog、Badge
- Table、Select、Textarea、Tabs
- Skeleton、Label、Pagination、Checkbox

**文件**:
- `frontend/src/App.tsx` - 应用入口
- `frontend/src/main.tsx` - 渲染入口
- `frontend/src/layouts/MainLayout.tsx` - 主布局
- `frontend/src/components/layout/Sidebar.tsx` - 侧边栏
- `frontend/src/components/layout/Topbar.tsx` - 顶部导航
- `frontend/src/components/ui/` - shadcn/ui 组件
- `frontend/src/pages/dashboard/` - 仪表盘页面
- `frontend/src/pages/competitors/` - 竞品管理页面
- `frontend/src/pages/analysis/` - 分析任务页面
- `frontend/src/pages/reports/` - 报告中心页面
- `frontend/src/pages/qa/` - 智能问答页面
- `frontend/src/lib/api.ts` - API 封装
- `frontend/src/lib/queryClient.ts` - React Query 配置
- `frontend/src/lib/utils.ts` - 工具函数
- `frontend/src/types/index.ts` - TypeScript 类型定义
- `frontend/src/hooks/useTheme.ts` - 主题切换 hook
- `frontend/src/styles/globals.css` - 全局样式

**测试结果**: ✅ TypeScript 编译通过，构建成功

### 9. 工具模块 (utils/) ✅

**完成时间**: 2026-06-12

**主要功能**:
- 日志工具 (logger.py) - 统一的 logging 封装，支持控制台和文件输出
- 日期工具 (date_utils.py) - 日期格式化、时间戳生成
- JSON 工具 (json_utils.py) - 序列化/反序列化，支持 datetime 和中文
- 文本工具 (text_utils.py) - 文本清理、分段
- LLM 解析工具 (llm_parser.py) - 从 LLM 响应中提取 JSON
- 元数据工具 (metadata_utils.py) - Chroma 元数据预处理（list/dict 转字符串）
- 报告辅助工具 (report_helpers.py) - 报告头生成、数据准备、降级报告

**文件**:
- `utils/__init__.py` - 模块导出
- `utils/logger.py` - 日志工具
- `utils/date_utils.py` - 日期工具
- `utils/json_utils.py` - JSON 工具
- `utils/text_utils.py` - 文本工具
- `utils/llm_parser.py` - LLM 解析工具
- `utils/metadata_utils.py` - 元数据工具
- `utils/report_helpers.py` - 报告辅助工具
- `utils/tests/test_logger.py` - 日志测试 (9个测试用例)
- `utils/tests/test_date_utils.py` - 日期测试 (4个测试用例)
- `utils/tests/test_json_utils.py` - JSON测试 (6个测试用例)
- `utils/tests/test_text_utils.py` - 文本测试 (9个测试用例)
- `utils/tests/test_llm_parser.py` - LLM解析测试 (7个测试用例)
- `utils/tests/test_metadata_utils.py` - 元数据测试 (7个测试用例)
- `utils/tests/test_report_helpers.py` - 报告辅助测试 (6个测试用例)

**测试结果**: ✅ 全部通过（48个测试用例）

## 开发统计

| 指标 | 数量 |
|------|------|
| 已完成模块 | 9/9 |
| Python文件 | 55+个 |
| 前端文件 | 30+个 |
| 测试文件 | 8个 |
| 测试用例 | 153个 |
| Python代码行数 | ~6500行 |
| 前端代码行数 | ~3000行 |

## 下一步计划

1. **前端功能增强**
   - 添加数据可视化图表（Recharts）
   - 实现报告详情页（Markdown 渲染）
   - 添加表单验证（react-hook-form + zod）
   - 优化移动端响应式布局

## 技术债务

- [ ] 添加更多单元测试
- [ ] 完善错误处理
- [ ] 添加日志记录
- [ ] 优化性能
- [ ] 添加类型注解

## 更新日志

### 2026-06-13 (大规模 Review + 修复)

**认证鉴权系统（新增）**
- 新增 `api/auth.py` JWT 工具模块（PyJWT HS256 + pbkdf2_hmac 密码哈希）
- 新增 `api/routers/auth.py` 登录/注册接口
- 所有路由添加 `require_user` / `get_current_user` 依赖，按 `user_id` 数据隔离
- 前端新增登录/注册页面、AuthContext、路由守卫
- 新增 `frontend/src/pages/login/`、`frontend/src/pages/register/` 页面
- 新增 `frontend/src/contexts/AuthContext.tsx` 认证上下文

**移除 quick/deep 分析类型**
- 删除 `config/prompts.py` 中 `QUICK_REPORT_PROMPT` 和 `DEEP_REPORT_PROMPT`
- 删除 `report/templates.py` 中 quick/deep 模板，统一为 standard
- 删除 `report/generator.py` 中 `_prepare_quick_data`、Quick/Deep 分支
- 删除 `models/analysis.py` 中 `ReportType.QUICK` / `ReportType.DEEP`
- 简化 `agent/graph.py`：移除条件路由，线性流程（planner→searcher→scraper→extractor→analyzer→reporter→knowledge_store）
- 前端分析类型选择器同步移除 quick/deep 选项

**竞品自动检测应用商店 ID**
- `api/routers/competitors.py` 新增 `_auto_detect_store_ids()` 函数
- 创建/更新竞品时自动通过 iTunes Search API 查找 App Store ID
- 通过 SerpAPI 搜索 Google Play 包名
- `CompetitorORM` 新增 `google_play_id` / `app_store_id` 字段

**WebSocket JWT 认证**
- `api/app.py` WebSocket 端点增加 token 验证（query param `?token=xxx`）
- 验证 token 有效性 + 任务归属权校验
- 前端 `[id].tsx` 连接 WS 时从 localStorage 取 token 传入

**知识库清理**
- `knowledge_base.py` 增强 `delete_competitor()`：同时清理 "competitors" 和 "reviews" 两个集合
- 竞品删除时自动清理 Chroma 中对应向量

**SerpAPI 未配置处理**
- `agent/nodes/searcher.py` 增加早期退出：`serpapi_key` 为空时直接返回错误信息
- `api/routers/analysis.py` 将 graph 错误传播到 `task.error_message`
- 前端完成状态展示 amber 警告横幅

**知识库写入流程**
- 新增 `agent/nodes/knowledge_store.py` 节点，分析完成后将结构化数据和用户评价写入 Chroma

**其它修复**
- `test_api.py` 修复 `test_list_reports_with_data`（user_id 查询）
- `test_agent.py` 修复 `test_header_generation`（移除 analysis_type 参数）

### 2026-06-12 (晚上)
- 完成工具模块（utils/）：日志、日期、JSON、文本、LLM解析、元数据、报告辅助
- 重构现有模块（agent/、report/、collector/、knowledge/）使用 utils 工具函数
- 添加 utils 模块单元测试（48个测试用例，全部通过）

### 2026-06-12 (下午)
- 完成前端模块（React 18 + TypeScript + Vite 8 + Tailwind CSS 4）
- 实现仪表盘页面（数据概览、最近任务/报告）
- 实现竞品管理页面（列表、搜索、新建/编辑/删除）
- 实现分析任务页面（任务列表、新建分析、状态轮询）
- 实现报告中心页面（卡片网格视图、搜索）
- 实现智能问答页面（ChatGPT 风格对话、打字机效果）
- 集成 shadcn/ui 组件库（13 个组件）
- 配置 axios 封装、React Query、主题切换

### 2026-06-12 (上午)
- 完成API接口模块（FastAPI应用、数据库ORM、14个API端点、28个测试用例）
- 竞品管理CRUD接口
- 异步分析任务（提交/查询/取消）
- 报告管理（查询/导出Markdown和HTML/删除）
- 智能问答接口（基于知识库RAG）

### 2026-06-11
- 完成数据模型模块
- 完成知识库模块
- 完成数据采集模块
- 完成Agent核心模块（LangGraph状态图、6个处理节点、3个工具）
- 完成报告生成模块（报告生成器、模板管理、Markdown/HTML导出）
- 创建项目文档（含CLAUDE.md开发规范）
- 添加单元测试（63个测试用例）
- 创建使用示例
