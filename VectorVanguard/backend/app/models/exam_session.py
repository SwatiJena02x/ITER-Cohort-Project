from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True,
    )

    exam_name: Mapped[str] = mapped_column(String(150), nullable=False)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    student: Mapped["Student"] = relationship(
        back_populates="exam_sessions"
    )

    evidence_records: Mapped[list["EvidenceRecord"]] = relationship(
        back_populates="exam_session",
        cascade="all, delete-orphan",
    )