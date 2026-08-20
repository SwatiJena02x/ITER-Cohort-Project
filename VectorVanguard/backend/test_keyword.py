import sys
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.models.evidence import EvidenceRecord
from app.services.retrieval import KeywordRetriever


def run_test():
    db = SessionLocal()

    student = None
    session = None

    try:
        print("[*] 1. Setting up mock relational data...")

        # Create test student
        student = Student(
            name="Test Student",
            student_id="TS-100"
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        # Create test exam session
        session = ExamSession(
            student_id=student.id,
            exam_name="Test Exam",
            started_at=datetime.now(timezone.utc)
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Create test evidence
        evidence = EvidenceRecord(
            evidence_id="EV-FTS-TEST",
            session_id=session.id,
            image_path="/dummy/path.jpg",
            ocr_text=(
                "Warning: The student has placed an unauthorized "
                "iPhone 15 Pro Max on the desk."
            ),
            timestamp=datetime.now(timezone.utc)
        )

        db.add(evidence)
        db.commit()

        print("[*] 2. Testing PostgreSQL Full-Text Search...")

        retriever = KeywordRetriever(db_session=db)

        search_query = "unauthorized iPhone"

        print(f"  -> Query: '{search_query}'")

        results = retriever.search(
            query=search_query,
            top_k=5
        )

        if results:
            print("\n[SUCCESS] Keyword Match Found!")
            print(f"  -> Evidence ID: {results[0]['evidence_id']}")
            print(f"  -> Rank Score: {results[0]['score']}")
            print(f"  -> Matched Text: {results[0]['ocr_text']}")

            return True

        print("\n[ERROR] No match found. FTS failed.")
        return False

    except Exception as e:
        db.rollback()

        print("\n[ERROR] Test failed:")
        print(e)

        return False

    finally:
        print("\n[*] 3. Cleaning up test data...")

        try:
            if session:
                db.query(EvidenceRecord).filter(
                    EvidenceRecord.evidence_id == "EV-FTS-TEST"
                ).delete()

                db.query(ExamSession).filter(
                    ExamSession.id == session.id
                ).delete()

            if student:
                db.query(Student).filter(
                    Student.id == student.id
                ).delete()

            db.commit()

        except Exception as e:
            db.rollback()
            print(f"[WARNING] Cleanup failed: {e}")

        finally:
            db.close()


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)