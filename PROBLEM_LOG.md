# 项目问题记录

> 每次解决问题时，在此文档记录：问题现象、根因、解决方案。

## 2026-06-13

### 预知失败测试 test_export_html 残留

**现象：** 运行全量测试时 `test_report.py::TestReportGenerator::test_export_html` 必失败，CLAUDE.md 标记为"1个预知失败"。

**根因：** `ReportGenerator.export_html` 方法已被移除，但对应的测试未删除，导致每次测试都报 `AttributeError`。

**解决方案：** 删除 `tests/test_report.py` 中的 `test_export_html` 方法，更新 CLAUDE.md 和 DEVELOPMENT_PROGRESS.md 中的测试计数（153→152，报告测试 13→12）。

**涉及文件：** `tests/test_report.py`、`CLAUDE.md`、`DEVELOPMENT_PROGRESS.md`

### WebSocket 缺少认证（安全漏洞）

**现象：** WebSocket 端点 `/ws/analysis/{task_id}` 无需任何认证即可连接，可查看任意分析任务的实时进度。

**根因：** 早期实现时未对 WebSocket 连接进行鉴权，任何知道任务 ID 的人都能连接。

**解决方案：** WebSocket 连接时要求客户端在 query param 中提供 JWT token (`?token=xxx`)，后端验证 token 有效性后还需校验任务所有权。

**涉及文件：** `api/app.py`、`frontend/src/pages/analysis/[id].tsx`

### SerpAPI 未配置导致竞品采集全部静默失败

**现象：** 未配置 SERPAPI_KEY 时，searcher 节点对所有竞品返回空数据，且没有任何明显提示。

**根因：** serpapi_key 为空时搜索工具调用失败，但异常被 try/except 吞掉，只输出了一行 debug 日志。

**解决方案：** searcher 节点入口处增加早期检查，key 不存在时直接返回错误信息；API 层将 graph 错误传播到 task.error_message；前端展示 amber 警告横幅。

**涉及文件：** `agent/nodes/searcher.py`、`api/routers/analysis.py`、`frontend/src/pages/analysis/[id].tsx`

### 删除竞品时未清理知识库

**现象：** 从管理界面删除竞品后，Chroma 知识库中对应的向量数据仍然存在，QA 问答仍能检索到已删除竞品的信息。

**根因：** `competitors.py` 中的 delete 接口只删了 SQLite 记录，没有调用 KnowledgeBase 清理向量数据。

**解决方案：** 删除竞品后在 KnowledgeBase 中同时清理 "competitors" 和 "reviews" 两个 collections 的相关文档。

**涉及文件：** `api/routers/competitors.py`、`knowledge/knowledge_base.py`

### Quick/Deep 分析类型冗余

**现象：** 系统定义了 quick/standard/deep 三种分析类型，但前端从未暴露过选择器，且 quick 和 deep 的实际数据流与 standard 差异很小。

**根因：** 设计初期规划的差异化分析路径，实际开发中发现 LLM 的能力足够覆盖所有场景，不需要通过 engineering 方式简化。

**解决方案：** 删除 quick/deep 相关的所有代码（prompts、templates、generator 分支、graph 条件路由、model 枚举），统一为 standard。

**涉及文件：** `config/prompts.py`、`report/templates.py`、`report/generator.py`、`agent/graph.py`、`models/analysis.py` 等

### LangChain OpenAIEmbeddings 与 DashScope 兼容接口不兼容

**现象：** `EmbeddingService` 初始化后调用 `embed_query("测试")` 返回 400 错误，DashScope 返回 `"contents is neither str nor list of str"`。但直接通过 `curl` 和 OpenAI Python SDK 调用 `/embeddings` 接口正常。

**根因：** LangChain 的 `OpenAIEmbeddings` 在底层调用 `_get_len_safe_embeddings` 时，会对输入进行 tokenization 后再发请求，DashScope 的兼容接口不认这种 tokenized 格式。而原生 OpenAI SDK 直接发送原始文本 JSON，DashScope 处理正确。

**解决方案：** 将 `EmbeddingService` 底层从 `langchain_openai.OpenAIEmbeddings` 替换为原生 `openai.OpenAI` SDK，直接调 `client.embeddings.create(model=..., input=...)`，保持 `embed_documents` / `embed_query` 接口不变。

**涉及文件：** `knowledge/embeddings.py`

---

### 知识库测试失败：Inconsistent number of IDs and embeddings

**现象：** 将 Embedding 服务连接到 Chroma 后，`test_knowledge_simple.py` 测试报错，提示 ID 数量和 embedding 数量不一致。

**根因：** 测试 mock 的 `embed_documents` 固定返回 `[[0.1, 0.2, 0.3]] * 10`，与实际输入文本数量不匹配。Chroma 在收到 embedding_function 后会调用它，获取返回的向量数必须等于文档数。

**解决方案：** mock 改为 `side_effect=lambda texts: [[0.1, 0.2, 0.3] for _ in texts]`，动态生成与输入数量匹配的向量。

**涉及文件：** `tests/test_knowledge.py`

---

### MIMO API 不提供 /embeddings 端点

**现象：** 使用 MIMO 的 `api_key` 和 `api_base` 初始化 `EmbeddingService` 时，调用 `/embeddings` 返回 404。

**根因：** MIMO 是对话模型 API，不提供 embedding 功能。Embedding 需要单独的模型服务（如 DashScope text-embedding-v4）。

**解决方案：** 配置分离，增加 `EMBEDDING_API_KEY`、`EMBEDDING_API_BASE`、`EMBEDDING_MODEL`、`EMBEDDING_DIMENSIONS` 独立配置项。`EmbeddingService` 优先使用 embedding 专用配置，再回退到通用 LLM 配置。同时在 `KnowledgeBase.__init__` 中加入探测机制（`embed_query("probe")`），API 不可用时自动回退到 Chroma 内置的 all-MiniLM-L6-v2。

**涉及文件：** `config/settings.py`、`knowledge/embeddings.py`、`knowledge/knowledge_base.py`、`.env`

---

### import create_chroma_embedding_function 未定义

**现象：** `knowledge_base.py` 启动时抛出 `ImportError: cannot import name 'create_chroma_embedding_function'`。

**根因：** `knowledge_base.py` 调用了 `create_chroma_embedding_function` 但没有从 `embeddings.py` 导入它。

**解决方案：** 在 `knowledge_base.py` 的 import 中添加 `create_chroma_embedding_function`。

**涉及文件：** `knowledge/knowledge_base.py`

---

### LangGraph 条件边映射缺失

**现象：** `_route_after_searcher` 在 quick 模式下返回 `"extractor"`，但条件边的映射字典缺少这个键，运行时抛出 `ValueError`。

**根因：** `graph.py` 条件边映射只配置了 `{"reporter": "reporter", "scraper": "scraper"}`，没有添加新增的 `"extractor"` 路由。

**解决方案：** 在条件边映射字典中添加 `"extractor": "extractor"`。

**涉及文件：** `agent/graph.py`

---

## 2026-06-12 之前

### 测试异步错误：coroutine was never awaited

**现象：** 异步测试中报 `coroutine was never awaited`，测试挂起或超时。

**根因：** 测试函数或 fixture 使用了 `async def` 但没有配置 `pytest-asyncio`，或者 fixture 的作用域与异步事件循环不匹配。

**解决方案：** 确保 `pytest-asyncio` 正确配置（`pyproject.toml` 设置 `asyncio_mode = "auto"`），异步 fixture 使用 `@pytest_asyncio.fixture`。

**涉及文件：** `pyproject.toml`、各测试文件

---

### Pydantic V2 json_encoders 弃用

**现象：** Pydantic 运行时警告 `json_encoders` 已弃用。

**根因：** 使用了 Pydantic V2 已废弃的 `json_encoders` 配置。

**解决方案：** 替换为 `@field_serializer` 装饰器方式。

**涉及文件：** 各模型文件

---

### xhtml2pdf 报告导出中文字体问题

**现象：** PDF 报告中的中文字符显示为方框乱码。

**根因：** xhtml2pdf 默认字体不支持中文。

**解决方案：** 在 HTML 模板中显式指定支持中文的字体（如 SimHei、Microsoft YaHei），并确保字体文件在系统中可用。

**涉及文件：** `report/generator.py`

---

### Redis 连接泄漏

**现象：** 长时间运行后 API 响应变慢，Redis 连接数持续增长。

**根因：** Redis 客户端使用完后没有正确关闭连接。

**解决方案：** 使用连接池管理 Redis 连接，确保请求结束后归还连接到池。

**涉及文件：** `utils/cache.py`
