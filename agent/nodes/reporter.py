"""
报告生成节点
============

使用LLM生成竞品分析报告。
"""

import json
import logging
from datetime import datetime
from agent.graph_state import AgentState
from agent.llm import create_llm
from config.prompts import REPORT_PROMPT

logger = logging.getLogger(__name__)


async def generate_report(state: AgentState) -> dict:
    """
    报告生成节点

    根据分析结果生成Markdown格式的竞品分析报告。
    """
    logger.info("开始生成报告...")

    analysis_results = state.get("analysis_results", {})
    competitors = state.get("competitors", [])

    try:
        llm = create_llm(temperature=0.3, max_tokens=8192)

        # 准备分析数据
        analysis_data = _prepare_analysis_data(analysis_results, competitors)

        prompt = REPORT_PROMPT.format(analysis_data=analysis_data)
        response = await llm.ainvoke(prompt)
        report = response.content

        # 添加报告头部
        header = _generate_header(competitors, state.get("analysis_type", "standard"))
        full_report = header + "\n\n" + report

        logger.info(f"报告生成完成，长度: {len(full_report)} 字符")
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


def _prepare_analysis_data(analysis_results: dict, competitors: list) -> str:
    """准备报告所需的分析数据"""
    data = {
        "competitors": competitors,
        "analysis_summary": analysis_results.get("summary", ""),
        "feature_matrix": analysis_results.get("feature_matrix", {}),
        "pricing_comparison": analysis_results.get("pricing_comparison", {}),
        "swot_analysis": analysis_results.get("swot_analysis", {}),
        "review_analysis": analysis_results.get("review_analysis", {})
    }

    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _generate_header(competitors: list, analysis_type: str) -> str:
    """生成报告头部"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    type_names = {"quick": "快速", "standard": "标准", "deep": "深度"}

    return f"""# 竞品分析报告

> 生成时间: {now}
> 分析类型: {type_names.get(analysis_type, analysis_type)}
> 竞品数量: {len(competitors)}
> 竞品列表: {', '.join(competitors)}

---"""


def _generate_simple_report(analysis_results: dict, competitors: list) -> str:
    """生成简化报告（降级方案）"""
    header = _generate_header(competitors, "standard")

    sections = [header, "\n## 分析摘要\n"]
    sections.append(analysis_results.get("summary", "暂无摘要"))

    # 功能矩阵
    matrix = analysis_results.get("feature_matrix", {})
    if matrix and matrix.get("features"):
        sections.append("\n## 功能对比\n")
        features = matrix["features"][:10]
        for feature in features:
            sections.append(f"- {feature}")

    # 定价对比
    pricing = analysis_results.get("pricing_comparison", {})
    if pricing and pricing.get("competitors"):
        sections.append("\n## 定价对比\n")
        for name, info in pricing["competitors"].items():
            if info.get("prices"):
                prices_str = ", ".join(f"{p.get('currency', '')} {p.get('price', '')}" for p in info["prices"][:3])
                sections.append(f"- **{name}**: {prices_str}")
            else:
                sections.append(f"- **{name}**: 暂无定价信息")

    # SWOT
    swot = analysis_results.get("swot_analysis", {})
    if swot:
        sections.append("\n## SWOT分析\n")
        for name, s in swot.items():
            sections.append(f"\n### {name}\n")
            if isinstance(s, dict) and "raw_response" not in s:
                for key in ["strengths", "weaknesses", "opportunities", "threats"]:
                    if key in s:
                        sections.append(f"\n**{key.title()}**:")
                        for item in s[key][:3]:
                            sections.append(f"- {item}")
            else:
                sections.append(json.dumps(s, ensure_ascii=False, default=str)[:500])

    sections.append(f"\n\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(sections)
