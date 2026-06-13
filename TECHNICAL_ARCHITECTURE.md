# 智能竞品分析Agent - 技术架构文档

## 1. 技术选型

### 1.1 核心技术栈

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **编程语言** | Python | 3.12 | 生态丰富，AI/ML库支持最好 |
| **LLM框架** | LangChain + LangGraph | 1.3.2 / 1.2.2 | Agent编排能力强，社区活跃 |
| **LLM模型** | MIMO | - | 多模态、长上下文、性价比高 |
| **向量数据库** | Chroma | 0.9+ | 轻量级、易部署、本地开发友好 |
| **后端框架** | FastAPI | 0.136.3+ | 异步、高性能、自动文档 |
| **前端框架** | React + TypeScript | 18+ | 组件化、类型安全、生态丰富 |
| **UI组件库** | shadcn/ui | - | 高质量、可定制、基于Radix UI |
| **CSS框架** | Tailwind CSS | 4+ | 原子化样式、开发效率高 |
| **图表库** | Recharts | 2+ | React生态、声明式图表 |
| **构建工具** | Vite | 6+ | 快速HMR、开箱即用 |
| **认证** | JWT (PyJWT) | 2.10+ | 无状态认证、HS256签名 |
| **数据存储** | SQLite/PostgreSQL | - | 结构化数据存储 |

### 1.2 工具与服务

| 工具 | 用途 | 替代方案 |
|------|------|---------|
| SerpAPI | 搜索引擎结果 | Google Custom Search |
| Selenium | 动态网页爬取 | Playwright |
| BeautifulSoup | HTML解析 | lxml |
| Unstructured | 文档解析 | PyMuPDF |
| python-docx | Word文档解析 | - |
| PyMuPDF | PDF解析 | pdfplumber |

### 1.3 开发工具

| 工具 | 用途 |
|------|------|
| uv | 包管理（替代pip） |
| ruff | 代码格式化与Lint |
| pytest | 单元测试 |
| Docker | 容器化部署 |
| GitHub Actions | CI/CD |

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层 (Frontend)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    React      │  │   REST API   │  │   CLI工具    │          │
│  │   Web应用     │  │   接口       │  │   命令行     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼─────────────────┐
│         ▼                  ▼                  ▼                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API网关层 (FastAPI)                    │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│    │
│  │  │ 路由管理  │  │ 请求验证  │  │ 认证鉴权  │  │ 限流控制  ││    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘│    │
│  └─────────────────────────┬───────────────────────────────┘    │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 Agent编排层 (LangGraph)                   │    │
│  │                                                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│    │
│  │  │ 任务规划  │  │ 工具调度  │  │ 状态管理  │  │ 结果聚合  ││    │
│  │  │   Node   │  │   Node   │  │   Node   │  │   Node   ││    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘│    │
│  │       │              │              │              │       │    │
│  │       ▼              ▼              ▼              ▼       │    │
│  │  ┌──────────────────────────────────────────────────────┐│    │
│  │  │                   工具层 (Tools)                      ││    │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    ││    │
│  │  │  │Search  │  │Scrape  │  │Extract │  │Analyze │    ││    │
│  │  │  │Tool    │  │Tool    │  │Tool    │  │Tool    │    ││    │
│  │  │  └────────┘  └────────┘  └────────┘  └────────┘    ││    │
│  │  └──────────────────────────────────────────────────────┘│    │
│  └──────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    数据层 (Data Layer)                     │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │  Chroma      │  │  Redis       │  │  SQLite      │   │   │
│  │  │  向量数据库   │  │  缓存/队列   │  │  结构化存储   │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐                     │   │
│  │  │  Celery      │  │  文件存储     │                     │   │
│  │  │  任务队列     │  │  报告/文档    │                     │   │
│  │  └──────────────┘  └──────────────┘                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  外部服务层 (External Services)            │   │
│  │                                                          │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌───────────┐     │   │
│  │  │ MIMO   │  │ SerpAPI│  │ Apify  │  │  iTunes   │     │   │
│  │  │ LLM API│  │ 搜索引擎│  │应用商店  │  │ Search API│     │   │
│  │  └────────┘  └────────┘  └────────┘  └───────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流架构

```
用户请求
    │
    ▼
┌─────────────────┐
│   API Gateway   │ ← 认证、限流、日志
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Task Scheduler │ ← 任务分解、优先级调度
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│同步任务│ │异步任务│
└───┬────┘ └───┬────┘
    │         │
    ▼         ▼
┌─────────────────┐
│  LangGraph Agent│ ← 工具编排、状态管理
└────────┬────────┘
         │
    ┌────┼────┬────────┐
    │    │    │        │
    ▼    ▼    ▼        ▼
┌────┐┌────┐┌────┐┌────┐
│搜  ││爬  ││抽  ││分  │
│索  ││取  ││取  ││析  │
└──┬─┘└──┬─┘└──┬─┘└──┬─┘
   │     │     │     │
   └─────┴─────┴─────┘
         │
         ▼
┌─────────────────┐
│   Knowledge     │ ← 向量化、索引、存储
│   Base          │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│结构化DB│ │向量DB  │
└────────┘ └────────┘
```

---

## 3. 模块详细设计

### 3.1 模块架构图

```
competitive-analysis-agent/
├── src/
│   ├── config/          # 配置模块
│   ├── agent/           # Agent核心模块
│   │   ├── nodes/       # LangGraph节点
│   │   └── tools/       # Agent工具
│   ├── collector/       # 数据采集模块
│   ├── knowledge/       # 知识库模块
│   ├── models/          # 数据模型
│   ├── report/          # 报告生成模块
│   └── api/             # API接口模块
├── frontend/            # React前端模块
└── tests/               # 测试模块
```

### 3.2 模块详细设计

#### 3.2.1 配置模块 (config/)

**职责**：管理全局配置、环境变量、Prompt模板

```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM配置
    openai_api_key: str
    anthropic_api_key: str
    default_model: str = "mimo"
    
    # 向量数据库配置
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "competitors"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # SerpAPI配置
    serpapi_key: str
    
    # 爬虫配置
    scrape_timeout: int = 30
    max_retries: int = 3
    request_delay: float = 1.0
    
    # 报告配置
    report_output_dir: str = "./data/reports"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# config/prompts.py
EXTRACTION_PROMPT = """
你是一个专业的竞品信息提取专家。请从以下文本中提取结构化的竞品信息。

文本内容：
{content}

请提取以下信息并以JSON格式返回：
{
    "company_name": "公司名称",
    "products": [
        {
            "name": "产品名称",
            "description": "产品描述",
            "features": ["功能1", "功能2"],
            "pricing": {
                "model": "定价模式",
                "tiers": [...]
            }
        }
    ],
    "target_market": "目标市场",
    "key_differentiators": ["差异化点1", "差异化点2"]
}

只返回JSON，不要其他内容。
"""

SWOT_PROMPT = """
基于以下竞品信息，生成SWOT分析。

竞品信息：
{competitor_info}

请按照以下格式输出：

## 优势 (Strengths)
- ...

## 劣势 (Weaknesses)
- ...

## 机会 (Opportunities)
- ...

## 威胁 (Threats)
- ...
"""

REPORT_PROMPT = """
你是一个专业的竞品分析师。请基于以下分析结果，生成一份专业的竞品分析报告。

分析数据：
{analysis_data}

报告要求：
1. 结构清晰，逻辑连贯
2. 数据准确，有来源引用
3. 观点明确，有洞察深度
4. 建议具体，可执行

请生成Markdown格式的报告。
"""
```

#### 3.2.2 Agent核心模块 (agent/)

**职责**：LangGraph Agent编排、工具调度、状态管理

```python
# agent/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    """Agent状态定义"""
    # 输入
    competitors: List[str]  # 竞品列表
    analysis_type: str  # 分析类型：standard
    dimensions: List[str]  # 分析维度
    
    # 中间状态
    raw_data: Annotated[dict, operator.add]  # 采集的原始数据
    extracted_info: Annotated[dict, operator.add]  # 提取的结构化信息
    analysis_results: Annotated[dict, operator.add]  # 分析结果
    
    # 输出
    report: str  # 生成的报告
    status: str  # 任务状态
    errors: List[str]  # 错误信息

def create_analysis_graph() -> StateGraph:
    """创建竞品分析Agent图"""
    
    graph = StateGraph(AgentState)
    
    # 线性流程（所有分析类型统一走此路径）
    graph.add_node("planner", plan_analysis)  # 任务规划
    graph.add_node("searcher", search_competitors)  # 搜索竞品
    graph.add_node("scraper", scrape_data)  # 爬取数据
    graph.add_node("extractor", extract_info)  # 提取信息
    graph.add_node("analyzer", analyze_competitors)  # 分析对比
    graph.add_node("reporter", generate_report)  # 生成报告
    graph.add_node("knowledge_store", store_knowledge)  # 写入知识库
    
    # 定义边（线性）
    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "scraper")
    graph.add_edge("scraper", "extractor")
    graph.add_edge("extractor", "analyzer")
    graph.add_edge("analyzer", "reporter")
    graph.add_edge("reporter", "knowledge_store")
    graph.add_edge("knowledge_store", END)
    
    return graph.compile()
```

```python
# agent/nodes/planner.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ..graph import AgentState
from ..config.settings import settings

async def plan_analysis(state: AgentState) -> AgentState:
    """任务规划节点：确定分析策略"""

    llm = ChatOpenAI(
        model=settings.default_model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0
    )
    
    prompt = f"""
    分析任务规划：
    - 竞品列表：{state['competitors']}
    - 分析类型：{state['analysis_type']}
    - 分析维度：{state['dimensions']}
    
    请规划数据采集策略，确定：
    1. 每个竞品需要搜索的关键词
    2. 需要爬取的URL列表
    3. 需要提取的信息类型
    
    返回JSON格式的采集计划。
    """
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    # 解析采集计划
    plan = parse_plan(response.content)
    
    return {
        **state,
        "raw_data": {"plan": plan},
        "status": "planning_complete"
    }
```

```python
# agent/nodes/searcher.py
from ...tools.search_tool import SearchTool
from ..graph import AgentState

async def search_competitors(state: AgentState) -> AgentState:
    """搜索节点：通过搜索引擎获取竞品信息"""
    
    search_tool = SearchTool()
    
    all_results = {}
    plan = state["raw_data"].get("plan", {})
    
    for competitor in state["competitors"]:
        keywords = plan.get(competitor, {}).get("keywords", [competitor])
        
        results = []
        for keyword in keywords:
            search_results = await search_tool.search(keyword)
            results.extend(search_results)
        
        all_results[competitor] = results
    
    return {
        **state,
        "raw_data": {**state["raw_data"], "search_results": all_results},
        "status": "search_complete"
    }
```

```python
# agent/nodes/scraper.py
from ...tools.scraper_tool import ScraperTool
from ..graph import AgentState

async def scrape_data(state: AgentState) -> AgentState:
    """爬取节点：爬取网页详细内容"""
    
    scraper = ScraperTool()
    
    all_content = {}
    search_results = state["raw_data"].get("search_results", {})
    
    for competitor, results in search_results.items():
        contents = []
        for result in results[:5]:  # 每个竞品取前5个结果
            try:
                content = await scraper.scrape(result["url"])
                contents.append({
                    "url": result["url"],
                    "title": result["title"],
                    "content": content
                })
            except Exception as e:
                # 记录错误但继续处理
                contents.append({
                    "url": result["url"],
                    "error": str(e)
                })
        
        all_content[competitor] = contents
    
    return {
        **state,
        "raw_data": {**state["raw_data"], "scraped_content": all_content},
        "status": "scrape_complete"
    }
```

```python
# agent/nodes/extractor.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ...config.prompts import EXTRACTION_PROMPT
from ...config.settings import settings
from ..graph import AgentState

async def extract_info(state: AgentState) -> AgentState:
    """提取节点：LLM结构化信息抽取"""

    llm = ChatOpenAI(
        model=settings.default_model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0
    )
    
    extracted = {}
    scraped_content = state["raw_data"].get("scraped_content", {})
    
    for competitor, contents in scraped_content.items():
        competitor_info = {
            "company_name": competitor,
            "products": [],
            "sources": []
        }
        
        for content_item in contents:
            if "error" in content_item:
                continue
            
            prompt = EXTRACTION_PROMPT.format(
                content=content_item["content"][:4000]  # 限制长度
            )
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            try:
                info = parse_json(response.content)
                merge_info(competitor_info, info)
                competitor_info["sources"].append(content_item["url"])
            except Exception:
                continue
        
        extracted[competitor] = competitor_info
    
    return {
        **state,
        "extracted_info": extracted,
        "status": "extraction_complete"
    }
```

```python
# agent/nodes/analyzer.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ...config.prompts import SWOT_PROMPT
from ...config.settings import settings
from ..graph import AgentState

async def analyze_competitors(state: AgentState) -> AgentState:
    """分析节点：多维度对比分析"""

    llm = ChatOpenAI(
        model=settings.default_model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0
    )
    
    extracted_info = state["extracted_info"]
    dimensions = state["dimensions"]
    
    analysis_results = {}
    
    # 功能矩阵对比
    if "features" in dimensions:
        analysis_results["feature_matrix"] = build_feature_matrix(extracted_info)
    
    # 价格对比
    if "pricing" in dimensions:
        analysis_results["pricing_comparison"] = build_pricing_comparison(extracted_info)
    
    # SWOT分析
    if "swot" in dimensions:
        swot_results = {}
        for competitor, info in extracted_info.items():
            prompt = SWOT_PROMPT.format(
                competitor_info=str(info)
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            swot_results[competitor] = response.content
        analysis_results["swot"] = swot_results
    
    # 用户评价分析
    if "reviews" in dimensions:
        analysis_results["review_analysis"] = analyze_reviews(extracted_info)
    
    return {
        **state,
        "analysis_results": analysis_results,
        "status": "analysis_complete"
    }
```

```python
# agent/nodes/reporter.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ...config.prompts import REPORT_PROMPT
from ...config.settings import settings
from ..graph import AgentState

async def generate_report(state: AgentState) -> AgentState:
    """报告节点：生成分析报告"""

    llm = ChatOpenAI(
        model=settings.default_model,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
        temperature=0.3
    )
    
    # 构建分析数据摘要
    analysis_summary = {
        "competitors": state["competitors"],
        "analysis_type": state["analysis_type"],
        "results": state["analysis_results"],
        "sources": {
            comp: info.get("sources", [])
            for comp, info in state["extracted_info"].items()
        }
    }
    
    prompt = REPORT_PROMPT.format(
        analysis_data=str(analysis_summary)
    )
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "report": response.content,
        "status": "complete"
    }
```

#### 3.2.3 工具模块 (agent/tools/)

```python
# agent/tools/search_tool.py
from langchain_core.tools import BaseTool
from serpapi import GoogleSearch
from typing import List, Dict
from ...config.settings import settings

class SearchTool(BaseTool):
    """搜索引擎工具"""
    
    name: str = "web_search"
    description: str = "搜索互联网获取最新信息"
    
    async def search(
        self, 
        query: str, 
        num_results: int = 10,
        language: str = "zh-cn"
    ) -> List[Dict]:
        """执行搜索"""
        
        params = {
            "q": query,
            "api_key": settings.serpapi_key,
            "num": num_results,
            "hl": language,
            "gl": "cn"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        return [
            {
                "title": r.get("title"),
                "url": r.get("link"),
                "snippet": r.get("snippet")
            }
            for r in results.get("organic_results", [])[:num_results]
        ]
    
    def _run(self, query: str) -> str:
        """同步调用（LangChain接口）"""
        import asyncio
        results = asyncio.run(self.search(query))
        return str(results)
```

```python
# agent/tools/scraper_tool.py
from langchain_core.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import Optional
from ...config.settings import settings

class ScraperTool(BaseTool):
    """网页爬取工具"""
    
    name: str = "web_scraper"
    description: str = "爬取指定URL的网页内容"
    
    def __init__(self):
        super().__init__()
        self._setup_driver()
    
    def _setup_driver(self):
        """初始化Selenium WebDriver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
    
    async def scrape(self, url: str) -> str:
        """爬取网页内容"""
        
        try:
            self.driver.get(url)
            
            # 等待页面加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            WebDriverWait(self.driver, settings.scrape_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 解析页面
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 提取文本
            text = soup.get_text(separator="\n", strip=True)
            
            # 清理文本
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            clean_text = "\n".join(lines)
            
            return clean_text[:5000]  # 限制长度
            
        except Exception as e:
            raise Exception(f"爬取失败: {url}, 错误: {str(e)}")
    
    def _run(self, url: str) -> str:
        """同步调用"""
        import asyncio
        return asyncio.run(self.scrape(url))
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'driver'):
            self.driver.quit()
```

```python
# agent/tools/vector_tool.py
from langchain_core.tools import BaseTool
from ...knowledge.vector_store import VectorStore
from typing import List, Dict

class VectorSearchTool(BaseTool):
    """向量检索工具"""
    
    name: str = "vector_search"
    description: str = "从知识库中检索相关信息"
    
    def __init__(self):
        super().__init__()
        self.vector_store = VectorStore()
    
    async def search(
        self, 
        query: str, 
        collection: str = "competitors",
        top_k: int = 5
    ) -> List[Dict]:
        """语义检索"""
        
        results = self.vector_store.search(
            query=query,
            collection=collection,
            top_k=top_k
        )
        
        return [
            {
                "content": r["document"],
                "metadata": r["metadata"],
                "score": r["distance"]
            }
            for r in results
        ]
    
    def _run(self, query: str) -> str:
        """同步调用"""
        import asyncio
        results = asyncio.run(self.search(query))
        return str(results)
```

#### 3.2.4 数据采集模块 (collector/)

```python
# collector/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    """采集器基类"""
    
    @abstractmethod
    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """采集数据"""
        pass
    
    @abstractmethod
    def parse(self, raw_data: Any) -> Dict[str, Any]:
        """解析数据"""
        pass
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗数据"""
        return data
```

```python
# collector/web_search.py
from .base import BaseCollector
from ..agent.tools.search_tool import SearchTool
from typing import Dict, Any, List

class WebSearchCollector(BaseCollector):
    """网页搜索采集器"""
    
    def __init__(self):
        self.search_tool = SearchTool()
    
    async def collect(
        self, 
        target: str, 
        keywords: List[str] = None,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """搜索采集"""
        
        if keywords is None:
            keywords = [target]
        
        all_results = []
        for keyword in keywords:
            results = await self.search_tool.search(
                query=keyword,
                num_results=num_results
            )
            all_results.extend(results)
        
        return {
            "target": target,
            "source": "web_search",
            "results": all_results,
            "count": len(all_results)
        }
    
    def parse(self, raw_data: Dict) -> Dict[str, Any]:
        """解析搜索结果"""
        return {
            "target": raw_data["target"],
            "urls": [r["url"] for r in raw_data["results"]],
            "titles": [r["title"] for r in raw_data["results"]],
            "snippets": [r["snippet"] for r in raw_data["results"]]
        }
```

```python
# collector/web_scraper.py
from .base import BaseCollector
from ..agent.tools.scraper_tool import ScraperTool
from typing import Dict, Any, List

class WebScraperCollector(BaseCollector):
    """网页爬取采集器"""
    
    def __init__(self):
        self.scraper_tool = ScraperTool()
    
    async def collect(
        self, 
        target: str, 
        urls: List[str]
    ) -> Dict[str, Any]:
        """爬取网页"""
        
        contents = []
        for url in urls:
            try:
                content = await self.scraper_tool.scrape(url)
                contents.append({
                    "url": url,
                    "content": content,
                    "status": "success"
                })
            except Exception as e:
                contents.append({
                    "url": url,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "target": target,
            "source": "web_scrape",
            "contents": contents,
            "success_count": sum(1 for c in contents if c["status"] == "success")
        }
    
    def parse(self, raw_data: Dict) -> Dict[str, Any]:
        """解析爬取内容"""
        return {
            "target": raw_data["target"],
            "contents": [
                {"url": c["url"], "text": c["content"]}
                for c in raw_data["contents"]
                if c["status"] == "success"
            ]
        }
```

#### 3.2.5 知识库模块 (knowledge/)

```python
# knowledge/vector_store.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from ..config.settings import settings

class VectorStore:
    """向量数据库管理"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    
    def get_or_create_collection(self, name: str):
        """获取或创建集合"""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ):
        """添加文档到向量库"""
        
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        collection: str = "competitors",
        top_k: int = 5,
        where: Dict = None
    ) -> List[Dict]:
        """语义检索"""
        
        collection_obj = self.get_or_create_collection(collection)
        
        results = collection_obj.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )
        
        return [
            {
                "document": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def delete_collection(self, name: str):
        """删除集合"""
        self.client.delete_collection(name)
```

```python
# knowledge/embeddings.py
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from typing import List
from ..config.settings import settings

class EmbeddingService:
    """Embedding服务"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量Embedding"""
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """单条Embedding"""
        return self.embeddings.embed_query(text)
```

#### 3.2.6 报告生成模块 (report/)

```python
# report/generator.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import Dict, Any
from ..config.prompts import REPORT_PROMPT
from ..config.settings import settings

class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.default_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
            temperature=0.3
        )
    
    async def generate(
        self,
        analysis_results: Dict[str, Any],
        report_type: str = "standard"
    ) -> str:
        """生成报告"""
        
        # 选择模板
        template = self._get_template(report_type)
        
        # 构建Prompt
        prompt = template.format(
            analysis_data=str(analysis_results)
        )
        
        # 生成报告
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        return response.content
    
    def _get_template(self, report_type: str) -> str:
        """获取报告模板"""
        
        templates = {
            "quick": QUICK_REPORT_PROMPT,
            "standard": REPORT_PROMPT,
            "deep": DEEP_REPORT_PROMPT
        }
        
        return templates.get(report_type, REPORT_PROMPT)
    
    async def export_markdown(self, report: str, filename: str):
        """导出Markdown文件"""
        
        filepath = f"{settings.report_output_dir}/{filename}.md"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        
        return filepath
    
    async def export_pdf(self, report: str, filename: str):
        """导出PDF文件"""
        
        # 使用markdown2和weasyprint转换
        import markdown2
        from weasyprint import HTML
        
        html_content = markdown2.markdown(report)
        filepath = f"{settings.report_output_dir}/{filename}.pdf"
        
        HTML(string=html_content).write_pdf(filepath)
        
        return filepath
```

#### 3.2.7 数据模型 (models/)

```python
# models/competitor.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ProductTier(BaseModel):
    """产品定价层级"""
    name: str
    price: str
    features: List[str] = []

class Product(BaseModel):
    """产品信息"""
    name: str
    description: str
    features: List[str] = []
    pricing: Optional[Dict[str, Any]] = None
    url: Optional[str] = None

class CompetitorInfo(BaseModel):
    """竞品信息"""
    competitor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company_name: str
    website: Optional[str] = None
    founded: Optional[str] = None
    location: Optional[str] = None
    funding: Optional[str] = None
    employees: Optional[str] = None
    products: List[Product] = []
    target_market: Optional[str] = None
    key_differentiators: List[str] = []
    sources: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CompetitorUpdate(BaseModel):
    """竞品更新记录"""
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competitor_id: str
    update_type: str  # product, pricing, news, etc.
    title: str
    content: str
    source: str
    detected_at: datetime = Field(default_factory=datetime.now)
```

```python
# models/report.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    """报告类型"""
    STANDARD = "standard"

class AnalysisDimension(str, Enum):
    """分析维度"""
    FEATURES = "features"
    PRICING = "pricing"
    SWOT = "swot"
    REVIEWS = "reviews"
    MARKET = "market"

class AnalysisRequest(BaseModel):
    """分析请求"""
    competitors: List[str]
    analysis_type: ReportType = ReportType.STANDARD
    dimensions: List[AnalysisDimension] = [
        AnalysisDimension.FEATURES,
        AnalysisDimension.PRICING,
        AnalysisDimension.SWOT
    ]
    my_product: Optional[str] = None  # 用于对比

class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: AnalysisRequest
    competitors_data: Dict[str, CompetitorInfo]
    feature_matrix: Optional[Dict[str, Any]] = None
    pricing_comparison: Optional[Dict[str, Any]] = None
    swot_analysis: Optional[Dict[str, str]] = None
    review_analysis: Optional[Dict[str, Any]] = None
    report: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class Report(BaseModel):
    """报告"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    report_type: ReportType
    content: str
    format: str = "markdown"  # markdown, pdf, json
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
```

---

## 4. API设计

### 4.1 API概览

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | ❌ |
| POST | /api/auth/login | 用户登录（返回JWT） | ❌ |
| POST | /api/analysis | 创建分析任务 | ✅ |
| GET | /api/analysis | 获取任务列表 | ✅ |
| GET | /api/analysis/{id} | 获取任务详情 | ✅ |
| DELETE | /api/analysis/{id} | 删除任务 | ✅ |
| POST | /api/competitors | 添加竞品 | ✅ |
| GET | /api/competitors | 获取竞品列表 | ✅ |
| GET | /api/competitors/{id} | 获取竞品详情 | ✅ |
| PUT | /api/competitors/{id} | 更新竞品 | ✅ |
| DELETE | /api/competitors/{id} | 删除竞品 | ✅ |
| GET | /api/reports | 获取报告列表 | ✅ |
| GET | /api/reports/{id} | 获取报告详情 | ✅ |
| DELETE | /api/reports/{id} | 删除报告 | ✅ |
| GET | /api/reports/{id}/export | 导出报告 | ✅ |
| POST | /api/qa/ask | 智能问答 | ✅ |
| WS | /ws/analysis/{id} | 分析进度推送 | ✅ (JWT token) |

### 4.2 接口详细设计

#### 4.2.1 创建分析任务

**请求**
```http
POST /api/v1/analysis
Content-Type: application/json
Authorization: Bearer {token}

{
    "competitors": ["竞品A", "竞品B", "竞品C"],
    "analysis_type": "standard",
    "dimensions": ["features", "pricing", "swot"],
    "my_product": "我的产品"
}
```

**响应**
```json
{
    "code": 200,
    "message": "分析任务已创建",
    "data": {
        "analysis_id": "anal_123456",
        "status": "processing",
        "estimated_time": 180,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 4.2.2 获取分析结果

**请求**
```http
GET /api/v1/analysis/anal_123456
Authorization: Bearer {token}
```

**响应**
```json
{
    "code": 200,
    "data": {
        "analysis_id": "anal_123456",
        "status": "completed",
        "competitors": ["竞品A", "竞品B", "竞品C"],
        "results": {
            "feature_matrix": {...},
            "pricing_comparison": {...},
            "swot_analysis": {...}
        },
        "report_summary": "竞品分析报告摘要...",
        "created_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:33:00Z"
    }
}
```

#### 4.2.3 智能问答

**请求**
```http
POST /api/v1/ask
Content-Type: application/json
Authorization: Bearer {token}

{
    "question": "竞品A和竞品B的核心差异是什么？",
    "context": {
        "competitors": ["竞品A", "竞品B"],
        "analysis_id": "anal_123456"
    }
}
```

**响应**
```json
{
    "code": 200,
    "data": {
        "answer": "竞品A和竞品B的核心差异主要体现在以下几个方面...",
        "sources": [
            {
                "competitor": "竞品A",
                "source": "https://example.com/competitor-a",
                "relevance": 0.92
            }
        ],
        "confidence": 0.85
    }
}
```

### 4.3 错误码

| 错误码 | 描述 | HTTP状态码 |
|--------|------|-----------|
| 10001 | 参数错误 | 400 |
| 10002 | 未授权 | 401 |
| 10003 | 资源不存在 | 404 |
| 10004 | 请求过频 | 429 |
| 20001 | 分析任务失败 | 500 |
| 20002 | 数据采集失败 | 500 |
| 20003 | LLM调用失败 | 500 |

---

## 5. 数据库设计

### 5.1 数据库选型

| 数据库 | 用途 | 选型理由 |
|--------|------|---------|
| SQLite | 结构化数据存储 | 轻量级、无需额外部署 |
| Chroma | 向量数据存储 | 专为Embedding优化 |
| Redis | 缓存与任务队列 | 高性能、支持过期策略 |

### 5.2 SQLite表设计

```sql
-- 用户表
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 竞品表（含应用商店 ID）
CREATE TABLE competitors (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    website TEXT,
    industry TEXT,
    tags TEXT,  -- JSON数组
    notes TEXT,
    google_play_id TEXT,  -- Google Play 包名
    app_store_id TEXT,    -- App Store trackId
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 分析任务表
CREATE TABLE analysis_tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    competitors TEXT NOT NULL,  -- JSON数组
    analysis_type TEXT NOT NULL,
    dimensions TEXT,  -- JSON数组
    my_product TEXT,
    status TEXT DEFAULT 'pending',
    result TEXT,  -- JSON对象
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 报告表
CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    analysis_id TEXT NOT NULL,
    title TEXT,
    report_type TEXT DEFAULT 'standard',
    format TEXT DEFAULT 'markdown',
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 5.3 Chroma集合设计

```
Collections:
├── competitors  # 竞品信息 + 网页内容向量
│   ├── documents: 竞品描述/网页内容
│   ├── metadatas: {competitor_id, type, user_id, source}
│   └── embeddings: openai / Chroma内置(all-MiniLM-L6-v2)
│
└── reviews  # 用户评价向量
    ├── documents: 评价内容
    ├── metadatas: {competitor_id, rating, source, user_id}
    └── embeddings: openai / Chroma内置(all-MiniLM-L6-v2)
```

---

## 6. 部署架构

### 6.1 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # API服务
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE=${OPENAI_API_BASE}
      - DEFAULT_MODEL=${DEFAULT_MODEL}
      - SERPAPI_KEY=${SERPAPI_KEY}
      - REDIS_URL=redis://redis:6379/0
      - CHROMA_PERSIST_DIR=/data/chroma
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
    restart: unless-stopped

  # React前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

  # Redis
  redis:
    image: redis:8.6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Celery Worker (可选)
  celery:
    build: .
    command: celery -A src.tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

### 6.2 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY pyproject.toml .
RUN pip install uv && uv pip install --system -e .

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.3 部署方案

**开发环境**
```bash
# 后端
uv pip install -e ".[dev]"
uvicorn src.api.app:app --reload

# 前端
cd frontend
npm install
npm run dev
```

**生产环境**
```bash
# Docker部署
docker-compose up -d

# 或使用Kubernetes
kubectl apply -f k8s/
```

---

## 7. 开发规范

### 7.1 代码风格

- 遵循PEP 8规范
- 使用type hints
- 函数和类必须有docstring
- 使用ruff进行代码格式化

```bash
# 格式化代码
ruff format .

# 检查代码
ruff check .
```

### 7.2 提交规范

```
<type>(<scope>): <subject>

类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例：
feat(agent): 添加SWOT分析功能
fix(scraper): 修复反爬检测问题
docs(api): 更新API文档
```

### 7.3 测试规范

```bash
# 运行测试
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

---

## 8. 性能优化

### 8.1 缓存策略

| 数据类型 | 缓存方式 | 过期时间 |
|---------|---------|---------|
| 竞品基础信息 | Redis | 24小时 |
| 搜索结果 | Redis | 1小时 |
| LLM响应 | Redis | 7天 |
| 向量检索结果 | 内存 | 5分钟 |

### 8.2 并发优化

- 使用asyncio进行异步IO
- 多数据源并行采集
- 批量Embedding计算
- 连接池管理

### 8.3 成本优化

- LLM调用结果缓存
- 小任务使用小模型（GPT-4o-mini）
- 批量处理减少API调用
- 向量检索替代部分LLM调用

---

## 9. 监控与日志

### 9.1 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 日志级别
logger.debug("调试信息")
logger.info("正常操作")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 9.2 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| API响应时间 | P95延迟 | >2秒 |
| 任务成功率 | 成功/总数 | <90% |
| LLM调用延迟 | 平均响应时间 | >10秒 |
| 错误率 | 错误/总请求 | >5% |
| 内存使用 | 进程内存 | >80% |

---

## 10. 安全设计

### 10.1 认证与授权

- JWT Token认证
- API Key管理
- 角色权限控制（可选）

### 10.2 数据安全

- 敏感配置使用环境变量
- API Key加密存储
- 数据传输HTTPS
- 定期备份

### 10.3 爬虫合规

- 遵守robots.txt
- 合理请求频率
- 用户代理标识
- 不采集敏感数据

---

## 附录

### A. 环境变量清单

```bash
# .env.example

# LLM配置（MIMO - OpenAI兼容格式）
OPENAI_API_KEY=your-mimo-api-key
OPENAI_API_BASE=https://api.mimo.com/v1
DEFAULT_MODEL=mimo

# SerpAPI配置
SERPAPI_KEY=xxx

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Chroma配置
CHROMA_PERSIST_DIR=./data/chroma

# 报告配置
REPORT_OUTPUT_DIR=./data/reports

# 安全配置
SECRET_KEY=xxx
JWT_EXPIRE_HOURS=24

# 爬虫配置
SCRAPE_TIMEOUT=30
MAX_RETRIES=3
REQUEST_DELAY=1.0
```

### B. 参考文档

- [LangChain文档](https://python.langchain.com/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Chroma文档](https://docs.trychroma.com/)
- [React文档](https://react.dev/)
- [shadcn/ui文档](https://ui.shadcn.com/)
- [Tailwind CSS文档](https://tailwindcss.com/)
- [Recharts文档](https://recharts.org/)
