"""
智能竞品分析Agent - 完整演示
==============================

展示已开发模块的功能。
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from models.competitor import (
    CompetitorInfo, CompanyInfo, Product, PricingModel, ProductTier,
    CompetitorCreate, CompetitorUpdate
)
from models.analysis import (
    AnalysisRequest, AnalysisResult, ReportType, AnalysisDimension,
    SwotAnalysis, ReviewAnalysis, AnalysisStatus
)
from models.report import (
    Report, ReportFormat, QuickReport, StandardReport, DeepReport
)


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_competitor_models():
    """演示竞品数据模型"""
    print_header("1. 竞品数据模型演示")

    # 创建多个竞品
    competitors = []

    # 竞品1: Notion
    notion = CompetitorInfo(
        name="Notion",
        company_info=CompanyInfo(
            company_name="Notion Labs",
            founded="2013",
            location="美国旧金山",
            funding="融资3.4亿美元，估值100亿美元",
            employees="500-1000",
            website="https://notion.so"
        ),
        products=[
            Product(
                name="Notion",
                description="All-in-one工作空间，集文档、知识库、项目管理于一体",
                features=["文档管理", "知识库", "项目管理", "数据库", "模板市场", "API接口"],
                pricing=PricingModel(
                    model="订阅制",
                    tiers=[
                        ProductTier(name="免费版", price="$0", features=["基础功能", "5个项目"]),
                        ProductTier(name="Plus版", price="$8/月", features=["无限项目", "文件上传"]),
                        ProductTier(name="Business版", price="$15/月", features=["高级权限", "高级分析"]),
                        ProductTier(name="Enterprise版", price="定制", features=["专属支持", "高级安全"]),
                    ]
                ),
                category="生产力工具"
            )
        ],
        target_market="个人用户、团队、企业",
        key_differentiators=["灵活性强", "模板丰富", "社区活跃", "All-in-one"],
        tags=["生产力", "知识管理", "协作", "SaaS"]
    )
    competitors.append(notion)

    # 竞品2: Obsidian
    obsidian = CompetitorInfo(
        name="Obsidian",
        company_info=CompanyInfo(
            company_name="Dynalist Inc.",
            founded="2020",
            location="加拿大",
            funding="自筹资金",
            employees="10-50",
            website="https://obsidian.md"
        ),
        products=[
            Product(
                name="Obsidian",
                description="基于本地Markdown文件的知识管理工具",
                features=["双向链接", "图谱视图", "插件系统", "本地存储", "Markdown原生"],
                pricing=PricingModel(
                    model="免费增值",
                    tiers=[
                        ProductTier(name="个人版", price="$0", features=["核心功能"]),
                        ProductTier(name="商业版", price="$50/年", features=["商业使用"]),
                        ProductTier(name="Sync", price="$4/月", features=["云同步"]),
                        ProductTier(name="Publish", price="$8/月", features=["发布网站"]),
                    ]
                ),
                category="知识管理工具"
            )
        ],
        target_market="个人用户、研究者、开发者",
        key_differentiators=["本地优先", "隐私保护", "高度可定制", "插件生态"],
        tags=["知识管理", "笔记", "Markdown", "本地优先"]
    )
    competitors.append(obsidian)

    # 竞品3: 飞书文档
    feishu = CompetitorInfo(
        name="飞书文档",
        company_info=CompanyInfo(
            company_name="字节跳动",
            founded="2016",
            location="中国北京",
            funding="上市公司",
            employees="10000+",
            website="https://feishu.cn"
        ),
        products=[
            Product(
                name="飞书文档",
                description="企业级协作办公套件",
                features=["在线文档", "表格", "思维导图", "项目管理", "视频会议", "即时通讯"],
                pricing=PricingModel(
                    model="订阅制",
                    tiers=[
                        ProductTier(name="免费版", price="¥0", features=["基础功能", "50人团队"]),
                        ProductTier(name="标准版", price="¥36/人/月", features=["高级功能", "无限人数"]),
                        ProductTier(name="企业版", price="定制", features=["专属部署", "高级安全"]),
                    ]
                ),
                category="企业协作"
            )
        ],
        target_market="中大型企业",
        key_differentiators=["一体化办公", "本地化服务", "视频会议", "即时通讯"],
        tags=["企业协作", "办公套件", "视频会议", "即时通讯"]
    )
    competitors.append(feishu)

    # 显示竞品信息
    for comp in competitors:
        print(f"竞品名称: {comp.name}")
        print(f"  公司: {comp.company_info.company_name}")
        print(f"  成立: {comp.company_info.founded}")
        print(f"  地点: {comp.company_info.location}")
        print(f"  产品: {len(comp.products)}个")
        print(f"  目标市场: {comp.target_market}")
        print(f"  差异化: {', '.join(comp.key_differentiators[:3])}...")
        print()

    return competitors


def demo_analysis_models(competitors):
    """演示分析数据模型"""
    print_header("2. 分析数据模型演示")

    # 创建分析请求
    request = AnalysisRequest(
        competitors=[c.name for c in competitors],
        analysis_type=ReportType.STANDARD,
        dimensions=[
            AnalysisDimension.FEATURES,
            AnalysisDimension.PRICING,
            AnalysisDimension.SWOT,
            AnalysisDimension.REVIEWS
        ],
        my_product="我的产品"
    )

    print(f"分析请求:")
    print(f"  竞品列表: {', '.join(request.competitors)}")
    print(f"  分析类型: {request.analysis_type.value}")
    print(f"  分析维度: {', '.join([d.value for d in request.dimensions])}")
    print()

    # 创建SWOT分析
    swot_analyses = {
        "Notion": SwotAnalysis(
            strengths=["功能全面", "用户体验好", "社区活跃", "模板丰富"],
            weaknesses=["价格较高", "性能一般", "学习曲线陡"],
            opportunities=["企业市场增长", "AI功能集成", "全球化扩张"],
            threats=["竞争加剧", "用户需求变化", "技术迭代快"]
        ),
        "Obsidian": SwotAnalysis(
            strengths=["本地优先", "隐私保护", "高度可定制", "插件丰富"],
            weaknesses=["学习成本高", "协作功能弱", "移动端体验差"],
            opportunities=["隐私意识增强", "开发者市场", "知识管理需求增长"],
            threats=["云端工具竞争", "用户习惯变化", "技术门槛高"]
        ),
        "飞书文档": SwotAnalysis(
            strengths=["一体化办公", "本地化服务", "视频会议", "即时通讯"],
            weaknesses=["国际化不足", "功能深度不够", "定制性差"],
            opportunities=["企业数字化转型", "远程办公趋势", "国产替代"],
            threats=["国际竞争", "用户习惯", "技术更新快"]
        )
    }

    print("SWOT分析示例 (Notion):")
    swot = swot_analyses["Notion"]
    print(f"  优势: {', '.join(swot.strengths)}")
    print(f"  劣势: {', '.join(swot.weaknesses)}")
    print(f"  机会: {', '.join(swot.opportunities)}")
    print(f"  威胁: {', '.join(swot.threats)}")
    print()

    # 创建用户评价分析
    review_analyses = {
        "Notion": ReviewAnalysis(
            total_reviews=15000,
            average_rating=4.6,
            positive_keywords=["功能强大", "灵活", "模板多", "社区好"],
            negative_keywords=["贵", "卡顿", "学习曲线"],
            sentiment_score=0.82,
            summary="用户普遍认可功能全面性，但对价格和性能有抱怨"
        ),
        "Obsidian": ReviewAnalysis(
            total_reviews=8000,
            average_rating=4.7,
            positive_keywords=["本地优先", "隐私好", "可定制", "插件多"],
            negative_keywords=["难上手", "协作差", "移动端弱"],
            sentiment_score=0.85,
            summary="技术用户高度认可，但普通用户学习成本高"
        ),
        "飞书文档": ReviewAnalysis(
            total_reviews=25000,
            average_rating=4.3,
            positive_keywords=["一体化", "视频会议好", "本地服务"],
            negative_keywords=["功能浅", "定制差", "国际化不足"],
            sentiment_score=0.75,
            summary="企业用户认可一体化体验，但对功能深度有期待"
        )
    }

    print("用户评价分析示例 (Notion):")
    review = review_analyses["Notion"]
    print(f"  总评价数: {review.total_reviews}")
    print(f"  平均评分: {review.average_rating}")
    print(f"  情感得分: {review.sentiment_score}")
    print(f"  好评关键词: {', '.join(review.positive_keywords)}")
    print(f"  差评关键词: {', '.join(review.negative_keywords)}")
    print()

    return request, swot_analyses, review_analyses


def demo_report_models(competitors, swot_analyses, review_analyses):
    """演示报告数据模型"""
    print_header("3. 报告数据模型演示")

    # 创建快速报告
    quick_report = QuickReport(
        competitor_name="Notion",
        company_overview="Notion Labs成立于2013年，总部位于美国旧金山。公司已完成多轮融资，估值达100亿美元。Notion是一款All-in-one工作空间工具，集文档、知识库、项目管理于一体。",
        key_products=[
            {"name": "Notion", "description": "All-in-one工作空间", "price": "免费-$15/月"},
            {"name": "Notion AI", "description": "AI写作助手", "price": "$10/月"},
        ],
        main_differentiators=["灵活性强", "模板丰富", "社区活跃", "All-in-one"],
        pricing_summary="免费版可用，Plus版$8/月，Business版$15/月，企业版定制",
        recent_updates=[
            {"date": "2024-01-15", "content": "发布Notion AI 2.0"},
            {"date": "2024-01-10", "content": "新增项目管理功能"},
            {"date": "2024-01-05", "content": "与Slack深度集成"},
        ]
    )

    print("快速报告示例:")
    print(f"  竞品名称: {quick_report.competitor_name}")
    print(f"  公司概况: {quick_report.company_overview[:80]}...")
    print(f"  主要产品: {len(quick_report.key_products)}个")
    print(f"  核心优势: {', '.join(quick_report.main_differentiators)}")
    print(f"  定价策略: {quick_report.pricing_summary}")
    print(f"  最新动态: {len(quick_report.recent_updates)}条")
    print()

    # 创建标准报告
    standard_report = StandardReport(
        executive_summary="本报告对Notion、Obsidian、飞书文档三款知识管理工具进行了全面对比分析。Notion以功能全面和灵活性见长，Obsidian主打本地优先和隐私保护，飞书文档则提供一体化企业办公解决方案。",
        competitor_overview=[
            {"name": "Notion", "position": "All-in-one工作空间", "market": "全球个人和团队用户"},
            {"name": "Obsidian", "position": "本地知识管理", "market": "技术用户和研究者"},
            {"name": "飞书文档", "position": "企业协作办公", "market": "中大型企业"},
        ],
        feature_comparison={
            "文档管理": {"Notion": True, "Obsidian": True, "飞书文档": True},
            "知识库": {"Notion": True, "Obsidian": True, "飞书文档": True},
            "项目管理": {"Notion": True, "Obsidian": False, "飞书文档": True},
            "视频会议": {"Notion": False, "Obsidian": False, "飞书文档": True},
            "即时通讯": {"Notion": False, "Obsidian": False, "飞书文档": True},
            "本地优先": {"Notion": False, "Obsidian": True, "飞书文档": False},
        },
        pricing_analysis={
            "Notion": {"免费版": "$0", "Plus版": "$8/月", "Business版": "$15/月"},
            "Obsidian": {"个人版": "$0", "商业版": "$50/年", "Sync": "$4/月"},
            "飞书文档": {"免费版": "¥0", "标准版": "¥36/人/月", "企业版": "定制"},
        },
        swot_analysis=swot_analyses,
        user_reviews=review_analyses,
        recommendations=[
            "个人用户推荐Notion，功能全面且社区活跃",
            "技术用户推荐Obsidian，本地优先且高度可定制",
            "企业用户推荐飞书文档，一体化办公且本地化服务好",
        ],
        data_sources=["官网", "App Store", "Google Play", "用户论坛", "行业报告"]
    )

    print("标准报告示例:")
    print(f"  执行摘要: {standard_report.executive_summary[:100]}...")
    print(f"  竞品数量: {len(standard_report.competitor_overview)}")
    print(f"  功能对比: {len(standard_report.feature_comparison)}项")
    print(f"  建议数量: {len(standard_report.recommendations)}条")
    print()

    return quick_report, standard_report


def demo_json_serialization(competitors):
    """演示JSON序列化"""
    print_header("4. JSON序列化演示")

    # 导出竞品数据
    print("导出竞品数据为JSON:")
    for comp in competitors[:1]:  # 只显示第一个
        json_data = comp.model_dump_json(indent=2)
        print(json_data[:800] + "...")
        print()

    # 从JSON导入
    print("从JSON导入竞品数据:")
    json_str = '''
    {
        "name": "测试竞品",
        "company_info": {
            "company_name": "测试公司",
            "founded": "2024",
            "location": "中国"
        },
        "products": [],
        "target_market": "测试市场",
        "key_differentiators": ["测试差异化"]
    }
    '''

    comp = CompetitorInfo.model_validate_json(json_str)
    print(f"  导入成功: {comp.name}")
    print(f"  公司名称: {comp.company_info.company_name}")
    print()


def demo_knowledge_base_simulation():
    """演示知识库功能（模拟）"""
    print_header("5. 知识库功能演示（模拟）")

    # 模拟向量数据库操作
    print("模拟向量数据库操作:")
    print()

    # 模拟添加文档
    documents = [
        {"id": "doc_001", "content": "Notion是一款All-in-one工作空间工具", "metadata": {"competitor": "Notion", "type": "description"}},
        {"id": "doc_002", "content": "Notion支持文档管理、知识库、项目管理", "metadata": {"competitor": "Notion", "type": "features"}},
        {"id": "doc_003", "content": "Notion定价：免费版$0，Plus版$8/月", "metadata": {"competitor": "Notion", "type": "pricing"}},
        {"id": "doc_004", "content": "Obsidian是本地优先的知识管理工具", "metadata": {"competitor": "Obsidian", "type": "description"}},
        {"id": "doc_005", "content": "Obsidian支持双向链接和图谱视图", "metadata": {"competitor": "Obsidian", "type": "features"}},
    ]

    print(f"  添加了 {len(documents)} 个文档到知识库")
    for doc in documents:
        print(f"    - {doc['id']}: {doc['content'][:30]}...")
    print()

    # 模拟语义检索
    print("模拟语义检索:")
    queries = [
        "Notion的功能有哪些",
        "知识管理工具的价格",
        "本地优先的笔记软件",
    ]

    for query in queries:
        print(f"  查询: {query}")
        # 模拟检索结果
        results = [
            {"document": doc["content"], "similarity": 0.85 + i * 0.05}
            for i, doc in enumerate(documents[:2])
        ]
        for result in results:
            print(f"    - {result['document'][:40]}... (相似度: {result['similarity']:.2f})")
        print()

    # 模拟RAG上下文
    print("模拟RAG上下文获取:")
    context = """
竞品信息：Notion

公司背景：
- 公司名称: Notion Labs
- 成立时间: 2013
- 所在地: 美国旧金山
- 融资情况: 融资3.4亿美元，估值100亿美元

产品信息：
- 产品名称: Notion
- 产品描述: All-in-one工作空间
- 功能特性: 文档管理, 知识库, 项目管理, 数据库
- 定价策略: 免费版$0，Plus版$8/月，Business版$15/月

目标市场: 个人用户、团队、企业
差异化优势: 灵活性强, 模板丰富, 社区活跃, All-in-one
"""
    print(f"  上下文长度: {len(context)} 字符")
    print(f"  可用于LLM生成回答")
    print()


def demo_workflow():
    """演示完整工作流"""
    print_header("6. 完整工作流演示")

    print("竞品分析工作流:")
    print()

    steps = [
        ("1. 用户输入", "输入竞品名称和分析需求"),
        ("2. 数据采集", "从官网、App Store、社交媒体等采集数据"),
        ("3. 信息提取", "使用LLM提取结构化信息"),
        ("4. 知识库存储", "将信息存储到向量数据库"),
        ("5. 对比分析", "进行功能、价格、SWOT等分析"),
        ("6. 报告生成", "生成结构化分析报告"),
        ("7. 智能问答", "基于知识库回答用户问题"),
    ]

    for step, description in steps:
        print(f"  {step}: {description}")
    print()

    print("当前已完成的模块:")
    print("  ✅ 数据模型模块 (models/) - 定义数据结构")
    print("  ✅ 知识库模块 (knowledge/) - 向量存储和检索")
    print("  ⏳ 数据采集模块 (collector/) - 待开发")
    print("  ⏳ Agent核心模块 (agent/) - 待开发")
    print("  ⏳ 报告生成模块 (report/) - 待开发")
    print("  ⏳ API接口模块 (api/) - 待开发")
    print("  ⏳ 前端模块 (display/) - 待开发")
    print()


def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("\n  智能竞品分析Agent - 功能演示")
    print("\n" + "🎯" * 30)

    # 1. 竞品数据模型
    competitors = demo_competitor_models()

    # 2. 分析数据模型
    request, swot_analyses, review_analyses = demo_analysis_models(competitors)

    # 3. 报告数据模型
    quick_report, standard_report = demo_report_models(competitors, swot_analyses, review_analyses)

    # 4. JSON序列化
    demo_json_serialization(competitors)

    # 5. 知识库功能
    demo_knowledge_base_simulation()

    # 6. 完整工作流
    demo_workflow()

    print("=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
