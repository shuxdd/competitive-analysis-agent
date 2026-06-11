"""
Agent状态定义
=============

定义LangGraph状态图的状态结构。
"""

from typing import List, Optional, Annotated
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    """Agent状态图状态"""

    # 输入
    competitors: List[str]
    analysis_type: str              # "quick" / "standard" / "deep"
    dimensions: List[str]           # ["features", "pricing", "swot", ...]
    my_product: Optional[str]

    # 中间数据
    collection_plan: dict           # planner输出的采集计划
    raw_data: Annotated[List[dict], operator.add]  # searcher+scraper追加
    extracted_info: Annotated[List[dict], operator.add]  # extractor追加
    analysis_results: dict          # analyzer输出

    # 输出
    report: str
    status: str
    errors: List[str]
