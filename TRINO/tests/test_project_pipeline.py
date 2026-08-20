from pathlib import Path

from utils.cache import LocalEvidenceCache
from utils.ingestion import build_metadata, load_image_evidence
from utils.process_monitor import detect_unauthorized_processes, detect_vm
from utils.schema import EvidenceRecord


def test_build_metadata_includes_required_fields():
    metadata = build_metadata(
        student_id="STU102",
        session_id="SESSION004",
        timestamp="2026-08-18T10:15:00Z",
        camera="webcam",
        category="incident",
        width=1920,
        height=1080,
        source_path="/tmp/sample.png",
    )

    assert metadata["student_id"] == "STU102"
    assert metadata["session_id"] == "SESSION004"
    assert metadata["camera"] == "webcam"
    assert metadata["resolution"] == "1920x1080"
    assert metadata["category"] == "incident"


def test_process_monitor_flags_unauthorized_apps():
    watchlist = ["zoom", "telegram", "teamviewer"]
    flags = detect_unauthorized_processes(["chrome", "telegram", "python"], watchlist)
    assert any(item["app_name"] == "telegram" for item in flags)


def test_vm_detection_returns_boolean():
    result = detect_vm()
    assert isinstance(result, bool)


def test_cache_store_and_queue_round_trip(tmp_path):
    cache = LocalEvidenceCache(db_path=str(tmp_path / "cache.db"), key="test-secret-key-123")
    record = EvidenceRecord(
        evidence_id="EV-1",
        student_id="STU102",
        session_id="SESSION004",
        timestamp="2026-08-18T10:15:00Z",
        camera="webcam",
        resolution="1920x1080",
        category="incident",
        source_path="/tmp/sample.png",
        ocr_text="phone visible",
        vision_description="A phone is on the desk.",
        metadata={"student_id": "STU102"},
    )

    assert cache.store_snapshot(record)
    assert cache.get_pending_queue() == []
    assert cache.get_latest_snapshot("STU102") is not None


def test_load_image_evidence_from_disk(tmp_path):
    image_path = tmp_path / "stu102_session004.png"
    image_path.write_bytes(b"fake")

    records = load_image_evidence(str(tmp_path), student_id="STU102", session_id="SESSION004")
    assert isinstance(records, list)


def test_root_entrypoints_delegate_to_real_project_modules():
    import api
    import streamlit_app

    assert callable(api.main)
    assert callable(streamlit_app.main)
