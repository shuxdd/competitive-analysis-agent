"""
应用商店采集器测试
==================
"""

import pytest
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
            "appId": "notion.id",
            "title": "Notion",
            "description": "All-in-one workspace",
            "developer": "Notion Labs",
            "score": 4.6,
            "ratings": 152000,
            "installs": "10,000,000+",
            "updated": "Jun 1, 2026",
            "version": "0.6.40",
            "genre": "Productivity",
            "price": 0,
            "containsAds": False,
        }

        result = collector.parse(raw_data)

        assert result["app_name"] == "Notion"
        assert result["store"] == "google_play"
        assert result["rating"] == 4.6
        assert result["ratings_count"] == 152000
        assert result["installs"] == "10,000,000+"
        assert result["current_version"] == "0.6.40"

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

    def test_parse_error_data(self):
        """测试解析错误数据"""
        collector = AppStoreCollector()
        raw_data = {"app_id": "test", "error": "not found", "status": "error"}
        result = collector.parse(raw_data)
        assert result["status"] == "error"

    def test_parse_review(self):
        """测试解析评论"""
        collector = AppStoreCollector()

        raw_review = {
            "userName": "张三",
            "content": "功能强大但偶尔卡顿",
            "score": 4,
            "at": "2026-06-10T00:00:00Z",
        }

        result = collector._parse_review(raw_review)

        assert result["user"] == "张三"
        assert result["text"] == "功能强大但偶尔卡顿"
        assert result["rating"] == 4

    def test_parse_generic_data(self):
        """测试通用解析"""
        collector = AppStoreCollector()

        raw_data = {
            "source": "unknown",
            "title": "TestApp",
            "score": 4.5,
            "ratings": 1000,
        }

        result = collector.parse(raw_data)
        assert result["app_name"] == "TestApp"
        assert result["store"] == "unknown"
        assert result["rating"] == 4.5

    def test_clean_removes_none(self):
        """测试清洗去除 None 和空值"""
        collector = AppStoreCollector()
        data = {
            "app_name": "TestApp",
            "rating": 4.5,
            "developer": None,
            "genre": "",
        }
        cleaned = collector.clean(data)
        assert cleaned["app_name"] == "TestApp"
        assert cleaned["rating"] == 4.5
        assert "developer" not in cleaned
        assert "genre" not in cleaned
