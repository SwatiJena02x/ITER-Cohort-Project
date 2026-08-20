"""
database/models.py
-------------------
SQLAlchemy ORM models: Admin, Student, MalpracticeEvent, RiskReport.

Changes from original:
 - Added Admin model (name, email, password_hash)
 - Extended Student: password_hash, roll_number, id_card_image_path,
   passport_image_path, identity_verified
 - Extended RiskReport: is_published flag so admins can control visibility
 - Removed pgvector Vector type (face_embedding stored as JSON already)
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base

FACE_EMBEDDING_DIM = 128  # face_recognition's default embedding size


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
class Admin(Base):
    """System administrators – can upload images, run analysis, publish reports."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # --- Identification ---
    student_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    course: Mapped[str] = mapped_column(String(150), nullable=True)

    # --- Auth ---
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)

    # --- Images ---
    profile_image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    id_card_image_path: Mapped[str] = mapped_column(String(500), nullable=True)
    passport_image_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # --- Face embedding (128-d vector stored as JSON list) ---
    face_embedding: Mapped[list] = mapped_column(JSON, nullable=True)

    # --- Identity verification ---
    identity_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_match_score: Mapped[float] = mapped_column(Float, nullable=True)
    face_match_score_reg: Mapped[float] = mapped_column(Float, nullable=True)
    face_match_score: Mapped[float] = mapped_column(Float, nullable=True)
    face_match_status: Mapped[str] = mapped_column(String(50), nullable=True)
    last_login_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    malpractice_events: Mapped[list["MalpracticeEvent"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    risk_reports: Mapped[list["RiskReport"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# MalpracticeEvent
# ---------------------------------------------------------------------------
class MalpracticeEvent(Base):
    """A single uploaded/analyzed malpractice image and what was found in it."""

    __tablename__ = "malpractice_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=True)

    image_path: Mapped[str] = mapped_column(String(500))
    malpractice_type: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    face_match_score: Mapped[float] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="malpractice_events")


# ---------------------------------------------------------------------------
# RiskReport
# ---------------------------------------------------------------------------
class RiskReport(Base):
    """Final, generated risk report for a student for one proctoring session/upload."""

    __tablename__ = "risk_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    malpractice_event_id: Mapped[int] = mapped_column(
        ForeignKey("malpractice_events.id"), nullable=True
    )

    risk_score: Mapped[float] = mapped_column(Float)          # 0-100
    risk_level: Mapped[str] = mapped_column(String(20))       # LOW / MEDIUM / HIGH / CRITICAL
    summary: Mapped[str] = mapped_column(Text)                # LLM-generated explanation
    report_path: Mapped[str] = mapped_column(String(500), nullable=True)
    pdf_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # Admin sets this to True to push the report to the student's notice board
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="risk_reports")
