"""
agent/nodes/risk_calculator.py
---------------------------------
Sixth agent node: calls the deterministic rule-based scorer (risk_scoring/)
to turn collected evidence into a 0-100 risk score and category.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from risk_scoring.rules import FACE_MATCH_DISTANCE_THRESHOLD
from risk_scoring.scorer import score_event

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    breakdown = score_event(
        malpractice_detections=state.get("malpractice_findings", []),
        face_count=state.get("face_count", 0),
        face_match_distance=state.get("face_match_distance"),
        face_match_threshold=FACE_MATCH_DISTANCE_THRESHOLD,
    )

    state["risk_score"] = breakdown.total_score
    state["risk_level"] = breakdown.risk_level
    state["score_contributions"] = breakdown.contributions

    if "evidence" in state and isinstance(state["evidence"], dict):
        state["evidence"]["score_contributions"] = breakdown.contributions

    logger.info("[risk_calculator] score=%.2f level=%s", breakdown.total_score, breakdown.risk_level)
    return state

