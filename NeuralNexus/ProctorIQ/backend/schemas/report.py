"""
backend/schemas/report.py
---------------------------
Pydantic validation models for the final risk report.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    malpractice_event_id: int | None
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    summary: str
    report_path: str | None
    created_at: datetime


class GenerateReportRequest(BaseModel):
    """Trigger the full agent workflow for a given malpractice event."""
    malpractice_event_id: int
