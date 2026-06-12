"""
GitHub 数据采集器
================

采集 GitHub 仓库的 star/fork/commit/release 等数据。
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging

from .base import BaseCollector
from utils.cache import CacheManager, make_cache_key
from config.settings import settings

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """GitHub 数据采集器"""

    def __init__(self, token: Optional[str] = None):
        super().__init__(name="github")
        self.token = token
        self._client = None
        self._cache = CacheManager(redis_url=settings.redis_url, prefix="github")

    def _get_client(self):
        """获取 PyGithub 客户端"""
        if self._client is None:
            try:
                from github import Github
                self._client = Github(self.token) if self.token else Github()
            except ImportError:
                raise ImportError("请安装 PyGithub: pip install PyGithub")
        return self._client

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        采集 GitHub 仓库数据

        Args:
            target: owner/repo 格式
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

            self._cache.set(cache_key, raw_data, ttl=3600 * 24)
            return raw_data

        except Exception as e:
            self.logger.error(f"GitHub 采集失败: {target}, 错误: {e}")
            return {"full_name": target, "error": str(e), "status": "error"}

    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析 GitHub 仓库数据"""
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
        """按关键词搜索仓库"""
        client = self._get_client()
        loop = asyncio.get_event_loop()

        try:
            repos = await loop.run_in_executor(
                None, lambda: list(client.search_repositories(keyword)[:limit])
            )
            return [
                {
                    "full_name": r.full_name,
                    "description": r.description or "",
                    "stars": r.stargazers_count,
                    "forks": r.forks_count,
                    "language": r.language,
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                }
                for r in repos
            ]
        except Exception as e:
            self.logger.error(f"GitHub 搜索失败: {keyword}, 错误: {e}")
            return []

    async def get_repo_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库详细统计"""
        return await self.run(f"{owner}/{repo}")
