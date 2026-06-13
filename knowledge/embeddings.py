"""
Embedding服务
=============

提供文本向量化功能，支持多种Embedding模型。
"""

from openai import OpenAI
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding服务（基于 OpenAI SDK，兼容 DashScope 等兼容接口）"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        dimensions: Optional[int] = None
    ):
        """
        初始化Embedding服务

        Args:
            model: Embedding模型名称（默认从 settings.embedding_model 读取）
            api_key: API密钥（默认从 settings.embedding_api_key 读取，再回退到 openai_api_key）
            api_base: API基础URL（默认从 settings.embedding_api_base 读取）
            dimensions: 向量维度
        """
        from config.settings import settings

        self.model = model or settings.embedding_model

        if api_key is None:
            api_key = settings.embedding_api_key or settings.openai_api_key
        if api_base is None:
            api_base = settings.embedding_api_base or settings.openai_api_base
        if dimensions is None:
            dimensions = settings.embedding_dimensions

        self._client = OpenAI(api_key=api_key, base_url=api_base)
        self._dimensions = dimensions
        logger.info(f"Embedding服务初始化完成，模型: {self.model}, api_base: {api_base}")

    def _call(self, input_text: str) -> List[float]:
        """底层 SDK 调用，提取为公共方法"""
        kwargs = {"model": self.model, "input": input_text}
        if self._dimensions:
            kwargs["dimensions"] = self._dimensions
        resp = self._client.embeddings.create(**kwargs)
        return resp.data[0].embedding

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
            # OpenAI SDK 支持批量 input
            kwargs = {"model": self.model, "input": texts}
            if self._dimensions:
                kwargs["dimensions"] = self._dimensions
            resp = self._client.embeddings.create(**kwargs)
            # 按传入顺序排序
            sorted_data = sorted(resp.data, key=lambda x: x.index)
            vectors = [d.embedding for d in sorted_data]
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
            vector = self._call(text)
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


def create_chroma_embedding_function(embedding_service: EmbeddingService):
    """
    将 EmbeddingService 包装为 Chroma 可接受的 embedding_function

    Chroma 要求: fn(inputs: List[str]) -> List[List[float]]
    """
    from chromadb import Documents, EmbeddingFunction as ChromaEmbeddingFunction

    class ServiceAdapter(ChromaEmbeddingFunction):
        def __init__(self, svc):
            self._svc = svc

        def __call__(self, inputs: Documents) -> List[List[float]]:
            return self._svc.embed_documents(inputs)

    return ServiceAdapter(embedding_service)


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
