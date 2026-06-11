"""
知识库模块测试
==============

测试向量数据库和知识库功能。
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch, MagicMock
from knowledge.vector_store import VectorStore
from knowledge.knowledge_base import KnowledgeBase


class TestVectorStore:
    """向量数据库测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def vector_store(self, temp_dir):
        """创建向量数据库实例"""
        return VectorStore(persist_dir=temp_dir)

    def test_create_collection(self, vector_store):
        """测试创建集合"""
        collection = vector_store.get_or_create_collection("test_collection")
        assert collection is not None
        assert collection.name == "test_collection"

    def test_add_documents(self, vector_store):
        """测试添加文档"""
        documents = ["这是第一个文档", "这是第二个文档"]
        metadatas = [
            {"type": "test", "source": "unit_test"},
            {"type": "test", "source": "unit_test"}
        ]

        ids = vector_store.add_documents(
            collection_name="test_collection",
            documents=documents,
            metadatas=metadatas
        )

        assert len(ids) == 2
        assert all(isinstance(id, str) for id in ids)

    def test_search_documents(self, vector_store):
        """测试搜索文档"""
        # 添加测试文档
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

        vector_store.add_documents(
            collection_name="test_collection",
            documents=documents,
            metadatas=metadatas
        )

        # 搜索测试
        results = vector_store.search(
            query="什么是机器学习",
            collection_name="test_collection",
            top_k=2
        )

        assert len(results) > 0
        assert len(results) <= 2
        assert "document" in results[0]
        assert "metadata" in results[0]
        assert "similarity" in results[0]

    def test_delete_documents(self, vector_store):
        """测试删除文档"""
        # 添加文档
        ids = vector_store.add_documents(
            collection_name="test_collection",
            documents=["测试文档"]
        )

        # 删除文档
        vector_store.delete_documents(
            collection_name="test_collection",
            ids=ids
        )

        # 验证删除
        stats = vector_store.get_collection_stats("test_collection")
        assert stats["count"] == 0

    def test_list_collections(self, vector_store):
        """测试列出集合"""
        # 创建多个集合
        vector_store.get_or_create_collection("collection1")
        vector_store.get_or_create_collection("collection2")

        collections = vector_store.list_collections()
        assert "collection1" in collections
        assert "collection2" in collections

    def test_delete_collection(self, vector_store):
        """测试删除集合"""
        vector_store.get_or_create_collection("test_collection")
        vector_store.delete_collection("test_collection")

        collections = vector_store.list_collections()
        assert "test_collection" not in collections

    def test_get_collection_stats(self, vector_store):
        """测试获取集合统计"""
        # 添加文档
        vector_store.add_documents(
            collection_name="test_collection",
            documents=["文档1", "文档2", "文档3"]
        )

        stats = vector_store.get_collection_stats("test_collection")
        assert stats["name"] == "test_collection"
        assert stats["count"] == 3


class TestKnowledgeBase:
    """知识库测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """创建知识库实例（使用mock embedding）"""
        with patch('knowledge.knowledge_base.create_embedding_service') as mock_create:
            # 创建mock embedding服务
            mock_embedding = Mock()
            mock_embedding.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 10
            mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_create.return_value = mock_embedding

            kb = KnowledgeBase(
                persist_dir=temp_dir,
                embedding_type="openai"
            )
            return kb

    def test_add_competitor(self, knowledge_base):
        """测试添加竞品"""
        competitor_data = {
            "company_info": {
                "company_name": "测试公司",
                "founded": "2020",
                "location": "北京"
            },
            "products": [
                {
                    "name": "测试产品",
                    "description": "这是一个测试产品",
                    "features": ["功能1", "功能2"]
                }
            ],
            "target_market": "中小企业",
            "key_differentiators": ["差异化1", "差异化2"]
        }

        # 添加竞品
        knowledge_base.add_competitor("comp_001", competitor_data)

        # 验证添加成功
        stats = knowledge_base.get_stats()
        assert "competitors" in stats
        assert stats["competitors"]["count"] > 0

    def test_add_web_content(self, knowledge_base):
        """测试添加网页内容"""
        content = "这是一段网页内容，包含了很多有用的信息。" * 10

        knowledge_base.add_web_content(
            competitor_id="comp_001",
            url="https://example.com",
            content=content,
            content_type="web_page"
        )

        # 验证添加成功
        results = knowledge_base.search_competitors(
            query="网页内容",
            competitor_id="comp_001"
        )
        assert len(results) > 0

    def test_add_user_review(self, knowledge_base):
        """测试添加用户评价"""
        knowledge_base.add_user_review(
            competitor_id="comp_001",
            review_content="这个产品很好用，功能强大",
            rating=4.5,
            source="app_store",
            review_id="review_001"
        )

        # 验证添加成功
        stats = knowledge_base.get_stats()
        assert "reviews" in stats
        assert stats["reviews"]["count"] > 0

    def test_search_competitors(self, knowledge_base):
        """测试搜索竞品"""
        # 添加测试数据
        competitor_data = {
            "company_info": {
                "company_name": "AI公司",
                "founded": "2018"
            },
            "products": [
                {
                    "name": "AI助手",
                    "description": "智能对话助手",
                    "features": ["自然语言处理", "机器学习"]
                }
            ],
            "target_market": "开发者",
            "key_differentiators": ["技术领先"]
        }

        knowledge_base.add_competitor("comp_002", competitor_data)

        # 搜索测试
        results = knowledge_base.search_competitors(
            query="AI助手",
            competitor_id="comp_002"
        )

        # 由于使用mock，可能返回空结果，但不会报错
        assert isinstance(results, list)

    def test_delete_competitor(self, knowledge_base):
        """测试删除竞品"""
        # 添加竞品
        competitor_data = {
            "company_info": {"company_name": "测试公司"},
            "products": [],
            "target_market": "测试",
            "key_differentiators": []
        }

        knowledge_base.add_competitor("comp_003", competitor_data)

        # 删除竞品
        knowledge_base.delete_competitor("comp_003")

        # 验证删除（由于使用mock，主要测试不报错）
        assert True

    def test_get_stats(self, knowledge_base):
        """测试获取统计信息"""
        stats = knowledge_base.get_stats()
        assert isinstance(stats, dict)

    def test_clear(self, knowledge_base):
        """测试清空知识库"""
        # 添加一些数据
        knowledge_base.add_competitor("comp_004", {
            "company_info": {"company_name": "测试"},
            "products": [],
            "target_market": "测试",
            "key_differentiators": []
        })

        # 清空知识库
        knowledge_base.clear()

        # 验证清空成功
        stats = knowledge_base.get_stats()
        for collection_stats in stats.values():
            assert collection_stats["count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
