from datetime import datetime
from utils.report_helpers import (
    generate_report_header,
    prepare_analysis_data,
    generate_fallback_report,
)


class TestGenerateReportHeader:
    """generate_report_header 函数测试"""

    def test_basic_header(self):
        """测试基本报告头部"""
        result = generate_report_header(
            title="测试报告",
            competitors=["竞品A", "竞品B"],
            report_type="standard"
        )
        assert "测试报告" in result
        assert "竞品A" in result
        assert "竞品B" in result
        assert "标准" in result

    def test_report_types(self):
        """测试报告头部"""
        result = generate_report_header("标题", ["A"], "standard")
        assert "标准" in result


class TestPrepareAnalysisData:
    """prepare_analysis_data 函数测试"""

    def test_returns_string(self):
        """测试返回字符串"""
        data = {"key": "value"}
        result = prepare_analysis_data(data)
        assert isinstance(result, str)

    def test_contains_original_keys(self):
        """测试包含原始键"""
        data = {"competitors": ["A"], "summary": "test"}
        result = prepare_analysis_data(data)
        assert "competitors" in result
        assert "summary" in result


class TestGenerateFallbackReport:
    """generate_fallback_report 函数测试"""

    def test_contains_competitor_name(self):
        """测试包含竞品名称"""
        data = {
            "feature_matrix": {"features": []},
            "pricing_comparison": {"competitors": {}},
            "swot_analysis": {}
        }
        result = generate_fallback_report("测试竞品", data)
        assert "测试竞品" in result

    def test_contains_features(self):
        """测试包含功能信息"""
        data = {
            "feature_matrix": {
                "features": [
                    {"name": "功能A", "description": "描述A"}
                ]
            },
            "pricing_comparison": {"competitors": {}},
            "swot_analysis": {}
        }
        result = generate_fallback_report("竞品", data)
        assert "功能A" in result
