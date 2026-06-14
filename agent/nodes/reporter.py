"""
报告生成节点
============

使用LLM生成竞品分析报告。
"""

import logging
from agent.graph_state import AgentState
from agent.llm import create_llm
from config.prompts import REPORT_PROMPT
from report.templates import ReportTemplates
from utils.retry import retry_async
from utils.report_helpers import (
    generate_report_header,
    generate_fallback_report,
    prepare_analysis_data,
)
from agent.progress import report_progress

logger = logging.getLogger(__name__)


async def generate_report(state: AgentState) -> dict:
    """
    报告生成节点

    根据分析结果生成Markdown格式的竞品分析报告。
    """
    logger.info("开始生成报告...")

    analysis_results = state.get("analysis_results", {})
    competitors = state.get("competitors", [])
    my_product = state.get("my_product")

    try:
        llm = create_llm(temperature=0.3, max_tokens=8192)

        # 根据是否有我方产品选择模板
        report_type = "comparison" if my_product else "standard"
        template_label = "对比分析" if my_product else "标准分析"
        logger.info(f"使用{template_label}模板")

        analysis_data = _prepare_analysis_data(analysis_results, competitors, my_product)
        prompt = ReportTemplates.get_prompt(report_type).format(analysis_data=analysis_data)

        response = await retry_async(lambda: llm.ainvoke(prompt))
        report = response.content

        # 添加报告头部
        header = _generate_header(competitors)
        full_report = header + "\n\n" + report

        logger.info(f"报告生成完成，长度: {len(full_report)} 字符")
        report_progress(state.get("progress_callback"), "reporter")
        return {
            "report": full_report,
            "status": "completed",
            "errors": state.get("errors", [])
        }

    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        # 降级：生成简单报告
        simple_report = _generate_simple_report(analysis_results, competitors)
        return {
            "report": simple_report,
            "status": "completed",
            "errors": state.get("errors", []) + [f"报告生成警告: {str(e)}，已生成简化报告"]
        }


def _prepare_analysis_data(analysis_results: dict, competitors: list, my_product: str = None) -> str:
    """准备报告所需的分析数据，只包含实际完成的维度"""
    dimension_keys = ["feature_matrix", "pricing_comparison", "swot_analysis", "review_analysis"]
    data = {
        "competitors": competitors,
        "analysis_summary": analysis_results.get("summary", ""),
    }
    if my_product:
        data["my_product"] = my_product
    for key in dimension_keys:
        val = analysis_results.get(key)
        if val:
            data[key] = val

    return prepare_analysis_data(data)


def _generate_header(competitors: list) -> str:
    """生成报告头部，委托给 utils.report_helpers"""
    return generate_report_header(
        title="竞品分析报告",
        competitors=competitors,
        report_type="standard",
    )


def _generate_simple_report(analysis_results: dict, competitors: list) -> str:
    """生成简化报告（降级方案），委托给 utils.report_helpers"""
    analysis_data = {
        "analysis_summary": analysis_results.get("summary", ""),
        "feature_matrix": analysis_results.get("feature_matrix", {}),
        "pricing_comparison": analysis_results.get("pricing_comparison", {}),
        "swot_analysis": analysis_results.get("swot_analysis", {}),
    }

    reports = []
    for competitor in competitors:
        reports.append(generate_fallback_report(competitor, analysis_data))

    return "\n\n".join(reports)
