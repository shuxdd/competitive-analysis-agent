"""
知识库存储节点
==============

将分析完成的结构化数据写入 Chroma 向量数据库，供 QA 接口使用。
"""

import logging
from agent.graph_state import AgentState
from knowledge.knowledge_base import KnowledgeBase
from agent.progress import report_progress

logger = logging.getLogger(__name__)


async def store_knowledge(state: AgentState) -> dict:
    """
    知识库存储节点

    将提取的结构化数据和分析结果写入 Chroma 知识库。
    """
    logger.info("开始写入知识库...")

    user_id = state.get("user_id")
    extracted_info = state.get("extracted_info", [])
    analysis_results = state.get("analysis_results", {})

    if not extracted_info:
        logger.info("  无提取数据，跳过知识库写入")
        report_progress(state.get("progress_callback"), "knowledge_store")
        return {"status": state["status"], "errors": state.get("errors", [])}

    try:
        kb = KnowledgeBase()

        for entry in extracted_info:
            competitor = entry.get("competitor", "unknown")
            info = entry.get("extracted_info", {})
            if not info:
                continue

            # 将提取的数据写入知识库（带用户隔离）
            kb.add_competitor(competitor_id=competitor, competitor_data=info, user_id=user_id)

            # 同时写入分析结果中的用户评价（如果有）
            review_analysis = analysis_results.get("review_analysis", {})
            comp_reviews = review_analysis.get(competitor, {})
            if comp_reviews and comp_reviews.get("recent_reviews"):
                for review in comp_reviews["recent_reviews"]:
                    kb.add_user_review(
                        competitor_id=competitor,
                        review_content=review.get("text", ""),
                        rating=review.get("rating", 0),
                        source=review.get("source", "unknown"),
                        user_id=user_id,
                    )

            logger.info(f"  {competitor}: 知识库写入完成")

        logger.info("知识库写入完成")
        report_progress(state.get("progress_callback"), "knowledge_store")
        return {"status": state["status"], "errors": state.get("errors", [])}

    except Exception as e:
        logger.error(f"知识库写入失败: {e}")
        return {
            "status": state["status"],
            "errors": state.get("errors", []) + [f"知识库写入错误: {str(e)}"]
        }
