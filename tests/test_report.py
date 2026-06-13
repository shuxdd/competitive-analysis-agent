"""
报告生成模块测试
================

测试报告生成功能。
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, AsyncMock, patch
from report.generator import ReportGenerator
from report.templates import ReportTemplates


class TestReportTemplates:
    """报告模板测试"""

    def test_list_templates(self):
        """测试列出所有模板"""
        templates = ReportTemplates.list_templates()

        assert len(templates) == 1
        assert templates[0]["type"] == "standard"

    def test_get_standard_template(self):
        """测试获取标准报告模板"""
        template = ReportTemplates.get_template("standard")

        assert template["name"] == "标准报告"
        assert "功能对比" in template["sections"]

    def test_get_default_template(self):
        """测试获取默认模板（未知类型）"""
        template = ReportTemplates.get_template("unknown")

        assert template["name"] == "标准报告"

    def test_get_prompt(self):
        """测试获取Prompt"""
        prompt = ReportTemplates.get_prompt("standard")

        assert "{analysis_data}" in prompt
        assert len(prompt) > 50

    def test_get_sections(self):
        """测试获取章节列表"""
        sections = ReportTemplates.get_sections("standard")

        assert isinstance(sections, list)
        assert len(sections) > 0


class TestReportGenerator:
    """报告生成器测试"""

    def test_initialization(self):
        """测试初始化"""
        with patch("report.generator.settings") as mock_settings:
            mock_settings.report_output_dir = tempfile.mkdtemp()
            generator = ReportGenerator()

            assert generator.output_dir is not None
            assert os.path.exists(generator.output_dir)

    def test_generate_header(self):
        """测试报告头部生成"""
        with patch("report.generator.settings") as mock_settings:
            mock_settings.report_output_dir = tempfile.mkdtemp()
            generator = ReportGenerator()

            header = generator._generate_header(["Notion", "Obsidian"], "standard")

            assert "竞品分析报告" in header
            assert "Notion" in header
            assert "标准" in header

    def test_export_markdown(self):
        """测试Markdown导出"""
        with patch("report.generator.settings") as mock_settings:
            tmpdir = tempfile.mkdtemp()
            mock_settings.report_output_dir = tmpdir
            generator = ReportGenerator()

            report = "# 测试报告\n\n这是测试内容。"
            filepath = generator.export_markdown(report, "test_report")

            assert os.path.exists(filepath)
            assert filepath.endswith(".md")

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "测试报告" in content

    def test_generate_fallback(self):
        """测试降级报告生成"""
        with patch("report.generator.settings") as mock_settings:
            mock_settings.report_output_dir = tempfile.mkdtemp()
            generator = ReportGenerator()

            analysis_results = {
                "summary": "测试摘要",
                "feature_matrix": {
                    "features": ["功能A", "功能B"],
                    "competitors": {"Notion": {"功能A": True}},
                },
                "pricing_comparison": {},
                "swot_analysis": {},
            }

            report = generator._generate_fallback(
                analysis_results, ["Notion"], "standard"
            )

            assert "竞品分析报告" in report
            assert "测试摘要" in report

    @pytest.mark.asyncio
    async def test_generate_with_mock_llm(self):
        """测试使用mock LLM生成报告"""
        with patch("report.generator.settings") as mock_settings:
            mock_settings.report_output_dir = tempfile.mkdtemp()

            mock_response = Mock()
            mock_response.content = "## 测试报告内容\n\n这是LLM生成的报告。"

            with patch("report.generator.create_llm") as mock_create:
                mock_llm = AsyncMock()
                mock_llm.ainvoke.return_value = mock_response
                mock_create.return_value = mock_llm

                generator = ReportGenerator()
                report = await generator.generate(
                    analysis_results={"summary": "测试"},
                    report_type="standard",
                    competitors=["Notion"],
                )

                assert "竞品分析报告" in report
                assert "测试报告内容" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
