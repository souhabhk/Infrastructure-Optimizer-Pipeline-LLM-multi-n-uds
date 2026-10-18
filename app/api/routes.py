from typing import Any

from fastapi import APIRouter, Body, HTTPException

from app.domain.models import Report
from app.pipeline.graph import run_pipeline

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=Report)
def analyze(records: list[dict[str, Any]] = Body(...)) -> Report:  # invalides ignorées
    if not records:
        raise HTTPException(400, "Provide a non-empty array of records.")
    try:
        return run_pipeline(records)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
