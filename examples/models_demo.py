"""
数据模型使用示例
================

展示如何使用竞品分析系统的数据模型。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置标准输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

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


def demo_competitor_models():
    """竞品模型示例"""
    print("=== 竞品模型示例 ===\n")

    # 创建产品定价
    pricing = PricingModel(
        model="订阅制",
        tiers=[
            ProductTier(name="基础版", price="¥99/月", features=["基础功能", "5GB存储"]),
            ProductTier(name="专业版", price="¥299/月", features=["全部功能", "50GB存储", "优先支持"]),
            ProductTier(name="企业版", price="定制", features=["定制功能", "无限存储", "专属客服"]),
        ],
        currency="CNY"
    )

    # 创建产品
    product = Product(
        name="AI助手",
        description="基于大语言模型的智能助手",
        features=["自然语言对话", "文档分析", "代码生成", "多语言支持"],
        pricing=pricing,
        url="https://example.com/ai-assistant",
        category="AI工具"
    )

    # 创建公司信息
    company = CompanyInfo(
        company_name="示例科技有限公司",
        founded="2020",
        location="北京",
        funding="B轮 1亿美元",
        employees="100-500",
        website="https://example.com",
        industry="人工智能"
    )

    # 创建竞品信息
    competitor = CompetitorInfo(
        name="示例AI",
        company_info=company,
        products=[product],
        target_market="中小企业和开发者",
        key_differentiators=["技术领先", "价格优势", "本地化服务"],
        tags=["AI", "SaaS", "开发者工具"]
    )

    print(f"竞品名称: {competitor.name}")
    print(f"公司名称: {competitor.company_info.company_name}")
    print(f"产品数量: {len(competitor.products)}")
    print(f"目标市场: {competitor.target_market}")
    print(f"差异化优势: {', '.join(competitor.key_differentiators)}")
    print()


def demo_analysis_models():
    """分析模型示例"""
    print("=== 分析模型示例 ===\n")

    # 创建分析请求
    request = AnalysisRequest(
        competitors=["竞品A", "竞品B", "竞品C"],
        analysis_type=ReportType.STANDARD,
        dimensions=[
            AnalysisDimension.FEATURES,
            AnalysisDimension.PRICING,
            AnalysisDimension.SWOT,
            AnalysisDimension.REVIEWS,
        ],
        my_product="我的产品"
    )

    print(f"竞品列表: {', '.join(request.competitors)}")
    print(f"分析类型: {request.analysis_type.value}")
    print(f"分析维度: {', '.join([d.value for d in request.dimensions])}")

    # 创建SWOT分析
    swot = SwotAnalysis(
        strengths=["技术领先", "用户基数大", "品牌知名度高"],
        weaknesses=["定价较高", "移动端体验一般"],
        opportunities=["市场增长迅速", "新进入者少"],
        threats=["新竞品不断涌现", "技术迭代快"]
    )

    print("\nSWOT分析:")
    print(f"  优势: {', '.join(swot.strengths)}")
    print(f"  劣势: {', '.join(swot.weaknesses)}")
    print(f"  机会: {', '.join(swot.opportunities)}")
    print(f"  威胁: {', '.join(swot.threats)}")

    # 创建用户评价分析
    review = ReviewAnalysis(
        total_reviews=1500,
        average_rating=4.3,
        positive_keywords=["好用", "稳定", "功能强大", "性价比高"],
        negative_keywords=["学习曲线陡", "文档不完善"],
        sentiment_score=0.75,
        summary="整体评价良好，用户认可产品功能和性价比"
    )

    print(f"\n用户评价分析:")
    print(f"  总评价数: {review.total_reviews}")
    print(f"  平均评分: {review.average_rating}")
    print(f"  情感得分: {review.sentiment_score}")
    print(f"  好评关键词: {', '.join(review.positive_keywords)}")
    print(f"  差评关键词: {', '.join(review.negative_keywords)}")
    print()


def demo_report_models():
    """报告模型示例"""
    print("=== 报告模型示例 ===\n")

    # 创建快速报告
    quick_report = QuickReport(
        competitor_name="竞品A",
        company_overview="这是一家专注于人工智能的科技公司，成立于2018年，已完成B轮融资。",
        key_products=[
            {"name": "AI助手", "description": "智能对话助手", "price": "¥199/月"},
            {"name": "数据分析平台", "description": "企业级数据分析", "price": "¥499/月"},
        ],
        main_differentiators=["技术领先", "本地化服务", "价格优势"],
        pricing_summary="基础版¥99/月，专业版¥299/月，企业版定制",
        recent_updates=[
            {"date": "2024-01-15", "content": "发布新版本3.0"},
            {"date": "2024-01-10", "content": "获得1亿美元融资"},
            {"date": "2024-01-05", "content": "与某大型企业达成合作"},
        ]
    )

    print(f"竞品名称: {quick_report.competitor_name}")
    print(f"公司概况: {quick_report.company_overview}")
    print(f"主要产品: {len(quick_report.key_products)}个")
    print(f"核心优势: {', '.join(quick_report.main_differentiators)}")
    print(f"定价策略: {quick_report.pricing_summary}")
    print(f"最新动态: {len(quick_report.recent_updates)}条")
    print()


def demo_json_serialization():
    """JSON序列化示例"""
    print("=== JSON序列化示例 ===\n")

    # 创建竞品对象
    competitor = CompetitorInfo(
        name="测试竞品",
        company_info=CompanyInfo(
            company_name="测试公司",
            founded="2020"
        ),
        products=[
            Product(
                name="测试产品",
                description="这是一个测试产品",
                features=["功能1", "功能2"]
            )
        ],
        target_market="测试市场"
    )

    # 序列化为JSON
    json_data = competitor.model_dump_json(indent=2)
    print("竞品JSON数据:")
    print(json_data[:500] + "..." if len(json_data) > 500 else json_data)
    print()

    # 从JSON反序列化
    competitor_from_json = CompetitorInfo.model_validate_json(json_data)
    print(f"从JSON恢复的竞品名称: {competitor_from_json.name}")
    print(f"从JSON恢复的公司名称: {competitor_from_json.company_info.company_name}")
    print()


if __name__ == "__main__":
    print("智能竞品分析Agent - 数据模型使用示例\n")
    print("=" * 50)
    print()

    demo_competitor_models()
    demo_analysis_models()
    demo_report_models()
    demo_json_serialization()

    print("=" * 50)
    print("示例运行完成！")
