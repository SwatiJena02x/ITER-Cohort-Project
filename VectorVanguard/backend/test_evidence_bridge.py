import uuid

from app.core.database import SessionLocal
from app.services.evidence_store import store_evidence
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection


def test_evidence_postgres_chroma_bridge():
    """
    Verify that evidence is stored correctly in PostgreSQL
    and indexed correctly in ChromaDB.
    """

    db = SessionLocal()

    # Generate unique IDs so the test is repeatable.
    unique_id = uuid.uuid4().hex[:8]

    test_student_id = f"BRIDGE-TEST-{unique_id}"
    test_evidence_id = f"EV-BRIDGE-TEST-{unique_id}"

    try:
        # ------------------------------------------------------------------
        # 1. Create test student
        # ------------------------------------------------------------------
        student = Student(
            student_id=test_student_id,
            name="Bridge Test Student",
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        # ------------------------------------------------------------------
        # 2. Create test exam session
        # ------------------------------------------------------------------
        session = ExamSession(
            student_id=student.id,
            exam_name="Bridge Test Exam",
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # ------------------------------------------------------------------
        # 3. Store evidence
        # ------------------------------------------------------------------
        evidence = store_evidence(
            db=db,
            evidence_id=test_evidence_id,
            session_id=session.id,
            image_path="data/raw/bridge_test.jpg",
            ocr_text="A mobile phone was visible near the student.",
        )

        # ------------------------------------------------------------------
        # 4. Verify PostgreSQL
        # ------------------------------------------------------------------
        assert evidence.evidence_id == test_evidence_id

        db_evidence = (
            db.query(EvidenceRecord)
            .filter(
                EvidenceRecord.evidence_id == test_evidence_id
            )
            .first()
        )

        assert db_evidence is not None
        assert db_evidence.ocr_text == (
            "A mobile phone was visible near the student."
        )

        # ------------------------------------------------------------------
        # 5. Verify ChromaDB
        # ------------------------------------------------------------------
        result = collection.get(
            ids=[test_evidence_id]
        )

        assert result["ids"]
        assert result["ids"][0] == test_evidence_id

        assert result["metadatas"]
        assert (
            result["metadatas"][0]["evidence_id"]
            == test_evidence_id
        )

        print(
            f"\n[SUCCESS] PostgreSQL <-> ChromaDB bridge verified "
            f"for {test_evidence_id}"
        )

    finally:
        # ------------------------------------------------------------------
        # 6. Cleanup PostgreSQL test data
        # ------------------------------------------------------------------
        if "session" in locals() and session.id:
            db.query(EvidenceRecord).filter(
                EvidenceRecord.evidence_id == test_evidence_id
            ).delete(
                synchronize_session=False
            )

            db.query(ExamSession).filter(
                ExamSession.id == session.id
            ).delete(
                synchronize_session=False
            )

        if "student" in locals() and student.id:
            db.query(Student).filter(
                Student.id == student.id
            ).delete(
                synchronize_session=False
            )

        db.commit()

        # ------------------------------------------------------------------
        # 7. Cleanup ChromaDB test vector
        # ------------------------------------------------------------------
        try:
            collection.delete(
                ids=[test_evidence_id]
            )
        except Exception:
            pass

        db.close()