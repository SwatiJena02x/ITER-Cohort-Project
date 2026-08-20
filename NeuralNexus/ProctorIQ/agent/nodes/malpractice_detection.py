"""
agent/nodes/malpractice_detection.py
---------------------------------------
Fourth agent node: normalises raw object/face signals collected so far
into a single list of malpractice findings, and folds in identity-based
findings (e.g. impersonation) discovered by student_lookup.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from risk_scoring.rules import FACE_MATCH_DISTANCE_THRESHOLD

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    findings: list[dict] = list(state.get("detected_objects", []))

    face_count = state.get("face_count", 0)
    person_count = state.get("person_count", 0)

    if face_count > 1 or person_count > 1:
        if not any(f.get("malpractice_type") == "multiple_people" for f in findings):
            findings.append(
                {
                    "label": f"Multiple People ({max(face_count, person_count)} present)",
                    "malpractice_type": "multiple_people",
                    "confidence": 0.95,
                    "box": None,
                }
            )
            logger.info("[malpractice_detection] flagged multiple people (faces=%d, persons=%d)", face_count, person_count)

    distance = state.get("face_match_distance")
    if distance is not None and distance > FACE_MATCH_DISTANCE_THRESHOLD:
        findings.append(
            {
                "label": "identity_mismatch",
                "malpractice_type": "impersonation",
                "confidence": min(1.0, distance),  # larger distance -> more confident mismatch
                "box": None,
            }
        )
        logger.info("[malpractice_detection] flagged possible impersonation (distance=%.3f)", distance)

    if face_count == 0 and person_count == 0:
        findings.append(
            {
                "label": "no_face",
                "malpractice_type": "no_face_detected",
                "confidence": 1.0,
                "box": None,
            }
        )

    state["malpractice_findings"] = findings
    return state

