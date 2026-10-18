from app.domain.models import (
    Anomaly,
    Insights,
    MetricRecord,
    ServiceState,
    ServiceStatusSummary,
    Severity,
)
from app.domain.thresholds import THRESHOLDS
from app.pipeline.state import PipelineState

_STATE_RANK = {
    ServiceState.ONLINE: 0,
    ServiceState.DEGRADED: 1,
    ServiceState.OFFLINE: 2,
}
_SEVERITY_RANK = {Severity.HIGH: 0, Severity.MEDIUM: 1, Severity.LOW: 2}


def compute_insights(records: list[MetricRecord]) -> Insights:
    n = len(records)  # moyennes maxima dernier
    return Insights(
        average_latency_ms=round(sum(r.latency_ms for r in records) / n, 2),
        max_cpu_usage=max(r.cpu_usage for r in records),
        max_memory_usage=max(r.memory_usage for r in records),
        error_rate=round(sum(r.error_rate for r in records) / n, 4),
        uptime_seconds=max(r.uptime_seconds for r in records),
    )


def _iso(record: MetricRecord) -> str:
    return record.timestamp.isoformat().replace("+00:00", "Z")


def detect_anomalies(records: list[MetricRecord]) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    for metric, t in THRESHOLDS.items():
        breaches = [
            (getattr(r, metric), r) for r in records if t.classify(getattr(r, metric))
        ]
        if not breaches:
            continue
        peak, record = max(
            breaches, key=lambda pair: pair[0]
        )  # 1 anomalie par métrique
        severity = t.classify(peak)
        anomalies.append(
            Anomaly(
                metric=metric,
                value=peak,
                threshold=t.high if severity is Severity.HIGH else t.medium,
                severity=severity,
                description=(
                    f"{metric} over threshold in {len(breaches)} of {len(records)} samples; "
                    f"peak {peak:g}{t.unit} at {_iso(record)}."
                ),
            )
        )
    anomalies.sort(key=lambda a: (_SEVERITY_RANK[a.severity], a.metric))
    return anomalies


def summarize_service_status(records: list[MetricRecord]) -> ServiceStatusSummary:
    worst: dict[str, ServiceState] = {}  # pire état observé
    for r in records:
        for svc, state in r.service_status.items():
            if svc not in worst or _STATE_RANK[state] > _STATE_RANK[worst[svc]]:
                worst[svc] = state

    summary = ServiceStatusSummary()
    for svc, state in worst.items():
        getattr(summary, state.value).append(svc)
    for bucket in (summary.online, summary.degraded, summary.offline):
        bucket.sort()
    return summary


def analysis_node(state: PipelineState) -> PipelineState:
    records = state["records"]
    if not records:
        raise ValueError("no valid records to analyse")
    return {
        "insights": compute_insights(records),
        "anomalies": detect_anomalies(records),
        "service_status_summary": summarize_service_status(records),
    }
