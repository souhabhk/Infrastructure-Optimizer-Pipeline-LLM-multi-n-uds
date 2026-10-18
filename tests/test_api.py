from datetime import datetime, timezone

from fastapi.testclient import TestClient

import app.api.routes as routes
from app.domain.models import Insights, Report, ServiceStatusSummary
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_analyze_returns_a_report(monkeypatch):
    report = Report(
        timestamp=datetime.now(timezone.utc),
        insights=Insights(
            average_latency_ms=150,
            max_cpu_usage=99,
            max_memory_usage=90,
            error_rate=0.03,
            uptime_seconds=1000,
        ),
        service_status_summary=ServiceStatusSummary(online=["database"]),
    )
    monkeypatch.setattr(routes, "run_pipeline", lambda records: report)
    resp = client.post("/analyze", json=[{"cpu_usage": 99}])
    assert resp.status_code == 200
    assert "recommendations" in resp.json()
