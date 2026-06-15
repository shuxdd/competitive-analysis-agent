# 智能竞品分析Agent

基于LLM的自动化竞品分析系统，支持多源数据采集、结构化分析和智能报告生成。

## 项目文档

- [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) - 技术架构文档

## 目录结构

```
jpleida/
│
├── README.md                       # 项目说明
│
├── agent/                          # Agent核心
│   ├── graph.py                    # LangGraph 状态图
│   ├── nodes/                      # 处理节点
│   └── tools/                      # Agent工具
│
├── api/                            # API接口层
│   ├── app.py                      # FastAPI入口
│   ├── routes/                     # 路由
│   └── schemas/                    # 数据模式
│
├── collector/                      # 数据采集
│   ├── base.py                     # 基础采集器
│   ├── web_search.py               # 网页搜索
│   ├── web_scraper.py              # 网页爬取
│   └── cleaner.py                  # 数据清洗
│
├── config/                         # 配置管理
│   ├── settings.py                 # 全局配置
│   └── prompts.py                  # Prompt模板
│
├── frontend/                       # React前端界面
│
├── knowledge/                      # 知识库管理
│   ├── vector_store.py             # Chroma向量存储
│   ├── embeddings.py               # Embedding服务
│   ├── knowledge_base.py           # 知识库管理
│   └── README.md                   # 知识库文档
│
├── models/                         # 数据模型
│   ├── competitor.py               # 竞品结构
│   ├── analysis.py                 # 分析结构
│   └── report.py                   # 报告结构
│
├── report/                         # 报告生成
│   ├── analyzer.py                 # 数据分析
│   └── generator.py                # 报告生成
│
├── utils/                          # 工具类
│
└── tests/                          # 单元测试
```

## 模块职责

| 模块 | 职责 | 关键文件 |
|------|------|---------|
| **agent/** | Agent编排核心 | graph.py, nodes/*, tools/* |
| **api/** | HTTP接口 | app.py, routes/* |
| **collector/** | 数据采集 | web_search.py, web_scraper.py, cleaner.py |
| **knowledge/** | 知识库管理 | vector_store.py, embeddings.py, knowledge_base.py |
| **report/** | 报告生成 | analyzer.py, generator.py |
| **config/** | 配置管理 | settings.py, prompts.py |
| **models/** | 数据结构 | competitor.py, analysis.py, report.py |
| **frontend/** | React前端界面 | pages/*, components/* |
| **utils/** | 工具类 | logger.py |

## 数据流

```
用户请求 → api/ → agent/graph.py → nodes/ 调用 tools/ → report/ 生成报告
                              ↓
                        knowledge/ 提供检索
```

## 技术栈

- **LLM框架**: LangChain + LangGraph
- **向量数据库**: Chroma
- **后端**: FastAPI
- **前端**: React + TypeScript + Tailwind CSS + shadcn/ui
- **爬虫**: Selenium + BeautifulSoup + Apify

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制`.env.example`为`.env`，并填写配置：

```bash
cp .env.example .env
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行模型测试
pytest tests/test_models.py -v

# 运行知识库测试
pytest tests/test_knowledge_simple.py -v
```


## 模块说明

### 知识库模块

知识库模块提供向量数据库管理和语义检索功能：

- **VectorStore**: 基于Chroma的向量数据库管理
- **EmbeddingService**: 支持OpenAI和本地Embedding模型
- **KnowledgeBase**: 整合向量数据库和Embedding服务的高级接口

详细使用说明请参考[knowledge/README.md](knowledge/README.md)

## License

MIT
