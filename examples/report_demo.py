"""
报告生成模块演示
================

展示报告生成功能。
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from report.templates import ReportTemplates
from report.generator import ReportGenerator
from config.settings import settings


def demo_templates():
    """演示报告模板"""
    print("=== 报告模板演示 ===\n")

    templates = ReportTemplates.list_templates()
    print(f"可用模板数量: {len(templates)}\n")

    for t in templates:
        print(f"类型: {t['type']}")
        print(f"  名称: {t['name']}")
        print(f"  描述: {t['description']}")
        print(f"  章节: {', '.join(t['sections'])}")
        print()


def demo_prompts():
    """演示Prompt模板"""
    print("=== Prompt模板演示 ===\n")

    for report_type in ["quick", "standard", "deep"]:
        prompt = ReportTemplates.get_prompt(report_type)
        template = ReportTemplates.get_template(report_type)
        print(f"【{template['name']}】")
        print(f"  Prompt长度: {len(prompt)} 字符")
        print(f"  包含占位符: {'{analysis_data}' in prompt}")
        print()


def demo_fallback_report():
    """演示降级报告生成"""
    print("=== 降级报告生成演示 ===\n")

    # 模拟分析结果
    analysis_results = {
        "summary": "已完成对3个竞品的分析，分析维度: features, pricing, swot。",
        "feature_matrix": {
            "features": ["文档管理", "知识库", "项目管理", "API接口", "移动端"],
            "competitors": {
                "Notion": {"文档管理": True, "知识库": True, "项目管理": True, "API接口": True, "移动端": True},
                "Obsidian": {"文档管理": True, "知识库": True, "项目管理": False, "API接口": False, "移动端": True},
                "飞书文档": {"文档管理": True, "知识库": True, "项目管理": True, "API接口": True, "移动端": True},
            },
        },
        "pricing_comparison": {
            "competitors": {
                "Notion": {"prices": [{"price": 0, "currency": "USD"}, {"price": 8, "currency": "USD"}, {"price": 15, "currency": "USD"}], "min_price": 0, "max_price": 15, "currency": "USD"},
                "Obsidian": {"prices": [{"price": 0, "currency": "USD"}, {"price": 50, "currency": "USD"}], "min_price": 0, "max_price": 50, "currency": "USD"},
                "飞书文档": {"prices": [], "note": "未找到定价信息"},
            }
        },
        "swot_analysis": {
            "Notion": {
                "strengths": ["功能全面", "用户体验好", "生态丰富"],
                "weaknesses": ["价格较高", "国内访问慢"],
                "opportunities": ["AI集成", "企业市场"],
                "threats": ["竞品增多", "用户迁移成本低"],
            },
        },
    }

    competitors = ["Notion", "Obsidian", "飞书文档"]

    # 生成三种类型的报告
    import tempfile
    with patch_settings():
        generator = ReportGenerator()

        for report_type in ["quick", "standard", "deep"]:
            template = ReportTemplates.get_template(report_type)
            print(f"--- {template['name']} ---")

            report = generator._generate_fallback(analysis_results, competitors, report_type)
            print(report[:600])
            if len(report) > 600:
                print(f"\n... (报告长度: {len(report)} 字符)")
            print()


def demo_export():
    """演示报告导出"""
    print("=== 报告导出演示 ===\n")

    report_content = """# 竞品分析报告

> 生成时间: 2026-06-11
> 分析类型: 标准

---

## 分析摘要

已完成对2个竞品的分析。

## 功能对比

- 文档管理
- 知识库
- 项目管理

## 定价对比

- **Notion**: USD 8/月
- **Obsidian**: USD 50/年
"""

    with patch_settings():
        generator = ReportGenerator()

        # 导出Markdown
        md_path = generator.export_markdown(report_content, "demo_report")
        print(f"Markdown已导出: {md_path}")

        # 导出HTML
        html_path = generator.export_html(report_content, "demo_report")
        print(f"HTML已导出: {html_path}")

        # 检查文件
        print(f"\nMarkdown文件大小: {os.path.getsize(md_path)} 字节")
        print(f"HTML文件大小: {os.path.getsize(html_path)} 字节")

        # 清理
        os.remove(md_path)
        os.remove(html_path)
        print("\n演示文件已清理")
        print()


class patch_settings:
    """临时设置上下文管理器"""
    def __enter__(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self._original = settings.report_output_dir
        settings.report_output_dir = self.tmpdir
        return self

    def __exit__(self, *args):
        settings.report_output_dir = self._original


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  智能竞品分析Agent - 报告生成模块演示")
    print("=" * 60 + "\n")

    demo_templates()
    demo_prompts()
    demo_fallback_report()
    demo_export()

    print("=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
