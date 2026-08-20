"""
agent/nodes/image_analysis.py
--------------------------------
First agent node: runs YOLO object detection on the uploaded malpractice
image and records any suspicious objects (phone, book, extra person, etc.).
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from detection.bluetooth_detection import detect_bluetooth_and_earbuds
from detection.object_detection import detect_objects

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    image_path = state["image_path"]
    logger.info("[image_analysis] analysing %s", image_path)

    result = detect_objects(image_path)

    detected_list = [
        {
            "label": d.label,
            "malpractice_type": d.malpractice_type,
            "confidence": d.confidence,
            "box": d.box,
        }
        for d in result.detections
    ]

    # Collect object boxes to check overlap with ear regions
    object_boxes = [d.box for d in result.detections]
    bt_detections = detect_bluetooth_and_earbuds(image_path, detected_boxes=object_boxes)

    for bd in bt_detections:
        detected_list.append(
            {
                "label": bd.label,
                "malpractice_type": bd.malpractice_type,
                "confidence": bd.confidence,
                "box": bd.box,
            }
        )

    state["detected_objects"] = detected_list
    state["person_count"] = result.person_count
    return state
