# CLAUDE.md

## 项目简介

智能竞品分析Agent - 基于LLM的自动化竞品分析系统，支持多源数据采集、结构化分析和智能报告生成。

## 技术栈

- **Python**: 3.13+
- **LLM框架**: LangChain + LangGraph
- **向量数据库**: Chroma
- **后端**: FastAPI
- **前端**: React + TypeScript + Tailwind CSS + shadcn/ui
- **爬虫**: Selenium + BeautifulSoup
- **数据验证**: Pydantic V2
- **LLM**: MIMO (OpenAI兼容格式)

## 目录结构

```
agent/          - Agent核心（LangGraph状态图、节点、工具）
api/            - FastAPI接口层
collector/      - 数据采集（搜索、爬取、清洗）
config/         - 配置管理（设置、Prompt模板）
frontend/       - React前端界面
examples/       - 使用示例
knowledge/      - 知识库（向量存储、Embedding、RAG）
models/         - 数据模型（Pydantic）
report/         - 报告生成
tests/          - 单元测试
utils/          - 工具类
```

## 开发规范

### Git规范

- 每完成一个小功能就提交一次，不要攒大提交
- 提交信息格式：`类型: 简短描述`
  - `feat`: 新功能
  - `fix`: 修复bug
  - `docs`: 文档更新
  - `test`: 测试相关
  - `refactor`: 重构
- 示例：`feat: 添加用户评价采集功能`、`fix: 修复价格提取正则表达式`

### 文档同步更新

每次开发新功能时，必须同步更新：
1. **CLAUDE.md** - 更新模块状态、新增命令等
2. **DEVELOPMENT_PROGRESS.md** - 更新开发进度
3. **README.md** - 如有目录结构变更
4. **TECHNICAL_ARCHITECTURE.md** - 如有架构变更

### 代码Review标准

每次开发完一个功能后，必须执行以下Review检查：

**1. 全量测试**
- 运行所有测试（不仅是新增的），确认没有破坏已有功能
- 命令：`pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py -v`

**2. 代码质量检查**
- 是否有未使用的 import
- 是否有硬编码的值应该提取为配置
- 是否有重复代码可以复用已有模块
- 异步函数是否正确使用了 await
- 异常处理是否完整（不能吞掉异常）

**3. 接口兼容性**
- 修改已有模块时，是否影响了其他模块的调用
- 新增的函数/类是否有完整的类型注解
- 返回值格式是否与已有约定一致

**4. 文档一致性**
- CLAUDE.md 中的模块状态是否已更新
- DEVELOPMENT_PROGRESS.md 是否已更新
- 新增的命令/功能是否在文档中有说明

### 代码规范

- 使用异步模式（async/await）处理IO操作
- 使用Pydantic V2的`@field_serializer`替代已废弃的`json_encoders`
- 使用`logging`模块记录日志，不用`print`
- 类型注解必须完整
- 中文注释和文档字符串

### 测试规范

- 每个模块都要有对应的测试文件
- 使用`pytest`和`pytest-asyncio`
- Mock外部依赖（LLM、API、数据库）
- 测试文件命名：`tests/test_<模块名>.py`

## 常用命令

> 所有 Python 命令都需在虚拟环境中运行。激活方式：
> - **Windows PowerShell**: `.venv\Scripts\Activate.ps1`
> - **Windows CMD**: `.venv\Scripts\activate.bat`
> - **Linux/macOS**: `source .venv/bin/activate`

```bash
# 安装依赖（首次使用前先激活虚拟环境）
pip install -r requirements.txt

# 运行全部测试
pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py utils/tests/ -v

# 运行单个模块测试
pytest tests/test_agent.py -v

# 运行示例
python examples/models_demo.py
python examples/knowledge_demo.py
python examples/collector_demo.py
python examples/agent_demo.py
python examples/report_demo.py

# 启动API服务
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd frontend && npm run dev

# 写入种子数据（启动API后运行）
python seed.py              # 写入15个竞品
python seed.py --clear      # 清空后重新写入
python seed.py --dry-run    # 仅预览，不写入
```

## 环境配置

复制`.env.example`为`.env`，填写以下配置：

```env
OPENAI_API_KEY=your-mimo-api-key
OPENAI_API_BASE=https://api.mimo.com/v1
SERPAPI_KEY=your-serpapi-key
GITHUB_TOKEN=your-github-token（可选，无限流限制）
```

## 模块状态

| 模块 | 状态 | 说明 |
|------|------|------|
| models/ | ✅ 完成 | 数据模型（竞品、分析、报告） |
| knowledge/ | ✅ 完成 | 知识库（向量存储、RAG） |
| collector/ | ✅ 完成 | 数据采集（搜索、爬取、清洗、GitHub、Apify应用商店） |
| config/ | ✅ 完成 | 配置管理 |
| agent/ | ✅ 完成 | Agent核心（LangGraph状态图） |
| report/ | ✅ 完成 | 报告生成（模板管理、Markdown/HTML导出） |
| api/ | ✅ 完成 | FastAPI接口（竞品CRUD、分析任务、报告管理、智能问答） |
| frontend/ | ✅ 完成 | React前端（TypeScript + Tailwind + shadcn/ui） |
| utils/ | ✅ 完成 | 工具类（日志、JSON、日期、文本、元数据、LLM解析、报告辅助） |

## 测试统计

- 测试文件：8个（含 utils/tests/）
- 测试用例：153个（含 Apify 采集器 12 个、收集器原有 16 个、模型 15 个、知识库 8 个、Agent 11 个、报告 13 个、API 28 个、utils 48 个）
- 状态：全部通过（1个预知失败：ReportGenerator.export_html 方法已移除）

## 相关文档

- [OPTIMIZATION_ROADMAP.md](OPTIMIZATION_ROADMAP.md) - 优化路线图
- [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md) - 开发进度
- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - 技术架构
- [PRD.md](PRD.md) - 产品需求文档
