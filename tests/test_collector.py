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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
