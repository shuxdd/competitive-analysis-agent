"""
搜索工具
========

LangChain搜索工具，封装WebSearchCollector。
"""

import json
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from collector.web_search import WebSearchCollector
from config.settings import settings


class SearchInput(BaseModel):
    """搜索输入"""
    query: str = Field(description="搜索查询关键词")
    num_results: int = Field(default=5, description="返回结果数量")


class SearchTool(BaseTool):
    """网页搜索工具"""
    name: str = "web_search"
    description: str = "使用搜索引擎搜索信息，返回搜索结果列表"
    args_schema: Type[BaseModel] = SearchInput

    _collector: Optional[WebSearchCollector] = None

    def _get_collector(self) -> WebSearchCollector:
        if self._collector is None:
            self._collector = WebSearchCollector(api_key=settings.serpapi_key)
        return self._collector

    def _run(self, query: str, num_results: int = 5) -> str:
        """同步搜索（不推荐，建议使用arun）"""
        return "请使用异步调用"

    async def _arun(self, query: str, num_results: int = 5) -> str:
        """异步搜索"""
        try:
            collector = self._get_collector()
            result = await collector.collect(query, num_results=num_results)
            parsed = collector.parse(result)
            cleaned = collector.clean(parsed)
            return json.dumps(cleaned, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
