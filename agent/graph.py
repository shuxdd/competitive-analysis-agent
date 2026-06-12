"""
LangGraph状态图
===============

组装竞品分析Agent的状态图。
"""

import logging
from langgraph.graph import StateGraph, START, END

from agent.graph_state import AgentState
from agent.nodes.planner import plan_analysis
from agent.nodes.searcher import search_competitors
from agent.nodes.scraper import scrape_data
from agent.nodes.extractor import extract_info
from agent.nodes.analyzer import analyze_competitors
from agent.nodes.reporter import generate_report

logger = logging.getLogger(__name__)


def _route_after_searcher(state: AgentState) -> str:
    """搜索后的条件路由：quick 直接跳到 reporter，其他继续爬取"""
    analysis_type = state.get("analysis_type", "standard")
    if analysis_type == "quick":
        return "reporter"
    return "scraper"


def create_analysis_graph():
    """
    创建竞品分析状态图

    流程:
    - quick:    planner -> searcher -> reporter
    - standard: planner -> searcher -> scraper -> extractor -> analyzer -> reporter
    - deep:     planner -> searcher -> scraper -> extractor -> analyzer -> reporter

    Returns:
        编译后的状态图
    """
    logger.info("创建竞品分析状态图...")

    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("planner", plan_analysis)
    graph.add_node("searcher", search_competitors)
    graph.add_node("scraper", scrape_data)
    graph.add_node("extractor", extract_info)
    graph.add_node("analyzer", analyze_competitors)
    graph.add_node("reporter", generate_report)

    # 设置边
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "searcher")

    # 条件分支：quick 跳过爬取/提取/分析
    graph.add_conditional_edges(
        "searcher",
        _route_after_searcher,
        {
            "reporter": "reporter",
            "scraper": "scraper",
        },
    )

    graph.add_edge("scraper", "extractor")
    graph.add_edge("extractor", "analyzer")
    graph.add_edge("analyzer", "reporter")
    graph.add_edge("reporter", END)

    logger.info("状态图创建完成")
    return graph.compile()
