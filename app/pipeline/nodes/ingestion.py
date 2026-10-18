import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.domain.models import MetricRecord
from app.pipeline.state import PipelineState

logger = logging.getLogger(__name__)


def load_raw_records(path: str | Path) -> list[dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError(f"Expected a JSON array or object, got {type(raw).__name__}.")


def ingestion_node(state: PipelineState) -> PipelineState:
    records: list[MetricRecord] = []
    invalid = 0
    for i, item in enumerate(state.get("raw_records", [])):
        try:
            records.append(MetricRecord.model_validate(item))
        except ValidationError as exc:
            invalid += 1
            logger.warning("skipping bad record #%d: %s", i, exc.errors())
    logger.info("ingested %d records, skipped %d", len(records), invalid)
    return {"records": records, "invalid_count": invalid}
