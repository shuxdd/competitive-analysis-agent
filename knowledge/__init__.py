"""
知识库模块
==========

提供向量数据库管理和知识库功能。
"""

from .vector_store import VectorStore
from .embeddings import EmbeddingService, LocalEmbeddingService, create_embedding_service
from .knowledge_base import KnowledgeBase

__all__ = [
    "VectorStore",
    "EmbeddingService",
    "LocalEmbeddingService",
    "create_embedding_service",
    "KnowledgeBase",
]
