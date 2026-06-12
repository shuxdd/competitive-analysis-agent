"""
报告生成节点
============

使用LLM生成竞品分析报告。
"""

import logging
from agent.graph_state import AgentState
from agent.llm import create_llm
from config.prompts import REPORT_PROMPT, QUICK_REPORT_PROMPT
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
    quick 模式直接用搜索数据，跳过爬取/提取/分析。
    """
    logger.info("开始生成报告...")

    analysis_type = state.get("analysis_type", "standard")
    analysis_results = state.get("analysis_results", {})
    competitors = state.get("competitors", [])

    try:
        llm = create_llm(temperature=0.3, max_tokens=8192)

        if analysis_type == "quick":
            # quick 模式：用搜索摘要数据直接生成报告
            analysis_data = _prepare_quick_data(state)
            prompt = QUICK_REPORT_PROMPT.format(analysis_data=analysis_data)
        else:
            # standard/deep 模式：用完整分析数据
            analysis_data = _prepare_analysis_data(analysis_results, competitors)
            report_type = analysis_type if analysis_type in ("standard", "deep") else "standard"
            prompt = ReportTemplates.get_prompt(report_type).format(analysis_data=analysis_data)

        response = await retry_async(lambda: llm.ainvoke(prompt))
        report = response.content

        # 添加报告头部
        header = _generate_header(competitors, analysis_type)
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


def _prepare_quick_data(state: AgentState) -> str:
    """从搜索结果中准备快速报告数据"""
    raw_data = state.get("raw_data", [])
    competitors = state.get("competitors", [])

    sections = []
    for entry in raw_data:
        competitor = entry.get("competitor", "")
        data = entry.get("data", {})
        results = data.get("results", [])

        snippets = []
        for r in results[:5]:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            if title or snippet:
                snippets.append(f"- {title}: {snippet}")

        if snippets:
            sections.append(f"### {competitor}\n" + "\n".join(snippets))

    if not sections:
        # 没有搜索结果时的降级
        return f"竞品列表: {', '.join(competitors)}\n暂无搜索数据。"

    return f"竞品列表: {', '.join(competitors)}\n\n" + "\n\n".join(sections)


def _prepare_analysis_data(analysis_results: dict, competitors: list) -> str:
    """准备报告所需的分析数据，委托给 utils 模块"""
    data = {
        "competitors": competitors,
        "analysis_summary": analysis_results.get("summary", ""),
        "feature_matrix": analysis_results.get("feature_matrix", {}),
        "pricing_comparison": analysis_results.get("pricing_comparison", {}),
        "swot_analysis": analysis_results.get("swot_analysis", {}),
        "review_analysis": analysis_results.get("review_analysis", {})
    }

    return prepare_analysis_data(data)


def _generate_header(competitors: list, analysis_type: str) -> str:
    """生成报告头部，委托给 utils.report_helpers"""
    return generate_report_header(
        title="竞品分析报告",
        competitors=competitors,
        report_type=analysis_type,
    )


def _generate_simple_report(analysis_results: dict, competitors: list) -> str:
    """生成简化报告（降级方案），委托给 utils.report_helpers"""
    # 适配 analysis_results -> analysis_data 格式
    analysis_data = {
        "analysis_summary": analysis_results.get("summary", ""),
        "feature_matrix": analysis_results.get("feature_matrix", {}),
        "pricing_comparison": analysis_results.get("pricing_comparison", {}),
        "swot_analysis": analysis_results.get("swot_analysis", {}),
    }

    # 为每个竞品生成报告并合并
    reports = []
    for competitor in competitors:
        reports.append(generate_fallback_report(competitor, analysis_data))

    return "\n\n".join(reports)
