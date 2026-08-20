from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from PIL import Image

try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None

from .schema import EvidenceRecord

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}


def build_metadata(
    student_id: str,
    session_id: str,
    timestamp: Optional[str] = None,
    camera: str = "webcam",
    category: str = "incident",
    width: Optional[int] = None,
    height: Optional[int] = None,
    source_path: str = "",
    evidence_id: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resolution = ""
    if width and height:
        resolution = f"{int(width)}x{int(height)}"
    if evidence_id is None:
        evidence_id = f"{student_id}-{session_id}-{uuid.uuid4().hex[:8]}"

    return {
        "evidence_id": evidence_id,
        "student_id": student_id,
        "session_id": session_id,
        "timestamp": resolved_timestamp,
        "camera": camera,
        "resolution": resolution,
        "category": category,
        "source_path": source_path,
    }


def _extract_student_session_tokens(ocr_text: str) -> Dict[str, Optional[str]]:
    patterns = {
        "student_id": r"STU[0-9A-Za-z-]+",
        "session_id": r"SESSION[0-9A-Za-z-]+",
        "timestamp": r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:?\d{2})?",
    }
    result: Dict[str, Optional[str]] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        result[key] = match.group(0) if match else None
    return result


def extract_ocr_text(file_path: str) -> str:
    image_path = Path(file_path)
    if not image_path.exists():
        return ""

    try:
        with Image.open(image_path) as img:
            if pytesseract is not None:
                try:
                    text = pytesseract.image_to_string(img)
                    if text and text.strip():
                        return text.strip()
                except Exception:
                    pass
            return f"No OCR text extracted for {image_path.name}."
    except Exception:
        return ""


def generate_vision_description(file_path: str, ocr_text: str = "") -> str:
    file_name = Path(file_path).name.lower()
    description_parts = []
    if "phone" in file_name or "mobile" in file_name:
        description_parts.append("a phone or handheld device is visible")
    if "id" in file_name:
        description_parts.append("an ID card or identity document is present")
    if "screen" in file_name:
        description_parts.append("a computer screen or exam interface is visible")
    if "webcam" in file_name:
        description_parts.append("a webcam frame is captured")

    ocr_lower = (ocr_text or "").lower()
    if "phone" in ocr_lower or "mobile" in ocr_lower:
        description_parts.append("the extracted text mentions a handheld device")
    if "student" in ocr_lower or "session" in ocr_lower:
        description_parts.append("the image contains student or session identifying information")

    if not description_parts:
        description_parts.append("a static exam evidence image with possible suspicious activity or identity context")
    return ". ".join(description_parts).capitalize() + "."


def load_image_evidence(directory: str, student_id: Optional[str] = None, session_id: Optional[str] = None) -> List[EvidenceRecord]:
    source_dir = Path(directory)
    if not source_dir.exists():
        return []

    records: List[EvidenceRecord] = []
    for path in sorted(source_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        ocr_text = extract_ocr_text(str(path))
        tokens = _extract_student_session_tokens(ocr_text)
        resolved_student = student_id or tokens.get("student_id") or "UNKNOWN_STUDENT"
        resolved_session = session_id or tokens.get("session_id") or "UNKNOWN_SESSION"
        timestamp = tokens.get("timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            with Image.open(path) as image:
                width, height = image.size
        except Exception:
            width, height = 0, 0

        metadata = build_metadata(
            student_id=resolved_student,
            session_id=resolved_session,
            timestamp=timestamp,
            camera="webcam",
            category="incident",
            width=width,
            height=height,
            source_path=str(path),
        )

        suspicious = "phone" in (ocr_text or "").lower() or "mobile" in (ocr_text or "").lower()
        risk_score = 0.75 if suspicious else 0.35

        record = EvidenceRecord(
            evidence_id=metadata["evidence_id"],
            student_id=resolved_student,
            session_id=resolved_session,
            timestamp=metadata["timestamp"],
            camera=metadata["camera"],
            resolution=metadata["resolution"],
            category=metadata["category"],
            source_path=metadata["source_path"],
            ocr_text=ocr_text,
            vision_description=generate_vision_description(str(path), ocr_text),
            metadata={
                "filename": path.name,
                "ocr_tokens": tokens,
            },
            suspicious=suspicious,
            risk_score=risk_score,
        )
        records.append(record)

    return records


def demo_evidence_records() -> List[EvidenceRecord]:
    payloads = [
        {
            "evidence_id": "EV-STU102-001",
            "student_id": "STU102",
            "session_id": "SESSION004",
            "timestamp": "2026-08-18T10:15:00Z",
            "camera": "webcam",
            "category": "incident",
            "ocr_text": "STU102 SESSION004 2026-08-18T10:15:00Z phone visible on desk",
            "vision_description": "A phone appears on the desk near the candidate.",
            "resolution": "1920x1080",
            "source_path": "demo/phone_capture.png",
        },
        {
            "evidence_id": "EV-STU102-002",
            "student_id": "STU102",
            "session_id": "SESSION004",
            "timestamp": "2026-08-18T10:18:00Z",
            "camera": "hall",
            "category": "hall_snapshot",
            "ocr_text": "STU102 SESSION004 multiple persons in frame",
            "vision_description": "A second person appears beside the main candidate.",
            "resolution": "1280x720",
            "source_path": "demo/hall_snapshot.png",
        },
        {
            "evidence_id": "EV-STU102-003",
            "student_id": "STU102",
            "session_id": "SESSION004",
            "timestamp": "2026-08-18T10:20:00Z",
            "camera": "webcam",
            "category": "absence",
            "ocr_text": "STU102 SESSION004 candidate out of frame",
            "vision_description": "Candidate is absent from the camera for a short interval.",
            "resolution": "1920x1080",
            "source_path": "demo/absence_capture.png",
        },
        {
            "evidence_id": "EV-STU001-001",
            "student_id": "STU001",
            "session_id": "SESSION001",
            "timestamp": "2026-08-19T10:05:00Z",
            "camera": "webcam",
            "category": "phone_activity",
            "ocr_text": "STU001 SESSION001 phone-like object near hand",
            "vision_description": "A phone-like object is visible near the candidate hand.",
            "resolution": "1920x1080",
            "source_path": "demo/stu001_phone.png",
        },
        {
            "evidence_id": "EV-STU001-002",
            "student_id": "STU001",
            "session_id": "SESSION001",
            "timestamp": "2026-08-19T10:12:00Z",
            "camera": "webcam",
            "category": "normal_exam",
            "ocr_text": "STU001 SESSION001 candidate writing normally",
            "vision_description": "The candidate appears alone and remains centered in the webcam frame.",
            "resolution": "1920x1080",
            "source_path": "demo/stu001_normal.png",
        },
        {
            "evidence_id": "EV-STU002-001",
            "student_id": "STU002",
            "session_id": "SESSION002",
            "timestamp": "2026-08-19T10:25:00Z",
            "camera": "webcam",
            "category": "multiple_person",
            "ocr_text": "STU002 SESSION002 multiple people in frame",
            "vision_description": "More than one person appears in the camera frame.",
            "resolution": "1280x720",
            "source_path": "demo/stu002_multiple_people.png",
        },
        {
            "evidence_id": "EV-STU002-002",
            "student_id": "STU002",
            "session_id": "SESSION002",
            "timestamp": "2026-08-19T10:31:00Z",
            "camera": "webcam",
            "category": "screen_activity",
            "ocr_text": "STU002 SESSION002 second screen detected",
            "vision_description": "A screen-like rectangle is visible beside the exam interface.",
            "resolution": "1280x720",
            "source_path": "demo/stu002_screen.png",
        },
        {
            "evidence_id": "EV-STU003-001",
            "student_id": "STU003",
            "session_id": "SESSION001",
            "timestamp": "2026-08-19T10:45:00Z",
            "camera": "id_camera",
            "category": "identity_document",
            "ocr_text": "STU003 SESSION001 synthetic identity document",
            "vision_description": "A synthetic ID document is visible for identity verification.",
            "resolution": "1024x768",
            "source_path": "demo/stu003_id_card.png",
        },
    ]

    records: List[EvidenceRecord] = []
    for item in payloads:
        metadata = build_metadata(
            student_id=item["student_id"],
            session_id=item["session_id"],
            timestamp=item["timestamp"],
            camera=item["camera"],
            category=item["category"],
            width=int(item["resolution"].split("x")[0]),
            height=int(item["resolution"].split("x")[1]),
            source_path=item["source_path"],
            evidence_id=item["evidence_id"],
        )
        suspicious = "phone" in item["ocr_text"].lower() or "multiple" in item["ocr_text"].lower()
        record = EvidenceRecord(
            evidence_id=metadata["evidence_id"],
            student_id=item["student_id"],
            session_id=item["session_id"],
            timestamp=item["timestamp"],
            camera=item["camera"],
            resolution=item["resolution"],
            category=item["category"],
            source_path=item["source_path"],
            ocr_text=item["ocr_text"],
            vision_description=item["vision_description"],
            metadata={"source": "demo"},
            suspicious=suspicious,
            risk_score=0.9 if "phone" in item["ocr_text"].lower() else 0.65,
        )
        records.append(record)
    return records


def validate_required_fields(records: Iterable[EvidenceRecord]) -> bool:
    required = {"evidence_id", "student_id", "session_id", "timestamp", "camera", "resolution", "category"}
    for record in records:
        values = {
            "evidence_id": record.evidence_id,
            "student_id": record.student_id,
            "session_id": record.session_id,
            "timestamp": record.timestamp,
            "camera": record.camera,
            "resolution": record.resolution,
            "category": record.category,
        }
        if not required.issubset(values.keys()):
            return False
        if any(value is None or value == "" for value in values.values()):
            return False
    return True
