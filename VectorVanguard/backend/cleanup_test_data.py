from app.core.database import SessionLocal
from app.models import Student, ExamSession, EvidenceRecord

db = SessionLocal()

try:
    evidence = db.query(EvidenceRecord).filter_by(
        evidence_id="EV-TEST-001"
    ).first()

    if evidence:
        db.delete(evidence)

    session = db.query(ExamSession).filter_by(
        exam_name="VectorVanguard Test Exam"
    ).first()

    if session:
        db.delete(session)

    student = db.query(Student).filter_by(
        student_id="TEST-001"
    ).first()

    if student:
        db.delete(student)

    db.commit()
    print("[SUCCESS] Test data removed.")

except Exception as error:
    db.rollback()
    print(f"[ERROR] Cleanup failed: {error}")

finally:
    db.close()