import sys
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection
from app.services.retrieval import HybridRetriever


TEST_EVIDENCE = [
    {
        "id": "EV-HYBRID-001",
        "text": "A mobile phone was visible near the examination desk.",
    },
    {
        "id": "EV-HYBRID-002",
        "text": "The student was sitting quietly at the examination desk.",
    },
    {
        "id": "EV-HYBRID-003",
        "text": "A water bottle was placed beside the examination desk.",
    },
]


def run_test():
    db = SessionLocal()

    student = None
    session = None

    try:
        print("[*] 1. Creating temporary relational data...")

        student = Student(
            student_id="HYBRID-STUDENT",
            name="Hybrid Test Student",
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        session = ExamSession(
            student_id=student.id,
            exam_name="Hybrid Test Exam",
            started_at=datetime.now(timezone.utc),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        print("[*] 2. Adding temporary evidence...")

        for item in TEST_EVIDENCE:
            evidence = EvidenceRecord(
                evidence_id=item["id"],
                session_id=session.id,
                image_path="/dummy/path.jpg",
                ocr_text=item["text"],
                timestamp=datetime.now(timezone.utc),
            )

            db.add(evidence)

        db.commit()

        print("[*] 3. Adding documents to ChromaDB...")

        collection.add(
            ids=[item["id"] for item in TEST_EVIDENCE],
            documents=[item["text"] for item in TEST_EVIDENCE],
            metadatas=[
                {
                    "evidence_id": item["id"],
                    "session_id": str(session.id),
                }
                for item in TEST_EVIDENCE
            ],
        )

        print("[*] 4. Testing hybrid retrieval...")

        retriever = HybridRetriever(db)

        query = "Was a mobile phone near the desk?"

        print(f"  -> Query: '{query}'")

        results = retriever.search(
            query=query,
            top_k=3,
        )

        if not results:
            print("\n[ERROR] Hybrid search returned no results.")
            return False

        print("\n[SUCCESS] Hybrid results:")

        for index, result in enumerate(results, start=1):
            print(f"\n  Rank {index}")
            print(f"  -> Evidence ID: {result['evidence_id']}")
            print(f"  -> RRF Score: {result['rrf_score']}")
            print(f"  -> Keyword Rank: {result['keyword_rank']}")
            print(f"  -> Semantic Rank: {result['semantic_rank']}")
            print(f"  -> Text: {result['ocr_text']}")

        # The mobile-phone evidence should be the top result.
        if results[0]["evidence_id"] != "EV-HYBRID-001":
            print(
                "\n[ERROR] Expected EV-HYBRID-001 "
                "to be the top hybrid result."
            )
            return False

        print("\n[SUCCESS] Hybrid retrieval test passed!")

        return True

    except Exception as e:
        db.rollback()

        print("\n[ERROR] Test failed:")
        print(e)

        return False

    finally:
        print("\n[*] 5. Cleaning up test data...")

        try:
            collection.delete(
                ids=[item["id"] for item in TEST_EVIDENCE]
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