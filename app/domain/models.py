from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ServiceState(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MetricRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    timestamp: datetime
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    latency_ms: float = Field(ge=0)
    disk_usage: float = Field(ge=0, le=100)
    network_in_kbps: float = Field(ge=0)
    network_out_kbps: float = Field(ge=0)
    io_wait: float = Field(ge=0, le=100)
    thread_count: int = Field(ge=0)
    active_connections: int = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    uptime_seconds: int = Field(ge=0)
    temperature_celsius: float = Field(ge=0)
    power_consumption_watts: float = Field(ge=0)
    service_status: dict[str, ServiceState]


class Insights(BaseModel):
    average_latency_ms: float
    max_cpu_usage: float
    max_memory_usage: float
    error_rate: float
    uptime_seconds: int


class Anomaly(BaseModel):
    metric: str
    value: float
    threshold: float
    severity: Severity
    description: str


class AnalysisWindow(BaseModel):
    start: str | None = None
    end: str | None = None
    record_count: int = 0


class ForecastWindow(BaseModel):
    start: str | None = None
    end: str | None = None
    horizon_hours: int = 24


class DataQuality(BaseModel):
    status: str  
    limitations: list[str] = Field(default_factory=list)


class TrendEvidence(BaseModel):
    timestamp: str
    field: str
    value: float


class Trend(BaseModel):
    id: str
    metrics: list[str] = Field(default_factory=list)
    pattern: str  
    evidence: list[TrendEvidence] = Field(default_factory=list)
    interpretation: str
    confidence: str 
    confidence_reason: str


class Risk(BaseModel):
    id: str
    type: str  
    target: str
    assessment: str 
    severity: str 
    expected_window: str | None = None
    supporting_trend_ids: list[str] = Field(default_factory=list)
    reasoning: str
    confidence: str
    confidence_reason: str


class PreventiveAction(BaseModel):
    risk_ids: list[str] = Field(default_factory=list)
    priority: str  
    category: str  
    action: str
    expected_benefit: str
    additional_data_needed: list[str] = Field(default_factory=list)


class PredictiveAnalysis(BaseModel):
    analysis_window: AnalysisWindow
    forecast_window: ForecastWindow
    data_quality: DataQuality
    summary: str
    trends: list[Trend] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    preventive_actions: list[PreventiveAction] = Field(default_factory=list)


class Recommendation(BaseModel):
    id: str
    action: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    benefit_estimate: str


class ServiceStatusSummary(BaseModel):
    online: list[str] = Field(default_factory=list)
    degraded: list[str] = Field(default_factory=list)
    offline: list[str] = Field(default_factory=list)

class Report(BaseModel):
    timestamp: datetime
    insights: Insights
    anomalies: list[Anomaly] = Field(default_factory=list)
    predictive_analysis: PredictiveAnalysis | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    service_status_summary: ServiceStatusSummary
