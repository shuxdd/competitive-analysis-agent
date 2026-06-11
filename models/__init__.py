"""
数据模型
========

导出所有数据模型。
"""

from .competitor import (
    ProductTier,
    PricingModel,
    Product,
    CompanyInfo,
    CompetitorInfo,
    CompetitorUpdate,
    CompetitorCreate,
    CompetitorUpdateRequest,
)

from .analysis import (
    ReportType,
    AnalysisDimension,
    AnalysisStatus,
    AnalysisRequest,
    FeatureMatrix,
    PricingComparison,
    SwotAnalysis,
    ReviewAnalysis,
    AnalysisResult,
    AnalysisTaskResponse,
    AnalysisResultResponse,
)

from .report import (
    ReportFormat,
    ReportSection,
    Report,
    ReportTemplate,
    ReportExportRequest,
    ReportListResponse,
    QuickReport,
    StandardReport,
    DeepReport,
)

__all__ = [
    # 竞品相关
    "ProductTier",
    "PricingModel",
    "Product",
    "CompanyInfo",
    "CompetitorInfo",
    "CompetitorUpdate",
    "CompetitorCreate",
    "CompetitorUpdateRequest",

    # 分析相关
    "ReportType",
    "AnalysisDimension",
    "AnalysisStatus",
    "AnalysisRequest",
    "FeatureMatrix",
    "PricingComparison",
    "SwotAnalysis",
    "ReviewAnalysis",
    "AnalysisResult",
    "AnalysisTaskResponse",
    "AnalysisResultResponse",

    # 报告相关
    "ReportFormat",
    "ReportSection",
    "Report",
    "ReportTemplate",
    "ReportExportRequest",
    "ReportListResponse",
    "QuickReport",
    "StandardReport",
    "DeepReport",
]
