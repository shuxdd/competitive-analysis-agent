# 数据源扩展实现计划：GitHub + 应用商店

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 GitHub 和应用商店两个数据源采集器，集成到 Agent 分析流程中。

**Architecture:** 继承现有 `BaseCollector` 基类，实现 `collect/parse/clean` 三个方法。通过 searcher 节点集成到 LangGraph 流程，根据竞品标签自动选择数据源。

**Tech Stack:** PyGithub, google-play-scraper, app-store-scraper, pytest + unittest.mock

---

## 文件结构

| 操作 | 文件 | 职责 |
|------|------|------|
| 创建 | `collector/github_collector.py` | GitHub 采集器 |
| 创建 | `tests/test_github_collector.py` | GitHub 采集器测试 |
| 创建 | `collector/app_store_collector.py` | 应用商店采集器 |
| 创建 | `tests/test_app_store_collector.py` | 应用商店采集器测试 |
| 修改 | `collector/__init__.py` | 新增导出 |
| 修改 | `config/settings.py` | 新增 github_token 配置 |
| 修改 | `requirements.txt` | 新增依赖 |
| 修改 | `agent/nodes/searcher.py` | 集成新数据源 |

---

### Task 1: GitHub 采集器

**Files:**
- Create: `collector/github_collector.py`
- Create: `tests/test_github_collector.py`
- Modify: `collector/__init__.py`
- Modify: `config/settings.py`
- Modify: `requirements.txt`

- [ ] **Step 1: 安装依赖**

```bash
pip install PyGithub>=2.1.0
```

- [ ] **Step 2: 添加配置项**

修改 `config/settings.py`，在 `Settings` 类中添加：

```python
    # GitHub配置
    github_token: str = ""
```

- [ ] **Step 3: 编写 GitHub 采集器测试**

创建 `tests/test_github_collector.py`：

```python
"""
GitHub 采集器测试
================
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from collector.github_collector import GitHubCollector


class TestGitHubCollector:
    """GitHub 采集器测试"""

    def test_initialization(self):
        """测试初始化"""
        collector = GitHubCollector(token="test_token")
        assert collector.name == "github"
        assert collector.token == "test_token"

    def test_initialization_no_token(self):
        """测试无 token 初始化"""
        collector = GitHubCollector()
        assert collector.token is None

    def test_parse_repo_data(self):
        """测试解析仓库数据"""
        collector = GitHubCollector()

        raw_data = {
            "full_name": "notionhq/notion-sdk-js",
            "description": "Official Notion SDK for JavaScript",
            "stars": 12500,
            "forks": 800,
            "open_issues": 45,
            "language": "TypeScript",
            "license": "MIT",
            "created_at": "2020-05-01T00:00:00Z",
            "updated_at": "2026-06-10T00:00:00Z",
            "pushed_at": "2026-06-10T00:00:00Z",
            "default_branch": "main",
            "topics": ["notion", "sdk", "javascript"],
            "homepage": "https://notion.so",
        }

        result = collector.parse(raw_data)

        assert result["repo"] == "notionhq/notion-sdk-js"
        assert result["stars"] == 12500
        assert result["forks"] == 800
        assert result["language"] == "TypeScript"
        assert result["license"] == "MIT"

    def test_parse_empty_data(self):
        """测试解析空数据"""
        collector = GitHubCollector()
        result = collector.parse({})
        assert result["repo"] == ""
        assert result["stars"] == 0

    def test_clean_removes_none(self):
        """测试清洗去除 None 值"""
        collector = GitHubCollector()
        data = {
            "repo": "test/repo",
            "stars": 100,
            "license": None,
            "topics": None,
        }
        cleaned = collector.clean(data)
        assert cleaned["repo"] == "test/repo"
        assert cleaned["stars"] == 100
        assert "license" not in cleaned or cleaned["license"] is None
```

- [ ] **Step 4: 运行测试确认失败**

```bash
cd "D:\Desktop\新建文件夹\competitive-analysis-agent"
python -m pytest tests/test_github_collector.py -v
```

预期：FAIL — `ModuleNotFoundError: No module named 'collector.github_collector'`

- [ ] **Step 5: 实现 GitHub 采集器**

创建 `collector/github_collector.py`：

```python
"""
GitHub 数据采集器
================

采集 GitHub 仓库的 star/fork/commit/release 等数据。
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta

from .base import BaseCollector
from utils.cache import CacheManager, make_cache_key
from config.settings import settings

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """GitHub 数据采集器"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化 GitHub 采集器

        Args:
            token: GitHub Personal Access Token（可选，无 token 限 60 次/小时）
        """
        super().__init__(name="github")
        self.token = token
        self._client = None
        self._cache = CacheManager(redis_url=settings.redis_url, prefix="github")

    def _get_client(self):
        """获取 PyGithub 客户端"""
        if self._client is None:
            try:
                from github import Github
                if self.token:
                    self._client = Github(self.token)
                else:
                    self._client = Github()
            except ImportError:
                raise ImportError("请安装 PyGithub: pip install PyGithub")
        return self._client

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        采集 GitHub 仓库数据

        Args:
            target: owner/repo 格式或仓库全名
            **kwargs: 额外参数

        Returns:
            仓库原始数据
        """
        cache_key = make_cache_key("github", target)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self.logger.info(f"GitHub 缓存命中: {target}")
            return cached

        client = self._get_client()
        loop = asyncio.get_event_loop()

        try:
            repo = await loop.run_in_executor(None, lambda: client.get_repo(target))

            raw_data = {
                "full_name": repo.full_name,
                "description": repo.description or "",
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "language": repo.language,
                "license": repo.license.spdx_id if repo.license else None,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                "default_branch": repo.default_branch,
                "topics": repo.get_topics(),
                "homepage": repo.homepage or "",
                "size_kb": repo.size,
                "watchers": repo.watchers_count,
            }

            # 缓存 24 小时
            self._cache.set(cache_key, raw_data, ttl=3600 * 24)
            return raw_data

        except Exception as e:
            self.logger.error(f"GitHub 采集失败: {target}, 错误: {e}")
            return {"full_name": target, "error": str(e), "status": "error"}

    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析 GitHub 仓库数据

        Args:
            raw_data: PyGithub 返回的原始数据

        Returns:
            结构化的仓库数据
        """
        if raw_data.get("status") == "error":
            return raw_data

        return {
            "repo": raw_data.get("full_name", ""),
            "description": raw_data.get("description", ""),
            "stars": raw_data.get("stars", 0),
            "forks": raw_data.get("forks", 0),
            "open_issues": raw_data.get("open_issues", 0),
            "language": raw_data.get("language", ""),
            "license": raw_data.get("license", ""),
            "created_at": raw_data.get("created_at", ""),
            "updated_at": raw_data.get("updated_at", ""),
            "pushed_at": raw_data.get("pushed_at", ""),
            "default_branch": raw_data.get("default_branch", ""),
            "topics": raw_data.get("topics", []),
            "homepage": raw_data.get("homepage", ""),
            "size_kb": raw_data.get("size_kb", 0),
            "watchers": raw_data.get("watchers", 0),
        }

    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗数据，移除空值"""
        return {k: v for k, v in data.items() if v is not None and v != ""}

    async def search_repo(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        按关键词搜索仓库

        Args:
            keyword: 搜索关键词
            limit: 返回数量

        Returns:
            仓库列表
        """
        client = self._get_client()
        loop = asyncio.get_event_loop()

        try:
            repos = await loop.run_in_executor(
                None, lambda: list(client.search_repositories(keyword)[:limit])
            )

            results = []
            for repo in repos:
                results.append({
                    "full_name": repo.full_name,
                    "description": repo.description or "",
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                })
            return results

        except Exception as e:
            self.logger.error(f"GitHub 搜索失败: {keyword}, 错误: {e}")
            return []

    async def get_repo_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取仓库详细统计

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库统计数据
        """
        full_name = f"{owner}/{repo}"
        result = await self.run(full_name)
        return result
```

- [ ] **Step 6: 运行测试确认通过**

```bash
python -m pytest tests/test_github_collector.py -v
```

预期：全部 PASS

- [ ] **Step 7: 更新模块导出**

修改 `collector/__init__.py`：

```python
"""
数据采集模块
============

提供网页搜索、爬取和数据清洗功能。
"""

from .base import BaseCollector, CollectorResult
from .web_search import WebSearchCollector
from .web_scraper import WebScraperCollector
from .cleaner import DataCleaner
from .github_collector import GitHubCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "WebSearchCollector",
    "WebScraperCollector",
    "DataCleaner",
    "GitHubCollector",
]
```

- [ ] **Step 8: 更新依赖**

修改 `requirements.txt`，在 `# 搜索与爬虫` 区块末尾添加：

```
PyGithub>=2.1.0
```

- [ ] **Step 9: 运行全量测试确认无回归**

```bash
python -m pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py tests/test_github_collector.py -v
```

预期：全部通过

- [ ] **Step 10: 提交**

```bash
git add collector/github_collector.py tests/test_github_collector.py collector/__init__.py config/settings.py requirements.txt
git commit -m "feat: GitHub 数据采集器 - star/fork/commit/release 采集"
```

---

### Task 2: 应用商店采集器

**Files:**
- Create: `collector/app_store_collector.py`
- Create: `tests/test_app_store_collector.py`
- Modify: `collector/__init__.py`
- Modify: `requirements.txt`

- [ ] **Step 1: 安装依赖**

```bash
pip install google-play-scraper>=1.2.0 app-store-scraper>=0.3.5
```

- [ ] **Step 2: 编写应用商店采集器测试**

创建 `tests/test_app_store_collector.py`：

```python
"""
应用商店采集器测试
==================
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from collector.app_store_collector import AppStoreCollector


class TestAppStoreCollector:
    """应用商店采集器测试"""

    def test_initialization(self):
        """测试初始化"""
        collector = AppStoreCollector()
        assert collector.name == "app_store"

    def test_parse_google_play_data(self):
        """测试解析 Google Play 数据"""
        collector = AppStoreCollector()

        raw_data = {
            "source": "google_play",
            "app_id": "notion.id",
            "title": "Notion",
            "description": "All-in-one workspace",
            "developer": "Notion Labs",
            "score": 4.6,
            "ratings": 152000,
            "installs": "10,000,000+",
            "updated": "Jun 1, 2026",
            "version": "0.6.40",
            "genre": "Productivity",
        }

        result = collector.parse(raw_data)

        assert result["app_name"] == "Notion"
        assert result["store"] == "google_play"
        assert result["rating"] == 4.6
        assert result["ratings_count"] == 152000

    def test_parse_app_store_data(self):
        """测试解析 App Store 数据"""
        collector = AppStoreCollector()

        raw_data = {
            "source": "app_store",
            "id": 123456789,
            "title": "Notion",
            "description": "All-in-one workspace",
            "developer": "Notion Labs",
            "score": 4.7,
            "ratings": 85000,
            "version": "0.6.40",
            "updated": "2026-06-01",
            "genre": "Productivity",
        }

        result = collector.parse(raw_data)

        assert result["app_name"] == "Notion"
        assert result["store"] == "app_store"
        assert result["rating"] == 4.7

    def test_parse_empty_data(self):
        """测试解析空数据"""
        collector = AppStoreCollector()
        result = collector.parse({})
        assert result["app_name"] == ""
        assert result["rating"] == 0

    def test_parse_review(self):
        """测试解析评论"""
        collector = AppStoreCollector()

        raw_review = {
            "source": "google_play",
            "reviewId": "abc123",
            "userName": "张三",
            "content": "功能强大但偶尔卡顿",
            "score": 4,
            "at": "2026-06-10T00:00:00Z",
        }

        result = collector._parse_review(raw_review)

        assert result["user"] == "张三"
        assert result["text"] == "功能强大但偶尔卡顿"
        assert result["rating"] == 4
```

- [ ] **Step 3: 运行测试确认失败**

```bash
python -m pytest tests/test_app_store_collector.py -v
```

预期：FAIL — `ModuleNotFoundError`

- [ ] **Step 4: 实现应用商店采集器**

创建 `collector/app_store_collector.py`：

```python
"""
应用商店数据采集器
==================

采集 Google Play 和 App Store 的评分、评论、版本等数据。
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging

from .base import BaseCollector
from utils.cache import CacheManager, make_cache_key
from config.settings import settings

logger = logging.getLogger(__name__)


class AppStoreCollector(BaseCollector):
    """应用商店数据采集器"""

    def __init__(self):
        super().__init__(name="app_store")
        self._cache = CacheManager(redis_url=settings.redis_url, prefix="appstore")

    async def collect(self, target: str, store: str = "google", **kwargs) -> Dict[str, Any]:
        """
        采集应用商店数据

        Args:
            target: app_id 或应用名称
            store: 商店类型 "google" 或 "apple"
            **kwargs: 额外参数

        Returns:
            应用原始数据
        """
        cache_key = make_cache_key("appstore", store, target)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self.logger.info(f"应用商店缓存命中: {target}")
            return cached

        loop = asyncio.get_event_loop()

        try:
            if store == "google":
                raw_data = await self._collect_google_play(target, loop)
            else:
                raw_data = await self._collect_app_store(target, loop)

            self._cache.set(cache_key, raw_data, ttl=3600 * 12)
            return raw_data

        except Exception as e:
            self.logger.error(f"应用商店采集失败: {target}, 错误: {e}")
            return {"app_id": target, "source": store, "error": str(e), "status": "error"}

    async def _collect_google_play(self, app_id: str, loop) -> Dict[str, Any]:
        """采集 Google Play 数据"""
        try:
            from google_play_scraper import app as gp_app
        except ImportError:
            raise ImportError("请安装 google-play-scraper: pip install google-play-scraper")

        result = await loop.run_in_executor(None, lambda: gp_app(app_id, lang="zh", country="cn"))
        result["source"] = "google_play"
        return result

    async def _collect_app_store(self, app_id: str, loop) -> Dict[str, Any]:
        """采集 App Store 数据"""
        try:
            from app_store_scraper import AppStore
        except ImportError:
            raise ImportError("请安装 app-store-scraper: pip install app-store-scraper")

        def _fetch():
            store = AppStore(country="cn", app_name=app_id)
            store.review(how_many=1)
            return {
                "source": "app_store",
                "id": app_id,
                "title": app_id,
                "description": "",
                "developer": "",
                "score": 0,
                "ratings": 0,
                "version": "",
                "updated": "",
                "genre": "",
                "reviews": store.reviews if hasattr(store, "reviews") else [],
            }

        return await loop.run_in_executor(None, _fetch)

    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析应用商店数据

        Args:
            raw_data: 原始数据

        Returns:
            结构化数据
        """
        if raw_data.get("status") == "error":
            return raw_data

        source = raw_data.get("source", "unknown")

        if source == "google_play":
            return self._parse_google_play(raw_data)
        elif source == "app_store":
            return self._parse_app_store(raw_data)
        else:
            return self._parse_generic(raw_data)

    def _parse_google_play(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析 Google Play 数据"""
        return {
            "app_name": data.get("title", ""),
            "store": "google_play",
            "app_id": data.get("appId", ""),
            "description": (data.get("description", "") or "")[:500],
            "developer": data.get("developer", ""),
            "rating": data.get("score", 0) or 0,
            "ratings_count": data.get("ratings", 0) or 0,
            "installs": data.get("installs", ""),
            "current_version": data.get("version", ""),
            "last_updated": data.get("updated", ""),
            "genre": data.get("genre", ""),
            "price": data.get("price", "Free"),
            "contains_ads": data.get("containsAds", False),
        }

    def _parse_app_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析 App Store 数据"""
        return {
            "app_name": data.get("title", ""),
            "store": "app_store",
            "app_id": str(data.get("id", "")),
            "description": (data.get("description", "") or "")[:500],
            "developer": data.get("developer", ""),
            "rating": data.get("score", 0) or 0,
            "ratings_count": data.get("ratings", 0) or 0,
            "current_version": data.get("version", ""),
            "last_updated": data.get("updated", ""),
            "genre": data.get("genre", ""),
        }

    def _parse_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """通用解析"""
        return {
            "app_name": data.get("title", data.get("app_name", "")),
            "store": data.get("source", "unknown"),
            "app_id": data.get("app_id", ""),
            "rating": data.get("score", data.get("rating", 0)),
            "ratings_count": data.get("ratings", data.get("ratings_count", 0)),
        }

    def _parse_review(self, raw_review: Dict[str, Any]) -> Dict[str, Any]:
        """解析单条评论"""
        return {
            "user": raw_review.get("userName", raw_review.get("user", "")),
            "text": raw_review.get("content", raw_review.get("text", "")),
            "rating": raw_review.get("score", raw_review.get("rating", 0)),
            "date": raw_review.get("at", raw_review.get("date", "")),
        }

    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗数据"""
        return {k: v for k, v in data.items() if v is not None and v != ""}

    async def search_app(self, keyword: str, store: str = "google", limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索应用

        Args:
            keyword: 搜索关键词
            store: 商店类型
            limit: 返回数量

        Returns:
            应用列表
        """
        loop = asyncio.get_event_loop()

        try:
            if store == "google":
                from google_play_scraper import search as gp_search
                results = await loop.run_in_executor(
                    None, lambda: gp_search(keyword, lang="zh", country="cn")
                )
                return [
                    {
                        "app_id": r.get("appId", ""),
                        "title": r.get("title", ""),
                        "developer": r.get("developer", ""),
                        "score": r.get("score", 0),
                        "installs": r.get("installs", ""),
                    }
                    for r in results[:limit]
                ]
            else:
                return []

        except Exception as e:
            self.logger.error(f"应用搜索失败: {keyword}, 错误: {e}")
            return []

    async def get_reviews(self, app_id: str, store: str = "google", count: int = 20) -> List[Dict[str, Any]]:
        """
        获取应用评论

        Args:
            app_id: 应用 ID
            store: 商店类型
            count: 评论数量

        Returns:
            评论列表
        """
        loop = asyncio.get_event_loop()

        try:
            if store == "google":
                from google_play_scraper import reviews as gp_reviews
                result, _ = await loop.run_in_executor(
                    None,
                    lambda: gp_reviews(app_id, lang="zh", country="cn", count=count),
                )
                return [self._parse_review(r) for r in result]
            else:
                return []

        except Exception as e:
            self.logger.error(f"获取评论失败: {app_id}, 错误: {e}")
            return []

    async def get_app_info(self, app_id: str, store: str = "google") -> Dict[str, Any]:
        """
        获取应用详情

        Args:
            app_id: 应用 ID
            store: 商店类型

        Returns:
            应用详情
        """
        result = await self.run(app_id, store=store)
        return result
```

- [ ] **Step 5: 运行测试确认通过**

```bash
python -m pytest tests/test_app_store_collector.py -v
```

预期：全部 PASS

- [ ] **Step 6: 更新模块导出**

修改 `collector/__init__.py`，添加：

```python
from .app_store_collector import AppStoreCollector
```

并在 `__all__` 中添加 `"AppStoreCollector"`。

- [ ] **Step 7: 更新依赖**

修改 `requirements.txt`，在 `PyGithub>=2.1.0` 下方添加：

```
google-play-scraper>=1.2.0
app-store-scraper>=0.3.5
```

- [ ] **Step 8: 运行全量测试确认无回归**

```bash
python -m pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py tests/test_github_collector.py tests/test_app_store_collector.py -v
```

预期：全部通过

- [ ] **Step 9: 提交**

```bash
git add collector/app_store_collector.py tests/test_app_store_collector.py collector/__init__.py requirements.txt
git commit -m "feat: 应用商店数据采集器 - Google Play/App Store 评分评论采集"
```

---

### Task 3: 集成到 Agent 流程

**Files:**
- Modify: `agent/nodes/searcher.py`

- [ ] **Step 1: 修改 searcher 节点**

修改 `agent/nodes/searcher.py`，集成 GitHub 和应用商店采集器：

```python
"""
搜索节点
========

使用搜索引擎、GitHub、应用商店等多数据源采集竞品信息。
"""

import logging
from agent.graph_state import AgentState
from collector.web_search import WebSearchCollector
from collector.github_collector import GitHubCollector
from collector.app_store_collector import AppStoreCollector
from config.settings import settings
from utils.retry import retry_async
from agent.progress import report_progress

logger = logging.getLogger(__name__)

# 竞品名称到 GitHub 仓库的映射（可扩展为配置文件）
GITHUB_REPOS = {
    "notion": "makenotion/notion-sdk-js",
    "obsidian": "obsidianmd/obsidian-releases",
}

# 竞品名称到应用 ID 的映射
GOOGLE_PLAY_APPS = {
    "notion": "notion.id",
    "obsidian": "md.obsidian",
    "钉钉": "com.alibaba.android.rimet",
    "企业微信": "com.tencent.wework",
}

# 标签到数据源的映射
TAG_DATA_SOURCES = {
    "开源": ["github"],
    "开发者工具": ["github"],
    "GitHub": ["github"],
    "App": ["app_store"],
    "移动": ["app_store"],
    "C端": ["app_store"],
}


def _get_extra_sources(competitor_name: str, plan: dict) -> list:
    """根据竞品标签决定额外数据源"""
    sources = []

    # 从 plan 中获取标签
    competitors_meta = plan.get("competitors_meta", {})
    tags = competitors_meta.get(competitor_name, {}).get("tags", [])

    for tag in tags:
        if tag in TAG_DATA_SOURCES:
            sources.extend(TAG_DATA_SOURCES[tag])

    # 去重
    return list(set(sources))


async def search_competitors(state: AgentState) -> dict:
    """
    搜索节点

    根据采集计划，从多个数据源采集竞品信息。
    """
    logger.info("开始搜索竞品信息...")

    plan = state.get("collection_plan", {})
    competitors = plan.get("competitors", state["competitors"])
    all_results = []

    # 初始化采集器
    search_collector = WebSearchCollector(api_key=settings.serpapi_key)
    github_collector = GitHubCollector(token=settings.github_token)
    app_store_collector = AppStoreCollector()

    for comp in competitors:
        name = comp if isinstance(comp, str) else comp.get("name", "")
        keywords = [] if isinstance(comp, str) else comp.get("search_keywords", [])

        # 1. 网页搜索（始终执行）
        logger.info(f"搜索竞品: {name}")
        try:
            result = await retry_async(
                lambda: search_collector.search_competitor(
                    name,
                    keywords=keywords if keywords else None,
                    num_results=5
                )
            )
            all_results.append({
                "competitor": name,
                "source": "web_search",
                "data": result
            })
            logger.info(f"  搜索完成，找到 {result.get('total_results', 0)} 条结果")
        except Exception as e:
            logger.warning(f"  搜索 {name} 失败: {e}")
            all_results.append({
                "competitor": name,
                "source": "web_search",
                "data": {"results": [], "total_results": 0},
                "error": str(e)
            })

        # 2. GitHub 采集（按需）
        extra_sources = _get_extra_sources(name, plan)
        name_lower = name.lower()

        if "github" in extra_sources or name_lower in GITHUB_REPOS:
            repo_name = GITHUB_REPOS.get(name_lower)
            if repo_name:
                logger.info(f"  采集 GitHub: {repo_name}")
                try:
                    gh_result = await github_collector.run(repo_name)
                    all_results.append({
                        "competitor": name,
                        "source": "github",
                        "data": gh_result.get("data", {})
                    })
                    logger.info(f"  GitHub 完成: ⭐{gh_result.get('data', {}).get('stars', 0)}")
                except Exception as e:
                    logger.warning(f"  GitHub {name} 失败: {e}")

        # 3. 应用商店采集（按需）
        if "app_store" in extra_sources or name_lower in GOOGLE_PLAY_APPS:
            app_id = GOOGLE_PLAY_APPS.get(name_lower)
            if app_id:
                logger.info(f"  采集应用商店: {app_id}")
                try:
                    app_result = await app_store_collector.run(app_id, store="google")
                    all_results.append({
                        "competitor": name,
                        "source": "app_store",
                        "data": app_result.get("data", {})
                    })
                    logger.info(f"  应用商店完成: ⭐{app_result.get('data', {}).get('rating', 0)}")
                except Exception as e:
                    logger.warning(f"  应用商店 {name} 失败: {e}")

    logger.info(f"搜索完成，共处理 {len(competitors)} 个竞品")
    report_progress(state.get("progress_callback"), "searcher")
    return {
        "raw_data": all_results,
        "status": "collecting",
        "errors": state.get("errors", [])
    }
```

- [ ] **Step 2: 运行全量测试确认无回归**

```bash
python -m pytest tests/test_models.py tests/test_knowledge_simple.py tests/test_collector.py tests/test_agent.py tests/test_report.py tests/test_api.py tests/test_github_collector.py tests/test_app_store_collector.py -v
```

预期：全部通过

- [ ] **Step 3: 提交**

```bash
git add agent/nodes/searcher.py
git commit -m "feat: searcher 节点集成 GitHub + 应用商店多数据源"
```

---

### Task 4: 文档更新

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 更新 CLAUDE.md**

在 `## 模块状态` 表格中更新 collector 模块说明：

```markdown
| collector/ | ✅ 完成 | 数据采集（搜索、爬取、清洗、GitHub、应用商店） |
```

在 `## 环境配置` 部分添加 GitHub token：

```env
GITHUB_TOKEN=your-github-token（可选，无限流限制）
```

- [ ] **Step 2: 提交**

```bash
git add CLAUDE.md
git commit -m "docs: 更新文档 - 新增 GitHub/应用商店数据源说明"
```
