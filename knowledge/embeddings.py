"""
Embedding服务
=============

提供文本向量化功能，支持多种Embedding模型。
"""

from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding服务"""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        dimensions: Optional[int] = None
    ):
        """
        初始化Embedding服务

        Args:
            model: Embedding模型名称
            api_key: API密钥
            api_base: API基础URL
            dimensions: 向量维度
        """
        self.model = model

        # 构建初始化参数
        init_params = {"model": model}
        if api_key:
            init_params["openai_api_key"] = api_key
        if api_base:
            init_params["openai_api_base"] = api_base
        if dimensions:
            init_params["dimensions"] = dimensions

        self.embeddings = OpenAIEmbeddings(**init_params)
        logger.info(f"Embedding服务初始化完成，模型: {model}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量Embedding

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        try:
            vectors = self.embeddings.embed_documents(texts)
            logger.info(f"成功嵌入 {len(texts)} 个文档")
            return vectors
        except Exception as e:
            logger.error(f"文档嵌入失败: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        单条Embedding

        Args:
            text: 查询文本

        Returns:
            向量
        """
        try:
            vector = self.embeddings.embed_query(text)
            logger.debug(f"成功嵌入查询: {text[:50]}...")
            return vector
        except Exception as e:
            logger.error(f"查询嵌入失败: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        分批Embedding

        Args:
            texts: 文本列表
            batch_size: 批次大小

        Returns:
            向量列表
        """
        all_vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            vectors = self.embed_documents(batch)
            all_vectors.extend(vectors)
            logger.info(f"批次 {i // batch_size + 1} 完成，处理 {len(batch)} 个文本")

        return all_vectors

    def get_embedding_dimension(self) -> int:
        """
        获取Embedding维度

        Returns:
            向量维度
        """
        # 通过嵌入一个测试文本来获取维度
        test_vector = self.embed_query("test")
        return len(test_vector)


class LocalEmbeddingService:
    """本地Embedding服务（使用sentence-transformers）"""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        """
        初始化本地Embedding服务

        Args:
            model_name: 模型名称
            device: 计算设备 (cpu/cuda)
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            self.model_name = model_name
            logger.info(f"本地Embedding服务初始化完成，模型: {model_name}, 设备: {device}")
        except ImportError:
            logger.error("sentence-transformers未安装，请运行: pip install sentence-transformers")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量Embedding

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        try:
            vectors = self.model.encode(texts, show_progress_bar=False)
            logger.info(f"成功嵌入 {len(texts)} 个文档")
            return vectors.tolist()
        except Exception as e:
            logger.error(f"文档嵌入失败: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        单条Embedding

        Args:
            text: 查询文本

        Returns:
            向量
        """
        try:
            vector = self.model.encode([text], show_progress_bar=False)
            return vector[0].tolist()
        except Exception as e:
            logger.error(f"查询嵌入失败: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        获取Embedding维度

        Returns:
            向量维度
        """
        return self.model.get_sentence_embedding_dimension()


def create_embedding_service(
    service_type: str = "openai",
    **kwargs
) -> EmbeddingService:
    """
    创建Embedding服务工厂函数

    Args:
        service_type: 服务类型 (openai/local)
        **kwargs: 其他参数

    Returns:
        Embedding服务实例
    """
    if service_type == "openai":
        return EmbeddingService(**kwargs)
    elif service_type == "local":
        return LocalEmbeddingService(**kwargs)
    else:
        raise ValueError(f"不支持的Embedding服务类型: {service_type}")
