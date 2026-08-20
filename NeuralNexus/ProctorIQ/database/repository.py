"""
database/repository.py
Data-access layer.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database.models import (
    Admin,
    MalpracticeEvent,
    RiskReport,
    Student,
)


# ============================================================
# ADMIN
# ============================================================

def create_admin(
    db: Session,
    *,
    name: str,
    email: str,
    password_hash: str,
) -> Admin:

    admin = Admin(
        name=name,
        email=email.lower().strip(),
        password_hash=password_hash,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def get_admin_by_email(
    db: Session,
    email: str,
) -> Admin | None:

    stmt = select(Admin).where(
        func.lower(Admin.email) == email.lower().strip()
    )

    return db.execute(stmt).scalar_one_or_none()


def get_admin_by_id(
    db: Session,
    admin_id: int,
) -> Admin | None:

    return db.get(Admin, admin_id)


# ============================================================
# STUDENT
# ============================================================

def create_student(
    db: Session,
    *,
    student_code: str,
    full_name: str,
    email: str,
    course: str | None = None,
    roll_number: str | None = None,
    password_hash: str | None = None,
    profile_image_path: str | None = None,
    id_card_image_path: str | None = None,
    passport_image_path: str | None = None,
    face_embedding: list[float] | None = None,
    identity_verified: bool = False,
    ocr_match_score: float | None = None,
    face_match_score_reg: float | None = None,
    face_match_score: float | None = None,
    face_match_status: str | None = None,
    last_login_at: datetime | None = None,
) -> Student:

    student = Student(
        student_code=student_code.strip(),
        roll_number=(roll_number or student_code).strip(),
        full_name=full_name.strip(),
        email=email.lower().strip(),
        course=course,
        password_hash=password_hash,

        profile_image_path=profile_image_path,
        id_card_image_path=id_card_image_path,
        passport_image_path=passport_image_path,

        face_embedding=face_embedding,

        identity_verified=identity_verified,
        ocr_match_score=ocr_match_score,

        face_match_score_reg=face_match_score_reg,
        face_match_score=face_match_score,
        face_match_status=face_match_status,

        last_login_at=last_login_at,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


def get_student_by_id(
    db: Session,
    student_id: int,
) -> Student | None:

    return db.get(Student, student_id)


def get_student_by_code(
    db: Session,
    student_code: str,
) -> Student | None:

    if not student_code:
        return None

    code = student_code.strip()

    stmt = select(Student).where(
        (Student.student_code == code) |
        (Student.roll_number == code) |
        (func.lower(Student.email) == code.lower())
    )

    return db.execute(stmt).scalars().first()


def get_student_by_roll(
    db: Session,
    roll_number: str,
) -> Student | None:

    stmt = select(Student).where(
        Student.roll_number == roll_number.strip()
    )

    return db.execute(stmt).scalar_one_or_none()


def get_student_by_email(
    db: Session,
    email: str,
) -> Student | None:

    stmt = select(Student).where(
        func.lower(Student.email) == email.lower().strip()
    )

    return db.execute(stmt).scalar_one_or_none()


def list_students(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> list[Student]:

    stmt = (
        select(Student)
        .order_by(Student.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.execute(stmt).scalars())


def update_student_identity(
    db: Session,
    student_id: int,
    *,
    identity_verified: bool,
    ocr_match_score: float | None = None,
    face_match_score_reg: float | None = None,
    face_match_score: float | None = None,
    face_match_status: str | None = None,
) -> Student | None:

    student = db.get(Student, student_id)

    if not student:
        return None

    student.identity_verified = identity_verified

    if ocr_match_score is not None:
        student.ocr_match_score = ocr_match_score

    if face_match_score_reg is not None:
        student.face_match_score_reg = face_match_score_reg

    if face_match_score is not None:
        student.face_match_score = face_match_score

    if face_match_status is not None:
        student.face_match_status = face_match_status

    db.commit()
    db.refresh(student)

    return student


# ============================================================
# FACE MATCH
# ============================================================

def find_closest_student_by_embedding(
    db: Session,
    embedding: list[float],
    top_k: int = 1,
) -> list[tuple[Student, float]]:

    import numpy as np

    stmt = select(Student).where(
        Student.face_embedding.isnot(None)
    )

    students = list(db.execute(stmt).scalars())

    if not students:
        return []

    target = np.array(
        embedding,
        dtype=np.float32,
    )

    matches = []

    for student in students:

        if not student.face_embedding:
            continue

        stored = np.array(
            student.face_embedding,
            dtype=np.float32,
        )

        distance = float(
            np.linalg.norm(target - stored)
        )

        matches.append(
            (student, distance)
        )

    matches.sort(
        key=lambda item: item[1]
    )

    return matches[:top_k]


# ============================================================
# MALPRACTICE EVENTS
# ============================================================

def create_malpractice_event(
    db: Session,
    *,
    student_id: int | None,
    image_path: str,
    malpractice_type: str,
    confidence: float,
    evidence: dict,
    face_match_score: float | None = None,
) -> MalpracticeEvent:

    event = MalpracticeEvent(
        student_id=student_id,
        image_path=image_path,
        malpractice_type=malpractice_type,
        confidence=confidence,
        evidence=evidence,
        face_match_score=face_match_score,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_malpractice_event(
    db: Session,
    event_id: int,
) -> MalpracticeEvent | None:

    return db.get(MalpracticeEvent, event_id)


def list_events_for_student(
    db: Session,
    student_id: int,
) -> list[MalpracticeEvent]:

    stmt = (
        select(MalpracticeEvent)
        .where(
            MalpracticeEvent.student_id == student_id
        )
        .order_by(
            MalpracticeEvent.created_at.desc()
        )
    )

    return list(db.execute(stmt).scalars())


# ============================================================
# RISK REPORTS
# ============================================================

def create_risk_report(
    db: Session,
    *,
    student_id: int,
    malpractice_event_id: int | None,
    risk_score: float,
    risk_level: str,
    summary: str,
    report_path: str | None = None,
    pdf_path: str | None = None,
) -> RiskReport:

    report = RiskReport(
        student_id=student_id,
        malpractice_event_id=malpractice_event_id,
        risk_score=risk_score,
        risk_level=risk_level,
        summary=summary,
        report_path=report_path,
        pdf_path=pdf_path,
        is_published=False,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_risk_report(
    db: Session,
    report_id: int,
) -> RiskReport | None:

    return db.get(RiskReport, report_id)


def list_reports_for_student(
    db: Session,
    student_id: int,
) -> list[RiskReport]:

    stmt = (
        select(RiskReport)
        .where(
            RiskReport.student_id == student_id
        )
        .order_by(
            RiskReport.id.desc(),
            RiskReport.created_at.desc()
        )
    )

    return list(db.execute(stmt).scalars())


def list_published_reports_for_student(
    db: Session,
    student_id: int,
) -> list[RiskReport]:

    stmt = (
        select(RiskReport)
        .where(
            RiskReport.student_id == student_id,
            RiskReport.is_published.is_(True),
        )
        .order_by(
            RiskReport.id.desc(),
            RiskReport.created_at.desc()
        )
    )

    return list(db.execute(stmt).scalars())


def list_all_reports(
    db: Session,
    limit: int = 200,
    offset: int = 0,
) -> list[RiskReport]:

    stmt = (
        select(RiskReport)
        .order_by(RiskReport.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.execute(stmt).scalars())


def publish_report(
    db: Session,
    report_id: int,
) -> RiskReport | None:

    report = db.get(
        RiskReport,
        report_id,
    )

    if not report:
        return None

    report.is_published = True

    db.commit()
    db.refresh(report)

    return report


# ============================================================
# COUNTS
# ============================================================

def count_students(db: Session) -> int:

    return (
        db.execute(
            select(func.count(Student.id))
        ).scalar()
        or 0
    )


def count_malpractice_events(
    db: Session,
) -> int:

    return (
        db.execute(
            select(func.count(MalpracticeEvent.id))
        ).scalar()
        or 0
    )


def count_reports(db: Session) -> int:

    return (
        db.execute(
            select(func.count(RiskReport.id))
        ).scalar()
        or 0
    )


def count_high_risk(db: Session) -> int:

    stmt = select(
        func.count(RiskReport.id)
    ).where(
        RiskReport.risk_level.in_(
            ["HIGH", "CRITICAL"]
        )
    )

    return (
        db.execute(stmt).scalar()
        or 0
    )
