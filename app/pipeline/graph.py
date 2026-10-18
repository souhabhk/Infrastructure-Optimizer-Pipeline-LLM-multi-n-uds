from datetime import datetime, timezone
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.domain.models import Report
from app.pipeline.nodes.analysis import analysis_node
from app.pipeline.nodes.ingestion import ingestion_node
from app.pipeline.nodes.recommendation import recommendation_node
from app.pipeline.nodes.predictive_analysis import predictive_analysis_node
from app.pipeline.state import PipelineState


def build_graph():
    g = StateGraph(PipelineState)
    g.add_node("ingestion", ingestion_node)
    g.add_node("analysis", analysis_node)
    g.add_node("prediction", predictive_analysis_node)
    g.add_node("recommendation", recommendation_node)
    g.add_edge(START, "ingestion")
    g.add_edge("ingestion", "analysis")
    g.add_edge("analysis", "prediction")
    g.add_edge("prediction", "recommendation")
    g.add_edge("recommendation", END)
    return g.compile()


def _build_report(state: PipelineState) -> Report:
    return Report(
        timestamp=datetime.now(timezone.utc),
        insights=state["insights"],
        anomalies=state["anomalies"],
        predictive_analysis=state.get("predictive_analysis"),
        recommendations=state["recommendations"],
        service_status_summary=state["service_status_summary"],
    )


_PIPELINE = build_graph()


def run_pipeline(raw_records: list[dict[str, Any]]) -> Report:
    return _build_report(_PIPELINE.invoke({"raw_records": raw_records}))
