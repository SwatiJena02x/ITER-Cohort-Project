import sys
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection
from app.services.retrieval import HybridRetriever


TEST_EVIDENCE = {
    "id": "EV-HYDRATION-TEST",
    "text": "A mobile phone was detected near the examination desk.",
}


def run_test():
    db = SessionLocal()

    student = None
    session = None

    try:
        print("[*] 1. Creating relational test data...")

        student = Student(
            student_id="HYDRATION-STUDENT",
            name="Hydration Test Student",
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        session = ExamSession(
            student_id=student.id,
            exam_name="Hydration Test Exam",
            started_at=datetime.now(timezone.utc),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        evidence = EvidenceRecord(
            evidence_id=TEST_EVIDENCE["id"],
            session_id=session.id,
            image_path="/evidence/mobile_phone.jpg",
            ocr_text=TEST_EVIDENCE["text"],
            timestamp=datetime.now(timezone.utc),
        )

        db.add(evidence)
        db.commit()

        print("[*] 2. Adding evidence to ChromaDB...")

        collection.add(
            ids=[TEST_EVIDENCE["id"]],
            documents=[TEST_EVIDENCE["text"]],
            metadatas=[
                {
                    "evidence_id": TEST_EVIDENCE["id"],
                    "session_id": str(session.id),
                }
            ],
        )

        print("[*] 3. Running hybrid retrieval...")

        retriever = HybridRetriever(db)

        results = retriever.search(
            query="mobile phone near desk",
            top_k=5,
        )

        if not results:
            print("[ERROR] Hybrid search returned no results.")
            return False

        print("[SUCCESS] Hybrid result found.")

        print("[*] 4. Hydrating results from PostgreSQL...")

        hydrated = retriever.hydrate_results(results)

        matching = [
            item
            for item in hydrated
            if item["evidence_id"] == TEST_EVIDENCE["id"]
        ]

        if not matching:
            print("[ERROR] PostgreSQL hydration failed.")
            return False

        result = matching[0]

        print("\n[SUCCESS] PostgreSQL hydration passed!")
        print(f"  -> Evidence ID: {result['evidence_id']}")
        print(f"  -> Session ID: {result['session_id']}")
        print(f"  -> Image Path: {result['image_path']}")
        print(f"  -> OCR Text: {result['ocr_text']}")
        print(f"  -> Timestamp: {result['timestamp']}")
        print(f"  -> RRF Score: {result['rrf_score']}")

        return True

    except Exception as e:
        db.rollback()

        print("\n[ERROR] Test failed:")
        print(e)

        return False

    finally:
        print("\n[*] 5. Cleaning up...")

        try:
            collection.delete(
                ids=[TEST_EVIDENCE["id"]]
            )

            if session:
                db.query(EvidenceRecord).filter(
                    EvidenceRecord.session_id == session.id
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