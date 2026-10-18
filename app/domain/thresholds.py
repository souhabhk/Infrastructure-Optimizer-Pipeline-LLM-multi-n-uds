from dataclasses import dataclass

from app.domain.models import Severity


@dataclass(frozen=True)
class Threshold:
    medium: float
    high: float
    unit: str

    def classify(self, value: float) -> Severity | None:
        if value >= self.high:
            return Severity.HIGH
        if value >= self.medium:
            return Severity.MEDIUM
        return None


THRESHOLDS: dict[str, Threshold] = {  # seuils/ métrique
    "cpu_usage": Threshold(75, 85, "%"),
    "memory_usage": Threshold(75, 85, "%"),
    "latency_ms": Threshold(200, 300, "ms"),
    "disk_usage": Threshold(75, 85, "%"),
    "error_rate": Threshold(0.05, 0.10, ""),
    "temperature_celsius": Threshold(70, 80, "°C"),
    "io_wait": Threshold(8, 12, "%"),
}
