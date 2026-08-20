"""
tests/test_risk_scoring.py
------------------------------
Unit tests for the deterministic rule-based risk scorer.
These require no database or model weights.
"""
from risk_scoring.rules import classify_risk_level
from risk_scoring.scorer import score_event


def test_no_findings_gives_zero_score():
    result = score_event(
        malpractice_detections=[],
        face_count=1,
        face_match_distance=0.1,
    )
    assert result.total_score == 0.0
    assert result.risk_level == "LOW"


def test_phone_usage_increases_score():
    result = score_event(
        malpractice_detections=[{"malpractice_type": "phone_usage", "confidence": 1.0}],
        face_count=1,
        face_match_distance=0.1,
    )
    assert result.total_score == 40.0
    assert result.contributions["phone_usage"] == 40.0


def test_no_face_detected_adds_penalty():
    result = score_event(
        malpractice_detections=[],
        face_count=0,
        face_match_distance=None,
    )
    assert result.total_score == 20.0
    assert "no_face_detected" in result.contributions


def test_multiple_faces_adds_penalty():
    result = score_event(
        malpractice_detections=[],
        face_count=2,
        face_match_distance=None,
    )
    assert result.contributions["multiple_faces"] == 25.0


def test_identity_mismatch_adds_penalty_above_threshold():
    result = score_event(
        malpractice_detections=[],
        face_count=1,
        face_match_distance=0.9,
        face_match_threshold=0.55,
    )
    assert "identity_mismatch" in result.contributions


def test_identity_match_below_threshold_adds_no_penalty():
    result = score_event(
        malpractice_detections=[],
        face_count=1,
        face_match_distance=0.2,
        face_match_threshold=0.55,
    )
    assert "identity_mismatch" not in result.contributions


def test_score_is_clamped_to_100():
    detections = [
        {"malpractice_type": "phone_usage", "confidence": 1.0},
        {"malpractice_type": "unauthorized_material", "confidence": 1.0},
        {"malpractice_type": "unauthorized_device", "confidence": 1.0},
        {"malpractice_type": "multiple_people", "confidence": 1.0},
        {"malpractice_type": "impersonation", "confidence": 1.0},
    ]
    result = score_event(malpractice_detections=detections, face_count=2, face_match_distance=0.9)
    assert result.total_score <= 100.0


def test_classify_risk_level_boundaries():
    assert classify_risk_level(0) == "LOW"
    assert classify_risk_level(34.9) == "LOW"
    assert classify_risk_level(35) == "MEDIUM"
    assert classify_risk_level(64.9) == "MEDIUM"
    assert classify_risk_level(65) == "HIGH"
    assert classify_risk_level(85) == "CRITICAL"
    assert classify_risk_level(100) == "CRITICAL"
