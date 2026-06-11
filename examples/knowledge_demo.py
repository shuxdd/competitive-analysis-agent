"""
知识库使用示例
==============

展示如何使用知识库模块。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置标准输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from unittest.mock import Mock, patch
from knowledge.vector_store import VectorStore
from knowledge.knowledge_base import KnowledgeBase


def demo_vector_store():
    """向量数据库示例"""
    print("=== 向量数据库示例 ===\n")

    # 使用mock演示
    with patch('knowledge.vector_store.chromadb.PersistentClient') as mock_client:
        # 设置mock
        mock_collection = Mock()
        mock_collection.name = "competitors"
        mock_collection.count.return_value = 0
        mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [
                ["人工智能是计算机科学的一个分支", "机器学习是AI的子领域"]
            ],
            "metadatas": [
                [{"type": "definition"}, {"type": "definition"}]
            ],
            "distances": [[0.1, 0.2]]
        }

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        # 创建向量数据库
        store = VectorStore(persist_dir="./demo_data")

        print("1. 创建集合")
        collection = store.get_or_create_collection("competitors")
        print(f"   集合名称: {collection.name}")

        print("\n2. 添加文档")
        documents = [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的子领域",
            "深度学习是机器学习的一种方法"
        ]
        metadatas = [
            {"topic": "AI", "level": "basic"},
            {"topic": "ML", "level": "intermediate"},
            {"topic": "DL", "level": "advanced"}
        ]

        ids = store.add_documents(
            collection_name="competitors",
            documents=documents,
            metadatas=metadatas
        )
        print(f"   添加了 {len(documents)} 个文档")
        print(f"   文档ID: {ids[:3]}...")

        print("\n3. 搜索文档")
        results = store.search(
            query="什么是机器学习",
            collection_name="competitors",
            top_k=2
        )
        print(f"   搜索到 {len(results)} 个结果")
        for i, result in enumerate(results):
            print(f"   结果 {i+1}: {result['document'][:50]}...")
            print(f"   相似度: {result['similarity']:.2f}")

        print("\n4. 获取统计信息")
        stats = store.get_collection_stats("competitors")
        print(f"   集合名称: {stats['name']}")
        print(f"   文档数量: {stats['count']}")


def demo_knowledge_base():
    """知识库示例"""
    print("\n=== 知识库示例 ===\n")

    with patch('knowledge.knowledge_base.create_embedding_service') as mock_embedding:
        # 设置mock
        mock_embedding_service = Mock()
        mock_embedding_service.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 10
        mock_embedding_service.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_embedding.return_value = mock_embedding_service

        with patch('knowledge.vector_store.chromadb.PersistentClient') as mock_client:
            # 设置mock
            mock_collection = Mock()
            mock_collection.name = "competitors"
            mock_collection.count.return_value = 0
            mock_collection.query.return_value = {
                "ids": [["id1"]],
                "documents": [["竞品信息"]],
                "metadatas": [[{"competitor_id": "comp_001"}]],
                "distances": [[0.1]]
            }

            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = mock_collection
            mock_client_instance.list_collections.return_value = [mock_collection]
            mock_client.return_value = mock_client_instance

            # 创建知识库
            kb = KnowledgeBase(persist_dir="./demo_data")

            print("1. 添加竞品信息")
            competitor_data = {
                "company_info": {
                    "company_name": "示例科技有限公司",
                    "founded": "2020",
                    "location": "北京",
                    "funding": "B轮 1亿美元",
                    "employees": "100-500"
                },
                "products": [
                    {
                        "name": "AI助手",
                        "description": "基于大语言模型的智能助手",
                        "features": ["自然语言对话", "文档分析", "代码生成"],
                        "pricing": {
                            "model": "订阅制",
                            "tiers": [
                                {"name": "基础版", "price": "¥99/月"},
                                {"name": "专业版", "price": "¥299/月"}
                            ]
                        }
                    }
                ],
                "target_market": "中小企业和开发者",
                "key_differentiators": ["技术领先", "价格优势", "本地化服务"]
            }

            kb.add_competitor("comp_001", competitor_data)
            print("   竞品信息添加成功")

            print("\n2. 添加网页内容")
            web_content = """
            示例科技是一家专注于人工智能的科技公司，成立于2020年。
            公司总部位于北京，在上海和深圳设有研发中心。
            公司已完成B轮融资，融资金额达1亿美元。
            主要产品包括AI助手、数据分析平台等。
            """

            kb.add_web_content(
                competitor_id="comp_001",
                url="https://example.com/about",
                content=web_content,
                content_type="company_intro"
            )
            print("   网页内容添加成功")

            print("\n3. 添加用户评价")
            reviews = [
                {"content": "产品很好用，功能强大", "rating": 4.5, "source": "app_store"},
                {"content": "界面友好，学习成本低", "rating": 4.0, "source": "google_play"},
                {"content": "客服响应快，解决问题及时", "rating": 4.8, "source": "官网"}
            ]

            for review in reviews:
                kb.add_user_review(
                    competitor_id="comp_001",
                    review_content=review["content"],
                    rating=review["rating"],
                    source=review["source"]
                )
            print(f"   添加了 {len(reviews)} 条用户评价")

            print("\n4. 搜索竞品信息")
            results = kb.search_competitors(
                query="AI助手功能",
                competitor_id="comp_001"
            )
            print(f"   搜索到 {len(results)} 条结果")

            print("\n5. 搜索用户评价")
            review_results = kb.search_reviews(
                query="产品好用",
                competitor_id="comp_001"
            )
            print(f"   搜索到 {len(review_results)} 条评价")

            print("\n6. 获取竞品上下文")
            context = kb.get_competitor_context(
                competitor_id="comp_001",
                query="公司背景",
                max_tokens=500
            )
            print(f"   上下文长度: {len(context)} 字符")

            print("\n7. 获取统计信息")
            stats = kb.get_stats()
            print(f"   统计信息: {stats}")


def demo_text_splitting():
    """文本分割示例"""
    print("\n=== 文本分割示例 ===\n")

    with patch('knowledge.knowledge_base.create_embedding_service') as mock_embedding:
        mock_embedding_service = Mock()
        mock_embedding.return_value = mock_embedding_service

        with patch('knowledge.vector_store.chromadb.PersistentClient') as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance

            kb = KnowledgeBase(persist_dir="./demo_data")

            # 测试文本分割
            long_text = "这是一段很长的文本。" * 100
            chunks = kb._split_text(long_text, max_chunk_size=200, overlap=50)

            print(f"原始文本长度: {len(long_text)} 字符")
            print(f"分割后块数: {len(chunks)}")
            print(f"第一块长度: {len(chunks[0])} 字符")
            print(f"最后一块长度: {len(chunks[-1])} 字符")


if __name__ == "__main__":
    print("智能竞品分析Agent - 知识库使用示例\n")
    print("=" * 50)
    print()

    demo_vector_store()
    demo_knowledge_base()
    demo_text_splitting()

    print("\n" + "=" * 50)
    print("示例运行完成！")
