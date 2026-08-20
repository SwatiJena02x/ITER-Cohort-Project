"""
tests/test_agent.py
-----------------------
Tests for the individual agent nodes and the overall sequential fallback
pipeline. Heavy dependencies (DB, detectors, LLM) are mocked so the tests
verify orchestration logic rather than model accuracy.
"""
from unittest.mock import MagicMock, patch

from agent import risk_scoring_agent
from agent.nodes import malpractice_detection, risk_calculator
from agent.state import RiskScoringState


def test_malpractice_detection_flags_impersonation_above_threshold():
    state: RiskScoringState = {
        "detected_objects": [],
        "face_match_distance": 0.9,  # above FACE_MATCH_DISTANCE_THRESHOLD (0.55)
        "face_count": 1,
    }
    result = malpractice_detection.run(state)
    types = [f["malpractice_type"] for f in result["malpractice_findings"]]
    assert "impersonation" in types


def test_malpractice_detection_no_flag_below_threshold():
    state: RiskScoringState = {
        "detected_objects": [],
        "face_match_distance": 0.1,
        "face_count": 1,
    }
    result = malpractice_detection.run(state)
    types = [f["malpractice_type"] for f in result["malpractice_findings"]]
    assert "impersonation" not in types


def test_malpractice_detection_flags_no_face():
    state: RiskScoringState = {"detected_objects": [], "face_match_distance": None, "face_count": 0}
    result = malpractice_detection.run(state)
    types = [f["malpractice_type"] for f in result["malpractice_findings"]]
    assert "no_face_detected" in types


def test_risk_calculator_populates_score_and_level():
    state: RiskScoringState = {
        "malpractice_findings": [{"malpractice_type": "phone_usage", "confidence": 1.0}],
        "face_count": 1,
        "face_match_distance": 0.1,
    }
    result = risk_calculator.run(state)
    assert result["risk_score"] == 40.0
    assert result["risk_level"] == "MEDIUM"
    assert result["score_contributions"]["phone_usage"] == 40.0


def test_sequential_pipeline_runs_all_nodes_and_produces_report(tmp_path):
    """
    Runs the fallback sequential pipeline (no LangGraph, no real DB/models)
    end-to-end, with every node's heavy dependency mocked, to verify state
    flows correctly from node to node.
    """
    fake_image_path = str(tmp_path / "frame.jpg")
    open(fake_image_path, "wb").close()

    with (
        patch("agent.nodes.image_analysis.detect_objects") as mock_detect_objects,
        patch("agent.nodes.face_matching.detect_faces") as mock_detect_faces,
        patch("agent.nodes.student_lookup.session_scope") as mock_session_scope,
        patch("agent.nodes.report_generator.get_llm", return_value=None),
    ):
        mock_detect_objects.return_value = MagicMock(detections=[], person_count=1)
        mock_detect_faces.return_value = []  # no face found -> triggers no_face_detected

        mock_db = MagicMock()
        mock_session_scope.return_value.__enter__.return_value = mock_db
        with patch("agent.nodes.student_lookup.find_closest_student_by_embedding", return_value=[]):
            with patch("agent.nodes.student_lookup.get_student_by_code", return_value=None):
                final_state = risk_scoring_agent._run_sequential(
                    {"image_path": fake_image_path, "claimed_student_code": None, "errors": []}
                )

    assert final_state["face_count"] == 0
    assert final_state["risk_score"] > 0  # no_face_detected penalty applied
    assert "report_summary" in final_state
    assert final_state["report_path"] is not None
