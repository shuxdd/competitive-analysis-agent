"""
向量检索工具
============

LangChain向量检索工具，封装KnowledgeBase。
"""

import json
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from knowledge.knowledge_base import KnowledgeBase
from config.settings import settings


class VectorSearchInput(BaseModel):
    """向量检索输入"""
    query: str = Field(description="检索查询")
    competitor_id: Optional[str] = Field(default=None, description="竞品ID，用于过滤")
    top_k: int = Field(default=5, description="返回结果数量")


class VectorSearchTool(BaseTool):
    """向量检索工具"""
    name: str = "vector_search"
    description: str = "从知识库中语义检索竞品信息"
    args_schema: Type[BaseModel] = VectorSearchInput

    _kb: Optional[KnowledgeBase] = None

    def _get_kb(self) -> KnowledgeBase:
        if self._kb is None:
            self._kb = KnowledgeBase(persist_dir=settings.chroma_persist_dir)
        return self._kb

    def _run(self, query: str, competitor_id: Optional[str] = None, top_k: int = 5) -> str:
        """同步检索（不推荐，建议使用arun）"""
        return "请使用异步调用"

    async def _arun(self, query: str, competitor_id: Optional[str] = None, top_k: int = 5) -> str:
        """异步检索"""
        try:
            kb = self._get_kb()
            results = kb.search_competitors(
                query=query,
                competitor_id=competitor_id,
                top_k=top_k
            )
            return json.dumps(results, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
