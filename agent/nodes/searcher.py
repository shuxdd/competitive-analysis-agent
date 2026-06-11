"""
搜索节点
========

使用搜索引擎采集竞品信息。
"""

import logging
from agent.graph_state import AgentState
from collector.web_search import WebSearchCollector
from config.settings import settings

logger = logging.getLogger(__name__)


async def search_competitors(state: AgentState) -> dict:
    """
    搜索节点

    根据采集计划，搜索每个竞品的相关信息。
    """
    logger.info("开始搜索竞品信息...")

    plan = state.get("collection_plan", {})
    competitors = plan.get("competitors", state["competitors"])
    all_results = []

    try:
        collector = WebSearchCollector(api_key=settings.serpapi_key)

        for comp in competitors:
            name = comp if isinstance(comp, str) else comp.get("name", "")
            keywords = [] if isinstance(comp, str) else comp.get("search_keywords", [])

            logger.info(f"搜索竞品: {name}")

            try:
                result = await collector.search_competitor(
                    name,
                    keywords=keywords if keywords else None,
                    num_results=5
                )

                all_results.append({
                    "competitor": name,
                    "source": "web_search",
                    "data": result
                })

                logger.info(f"  搜索完成，找到 {result.get('total_results', 0)} 条结果")

            except Exception as e:
                logger.warning(f"  搜索 {name} 失败: {e}")
                all_results.append({
                    "competitor": name,
                    "source": "web_search",
                    "data": {"results": [], "total_results": 0},
                    "error": str(e)
                })

        logger.info(f"搜索完成，共处理 {len(competitors)} 个竞品")
        return {
            "raw_data": all_results,
            "status": "collecting",
            "errors": state.get("errors", [])
        }

    except Exception as e:
        logger.error(f"搜索节点失败: {e}")
        return {
            "raw_data": all_results,
            "status": "collecting",
            "errors": state.get("errors", []) + [f"搜索节点错误: {str(e)}"]
        }
