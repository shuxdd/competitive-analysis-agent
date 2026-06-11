"""
竞品数据模型
============

定义竞品、产品、定价等核心数据结构。
"""

from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ProductTier(BaseModel):
    """产品定价层级"""
    name: str
    price: str
    features: List[str] = []


class PricingModel(BaseModel):
    """定价模型"""
    model: str = ""  # 订阅制、一次性、免费增值等
    tiers: List[ProductTier] = []
    currency: str = "CNY"
    notes: Optional[str] = None


class Product(BaseModel):
    """产品信息"""
    product_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    features: List[str] = []
    pricing: Optional[PricingModel] = None
    url: Optional[str] = None
    category: Optional[str] = None
    release_date: Optional[str] = None


class CompanyInfo(BaseModel):
    """公司基本信息"""
    company_name: str
    founded: Optional[str] = None
    location: Optional[str] = None
    funding: Optional[str] = None
    employees: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class CompetitorInfo(BaseModel):
    """竞品完整信息"""
    competitor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    company_info: CompanyInfo
    products: List[Product] = []
    target_market: Optional[str] = None
    key_differentiators: List[str] = []
    sources: List[str] = []
    tags: List[str] = []
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class CompetitorUpdate(BaseModel):
    """竞品更新记录"""
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competitor_id: str
    update_type: str  # product, pricing, news, partnership, etc.
    title: str
    content: str
    source: str
    url: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.now)

    @field_serializer('detected_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class CompetitorCreate(BaseModel):
    """创建竞品请求"""
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    tags: List[str] = []


class CompetitorUpdateRequest(BaseModel):
    """更新竞品请求"""
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
