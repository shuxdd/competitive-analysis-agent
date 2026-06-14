"""
报告模板管理
============

管理不同类型的报告模板。
"""

from typing import Dict, List
from config.prompts import REPORT_PROMPT, COMPARISON_REPORT_PROMPT


class ReportTemplates:
    """报告模板管理器"""

    # 模板定义
    TEMPLATES = {
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
        "comparison": {
            "name": "对比分析报告",
            "description": "我方产品 vs 竞品的对比分析",
            "sections": [
                "执行摘要",
                "我方 vs 竞品概览",
                "功能对比",
                "定价对比",
                "SWOT 对比",
                "竞争格局",
                "战略建议",
            ],
            "prompt": COMPARISON_REPORT_PROMPT,
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
