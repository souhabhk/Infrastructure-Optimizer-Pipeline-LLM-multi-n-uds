from app.domain.models import (
    Anomaly,
    Insights,
    Recommendation,
    ServiceStatusSummary,
    Severity,
)
from app.pipeline.nodes import recommendation as rec_mod
from app.pipeline.nodes.recommendation import (
    RecommendationBundle,
    build_rule_drafts,
    recommendation_node,
)


def make_state(anomalies, summary):
    insights = Insights(
        average_latency_ms=150,
        max_cpu_usage=99,
        max_memory_usage=90,
        error_rate=0.03,
        uptime_seconds=1000,
    )
    return {
        "insights": insights,
        "anomalies": anomalies,
        "service_status_summary": summary,
    }


def cpu_anomaly():
    return Anomaly(
        metric="cpu_usage",
        value=99,
        threshold=85,
        severity=Severity.HIGH,
        description="",
    )


def test_build_rule_drafts():
    drafts = build_rule_drafts(
        [cpu_anomaly()], ServiceStatusSummary(offline=["database"])
    )
    assert len(drafts) == 2  # un cpu un service


def test_healthy_input_returns_nothing():
    out = recommendation_node(make_state([], ServiceStatusSummary(online=["database"])))
    assert out["recommendations"] == []


def test_llm_result_is_used(monkeypatch):
    fake = RecommendationBundle(
        recommendations=[
            Recommendation(
                id="rec-001",
                action="scale up",
                target="cluster",
                parameters={},
                benefit_estimate="less load",
            ),
        ]
    )
    monkeypatch.setattr(rec_mod.llm, "generate_structured", lambda *a, **k: fake)
    out = recommendation_node(
        make_state([cpu_anomaly()], ServiceStatusSummary(offline=["database"]))
    )
    assert out["recommendations"][0].action == "scale up"


def test_falls_back_to_rules_if_llm_fails(monkeypatch):
    def fail(*a, **k):
        raise RuntimeError("api down")

    monkeypatch.setattr(rec_mod.llm, "generate_structured", fail)
    out = recommendation_node(
        make_state([cpu_anomaly()], ServiceStatusSummary(offline=["database"]))
    )
    assert len(out["recommendations"]) == 2
