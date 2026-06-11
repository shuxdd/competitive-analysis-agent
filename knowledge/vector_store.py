"""
向量数据库管理
==============

管理Chroma向量数据库，提供文档存储和语义检索功能。
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """向量数据库管理"""

    def __init__(
        self,
        persist_dir: str = "./data/chroma",
        anonymized_telemetry: bool = False
    ):
        """
        初始化向量数据库

        Args:
            persist_dir: 持久化目录
            anonymized_telemetry: 是否启用匿名遥测
        """
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=anonymized_telemetry)
        )
        logger.info(f"向量数据库初始化完成，持久化目录: {persist_dir}")

    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        获取或创建集合

        Args:
            name: 集合名称
            metadata: 集合元数据

        Returns:
            Chroma集合对象
        """
        if metadata is None:
            metadata = {"hnsw:space": "cosine"}

        collection = self.client.get_or_create_collection(
            name=name,
            metadata=metadata
        )
        logger.info(f"获取/创建集合: {name}, 当前文档数: {collection.count()}")
        return collection

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文档到向量库

        Args:
            collection_name: 集合名称
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表

        Returns:
            文档ID列表
        """
        collection = self.get_or_create_collection(collection_name)

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        # 确保元数据中的值都是字符串
        if metadatas:
            cleaned_metadatas = []
            for meta in metadatas:
                cleaned = {}
                for key, value in meta.items():
                    if isinstance(value, (list, dict)):
                        cleaned[key] = str(value)
                    else:
                        cleaned[key] = value
                cleaned_metadatas.append(cleaned)
            metadatas = cleaned_metadatas

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"添加 {len(documents)} 个文档到集合 {collection_name}")
        return ids

    def update_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        更新文档

        Args:
            collection_name: 集合名称
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表
        """
        collection = self.get_or_create_collection(collection_name)

        if metadatas:
            cleaned_metadatas = []
            for meta in metadatas:
                cleaned = {}
                for key, value in meta.items():
                    if isinstance(value, (list, dict)):
                        cleaned[key] = str(value)
                    else:
                        cleaned[key] = value
                cleaned_metadatas.append(cleaned)
            metadatas = cleaned_metadatas

        collection.update(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"更新 {len(ids)} 个文档在集合 {collection_name}")

    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ):
        """
        删除文档

        Args:
            collection_name: 集合名称
            ids: 文档ID列表
        """
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
        logger.info(f"删除 {len(ids)} 个文档从集合 {collection_name}")

    def search(
        self,
        query: str,
        collection_name: str = "competitors",
        top_k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        语义检索

        Args:
            query: 查询文本
            collection_name: 集合名称
            top_k: 返回结果数量
            where: 元数据过滤条件
            where_document: 文档内容过滤条件

        Returns:
            检索结果列表
        """
        collection = self.get_or_create_collection(collection_name)

        query_params = {
            "query_texts": [query],
            "n_results": top_k
        }

        if where:
            query_params["where"] = where

        if where_document:
            query_params["where_document"] = where_document

        results = collection.query(**query_params)

        # 格式化结果
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0] if results["metadatas"] else [{}] * len(results["documents"][0]),
                results["distances"][0] if results["distances"] else [0] * len(results["documents"][0])
            )):
                formatted_results.append({
                    "id": results["ids"][0][i] if results["ids"] else None,
                    "document": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": 1 - dist  # cosine距离转换为相似度
                })

        logger.info(f"检索到 {len(formatted_results)} 个结果，查询: {query[:50]}...")
        return formatted_results

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        获取集合统计信息

        Args:
            collection_name: 集合名称

        Returns:
            统计信息
        """
        collection = self.get_or_create_collection(collection_name)
        return {
            "name": collection_name,
            "count": collection.count(),
            "metadata": collection.metadata
        }

    def list_collections(self) -> List[str]:
        """
        列出所有集合

        Returns:
            集合名称列表
        """
        return [col.name for col in self.client.list_collections()]

    def delete_collection(self, name: str):
        """
        删除集合

        Args:
            name: 集合名称
        """
        self.client.delete_collection(name)
        logger.info(f"删除集合: {name}")

    def clear_collection(self, name: str):
        """
        清空集合

        Args:
            name: 集合名称
        """
        self.delete_collection(name)
        self.get_or_create_collection(name)
        logger.info(f"清空集合: {name}")
