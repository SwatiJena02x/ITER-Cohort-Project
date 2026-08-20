"""
backend/api/admin.py
---------------------
Admin-only endpoints:
  GET /api/admin/dashboard   – summary statistics for the admin dashboard
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth_utils import require_admin
from database.connection import get_db
from database.repository import (
    count_high_risk,
    count_malpractice_events,
    count_reports,
    count_students,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


class DashboardStats(BaseModel):
    total_students: int
    total_analyzed: int
    total_reports: int
    high_risk_count: int


@router.get("/dashboard", response_model=DashboardStats)
def admin_dashboard(
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Returns aggregate statistics for the admin dashboard cards."""
    return DashboardStats(
        total_students=count_students(db),
        total_analyzed=count_malpractice_events(db),
        total_reports=count_reports(db),
        high_risk_count=count_high_risk(db),
    )
