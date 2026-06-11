"""
数据采集基类
============

定义数据采集器的基础接口。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """采集器基类"""

    def __init__(self, name: str = "base"):
        self.name = name
        self.logger = logging.getLogger(f"collector.{name}")

    @abstractmethod
    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        采集数据

        Args:
            target: 采集目标（关键词、URL等）
            **kwargs: 其他参数

        Returns:
            采集结果
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> Dict[str, Any]:
        """
        解析原始数据

        Args:
            raw_data: 原始数据

        Returns:
            解析后的结构化数据
        """
        pass

    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗数据

        Args:
            data: 原始数据

        Returns:
            清洗后的数据
        """
        return data

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据

        Args:
            data: 数据

        Returns:
            是否有效
        """
        return True

    async def run(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        执行完整的采集流程

        Args:
            target: 采集目标
            **kwargs: 其他参数

        Returns:
            采集结果
        """
        try:
            self.logger.info(f"开始采集: {target}")

            # 采集
            raw_data = await self.collect(target, **kwargs)

            # 解析
            parsed_data = self.parse(raw_data)

            # 清洗
            cleaned_data = self.clean(parsed_data)

            # 验证
            if not self.validate(cleaned_data):
                self.logger.warning(f"数据验证失败: {target}")
                return {"status": "invalid", "target": target, "data": cleaned_data}

            self.logger.info(f"采集完成: {target}")
            return {
                "status": "success",
                "target": target,
                "source": self.name,
                "data": cleaned_data
            }

        except Exception as e:
            self.logger.error(f"采集失败: {target}, 错误: {e}")
            return {
                "status": "error",
                "target": target,
                "source": self.name,
                "error": str(e)
            }


class CollectorResult:
    """采集结果封装"""

    def __init__(
        self,
        status: str,
        target: str,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.target = target
        self.source = source
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "target": self.target,
            "source": self.source,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }
