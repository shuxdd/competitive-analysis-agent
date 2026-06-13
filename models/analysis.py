"""
分析任务数据模型
================

定义分析请求、分析结果、报告等数据结构。
"""

from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ReportType(str, Enum):
    """报告类型"""
    STANDARD = "standard"  # 标准分析


class AnalysisDimension(str, Enum):
    """分析维度"""
    FEATURES = "features"    # 功能对比
    PRICING = "pricing"      # 价格对比
    SWOT = "swot"           # SWOT分析
    REVIEWS = "reviews"      # 用户评价
    MARKET = "market"        # 市场分析
    TRENDS = "trends"        # 趋势分析


class AnalysisStatus(str, Enum):
    """分析任务状态"""
    PENDING = "pending"
    PLANNING = "planning"
    COLLECTING = "collecting"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """分析请求"""
    competitors: List[str]
    analysis_type: ReportType = ReportType.STANDARD
    dimensions: List[AnalysisDimension] = [
        AnalysisDimension.FEATURES,
        AnalysisDimension.PRICING,
        AnalysisDimension.SWOT
    ]
    my_product: Optional[str] = None  # 用于对比
    include_reviews: bool = True
    max_sources_per_competitor: int = 5


class FeatureMatrix(BaseModel):
    """功能矩阵对比"""
    features: List[str]
    competitors: Dict[str, Dict[str, bool]]  # competitor -> feature -> supported


class PricingComparison(BaseModel):
    """价格对比"""
    competitors: Dict[str, Dict[str, Any]]  # competitor -> pricing info
    analysis: Optional[str] = None


class SwotAnalysis(BaseModel):
    """SWOT分析"""
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []


class ReviewAnalysis(BaseModel):
    """用户评价分析"""
    total_reviews: int = 0
    average_rating: float = 0.0
    positive_keywords: List[str] = []
    negative_keywords: List[str] = []
    sentiment_score: float = 0.0  # -1 to 1
    summary: str = ""


class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: AnalysisRequest
    competitors_data: Dict[str, Any] = {}
    feature_matrix: Optional[FeatureMatrix] = None
    pricing_comparison: Optional[PricingComparison] = None
    swot_analysis: Optional[Dict[str, SwotAnalysis]] = None
    review_analysis: Optional[Dict[str, ReviewAnalysis]] = None
    market_analysis: Optional[str] = None
    trends_analysis: Optional[str] = None
    recommendations: List[str] = []
    status: AnalysisStatus = AnalysisStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None  # seconds

    @field_serializer('created_at', 'completed_at')
    def serialize_datetime(self, dt: datetime) -> str:
        if dt is None:
            return None
        return dt.isoformat()


class AnalysisTaskResponse(BaseModel):
    """分析任务响应"""
    analysis_id: str
    status: AnalysisStatus
    message: str
    estimated_time: Optional[int] = None  # seconds
    created_at: datetime


class AnalysisResultResponse(BaseModel):
    """分析结果响应"""
    analysis_id: str
    status: AnalysisStatus
    competitors: List[str]
    analysis_type: ReportType
    results: Optional[Dict[str, Any]] = None
    report_summary: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
