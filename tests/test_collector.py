"""
数据采集模块测试
================

测试数据采集和清洗功能。
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from collector.base import BaseCollector, CollectorResult
from collector.web_search import WebSearchCollector
from collector.web_scraper import WebScraperCollector
from collector.cleaner import DataCleaner
from collector.apify_collector import ApifyCollector


class TestBaseCollector:
    """基础采集器测试"""

    def test_collector_result_creation(self):
        """测试采集结果创建"""
        result = CollectorResult(
            status="success",
            target="test",
            source="test_collector",
            data={"key": "value"}
        )

        assert result.is_success
        assert result.status == "success"
        assert result.target == "test"
        assert result.data == {"key": "value"}

    def test_collector_result_error(self):
        """测试错误结果"""
        result = CollectorResult(
            status="error",
            target="test",
            source="test_collector",
            error="测试错误"
        )

        assert not result.is_success
        assert result.error == "测试错误"

    def test_collector_result_to_dict(self):
        """测试结果转字典"""
        result = CollectorResult(
            status="success",
            target="test",
            source="test_collector"
        )

        data = result.to_dict()
        assert "status" in data
        assert "target" in data
        assert "source" in data


class TestDataCleaner:
    """数据清洗测试"""

    def test_clean_text(self):
        """测试文本清理"""
        text = "  Hello   World  \n\n  Test  "
        cleaned = DataCleaner.clean_text(text)
        assert cleaned == "Hello World\n\nTest"

    def test_clean_text_html(self):
        """测试HTML清理"""
        html = "<p>Hello <b>World</b></p>"
        cleaned = DataCleaner.clean_text(html)
        assert cleaned == "Hello World"

    def test_extract_price_cny(self):
        """测试人民币价格提取"""
        text = "基础版¥99/月，专业版¥299/月"
        prices = DataCleaner.extract_price(text)

        assert len(prices) >= 2
        assert any(p["price"] == 99 for p in prices)
        assert any(p["price"] == 299 for p in prices)

    def test_extract_price_usd(self):
        """测试美元价格提取"""
        text = "Basic $9/month, Pro $29/month"
        prices = DataCleaner.extract_price(text)

        assert len(prices) >= 2
        assert any(p["price"] == 9 for p in prices)
        assert any(p["price"] == 29 for p in prices)

    def test_extract_features(self):
        """测试功能提取"""
        text = "支持文档管理，提供知识库功能，具备项目管理能力"
        features = DataCleaner.extract_features(text)

        assert len(features) > 0
        assert any("文档管理" in f for f in features)

    def test_extract_company_info(self):
        """测试公司信息提取"""
        text = "公司成立于2020年，总部位于北京，获得A轮融资1000万美元"
        info = DataCleaner.extract_company_info(text)

        assert info.get("founded") == "2020"
        assert "北京" in info.get("location", "")

    def test_extract_contact_info(self):
        """测试联系信息提取"""
        text = "联系我们：test@example.com，电话：13800138000"
        info = DataCleaner.extract_contact_info(text)

        assert "test@example.com" in info.get("emails", [])
        assert "13800138000" in info.get("phones", [])

    def test_merge_data(self):
        """测试数据合并"""
        data_list = [
            {
                "text": "文本1",
                "prices": [{"price": 99}],
                "features": ["功能1"],
                "url": "http://example.com/1"
            },
            {
                "text": "文本2",
                "prices": [{"price": 199}],
                "features": ["功能2"],
                "url": "http://example.com/2"
            }
        ]

        merged = DataCleaner.merge_data(data_list)

        assert len(merged["texts"]) == 2
        assert len(merged["prices"]) == 2
        assert len(merged["features"]) == 2
        assert len(merged["sources"]) == 2


class TestWebSearchCollector:
    """搜索采集器测试"""

    def test_initialization(self):
        """测试初始化"""
        collector = WebSearchCollector(api_key="test_key")
        assert collector.name == "web_search"
        assert collector.api_key == "test_key"

    def test_parse_results(self):
        """测试解析搜索结果"""
        collector = WebSearchCollector(api_key="test")

        raw_data = {
            "search_parameters": {"q": "test"},
            "organic_results": [
                {
                    "title": "Test Title",
                    "link": "https://example.com",
                    "snippet": "Test snippet",
                    "position": 1
                }
            ]
        }

        result = collector.parse(raw_data)

        assert result["query"] == "test"
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Title"

    def test_clean_results(self):
        """测试清洗搜索结果"""
        collector = WebSearchCollector(api_key="test")

        data = {
            "results": [
                {"title": "Title 1", "url": "https://example.com/1", "snippet": "Snippet 1"},
                {"title": "", "url": "", "snippet": ""},  # 空结果
                {"title": "Title 2", "url": "https://example.com/2", "snippet": "Snippet 2"},
            ],
            "total_results": 3
        }

        cleaned = collector.clean(data)

        assert cleaned["total_results"] == 2  # 空结果被过滤


class TestWebScraperCollector:
    """爬取采集器测试"""

    def test_initialization(self):
        """测试初始化"""
        collector = WebScraperCollector(timeout=60, headless=True)
        assert collector.name == "web_scraper"
        assert collector.timeout == 60
        assert collector.headless is True

    def test_parse_without_beautifulsoup(self):
        """测试无BeautifulSoup时的解析"""
        collector = WebScraperCollector()

        raw_data = {
            "url": "https://example.com",
            "title": "Test Page",
            "html": "<html><body><p>Hello World</p></body></html>",
            "status": "success"
        }

        # 即使没有BeautifulSoup，也应该能处理
        result = collector.parse(raw_data)
        assert result["url"] == "https://example.com"


class TestApifyCollector:
    """Apify 采集器测试"""

    def test_initialization_default_token(self):
        """测试默认初始化（从 settings 读取 token）"""
        collector = ApifyCollector()
        assert collector.name == "apify"

    def test_initialization_custom_token(self):
        """测试自定义 token"""
        collector = ApifyCollector(api_token="custom_token")
        assert collector.api_token == "custom_token"

    # ── parse ──────────────────────────────────────────────

    def test_parse_google_play(self):
        """测试 Google Play 评论解析"""
        collector = ApifyCollector(api_token="test")

        raw_data = {
            "app_id": "com.example.app",
            "store": "google",
            "reviews": [
                {"userName": "用户A", "text": "很好用", "score": 5, "at": "2024-01-15", "version": "1.0"},
                {"userName": "用户B", "text": "一般", "score": 3, "at": "2024-01-10"},
                {"userName": "用户C", "text": "不好用", "score": 1, "at": "2024-01-05", "version": "1.1"},
            ],
        }

        result = collector.parse(raw_data)

        assert result["store"] == "google_play"
        assert result["app_id"] == "com.example.app"
        assert result["rating"] == 3.0  # (5+3+1)/3
        assert result["ratings_count"] == 3
        assert len(result["reviews"]) == 3
        assert result["reviews"][0]["user"] == "用户A"
        assert result["reviews"][0]["text"] == "很好用"
        assert result["reviews"][0]["rating"] == 5

    def test_parse_app_store(self):
        """测试 App Store 评论解析"""
        collector = ApifyCollector(api_token="test")

        raw_data = {
            "app_id": "123456789",
            "store": "apple",
            "reviews": [
                {"userName": "User X", "text": "Great app", "score": 5, "date": "2024-02-01"},
                {"userName": "User Y", "text": "Good", "score": 4, "date": "2024-01-20"},
            ],
        }

        result = collector.parse(raw_data)

        assert result["store"] == "app_store"
        assert result["rating"] == 4.5
        assert result["ratings_count"] == 2
        assert len(result["reviews"]) == 2
        assert result["reviews"][1]["user"] == "User Y"

    def test_parse_google_play_text_fallback(self):
        """测试 Google Play text/content 字段兼容"""
        collector = ApifyCollector(api_token="test")

        raw_data = {
            "app_id": "com.example.app",
            "store": "google",
            "reviews": [
                {"userName": "用户A", "content": "content 字段内容", "score": 4},
            ],
        }

        result = collector.parse(raw_data)
        assert result["reviews"][0]["text"] == "content 字段内容"

    def test_parse_error_status(self):
        """测试错误状态直接返回"""
        collector = ApifyCollector(api_token="test")

        raw_data = {
            "app_id": "com.example.app",
            "store": "google",
            "error": "API token 无效",
            "status": "error",
        }

        result = collector.parse(raw_data)
        assert result["status"] == "error"
        assert result["error"] == "API token 无效"

    def test_parse_empty_reviews(self):
        """测试空评论列表"""
        collector = ApifyCollector(api_token="test")

        raw_data = {
            "app_id": "com.example.app",
            "store": "google",
            "reviews": [],
        }

        result = collector.parse(raw_data)
        assert result["rating"] == 0
        assert result["ratings_count"] == 0
        assert result["reviews"] == []

    # ── clean ──────────────────────────────────────────────

    def test_clean_removes_empty_reviews(self):
        """清洗应移除无文本且无评分的评论"""
        collector = ApifyCollector(api_token="test")

        data = {
            "store": "google_play",
            "rating": 4.0,
            "reviews": [
                {"user": "用户A", "text": "正常评论", "rating": 5},
                {"user": "用户B", "text": "", "rating": 0},  # 空文本+0分
                {"user": "用户C", "text": "", "rating": 3},  # 有评分，保留
            ],
        }

        cleaned = collector.clean(data)
        assert len(cleaned["reviews"]) == 2

    # ── collect (mock, 不调用真实 API) ──────────────────────

    @pytest.mark.asyncio
    async def test_collect_google_play_success(self):
        """测试 Google Play 采集成功（mock Apify API）"""
        collector = ApifyCollector(api_token="test_token")

        # mock 返回的评论数据
        mock_reviews = [
            {"userName": "用户A", "text": "好用", "score": 5},
            {"userName": "用户B", "text": "还行", "score": 4},
        ]

        # 注入 mock apify_client 模块，避免真实导入
        import sys
        from unittest.mock import MagicMock

        mock_apify_module = MagicMock()
        mock_client_instance = MagicMock()

        mock_actor_instance = MagicMock()
        mock_actor_instance.call.return_value = {"defaultDatasetId": "ds-123"}

        mock_dataset_instance = MagicMock()
        mock_dataset_instance.iterate_items.return_value = iter(mock_reviews)

        mock_client_instance.actor.return_value = mock_actor_instance
        mock_client_instance.dataset.return_value = mock_dataset_instance
        mock_apify_module.ApifyClient.return_value = mock_client_instance

        with (
            patch.object(collector._cache, "get", return_value=None),
            patch.object(collector._cache, "set"),
            patch.dict("sys.modules", {"apify_client": mock_apify_module}),
        ):
            result = await collector.collect("com.example.app", store="google")

        assert result["app_id"] == "com.example.app"
        assert result["store"] == "google"
        assert result["total_fetched"] == 2
        assert len(result["reviews"]) == 2
        mock_client_instance.actor.assert_called_once_with(
            "neatrat/google-play-store-reviews-scraper"
        )

    @pytest.mark.asyncio
    async def test_collect_app_store_success(self):
        """测试 App Store 采集成功（mock Apify API）"""
        collector = ApifyCollector(api_token="test_token")

        import sys
        from unittest.mock import MagicMock

        mock_reviews = [{"userName": "User A", "text": "Great!", "score": 5}]

        mock_apify_module = MagicMock()
        mock_client_instance = MagicMock()

        mock_actor_instance = MagicMock()
        mock_actor_instance.call.return_value = {"defaultDatasetId": "ds-456"}

        mock_dataset_instance = MagicMock()
        mock_dataset_instance.iterate_items.return_value = iter(mock_reviews)

        mock_client_instance.actor.return_value = mock_actor_instance
        mock_client_instance.dataset.return_value = mock_dataset_instance
        mock_apify_module.ApifyClient.return_value = mock_client_instance

        with (
            patch.object(collector._cache, "get", return_value=None),
            patch.object(collector._cache, "set"),
            patch.dict("sys.modules", {"apify_client": mock_apify_module}),
        ):
            result = await collector.collect("123456789", store="apple")

        assert result["store"] == "apple"
        assert result["total_fetched"] == 1
        mock_client_instance.actor.assert_called_once_with(
            "thewolves/appstore-reviews-scraper"
        )

    @pytest.mark.asyncio
    async def test_collect_cache_hit(self):
        """测试缓存命中时跳过 API 调用"""
        collector = ApifyCollector(api_token="test_token")

        import sys
        from unittest.mock import MagicMock

        cached_data = {"app_id": "com.example.app", "store": "google", "reviews": [], "total_fetched": 0}

        with (
            patch.object(collector._cache, "get", return_value=cached_data),
            patch.dict("sys.modules", {"apify_client": MagicMock()}),
        ):
            result = await collector.collect("com.example.app", store="google")

        assert result == cached_data

    @pytest.mark.asyncio
    async def test_collect_api_failure(self):
        """测试 API 调用失败时的错误处理"""
        collector = ApifyCollector(api_token="invalid_token")

        import sys
        from unittest.mock import MagicMock

        mock_apify_module = MagicMock()
        mock_apify_module.ApifyClient.return_value.actor.return_value.call.side_effect = Exception("API 错误")

        with (
            patch.object(collector._cache, "get", return_value=None),
            patch.dict("sys.modules", {"apify_client": mock_apify_module}),
        ):
            result = await collector.collect("com.example.app", store="google")

        assert result["status"] == "error"
        assert "API 错误" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
