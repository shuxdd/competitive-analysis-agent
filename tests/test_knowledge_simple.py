"""
知识库模块简单测试
==================

使用mock测试知识库功能。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from knowledge.vector_store import VectorStore
from knowledge.knowledge_base import KnowledgeBase


class TestVectorStoreSimple:
    """向量数据库简单测试"""

    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_vector_store_init(self, mock_client):
        """测试向量数据库初始化"""
        store = VectorStore(persist_dir="./test_data")
        assert store is not None
        mock_client.assert_called_once()

    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_get_or_create_collection(self, mock_client):
        """测试获取或创建集合"""
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 0

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        store = VectorStore(persist_dir="./test_data")
        collection = store.get_or_create_collection("test_collection")

        assert collection.name == "test_collection"
        mock_client_instance.get_or_create_collection.assert_called_once()

    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_add_documents(self, mock_client):
        """测试添加文档"""
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 0

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        store = VectorStore(persist_dir="./test_data")
        ids = store.add_documents(
            collection_name="test_collection",
            documents=["文档1", "文档2"],
            metadatas=[{"type": "test"}, {"type": "test"}]
        )

        assert len(ids) == 2
        mock_collection.add.assert_called_once()

    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_search_documents(self, mock_client):
        """测试搜索文档"""
        mock_collection = Mock()
        mock_collection.name = "test_collection"
        mock_collection.count.return_value = 0
        mock_collection.query.return_value = {
            "ids": [["id1", "id2"]],
            "documents": [["文档1", "文档2"]],
            "metadatas": [[{"type": "test"}, {"type": "test"}]],
            "distances": [[0.1, 0.2]]
        }

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        store = VectorStore(persist_dir="./test_data")
        results = store.search(
            query="测试查询",
            collection_name="test_collection",
            top_k=2
        )

        assert len(results) == 2
        assert "document" in results[0]
        assert "similarity" in results[0]


class TestKnowledgeBaseSimple:
    """知识库简单测试"""

    @patch('knowledge.knowledge_base.create_embedding_service')
    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_knowledge_base_init(self, mock_client, mock_embedding):
        """测试知识库初始化"""
        mock_embedding_service = Mock()
        mock_embedding.return_value = mock_embedding_service

        kb = KnowledgeBase(persist_dir="./test_data")
        assert kb is not None

    @patch('knowledge.knowledge_base.create_embedding_service')
    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_add_competitor(self, mock_client, mock_embedding):
        """测试添加竞品"""
        mock_embedding_service = Mock()
        mock_embedding_service.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 5
        mock_embedding.return_value = mock_embedding_service

        mock_collection = Mock()
        mock_collection.name = "competitors"
        mock_collection.count.return_value = 0

        mock_client_instance = Mock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        kb = KnowledgeBase(persist_dir="./test_data")

        competitor_data = {
            "company_info": {
                "company_name": "测试公司",
                "founded": "2020"
            },
            "products": [
                {
                    "name": "测试产品",
                    "description": "测试描述",
                    "features": ["功能1", "功能2"]
                }
            ],
            "target_market": "测试市场",
            "key_differentiators": ["差异化1"]
        }

        kb.add_competitor("comp_001", competitor_data)
        mock_collection.add.assert_called_once()

    @patch('knowledge.knowledge_base.create_embedding_service')
    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_search_competitors(self, mock_client, mock_embedding):
        """测试搜索竞品"""
        mock_embedding_service = Mock()
        mock_embedding_service.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_embedding.return_value = mock_embedding_service

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
        mock_client.return_value = mock_client_instance

        kb = KnowledgeBase(persist_dir="./test_data")
        results = kb.search_competitors(
            query="测试查询",
            competitor_id="comp_001"
        )

        assert isinstance(results, list)

    @patch('knowledge.knowledge_base.create_embedding_service')
    @patch('knowledge.vector_store.chromadb.PersistentClient')
    def test_get_stats(self, mock_client, mock_embedding):
        """测试获取统计信息"""
        mock_embedding_service = Mock()
        mock_embedding.return_value = mock_embedding_service

        mock_collection = Mock()
        mock_collection.name = "competitors"
        mock_collection.count.return_value = 10
        mock_collection.metadata = {"hnsw:space": "cosine"}

        mock_client_instance = Mock()
        mock_client_instance.list_collections.return_value = [mock_collection]
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = mock_client_instance

        kb = KnowledgeBase(persist_dir="./test_data")
        stats = kb.get_stats()

        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
