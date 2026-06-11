"""
Agent模块演示
=============

展示Agent核心模块的状态图和节点功能。
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from agent.graph import create_analysis_graph
from agent.graph_state import AgentState
from agent.nodes.planner import _generate_default_plan
from agent.nodes.analyzer import _build_feature_matrix, _build_pricing_comparison
from agent.nodes.reporter import _generate_header, _generate_simple_report


def demo_graph_creation():
    """演示状态图创建"""
    print("=== 状态图创建演示 ===\n")

    graph = create_analysis_graph()

    print(f"状态图创建成功")
    nodes = list(graph.get_graph().nodes)
    print(f"节点列表: {nodes}")
    print(f"节点数量: {len(nodes)}")
    print()


def demo_planner():
    """演示规划节点"""
    print("=== 规划节点演示 ===\n")

    competitors = ["Notion", "Obsidian", "飞书文档"]
    dimensions = ["features", "pricing", "swot"]

    plan = _generate_default_plan(competitors, dimensions)

    print(f"竞品数量: {len(plan['competitors'])}")
    print(f"分析维度: {plan['analysis_dimensions']}")
    print()

    for comp in plan["competitors"]:
        print(f"竞品: {comp['name']}")
        print(f"  搜索关键词: {comp['search_keywords']}")
        print(f"  信息类型: {comp['info_types']}")
        print()


def demo_feature_matrix():
    """演示功能矩阵"""
    print("=== 功能矩阵演示 ===\n")

    merged_data = {
        "Notion": {"features": ["文档管理", "知识库", "项目管理", "数据库", "API接口"]},
        "Obsidian": {"features": ["文档管理", "知识库", "双向链接", "插件系统", "本地存储"]},
        "飞书文档": {"features": ["文档管理", "知识库", "项目管理", "即时通讯", "视频会议"]}
    }

    matrix = _build_feature_matrix(merged_data)

    print(f"功能总数: {len(matrix['features'])}")
    print(f"竞品数量: {len(matrix['competitors'])}")
    print()

    # 打印矩阵表头
    header = "功能".ljust(12)
    for name in matrix["competitors"]:
        header += name.ljust(12)
    print(header)
    print("-" * len(header))

    # 打印矩阵内容
    for feature in matrix["features"][:10]:
        row = feature.ljust(12)
        for name in matrix["competitors"]:
            has = "✓" if matrix["competitors"][name].get(feature) else "✗"
            row += has.ljust(12)
        print(row)
    print()


def demo_pricing_comparison():
    """演示定价对比"""
    print("=== 定价对比演示 ===\n")

    merged_data = {
        "Notion": {"prices": [
            {"price": 0, "currency": "USD"},
            {"price": 8, "currency": "USD"},
            {"price": 15, "currency": "USD"}
        ]},
        "Obsidian": {"prices": [
            {"price": 0, "currency": "USD"},
            {"price": 50, "currency": "USD"}
        ]},
        "飞书文档": {"prices": []}
    }

    comparison = _build_pricing_comparison(merged_data)

    for name, info in comparison["competitors"].items():
        print(f"竞品: {name}")
        if info.get("prices"):
            print(f"  最低价: {info['currency']} {info['min_price']}")
            print(f"  最高价: {info['currency']} {info['max_price']}")
            print(f"  价格档位: {len(info['prices'])} 个")
        else:
            print(f"  {info.get('note', '暂无定价信息')}")
        print()


def demo_report_generation():
    """演示报告生成"""
    print("=== 报告生成演示 ===\n")

    analysis_results = {
        "summary": "已完成对3个竞品的分析，分析维度: features, pricing, swot。",
        "feature_matrix": {
            "features": ["文档管理", "知识库", "项目管理"],
            "competitors": {
                "Notion": {"文档管理": True, "知识库": True, "项目管理": True},
                "Obsidian": {"文档管理": True, "知识库": True, "项目管理": False}
            }
        },
        "pricing_comparison": {
            "competitors": {
                "Notion": {"prices": [{"price": 8, "currency": "USD"}], "min_price": 8, "max_price": 15, "currency": "USD"},
                "Obsidian": {"prices": [{"price": 50, "currency": "USD"}], "min_price": 0, "max_price": 50, "currency": "USD"}
            }
        },
        "swot_analysis": {}
    }

    report = _generate_simple_report(analysis_results, ["Notion", "Obsidian"])

    print(report[:1500])
    if len(report) > 1500:
        print(f"\n... (报告总长度: {len(report)} 字符)")
    print()


async def demo_state_transitions():
    """演示状态转换"""
    print("=== 状态转换演示 ===\n")

    states = [
        ("pending", "初始状态"),
        ("planning", "任务规划中"),
        ("collecting", "数据采集中"),
        ("extracting", "信息提取中"),
        ("analyzing", "分析对比中"),
        ("generating", "报告生成中"),
        ("completed", "分析完成"),
    ]

    for status, desc in states:
        print(f"  [{status}] {desc}")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  智能竞品分析Agent - Agent核心模块演示")
    print("=" * 60 + "\n")

    demo_graph_creation()
    demo_planner()
    demo_feature_matrix()
    demo_pricing_comparison()
    demo_report_generation()
    asyncio.run(demo_state_transitions())

    print("=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
