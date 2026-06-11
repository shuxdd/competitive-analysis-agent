"""
数据采集模块演示
================

展示数据采集和清洗功能。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from collector.cleaner import DataCleaner


def demo_text_cleaning():
    """文本清理演示"""
    print("=== 文本清理演示 ===\n")

    # HTML清理
    html = """
    <html>
    <head><title>测试页面</title></head>
    <body>
        <h1>欢迎</h1>
        <p>这是一段<strong>测试</strong>文本。</p>
        <script>alert('test')</script>
    </body>
    </html>
    """

    cleaned = DataCleaner.clean_text(html)
    print(f"原始HTML长度: {len(html)}")
    print(f"清理后长度: {len(cleaned)}")
    print(f"清理结果: {cleaned}")
    print()


def demo_price_extraction():
    """价格提取演示"""
    print("=== 价格提取演示 ===\n")

    texts = [
        "基础版¥99/月，专业版¥299/月，企业版定制",
        "Basic $9/month, Pro $29/month, Enterprise custom",
        "免费版0元，标准版199元/年，高级版499元/年",
        "€19/月起，€199/年起",
    ]

    for text in texts:
        print(f"文本: {text}")
        prices = DataCleaner.extract_price(text)
        print(f"提取到 {len(prices)} 个价格:")
        for price in prices:
            print(f"  - {price['currency']} {price['price']}")
        print()


def demo_feature_extraction():
    """功能提取演示"""
    print("=== 功能提取演示 ===\n")

    text = """
    我们的产品支持以下功能：
    1. 支持文档管理，可以创建和编辑文档
    2. 提供知识库功能，方便团队协作
    3. 具备项目管理能力，支持看板视图
    4. 拥有数据分析功能，生成可视化报表
    5. 支持API接口，方便集成第三方系统
    """

    print(f"原始文本:\n{text}")
    features = DataCleaner.extract_features(text)
    print(f"\n提取到 {len(features)} 个功能:")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")
    print()


def demo_company_info_extraction():
    """公司信息提取演示"""
    print("=== 公司信息提取演示 ===\n")

    text = """
    示例科技有限公司成立于2020年，总部位于北京市海淀区。
    公司专注于人工智能领域，已获得A轮融资1000万美元。
    目前团队规模在100-200人，拥有博士学历员工20余人。
    """

    print(f"原始文本:\n{text}")
    info = DataCleaner.extract_company_info(text)
    print(f"\n提取的公司信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()


def demo_contact_info_extraction():
    """联系信息提取演示"""
    print("=== 联系信息提取演示 ===\n")

    text = """
    联系我们：
    - 邮箱：contact@example.com, support@example.com
    - 电话：400-123-4567
    - 手机：13800138000
    - 官网：https://www.example.com
    - 地址：北京市海淀区中关村大街1号
    """

    print(f"原始文本:\n{text}")
    info = DataCleaner.extract_contact_info(text)
    print(f"\n提取的联系信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()


def demo_data_merging():
    """数据合并演示"""
    print("=== 数据合并演示 ===\n")

    # 模拟多个数据源
    data_sources = [
        {
            "url": "https://example.com/about",
            "text": "公司成立于2020年，总部位于北京",
            "company_info": {"founded": "2020", "location": "北京"}
        },
        {
            "url": "https://example.com/pricing",
            "text": "基础版¥99/月，专业版¥299/月",
            "prices": [
                {"price": 99, "currency": "CNY"},
                {"price": 299, "currency": "CNY"}
            ]
        },
        {
            "url": "https://example.com/features",
            "text": "支持文档管理，提供知识库功能",
            "features": ["文档管理", "知识库"]
        }
    ]

    print(f"数据源数量: {len(data_sources)}")
    for source in data_sources:
        print(f"  - {source['url']}")

    # 合并数据
    merged = DataCleaner.merge_data(data_sources)

    print(f"\n合并结果:")
    print(f"  文本数量: {len(merged['texts'])}")
    print(f"  价格数量: {len(merged['prices'])}")
    print(f"  功能数量: {len(merged['features'])}")
    print(f"  来源数量: {len(merged['sources'])}")
    print(f"  公司信息: {merged['company_info']}")
    print()


def demo_search_collector():
    """搜索采集器演示（模拟）"""
    print("=== 搜索采集器演示（模拟）===\n")

    # 模拟搜索结果
    mock_results = {
        "search_parameters": {"q": "Notion 产品"},
        "organic_results": [
            {
                "title": "Notion - 一款将笔记、知识库和项目管理融为一体的协作工具",
                "link": "https://www.notion.so/",
                "snippet": "Notion是一款将笔记、知识库和项目管理融为一体的协作工具。",
                "position": 1
            },
            {
                "title": "Notion定价 - 选择适合你的计划",
                "link": "https://www.notion.so/pricing",
                "snippet": "免费版可用，Plus版$8/月，Business版$15/月。",
                "position": 2
            },
            {
                "title": "Notion功能介绍",
                "link": "https://www.notion.so/product",
                "snippet": "文档管理、知识库、项目管理、数据库等功能。",
                "position": 3
            }
        ]
    }

    print(f"搜索查询: {mock_results['search_parameters']['q']}")
    print(f"结果数量: {len(mock_results['organic_results'])}")
    print()

    # 解析结果
    print("解析结果:")
    for result in mock_results["organic_results"]:
        print(f"  {result['position']}. {result['title']}")
        print(f"     URL: {result['link']}")
        print(f"     摘要: {result['snippet']}")
        print()


def demo_scraper_collector():
    """爬取采集器演示（模拟）"""
    print("=== 爬取采集器演示（模拟）===\n")

    # 模拟爬取结果
    mock_page = {
        "url": "https://example.com",
        "title": "示例公司官网",
        "text": """
        欢迎来到示例科技有限公司

        我们是一家专注于人工智能的科技公司，成立于2020年。

        主要产品：
        1. AI助手 - 智能对话工具
        2. 数据分析平台 - 企业级数据分析

        定价：
        - 基础版：¥99/月
        - 专业版：¥299/月
        - 企业版：定制

        联系我们：contact@example.com
        """,
        "links": [
            {"url": "/products", "text": "产品"},
            {"url": "/pricing", "text": "定价"},
            {"url": "/about", "text": "关于我们"}
        ]
    }

    print(f"URL: {mock_page['url']}")
    print(f"标题: {mock_page['title']}")
    print(f"文本长度: {len(mock_page['text'])} 字符")
    print(f"链接数量: {len(mock_page['links'])}")
    print()

    # 提取信息
    print("提取的信息:")
    prices = DataCleaner.extract_price(mock_page['text'])
    print(f"  价格: {prices}")

    features = DataCleaner.extract_features(mock_page['text'])
    print(f"  功能: {features}")

    company_info = DataCleaner.extract_company_info(mock_page['text'])
    print(f"  公司: {company_info}")

    contact_info = DataCleaner.extract_contact_info(mock_page['text'])
    print(f"  联系: {contact_info}")
    print()


def main():
    """主函数"""
    print("\n" + "🔍" * 30)
    print("\n  智能竞品分析Agent - 数据采集模块演示")
    print("\n" + "🔍" * 30)

    demo_text_cleaning()
    demo_price_extraction()
    demo_feature_extraction()
    demo_company_info_extraction()
    demo_contact_info_extraction()
    demo_data_merging()
    demo_search_collector()
    demo_scraper_collector()

    print("=" * 60)
    print("  演示完成！")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
