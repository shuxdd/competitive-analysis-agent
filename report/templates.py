"""
报告模板管理
============

管理不同类型的报告模板。
"""

from typing import Dict, List
from config.prompts import REPORT_PROMPT, QUICK_REPORT_PROMPT, DEEP_REPORT_PROMPT


class ReportTemplates:
    """报告模板管理器"""

    # 模板定义
    TEMPLATES = {
        "quick": {
            "name": "快速报告",
            "description": "简洁的竞品概览，适合快速了解",
            "sections": ["公司概览", "关键产品", "主要差异化", "定价摘要"],
            "prompt": QUICK_REPORT_PROMPT,
        },
        "standard": {
            "name": "标准报告",
            "description": "全面的竞品分析，适合日常决策",
            "sections": [
                "执行摘要",
                "竞品概览",
                "功能对比",
                "定价分析",
                "SWOT分析",
                "用户评价",
                "建议",
            ],
            "prompt": REPORT_PROMPT,
        },
        "deep": {
            "name": "深度报告",
            "description": "深入的竞品研究，适合战略规划",
            "sections": [
                "执行摘要",
                "市场分析",
                "竞品详细对比",
                "SWOT分析",
                "趋势分析",
                "竞争格局",
                "战略建议",
                "风险评估",
            ],
            "prompt": DEEP_REPORT_PROMPT,
        },
    }

    @classmethod
    def get_template(cls, report_type: str) -> Dict:
        """
        获取报告模板

        Args:
            report_type: 报告类型 (quick/standard/deep)

        Returns:
            模板信息
        """
        return cls.TEMPLATES.get(report_type, cls.TEMPLATES["standard"])

    @classmethod
    def get_prompt(cls, report_type: str) -> str:
        """
        获取报告Prompt

        Args:
            report_type: 报告类型

        Returns:
            Prompt模板
        """
        template = cls.get_template(report_type)
        return template["prompt"]

    @classmethod
    def get_sections(cls, report_type: str) -> List[str]:
        """
        获取报告章节列表

        Args:
            report_type: 报告类型

        Returns:
            章节列表
        """
        template = cls.get_template(report_type)
        return template["sections"]

    @classmethod
    def list_templates(cls) -> List[Dict]:
        """
        列出所有模板

        Returns:
            模板列表
        """
        return [
            {
                "type": k,
                "name": v["name"],
                "description": v["description"],
                "sections": v["sections"],
            }
            for k, v in cls.TEMPLATES.items()
        ]
