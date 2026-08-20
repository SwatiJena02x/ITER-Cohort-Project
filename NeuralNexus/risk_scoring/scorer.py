"""
risk_scoring/scorer.py
------------------------
Deterministic (non-LLM) calculation of a 0-100 risk score from collected
evidence. This is intentionally rule-based (not the LLM) so scores are
reproducible, auditable, and can't be talked into being different by
prompt-level phrasing - the LLM's job (see llm/) is only to *explain* the
score in plain language, not decide it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from risk_scoring.rules import (
    FACE_MATCH_PENALTY,
    MALPRACTICE_BASE_WEIGHTS,
    MAX_SCORE,
    MIN_SCORE,
    MULTIPLE_FACES_PENALTY,
    NO_FACE_PENALTY,
    classify_risk_level,
)


@dataclass
class ScoreBreakdown:
    total_score: float
    risk_level: str
    contributions: dict[str, float] = field(default_factory=dict)


def score_event(
    *,
    malpractice_detections: list[dict],  # [{"malpractice_type": str, "confidence": float}, ...]
    face_count: int,
    face_match_distance: float | None,  # None if no registered profile to compare against
    face_match_threshold: float = 0.55,
) -> ScoreBreakdown:
    """
    Combine object-detection evidence + face evidence into a single
    deterministic risk score with a transparent per-factor breakdown.
    """
    contributions: dict[str, float] = {}

    # --- Object/behaviour-based malpractice signals ---
    for det in malpractice_detections:
        mtype = det["malpractice_type"]
        confidence = det.get("confidence", 1.0)
        weight = MALPRACTICE_BASE_WEIGHTS.get(mtype, 15.0)
        points = weight * confidence
        contributions[mtype] = contributions.get(mtype, 0.0) + points

    # --- Face / identity signals ---
    if face_count == 0:
        contributions["no_face_detected"] = contributions.get("no_face_detected", 0.0) + NO_FACE_PENALTY
    elif face_count > 1:
        contributions["multiple_faces"] = contributions.get("multiple_faces", 0.0) + MULTIPLE_FACES_PENALTY

    if face_match_distance is not None and face_match_distance > face_match_threshold:
        contributions["identity_mismatch"] = contributions.get("identity_mismatch", 0.0) + FACE_MATCH_PENALTY

    total = sum(contributions.values())
    total = max(MIN_SCORE, min(MAX_SCORE, total))

    return ScoreBreakdown(
        total_score=round(total, 2),
        risk_level=classify_risk_level(total),
        contributions={k: round(v, 2) for k, v in contributions.items()},
    )
