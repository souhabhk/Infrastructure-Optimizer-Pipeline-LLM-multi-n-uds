from typing import Any, TypedDict

from app.domain.models import (
    Anomaly,
    Insights,
    MetricRecord,
    PredictiveAnalysis,
    Recommendation,
    ServiceStatusSummary,
)


class PipelineState(TypedDict, total=False):
    raw_records: list[dict[str, Any]]
    records: list[MetricRecord]
    invalid_count: int
    insights: Insights
    anomalies: list[Anomaly]
    service_status_summary: ServiceStatusSummary
    recommendations: list[Recommendation]
    predictive_analysis: PredictiveAnalysis
