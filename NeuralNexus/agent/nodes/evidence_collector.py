"""
agent/nodes/evidence_collector.py
------------------------------------
Fifth agent node: bundles everything gathered so far (detections, face
info, identity match) into one structured evidence dict, which gets stored
as JSON on the MalpracticeEvent row and handed to the LLM for explanation.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    evidence = {
        "image_path": state.get("image_path"),
        "detected_objects": state.get("detected_objects", []),
        "person_count": state.get("person_count", 0),
        "face_count": state.get("face_count", 0),
        "matched_student_id": state.get("matched_student_id"),
        "matched_student_code": state.get("matched_student_code"),
        "face_match_distance": state.get("face_match_distance"),
        "malpractice_findings": state.get("malpractice_findings", []),
    }
    state["evidence"] = evidence
    logger.info("[evidence_collector] evidence bundle ready (%d findings)",
                len(evidence["malpractice_findings"]))
    return state
