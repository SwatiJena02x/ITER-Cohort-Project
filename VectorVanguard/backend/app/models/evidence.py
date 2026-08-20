from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    __table_args__ = (
        UniqueConstraint(
            "evidence_id",
            name="uq_evidence_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    evidence_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("exam_sessions.id"),
        nullable=False,
        index=True,
    )

    image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Raw OCR output
    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Full vision-model response
    vision_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Structured information extracted by vision model
    structured_observations: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    exam_session: Mapped["ExamSession"] = relationship(
        back_populates="evidence_records"
    )