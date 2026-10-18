from app.domain.models import Severity
from app.pipeline.nodes.analysis import (
    compute_insights,
    detect_anomalies,
    summarize_service_status,
)


def test_insights_aggregation(make_record):
    records = [
        make_record(latency_ms=100, cpu_usage=50, error_rate=0.01, uptime_seconds=100),
        make_record(latency_ms=300, cpu_usage=99, error_rate=0.03, uptime_seconds=200),
    ]
    insights = compute_insights(records)
    assert insights.average_latency_ms == 200
    assert insights.max_cpu_usage == 99
    assert insights.error_rate == 0.02
    assert insights.uptime_seconds == 200


def test_detect_anomalies_flags_the_peak(make_record):
    records = [
        make_record(cpu_usage=50),
        make_record(cpu_usage=80),
        make_record(cpu_usage=99),
    ]
    anomalies = detect_anomalies(records)
    cpu = [a for a in anomalies if a.metric == "cpu_usage"][0]
    assert cpu.severity is Severity.HIGH
    assert cpu.value == 99
    assert cpu.threshold == 85


def test_no_anomalies_when_healthy(make_record):
    assert detect_anomalies([make_record(), make_record()]) == []


def test_service_status_takes_worst_state(make_record):
    records = [
        make_record(service_status={"database": "online", "cache": "online"}),
        make_record(service_status={"database": "offline", "cache": "online"}),
    ]
    summary = summarize_service_status(records)
    assert summary.offline == ["database"]
    assert summary.online == ["cache"]
