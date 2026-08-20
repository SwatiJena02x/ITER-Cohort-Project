"""
agent/nodes/talking_detection_node.py
----------------------------------------
Agent node: detects whether the student is talking during examination
using Mouth Aspect Ratio analysis.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from detection.talking_detection import detect_talking

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    image_path = state["image_path"]
    logger.info("[talking_detection] analysing talking in %s", image_path)

    result = detect_talking(image_path)

    state["talking_detected"]    = result["talking"]
    state["talking_confidence"]  = result["confidence"]

    if result["talking"] and result["confidence"] > 0.35:
        detected = list(state.get("detected_objects", []))
        detected.append({
            "label": "talking",
            "malpractice_type": "talking_detected",
            "confidence": result["confidence"],
            "box": None,
        })
        state["detected_objects"] = detected
        logger.info("[talking_detection] flagged talking (conf=%.2f)", result["confidence"])

    return state
