from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.core.vector_store import collection
from app.models.student import Student
from app.models.exam_session import ExamSession
from app.models.evidence import EvidenceRecord
from app.services.agent import agent


EVIDENCE_ID = "EV-AGENT-TEST"


def run_test():
    db = SessionLocal()

    student = None
    session = None

    try:
        print("[*] 1. Creating temporary relational data...")

        student = Student(
            student_id="AGENT-TEST-STUDENT",
            name="Agent Test Student",
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        session = ExamSession(
            student_id=student.id,
            exam_name="Agent Test Exam",
            started_at=datetime.now(timezone.utc),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        print("[*] 2. Creating temporary evidence...")

        evidence = EvidenceRecord(
            evidence_id=EVIDENCE_ID,
            session_id=session.id,
            image_path="/evidence/mobile_phone.jpg",
            ocr_text=(
                "A mobile phone was clearly visible "
                "near the student's examination desk."
            ),
            timestamp=datetime.now(timezone.utc),
        )

        db.add(evidence)
        db.commit()

        print("[*] 3. Adding evidence to ChromaDB...")

        collection.add(
            ids=[EVIDENCE_ID],
            documents=[
                evidence.ocr_text
            ],
            metadatas=[
                {
                    "evidence_id": EVIDENCE_ID,
                    "session_id": str(session.id),
                }
            ],
        )

        print("[*] 4. Running LangGraph agent...")

        question = (
            "Investigate whether a mobile phone was visible "
            "near the student's examination desk. "
            "Search the available evidence and answer "
            "only using the retrieved evidence."
        )

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            }
        )

        print("\n[*] 5. Agent execution trace:")

        tool_called = False

        for message in result["messages"]:
            print(f"\n--- {message.type} ---")
            print(message.content)

            if message.type == "tool":
                tool_called = True

        final_message = result["messages"][-1]

        print("\n[*] 6. Verification...")

        if not tool_called:
            print("[ERROR] Agent did not call the retrieval tool.")
            return False

        if EVIDENCE_ID not in str(result["messages"]):
            print("[ERROR] Expected evidence was not retrieved.")
            return False

        if not final_message.content:
            print("[ERROR] Agent produced no final answer.")
            return False

        print("\n[SUCCESS] Real agent evidence test passed!")
        print(f"  -> Tool called: {tool_called}")
        print(f"  -> Evidence found: {EVIDENCE_ID}")
        print(f"  -> Final answer: {final_message.content}")

        return True

    finally:
        print("\n[*] 7. Cleaning up test data...")

        try:
            collection.delete(ids=[EVIDENCE_ID])
        except Exception:
            pass

        if session is not None:
            db.query(EvidenceRecord).filter(
                EvidenceRecord.session_id == session.id
            ).delete()

            db.query(ExamSession).filter(
                ExamSession.id == session.id
            ).delete()

        if student is not None:
            db.query(Student).filter(
                Student.id == student.id
            ).delete()

        db.commit()
        db.close()

        print("[*] Test data removed.")


if __name__ == "__main__":
    success = run_test()

    raise SystemExit(0 if success else 1)
