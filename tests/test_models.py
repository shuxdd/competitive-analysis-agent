"""
数据模型测试
============

测试数据模型的创建和验证。
"""

import pytest
from datetime import datetime
from models.competitor import (
    ProductTier,
    PricingModel,
    Product,
    CompanyInfo,
    CompetitorInfo,
    CompetitorCreate,
)
from models.analysis import (
    ReportType,
    AnalysisDimension,
    AnalysisRequest,
    SwotAnalysis,
    ReviewAnalysis,
    AnalysisResult,
)
from models.report import (
    ReportFormat,
    Report,
    QuickReport,
)


class TestCompetitorModels:
    """竞品模型测试"""

    def test_product_tier_creation(self):
        """测试产品定价层级创建"""
        tier = ProductTier(
            name="基础版",
            price="¥99/月",
            features=["功能1", "功能2"]
        )
        assert tier.name == "基础版"
        assert tier.price == "¥99/月"
        assert len(tier.features) == 2

    def test_pricing_model_creation(self):
        """测试定价模型创建"""
        pricing = PricingModel(
            model="订阅制",
            tiers=[
                ProductTier(name="基础版", price="¥99/月"),
                ProductTier(name="专业版", price="¥299/月"),
            ],
            currency="CNY"
        )
        assert pricing.model == "订阅制"
        assert len(pricing.tiers) == 2
        assert pricing.currency == "CNY"

    def test_product_creation(self):
        """测试产品创建"""
        product = Product(
            name="测试产品",
            description="这是一个测试产品",
            features=["功能1", "功能2", "功能3"],
            pricing=PricingModel(
                model="订阅制",
                tiers=[ProductTier(name="基础版", price="¥99/月")]
            )
        )
        assert product.name == "测试产品"
        assert len(product.features) == 3
        assert product.pricing is not None

    def test_company_info_creation(self):
        """测试公司信息创建"""
        company = CompanyInfo(
            company_name="测试公司",
            founded="2020",
            location="北京",
            employees="100-500"
        )
        assert company.company_name == "测试公司"
        assert company.founded == "2020"

    def test_competitor_info_creation(self):
        """测试竞品信息创建"""
        competitor = CompetitorInfo(
            name="竞品A",
            company_info=CompanyInfo(
                company_name="竞品A公司",
                founded="2018"
            ),
            products=[
                Product(
                    name="产品1",
                    description="产品描述",
                    features=["功能1", "功能2"]
                )
            ],
            target_market="中小企业",
            key_differentiators=["差异化1", "差异化2"]
        )
        assert competitor.name == "竞品A"
        assert len(competitor.products) == 1
        assert len(competitor.key_differentiators) == 2

    def test_competitor_create_request(self):
        """测试创建竞品请求"""
        request = CompetitorCreate(
            name="新竞品",
            website="https://example.com",
            industry="SaaS",
            tags=["AI", "数据分析"]
        )
        assert request.name == "新竞品"
        assert request.website == "https://example.com"


class TestAnalysisModels:
    """分析模型测试"""

    def test_report_type_enum(self):
        """测试报告类型枚举"""
        assert ReportType.QUICK == "quick"
        assert ReportType.STANDARD == "standard"
        assert ReportType.DEEP == "deep"

    def test_analysis_dimension_enum(self):
        """测试分析维度枚举"""
        assert AnalysisDimension.FEATURES == "features"
        assert AnalysisDimension.PRICING == "pricing"
        assert AnalysisDimension.SWOT == "swot"

    def test_analysis_request_creation(self):
        """测试分析请求创建"""
        request = AnalysisRequest(
            competitors=["竞品A", "竞品B", "竞品C"],
            analysis_type=ReportType.STANDARD,
            dimensions=[
                AnalysisDimension.FEATURES,
                AnalysisDimension.PRICING,
                AnalysisDimension.SWOT
            ]
        )
        assert len(request.competitors) == 3
        assert request.analysis_type == ReportType.STANDARD
        assert len(request.dimensions) == 3

    def test_swot_analysis_creation(self):
        """测试SWOT分析创建"""
        swot = SwotAnalysis(
            strengths=["优势1", "优势2"],
            weaknesses=["劣势1"],
            opportunities=["机会1", "机会2"],
            threats=["威胁1"]
        )
        assert len(swot.strengths) == 2
        assert len(swot.weaknesses) == 1
        assert len(swot.opportunities) == 2
        assert len(swot.threats) == 1

    def test_review_analysis_creation(self):
        """测试用户评价分析创建"""
        review = ReviewAnalysis(
            total_reviews=100,
            average_rating=4.5,
            positive_keywords=["好用", "稳定"],
            negative_keywords=["贵", "复杂"],
            sentiment_score=0.7,
            summary="整体评价良好"
        )
        assert review.total_reviews == 100
        assert review.average_rating == 4.5
        assert review.sentiment_score == 0.7

    def test_analysis_result_creation(self):
        """测试分析结果创建"""
        result = AnalysisResult(
            request=AnalysisRequest(
                competitors=["竞品A", "竞品B"],
                analysis_type=ReportType.STANDARD
            ),
            status="pending"
        )
        assert result.analysis_id is not None
        assert result.status == "pending"
        assert result.created_at is not None


class TestReportModels:
    """报告模型测试"""

    def test_report_format_enum(self):
        """测试报告格式枚举"""
        assert ReportFormat.MARKDOWN == "markdown"
        assert ReportFormat.PDF == "pdf"
        assert ReportFormat.HTML == "html"

    def test_report_creation(self):
        """测试报告创建"""
        report = Report(
            analysis_id="test-analysis-id",
            title="竞品分析报告",
            report_type="standard",
            format=ReportFormat.MARKDOWN,
            content="# 竞品分析报告\n\n这是报告内容..."
        )
        assert report.report_id is not None
        assert report.title == "竞品分析报告"
        assert report.format == ReportFormat.MARKDOWN

    def test_quick_report_creation(self):
        """测试快速报告创建"""
        report = QuickReport(
            competitor_name="竞品A",
            company_overview="这是一家专注于AI的公司",
            key_products=[
                {"name": "产品1", "description": "AI助手"},
                {"name": "产品2", "description": "数据分析平台"}
            ],
            main_differentiators=["技术领先", "价格优势"],
            pricing_summary="基础版¥99/月，专业版¥299/月",
            recent_updates=[
                {"date": "2024-01-15", "content": "发布新版本"},
                {"date": "2024-01-10", "content": "获得融资"}
            ]
        )
        assert report.competitor_name == "竞品A"
        assert len(report.key_products) == 2
        assert len(report.main_differentiators) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
