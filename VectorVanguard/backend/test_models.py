from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models import Student, ExamSession, EvidenceRecord


db = SessionLocal()

try:
    student = Student(
        student_id="TEST-001",
        name="Test Student",
    )
    db.add(student)
    db.flush()

    session = ExamSession(
        student_id=student.id,
        exam_name="VectorVanguard Test Exam",
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.flush()

    evidence = EvidenceRecord(
        evidence_id="EV-TEST-001",
        session_id=session.id,
        image_path="data/raw/test_image.jpg",
        ocr_text="Test evidence: mobile phone detected.",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(evidence)

    db.commit()

    print("[SUCCESS] Test records inserted.")
    print(f"Student ID: {student.id}")
    print(f"Session ID: {session.id}")
    print(f"Evidence ID: {evidence.evidence_id}")

except Exception as error:
    db.rollback()
    print(f"[ERROR] {error}")

finally:
    db.close()