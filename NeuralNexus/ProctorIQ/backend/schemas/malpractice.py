"""
backend/schemas/malpractice.py
--------------------------------
Pydantic validation models for malpractice image upload & detection results.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    label: str
    confidence: float = Field(ge=0, le=1)


class MalpracticeEvidence(BaseModel):
    """Structured evidence collected by the detection nodes."""
    detected_objects: list[BoundingBox] = Field(default_factory=list)
    face_count: int = 0
    notes: str | None = None


class MalpracticeAnalysisRequest(BaseModel):
    """Metadata sent alongside the uploaded image (image itself is multipart)."""
    student_code: str | None = Field(
        default=None,
        description="If known, the student this image is claimed to belong to.",
    )


class MalpracticeEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int | None
    image_path: str
    malpractice_type: str
    confidence: float
    evidence: dict
    face_match_score: float | None
    created_at: datetime
