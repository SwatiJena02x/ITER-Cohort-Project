"""
agent/risk_scoring_agent.py
------------------------------
Main Risk Scoring Agent. Wires together every node into a single ordered
workflow using LangGraph, and exposes `run_risk_scoring_workflow()` as the
one function the FastAPI backend needs to call.

Workflow:
  image_analysis → eye_movement → talking_detection → face_matching
    → student_lookup → malpractice_detection → evidence_collector
    → risk_calculator → report_generator
"""
from __future__ import annotations

import logging

from agent.nodes import (
    evidence_collector,
    eye_movement,
    face_matching,
    image_analysis,
    malpractice_detection,
    report_generator,
    risk_calculator,
    student_lookup,
    talking_detection_node,
)
from agent.state import RiskScoringState

logger = logging.getLogger(__name__)


def _build_graph():
    """
    Builds the LangGraph StateGraph. Kept inside a function (rather than at
    import time) so the module still imports cleanly even if `langgraph`
    isn't installed - `run_risk_scoring_workflow` falls back to running the
    nodes as a plain sequential pipeline in that case.
    """
    from langgraph.graph import END, StateGraph

    graph = StateGraph(RiskScoringState)

    graph.add_node("image_analysis",       image_analysis.run)
    graph.add_node("eye_movement",         eye_movement.run)
    graph.add_node("talking_detection",    talking_detection_node.run)
    graph.add_node("face_matching",        face_matching.run)
    graph.add_node("student_lookup",       student_lookup.run)
    graph.add_node("malpractice_detection",malpractice_detection.run)
    graph.add_node("evidence_collector",   evidence_collector.run)
    graph.add_node("risk_calculator",      risk_calculator.run)
    graph.add_node("report_generator",     report_generator.run)

    graph.set_entry_point("image_analysis")
    graph.add_edge("image_analysis",        "eye_movement")
    graph.add_edge("eye_movement",          "talking_detection")
    graph.add_edge("talking_detection",     "face_matching")
    graph.add_edge("face_matching",         "student_lookup")
    graph.add_edge("student_lookup",        "malpractice_detection")
    graph.add_edge("malpractice_detection", "evidence_collector")
    graph.add_edge("evidence_collector",    "risk_calculator")
    graph.add_edge("risk_calculator",       "report_generator")
    graph.add_edge("report_generator",      END)

    return graph.compile()


_NODE_SEQUENCE = [
    image_analysis,
    eye_movement,
    talking_detection_node,
    face_matching,
    student_lookup,
    malpractice_detection,
    evidence_collector,
    risk_calculator,
    report_generator,
]


def _run_sequential(state: RiskScoringState) -> RiskScoringState:
    """Fallback runner: executes nodes in order without LangGraph."""
    for node in _NODE_SEQUENCE:
        state = node.run(state)
    return state


def run_risk_scoring_workflow(
    image_path: str, claimed_student_code: str | None = None
) -> RiskScoringState:
    """
    Entry point used by backend/api/reports.py. Runs the full agent
    workflow end-to-end for a single uploaded malpractice image and
    returns the final state (score, level, summary, report path, etc.).
    """
    initial_state: RiskScoringState = {
        "image_path": image_path,
        "claimed_student_code": claimed_student_code,
        "errors": [],
    }

    try:
        app = _build_graph()
        logger.info("[risk_scoring_agent] running via LangGraph")
        final_state = app.invoke(initial_state)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[risk_scoring_agent] LangGraph unavailable/failed (%s); running sequentially.", exc
        )
        final_state = _run_sequential(initial_state)

    return final_state
