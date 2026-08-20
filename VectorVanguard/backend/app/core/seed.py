from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.exam_session import ExamSession


SEED_STUDENT_ID = "DEMO-2026-001"
SEED_STUDENT_NAME = "Demo Student"
SEED_EXAM_NAME = "Offline AI Proctoring Demo"


def seed_database():
    db: Session = SessionLocal()

    try:
        # Check whether the demo student already exists.
        student = (
            db.query(Student)
            .filter(
                Student.student_id == SEED_STUDENT_ID
            )
            .first()
        )

        if student is None:
            student = Student(
                student_id=SEED_STUDENT_ID,
                name=SEED_STUDENT_NAME,
            )

            db.add(student)
            db.commit()
            db.refresh(student)

            print(
                f"[OK] Created student: "
                f"{student.student_id}"
            )

        else:
            print(
                f"[OK] Student already exists: "
                f"{student.student_id}"
            )

        # Check whether the demo exam session already exists.
        session = (
            db.query(ExamSession)
            .filter(
                ExamSession.student_id == student.id,
                ExamSession.exam_name == SEED_EXAM_NAME,
            )
            .first()
        )

        if session is None:
            session = ExamSession(
                student_id=student.id,
                exam_name=SEED_EXAM_NAME,
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            print(
                f"[OK] Created exam session: "
                f"{session.id}"
            )

        else:
            print(
                f"[OK] Exam session already exists: "
                f"{session.id}"
            )

        print("\n[SUCCESS] Database seed completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()