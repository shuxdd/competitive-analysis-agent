"""
分析对比节点
============

对提取的信息进行多维度分析对比。
"""

import json
import logging
from typing import Dict, List, Any
from agent.graph_state import AgentState
from agent.llm import create_llm
from collector.cleaner import DataCleaner
from config.prompts import SWOT_PROMPT
from utils.llm_parser import extract_json_from_llm
from utils.retry import retry_async

logger = logging.getLogger(__name__)


async def analyze_competitors(state: AgentState) -> dict:
    """
    分析对比节点

    对提取的竞品信息进行多维度分析。
    """
    logger.info("开始分析对比...")

    extracted_info = state.get("extracted_info", [])
    dimensions = state.get("dimensions", ["features", "pricing", "swot"])
    analysis_results = {}

    try:
        # 按竞品分组
        grouped = _group_by_competitor(extracted_info)

        # 合并每个竞品的数据
        merged_data = {}
        for competitor, entries in grouped.items():
            data_list = [e.get("extracted_info", {}) for e in entries if e.get("extracted_info")]
            if data_list:
                merged_data[competitor] = DataCleaner.merge_data(data_list)
                merged_data[competitor]["competitor_name"] = competitor

        analysis_results["competitors_data"] = merged_data

        # 按维度分析
        if "features" in dimensions:
            analysis_results["feature_matrix"] = _build_feature_matrix(merged_data)
            logger.info("  功能矩阵构建完成")

        if "pricing" in dimensions:
            analysis_results["pricing_comparison"] = _build_pricing_comparison(merged_data)
            logger.info("  定价对比完成")

        if "swot" in dimensions:
            analysis_results["swot_analysis"] = await _generate_swot(merged_data)
            logger.info("  SWOT分析完成")

        if "reviews" in dimensions:
            analysis_results["review_analysis"] = _analyze_reviews(merged_data)
            logger.info("  用户评价分析完成")

        analysis_results["summary"] = _generate_summary(merged_data, dimensions)

        logger.info("分析对比完成")
        return {
            "analysis_results": analysis_results,
            "status": "analyzing",
            "errors": state.get("errors", [])
        }

    except Exception as e:
        logger.error(f"分析对比节点失败: {e}")
        return {
            "analysis_results": analysis_results,
            "status": "analyzing",
            "errors": state.get("errors", []) + [f"分析节点错误: {str(e)}"]
        }


def _group_by_competitor(extracted_info: List[Dict]) -> Dict[str, List[Dict]]:
    """按竞品名称分组"""
    grouped = {}
    for entry in extracted_info:
        name = entry.get("competitor", "unknown")
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(entry)
    return grouped


def _build_feature_matrix(merged_data: Dict[str, Any]) -> Dict:
    """构建功能矩阵"""
    all_features = set()
    competitor_features = {}

    for name, data in merged_data.items():
        features = data.get("features", [])
        all_features.update(features)
        competitor_features[name] = set(features)

    feature_list = sorted(list(all_features))[:30]  # 最多30个功能

    matrix = {
        "features": feature_list,
        "competitors": {}
    }

    for name in merged_data:
        matrix["competitors"][name] = {
            f: f in competitor_features.get(name, set())
            for f in feature_list
        }

    return matrix


def _build_pricing_comparison(merged_data: Dict[str, Any]) -> Dict:
    """构建定价对比"""
    comparison = {"competitors": {}}

    for name, data in merged_data.items():
        prices = data.get("prices", [])
        if prices:
            comparison["competitors"][name] = {
                "prices": prices,
                "min_price": min(p["price"] for p in prices if "price" in p),
                "max_price": max(p["price"] for p in prices if "price" in p),
                "currency": prices[0].get("currency", "CNY") if prices else "CNY"
            }
        else:
            comparison["competitors"][name] = {"prices": [], "note": "未找到定价信息"}

    return comparison


async def _generate_swot(merged_data: Dict[str, Any]) -> Dict:
    """生成SWOT分析"""
    swot_results = {}

    try:
        llm = create_llm(temperature=0.3)

        for name, data in merged_data.items():
            try:
                info_str = json.dumps(data, ensure_ascii=False, default=str)[:3000]
                prompt = SWOT_PROMPT.format(competitor_info=info_str)

                response = await retry_async(lambda: llm.ainvoke(prompt))
                content = response.content

                # 解析SWOT
                swot = extract_json_from_llm(content)
                if swot is None:
                    swot = {"raw_response": content}

                swot_results[name] = swot

            except Exception as e:
                logger.warning(f"  {name} SWOT分析失败: {e}")
                swot_results[name] = {"error": str(e)}

    except Exception as e:
        logger.error(f"SWOT分析整体失败: {e}")

    return swot_results


def _analyze_reviews(merged_data: Dict[str, Any]) -> Dict:
    """分析用户评价（占位实现）"""
    return {
        "note": "用户评价分析需要评价数据源支持",
        "competitors": list(merged_data.keys())
    }


def _generate_summary(merged_data: Dict[str, Any], dimensions: List[str]) -> str:
    """生成分析摘要"""
    competitors = list(merged_data.keys())
    return (
        f"已完成对 {len(competitors)} 个竞品的分析，"
        f"分析维度: {', '.join(dimensions)}。"
        f"竞品: {', '.join(competitors)}。"
    )
