"""
agent/state.py
-----------------
Shared state object passed between every node in the risk-scoring agent's
graph (LangGraph-style). Each node reads what it needs and writes its
results back into the same state object.
"""
from __future__ import annotations

from typing import Any, TypedDict


class RiskScoringState(TypedDict, total=False):
    # --- Input ---
    image_path: str
    claimed_student_code: str | None  # optional hint from the frontend

    # --- image_analysis node ---
    detected_objects: list[dict]       # [{"label", "malpractice_type", "confidence", "box"}, ...]
    person_count: int

    # --- face_matching node ---
    faces_found: list[dict]            # [{"box": (...), "embedding": [...]}, ...]
    face_count: int
    primary_embedding: list[float] | None

    # --- student_lookup node ---
    matched_student_id: int | None
    matched_student_name: str | None
    matched_student_code: str | None
    face_match_distance: float | None

    # --- malpractice_detection node ---
    malpractice_findings: list[dict]   # normalized list ready for scoring

    # --- evidence_collector node ---
    evidence: dict[str, Any]           # full structured evidence bundle (stored as JSON)

    # --- risk_calculator node ---
    risk_score: float
    risk_level: str
    score_contributions: dict[str, float]

    # --- report_generator node ---
    report_summary: str
    report_path: str | None

    # --- eye_movement node ---
    eye_looking_away: bool
    eye_direction: str            # "left" | "right" | "up" | "center" | "unknown"
    eye_gaze_confidence: float

    # --- talking_detection node ---
    talking_detected: bool
    talking_confidence: float

    # --- report_generator: PDF path ---
    pdf_path: str | None

    # --- bookkeeping ---
    malpractice_event_id: int | None
    errors: list[str]
