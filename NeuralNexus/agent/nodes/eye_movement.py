"""
agent/nodes/eye_movement.py
------------------------------
Agent node: detects eye/gaze direction and flags if student is looking
away from the exam screen.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from detection.eye_movement import detect_gaze

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    image_path = state["image_path"]
    logger.info("[eye_movement] analysing gaze in %s", image_path)

    result = detect_gaze(image_path)

    state["eye_looking_away"]       = result["looking_away"]
    state["eye_direction"]          = result["direction"]
    state["eye_gaze_confidence"]    = result["confidence"]

    if result["looking_away"] and result["confidence"] > 0.4:
        # Append to detected objects so the scorer picks it up
        detected = list(state.get("detected_objects", []))
        detected.append({
            "label": "looking_away",
            "malpractice_type": "eye_movement_away",
            "confidence": result["confidence"],
            "box": None,
        })
        state["detected_objects"] = detected
        logger.info("[eye_movement] flagged looking_away (direction=%s, conf=%.2f)",
                    result["direction"], result["confidence"])

    return state
