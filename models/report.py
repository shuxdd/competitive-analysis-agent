"""
报告数据模型
============

定义报告生成、导出等数据结构。
"""

from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ReportFormat(str, Enum):
    """报告格式"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class ReportSection(BaseModel):
    """报告章节"""
    title: str
    content: str
    order: int
    subsections: List['ReportSection'] = []


class Report(BaseModel):
    """报告"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    title: str
    report_type: str  # quick, standard, deep
    format: ReportFormat = ReportFormat.MARKDOWN
    content: str
    sections: List[ReportSection] = []
    metadata: Dict[str, Any] = {}
    file_path: Optional[str] = None
    file_size: Optional[int] = None  # bytes
    created_at: datetime = Field(default_factory=datetime.now)

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class ReportTemplate(BaseModel):
    """报告模板"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    report_type: str
    sections: List[Dict[str, Any]] = []
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class ReportExportRequest(BaseModel):
    """报告导出请求"""
    report_id: str
    format: ReportFormat = ReportFormat.MARKDOWN
    include_charts: bool = True
    include_raw_data: bool = False


class ReportListResponse(BaseModel):
    """报告列表响应"""
    reports: List[Report]
    total: int
    page: int
    page_size: int


class QuickReport(BaseModel):
    """快速报告"""
    competitor_name: str
    company_overview: str
    key_products: List[Dict[str, Any]]
    main_differentiators: List[str]
    pricing_summary: str
    recent_updates: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.now)


class StandardReport(BaseModel):
    """标准报告"""
    executive_summary: str
    competitor_overview: List[Dict[str, Any]]
    feature_comparison: Dict[str, Any]
    pricing_analysis: Dict[str, Any]
    swot_analysis: Dict[str, Any]
    user_reviews: Optional[Dict[str, Any]] = None
    recommendations: List[str]
    data_sources: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)


class DeepReport(BaseModel):
    """深度报告"""
    executive_summary: str
    market_analysis: str
    competitor_profiles: List[Dict[str, Any]]
    detailed_comparison: Dict[str, Any]
    swot_analysis: Dict[str, Any]
    trend_analysis: str
    competitive_landscape: str
    strategic_recommendations: List[str]
    risk_assessment: List[str]
    appendices: List[Dict[str, Any]]
    data_sources: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)
