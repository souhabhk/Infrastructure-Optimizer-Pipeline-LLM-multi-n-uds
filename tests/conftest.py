import pytest

from app.domain.models import MetricRecord

_DEFAULTS = {
    "timestamp": "2023-10-01T12:00:00Z",
    "cpu_usage": 55,
    "memory_usage": 60,
    "latency_ms": 120,
    "disk_usage": 55,
    "network_in_kbps": 1000,
    "network_out_kbps": 1000,
    "io_wait": 3,
    "thread_count": 150,
    "active_connections": 50,
    "error_rate": 0.02,
    "uptime_seconds": 360000,
    "temperature_celsius": 60,
    "power_consumption_watts": 250,
    "service_status": {
        "database": "online",
        "api_gateway": "online",
        "cache": "online",
    },
}


@pytest.fixture
def raw_record():
    def _make(**overrides) -> dict:
        return {**_DEFAULTS, **overrides}

    return _make


@pytest.fixture
def make_record(raw_record):
    def _make(**overrides) -> MetricRecord:
        return MetricRecord.model_validate(raw_record(**overrides))

    return _make
