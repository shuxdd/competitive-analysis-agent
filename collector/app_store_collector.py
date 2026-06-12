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
        """解析应用商店数据"""
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
        """搜索应用"""
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
        """获取应用评论"""
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
        """获取应用详情"""
        return await self.run(app_id, store=store)
