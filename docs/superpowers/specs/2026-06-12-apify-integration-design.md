# Apify 应用商店评论采集集成方案

## 目标

集成 Apify 平台，替代之前的 Google Play 和华为应用市场采集器，实现：
- Google Play 评论采集
- App Store 评论采集
- 支持数量控制、评分筛选、排序方式

## 技术方案

### 1. 数据源

| 平台 | Actor ID | 功能 |
|------|----------|------|
| Google Play | `neatrat/google-play-store-reviews-scraper` | 抓取安卓应用评论 |
| App Store | `thewolves/appstore-reviews-scraper` | 抓取 iOS 应用评论 |

### 2. 认证方式

- Apify API Token（注册后获取）
- 配置在 `.env` 文件中：`APIFY_API_TOKEN=your_token`

### 3. 采集参数

**Google Play 参数：**
```python
{
    "appId": "com.alibaba.android.rimet",  # 应用包名
    "maxReviews": 50,                       # 最大评论数
    "lang": "zh",                           # 语言
    "country": "cn",                        # 国家/地区
    "minScore": 4,                          # 最低评分（可选）
    "sort": "NEWEST"                        # 排序：NEWEST/RATING/RELEVANCE
}
```

**App Store 参数：**
```python
{
    "appId": "123456789",                   # 应用 ID
    "maxReviews": 50,                       # 最大评论数
    "lang": "zh",                           # 语言
    "country": "cn",                        # 国家/地区
    "sort": "mostRecent"                    # 排序：mostRecent/mostHelpful/mostFavorable/mostCritical
}
```

### 4. 返回数据结构

```python
{
    "app_name": "钉钉",
    "store": "google_play",  # 或 "app_store"
    "rating": 4.2,
    "ratings_count": 150,
    "reviews": [
        {
            "user": "张三",
            "text": "很好用的办公软件",
            "rating": 5,
            "date": "2024-01-15",
            "version": "7.0.0"
        }
    ]
}
```

## 代码结构

### 1. 新建文件

**`collector/apify_collector.py`**
```python
"""
Apify 应用商店评论采集器
========================

通过 Apify 平台采集 Google Play 和 App Store 的评论数据。
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging

from .base import BaseCollector
from utils.cache import CacheManager, make_cache_key
from config.settings import settings

logger = logging.getLogger(__name__)

# Actor ID 配置
GOOGLE_PLAY_ACTOR = "neatrat/google-play-store-reviews-scraper"
APP_STORE_ACTOR = "thewolves/appstore-reviews-scraper"


class ApifyCollector(BaseCollector):
    """Apify 应用商店评论采集器"""

    def __init__(self):
        super().__init__(name="apify")
        self._cache = CacheManager(redis_url=settings.redis_url, prefix="apify")

    async def collect(
        self,
        app_id: str,
        store: str = "google",
        max_reviews: int = 50,
        lang: str = "zh",
        country: str = "cn",
        min_score: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        采集应用评论

        Args:
            app_id: 应用 ID（包名或 App Store ID）
            store: 商店类型 "google" 或 "apple"
            max_reviews: 最大评论数
            lang: 语言
            country: 国家/地区
            min_score: 最低评分筛选（仅 Google Play）
            sort: 排序方式
        """
        cache_key = make_cache_key("apify", store, app_id, str(max_reviews))
        cached = self._cache.get(cache_key)
        if cached is not None:
            self.logger.info(f"Apify 缓存命中: {app_id}")
            return cached

        try:
            from apify_client import ApifyClient

            client = ApifyClient(settings.apify_api_token)

            if store == "google":
                actor_id = GOOGLE_PLAY_ACTOR
                run_input = {
                    "appId": app_id,
                    "maxReviews": max_reviews,
                    "lang": lang,
                    "country": country,
                }
                if min_score:
                    run_input["minScore"] = min_score
                if sort:
                    run_input["sort"] = sort
            else:
                actor_id = APP_STORE_ACTOR
                run_input = {
                    "appId": app_id,
                    "maxReviews": max_reviews,
                    "lang": lang,
                    "country": country,
                }
                if sort:
                    run_input["sort"] = sort

            # 在 executor 中运行同步调用
            loop = asyncio.get_event_loop()
            run = await loop.run_in_executor(
                None,
                lambda: client.actor(actor_id).call(run_input=run_input)
            )

            # 获取结果
            dataset_items = list(
                client.dataset(run["defaultDatasetId"]).iterate_items()
            )

            raw_data = {
                "app_id": app_id,
                "store": store,
                "source": "apify",
                "reviews": dataset_items,
                "total_fetched": len(dataset_items),
            }

            self._cache.set(cache_key, raw_data, ttl=3600 * 12)
            return raw_data

        except Exception as e:
            self.logger.error(f"Apify 采集失败: {app_id}, 错误: {e}")
            return {"app_id": app_id, "store": store, "error": str(e), "status": "error"}

    def parse(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析 Apify 返回的数据"""
        if raw_data.get("status") == "error":
            return raw_data

        store = raw_data.get("store", "unknown")
        reviews = raw_data.get("reviews", [])

        if store == "google":
            return self._parse_google_play(raw_data, reviews)
        else:
            return self._parse_app_store(raw_data, reviews)

    def _parse_google_play(self, raw_data: Dict[str, Any], reviews: List[Dict]) -> Dict[str, Any]:
        """解析 Google Play 数据"""
        parsed_reviews = []
        for r in reviews:
            parsed_reviews.append({
                "user": r.get("userName", ""),
                "text": r.get("text", r.get("content", "")),
                "rating": r.get("score", r.get("rating", 0)),
                "date": r.get("at", r.get("date", "")),
                "version": r.get("version", ""),
            })

        ratings = [r["rating"] for r in parsed_reviews if r["rating"] > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "app_name": raw_data.get("app_name", raw_data.get("app_id", "")),
            "store": "google_play",
            "app_id": raw_data.get("app_id", ""),
            "rating": round(avg_rating, 1),
            "ratings_count": len(parsed_reviews),
            "reviews": parsed_reviews,
        }

    def _parse_app_store(self, raw_data: Dict[str, Any], reviews: List[Dict]) -> Dict[str, Any]:
        """解析 App Store 数据"""
        parsed_reviews = []
        for r in reviews:
            parsed_reviews.append({
                "user": r.get("userName", ""),
                "text": r.get("text", r.get("content", "")),
                "rating": r.get("score", r.get("rating", 0)),
                "date": r.get("date", ""),
                "version": r.get("version", ""),
            })

        ratings = [r["rating"] for r in parsed_reviews if r["rating"] > 0]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "app_name": raw_data.get("app_name", raw_data.get("app_id", "")),
            "store": "app_store",
            "app_id": raw_data.get("app_id", ""),
            "rating": round(avg_rating, 1),
            "ratings_count": len(parsed_reviews),
            "reviews": parsed_reviews,
        }

    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗数据"""
        cleaned = {k: v for k, v in data.items() if v is not None and v != ""}
        if "reviews" in cleaned:
            cleaned["reviews"] = [
                r for r in cleaned["reviews"]
                if r.get("text") or r.get("rating", 0) > 0
            ]
        return cleaned
```

### 2. 修改文件

**`config/settings.py`** - 添加配置
```python
# Apify 配置
apify_api_token: str = ""
```

**`.env`** - 添加环境变量
```env
# Apify 配置
APIFY_API_TOKEN=your_apify_token_here
```

**`collector/__init__.py`** - 添加导出
```python
from .apify_collector import ApifyCollector

__all__ = [
    # ... 其他导出
    "ApifyCollector",
]
```

**`agent/nodes/searcher.py`** - 集成到搜索节点

```python
# 添加映射
GOOGLE_PLAY_APPS = {
    "钉钉": "com.alibaba.android.rimet",
    "企业微信": "com.tencent.wework",
    "飞书文档": "com.ss.android.lark",
}

APP_STORE_APPS = {
    "钉钉": "982102496",  # App Store ID
    "企业微信": "982102496",
    "飞书文档": "982102496",
}

# 在 _collect_one 中添加
# 3. Google Play（按需）
if name_lower in GOOGLE_PLAY_APPS:
    app_id = GOOGLE_PLAY_APPS[name_lower]
    async def _gp(aid=app_id):
        try:
            result = await apify_collector.run(
                aid, store="google", max_reviews=50, min_score=4
            )
            logger.info(f"  [{name}] Google Play 完成: ⭐{result.get('data', {}).get('rating', 0)}")
            return {"competitor": name, "source": "google_play", "data": result.get("data", {})}
        except Exception as e:
            logger.warning(f"  [{name}] Google Play 失败: {e}")
            return None
    tasks.append(_gp())

# 4. App Store（按需）
if name_lower in APP_STORE_APPS:
    app_id = APP_STORE_APPS[name_lower]
    async def _as(aid=app_id):
        try:
            result = await apify_collector.run(
                aid, store="apple", max_reviews=50
            )
            logger.info(f"  [{name}] App Store 完成: ⭐{result.get('data', {}).get('rating', 0)}")
            return {"competitor": name, "source": "app_store", "data": result.get("data", {})}
        except Exception as e:
            logger.warning(f"  [{name}] App Store 失败: {e}")
            return None
    tasks.append(_as())
```

**`requirements.txt`** - 添加依赖
```
apify-client>=1.6.0
```

## 需要准备的信息

1. **Apify API Token**
   - 注册 [apify.com](https://apify.com)
   - Settings → Integrations → API Token

2. **应用 ID 映射表**

   | 竞品 | Google Play 包名 | App Store ID |
   |------|-----------------|--------------|
   | 钉钉 | com.alibaba.android.rimet | ? |
   | 企业微信 | com.tencent.wework | ? |
   | 飞书文档 | com.ss.android.lark | ? |
   | Notion | notion.id | ? |
   | Obsidian | md.obsidian | ? |

3. **Actor 参数确认**
   - 需要测试 `neatrat/google-play-store-reviews-scraper` 的实际参数
   - 需要测试 `thewolves/appstore-reviews-scraper` 的实际参数

## 实施步骤

1. 注册 Apify 账号，获取 API Token
2. 安装依赖：`pip install apify-client`
3. 新建 `collector/apify_collector.py`
4. 修改 `config/settings.py` 添加配置
5. 修改 `.env` 添加 Token
6. 修改 `collector/__init__.py` 添加导出
7. 修改 `agent/nodes/searcher.py` 集成采集器
8. 填写应用 ID 映射表
9. 测试采集功能

## 注意事项

- Apify 免费额度：每月 $5（约 5000 条评论）
- 首次运行需要几秒钟启动 Actor
- 结果会缓存 12 小时，避免重复调用
- 需要网络可访问 apify.com（国内可能需要代理）
