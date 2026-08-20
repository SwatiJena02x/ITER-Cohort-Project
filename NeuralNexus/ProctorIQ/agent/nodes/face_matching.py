"""
agent/nodes/face_matching.py
-------------------------------
Second agent node: detects faces in the uploaded image and extracts an
embedding for the primary (largest) face, to be matched against registered
student profiles in the next node.
"""
from __future__ import annotations

import logging

from agent.state import RiskScoringState
from detection.face_detection import detect_faces

logger = logging.getLogger(__name__)


def run(state: RiskScoringState) -> RiskScoringState:
    image_path = state["image_path"]
    logger.info("[face_matching] detecting faces in %s", image_path)

    faces = detect_faces(image_path)

    state["faces_found"] = [{"box": f.box, "embedding": f.embedding} for f in faces]
    state["face_count"] = len(faces)

    if not faces:
        state["primary_embedding"] = None
        return state

    def area(f) -> int:
        top, right, bottom, left = f.box
        return (bottom - top) * (right - left)

    primary = max(faces, key=area)
    state["primary_embedding"] = primary.embedding
    return state
