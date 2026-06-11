"""
报告生成器
==========

生成和导出竞品分析报告。
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from agent.llm import create_llm
from config.settings import settings
from report.templates import ReportTemplates

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.output_dir = settings.report_output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate(
        self,
        analysis_results: Dict[str, Any],
        report_type: str = "standard",
        competitors: Optional[List[str]] = None,
    ) -> str:
        """
        生成报告

        Args:
            analysis_results: 分析结果
            report_type: 报告类型 (quick/standard/deep)
            competitors: 竞品列表

        Returns:
            Markdown格式的报告
        """
        logger.info(f"开始生成{report_type}报告...")

        competitors = competitors or []
        prompt_template = ReportTemplates.get_prompt(report_type)

        try:
            llm = create_llm(temperature=0.3, max_tokens=8192)

            analysis_data = self._prepare_data(analysis_results, competitors)
            prompt = prompt_template.format(analysis_data=analysis_data)

            response = await llm.ainvoke(prompt)
            report_content = response.content

            header = self._generate_header(competitors, report_type)
            full_report = header + "\n\n" + report_content

            logger.info(f"报告生成完成，长度: {len(full_report)} 字符")
            return full_report

        except Exception as e:
            logger.error(f"LLM报告生成失败: {e}，使用降级方案")
            return self._generate_fallback(analysis_results, competitors, report_type)

    def export_markdown(self, report: str, filename: Optional[str] = None) -> str:
        """
        导出Markdown文件

        Args:
            report: 报告内容
            filename: 文件名（不含扩展名）

        Returns:
            文件路径
        """
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = os.path.join(self.output_dir, f"{filename}.md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Markdown报告已导出: {filepath}")
        return filepath

    def export_html(self, report: str, filename: Optional[str] = None) -> str:
        """
        导出HTML文件

        Args:
            report: Markdown格式的报告内容
            filename: 文件名（不含扩展名）

        Returns:
            文件路径
        """
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = os.path.join(self.output_dir, f"{filename}.html")

        html_content = self._markdown_to_html(report)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML报告已导出: {filepath}")
        return filepath

    def _prepare_data(self, analysis_results: Dict, competitors: List[str]) -> str:
        """准备报告数据"""
        data = {
            "competitors": competitors,
            "analysis_summary": analysis_results.get("summary", ""),
            "feature_matrix": analysis_results.get("feature_matrix", {}),
            "pricing_comparison": analysis_results.get("pricing_comparison", {}),
            "swot_analysis": analysis_results.get("swot_analysis", {}),
            "review_analysis": analysis_results.get("review_analysis", {}),
        }
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

    def _generate_header(self, competitors: List[str], report_type: str) -> str:
        """生成报告头部"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        type_names = {"quick": "快速", "standard": "标准", "deep": "深度"}

        return f"""# 竞品分析报告

> 生成时间: {now}
> 分析类型: {type_names.get(report_type, report_type)}
> 竞品数量: {len(competitors)}
> 竞品列表: {', '.join(competitors)}

---"""

    def _generate_fallback(
        self, analysis_results: Dict, competitors: List[str], report_type: str
    ) -> str:
        """降级报告生成"""
        header = self._generate_header(competitors, report_type)
        sections = [header, "\n## 分析摘要\n"]

        sections.append(analysis_results.get("summary", "暂无摘要"))

        # 功能矩阵
        matrix = analysis_results.get("feature_matrix", {})
        if matrix and matrix.get("features"):
            sections.append("\n## 功能对比\n")
            for feature in matrix["features"][:10]:
                sections.append(f"- {feature}")

        # 定价对比
        pricing = analysis_results.get("pricing_comparison", {})
        if pricing and pricing.get("competitors"):
            sections.append("\n## 定价对比\n")
            for name, info in pricing["competitors"].items():
                if info.get("prices"):
                    prices = ", ".join(
                        f"{p.get('currency', '')} {p.get('price', '')}"
                        for p in info["prices"][:3]
                    )
                    sections.append(f"- **{name}**: {prices}")
                else:
                    sections.append(f"- **{name}**: 暂无定价信息")

        # SWOT
        swot = analysis_results.get("swot_analysis", {})
        if swot:
            sections.append("\n## SWOT分析\n")
            for name, s in swot.items():
                sections.append(f"\n### {name}\n")
                if isinstance(s, dict):
                    for key in ["strengths", "weaknesses", "opportunities", "threats"]:
                        if key in s:
                            sections.append(f"\n**{key.title()}**:")
                            for item in s[key][:3]:
                                sections.append(f"- {item}")

        sections.append(
            f"\n\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        )
        return "\n".join(sections)

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Markdown转HTML"""
        try:
            import markdown

            html_body = markdown.markdown(
                markdown_text,
                extensions=["tables", "fenced_code", "codehilite"],
            )
        except ImportError:
            # 降级：简单的换行处理
            html_body = markdown_text.replace("\n", "<br>")

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>竞品分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{ background-color: #f5f5f5; }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding: 0.5em 1em;
            background-color: #f9f9f9;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
