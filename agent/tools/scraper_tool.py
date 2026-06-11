"""
爬取工具
========

LangChain爬取工具，封装WebScraperCollector。
"""

import json
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from collector.web_scraper import WebScraperCollector
from collector.cleaner import DataCleaner
from config.settings import settings


class ScraperInput(BaseModel):
    """爬取输入"""
    url: str = Field(description="要爬取的网页URL")


class ScraperTool(BaseTool):
    """网页爬取工具"""
    name: str = "web_scraper"
    description: str = "爬取指定URL的网页内容，返回清理后的文本"
    args_schema: Type[BaseModel] = ScraperInput

    _collector: Optional[WebScraperCollector] = None

    def _get_collector(self) -> WebScraperCollector:
        if self._collector is None:
            self._collector = WebScraperCollector(
                timeout=settings.scrape_timeout,
                max_retries=settings.max_retries,
                headless=True
            )
        return self._collector

    def _run(self, url: str) -> str:
        """同步爬取（不推荐，建议使用arun）"""
        return "请使用异步调用"

    async def _arun(self, url: str) -> str:
        """异步爬取"""
        try:
            collector = self._get_collector()
            raw = await collector.collect(url)
            parsed = collector.parse(raw)
            cleaned = collector.clean(parsed)

            text = cleaned.get("text", "")
            text = DataCleaner.clean_text(text)

            return json.dumps({
                "url": cleaned.get("url", url),
                "title": cleaned.get("title", ""),
                "text": text[:8000],
                "text_length": len(text)
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e), "url": url}, ensure_ascii=False)

    def close(self):
        """关闭爬虫"""
        if self._collector:
            self._collector.close()
