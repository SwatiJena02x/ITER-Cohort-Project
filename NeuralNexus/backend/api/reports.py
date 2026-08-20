"""
backend/api/reports.py
-------------------------
Risk report management endpoints.

POST /api/reports/generate              – run full AI pipeline (admin)
POST /api/reports/{id}/publish          – publish report to student (admin)
GET  /api/reports/all                   – list all reports (admin)
GET  /api/reports/student/{student_id}  – reports for one student (admin)
GET  /api/reports/{id}                  – get single report
GET  /api/reports/{id}/download         – serve the PDF (student / admin)
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from agent.risk_scoring_agent import run_risk_scoring_workflow
from backend.auth_utils import get_current_user, require_admin
from database.connection import get_db
from database.repository import (
    create_risk_report,
    get_malpractice_event,
    get_risk_report,
    list_all_reports,
    list_reports_for_student,
    publish_report,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class GenerateReportRequest(BaseModel):
    malpractice_event_id: int


class RiskReportOut(BaseModel):
    id: int
    student_id: int
    student_name: str | None = None
    student_roll: str | None = None
    student_email: str | None = None
    malpractice_event_id: int | None
    risk_score: float
    risk_level: str
    summary: str
    report_path: str | None
    pdf_path: str | None
    is_published: bool
    evidence: dict | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_safe(cls, r, override_evidence: dict | None = None) -> "RiskReportOut":
        student_name = r.student.full_name if r.student else f"Student #{r.student_id}"
        student_roll = (r.student.roll_number or r.student.student_code) if r.student else f"STU-{r.student_id}"
        student_email = r.student.email if r.student else ""

        # Extract evidence from linked malpractice event if available
        ev_dict = override_evidence
        if ev_dict is None and r.student and r.student.malpractice_events:
            for ev in r.student.malpractice_events:
                if ev.id == r.malpractice_event_id and isinstance(ev.evidence, dict):
                    ev_dict = ev.evidence
                    break

        return cls(
            id=r.id,
            student_id=r.student_id,
            student_name=student_name,
            student_roll=student_roll,
            student_email=student_email,
            malpractice_event_id=r.malpractice_event_id,
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            summary=r.summary,
            report_path=r.report_path,
            pdf_path=r.pdf_path,
            is_published=r.is_published or False,
            evidence=ev_dict,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/generate", response_model=RiskReportOut, status_code=201)
def generate_report(
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """
    Runs image_analysis → face_matching → student_lookup → malpractice_detection
    → evidence_collector → eye_movement → talking_detection → risk_calculator
    → report_generator over the given malpractice event's image, then persists
    the resulting risk report to the database.
    """
    event = get_malpractice_event(db, payload.malpractice_event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Malpractice event not found.")

    claimed_code = None
    if event.student:
        claimed_code = event.student.student_code or event.student.roll_number

    result_state = run_risk_scoring_workflow(
        image_path=event.image_path,
        claimed_student_code=claimed_code,
    )

    matched_id = result_state.get("matched_student_id")
    if matched_id is not None:
        student_id = matched_id
    elif event.student_id is not None:
        student_id = event.student_id
    else:
        from database.models import Student
        first_stu = db.query(Student).order_by(Student.id.desc()).first()
        if first_stu:
            student_id = first_stu.id
        else:
            raise HTTPException(
                status_code=422,
                detail="Could not identify a student (no face match and no claimed student).",
            )

    # Sync the event record with what the agent found
    findings = result_state.get("malpractice_findings", [])
    if findings:
        event.malpractice_type = findings[0]["malpractice_type"]
        event.confidence = findings[0]["confidence"]
    event.evidence = result_state.get("evidence", {})
    event.face_match_score = result_state.get("face_match_distance")
    event.student_id = student_id
    db.add(event)
    db.commit()

    report = create_risk_report(
        db,
        student_id=student_id,
        malpractice_event_id=event.id,
        risk_score=result_state.get("risk_score", 0.0),
        risk_level=result_state.get("risk_level", "LOW"),
        summary=result_state.get("report_summary", ""),
        report_path=result_state.get("report_path"),
        pdf_path=result_state.get("pdf_path"),
    )
    return RiskReportOut.from_orm_safe(report, override_evidence=event.evidence)



@router.post("/{report_id}/publish", response_model=RiskReportOut)
def publish_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Admin publishes a report so the student can see it in their notice board."""
    report = publish_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return RiskReportOut.from_orm_safe(report)


@router.get("/all", response_model=list[RiskReportOut])
def get_all_reports(
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Admin: list all reports across all students."""
    reports = list_all_reports(db, limit=limit, offset=offset)
    return [RiskReportOut.from_orm_safe(r) for r in reports]


@router.get("/student/{student_id}", response_model=list[RiskReportOut])
def get_reports_for_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """All reports for a student (admin or the student themselves)."""
    if current_user.get("role") != "admin" and int(current_user.get("sub", 0)) != student_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only view your own reports.",
        )
    reports = list_reports_for_student(db, student_id)
    return [RiskReportOut.from_orm_safe(r) for r in reports]


@router.get("/{report_id}", response_model=RiskReportOut)
def get_single_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    report = get_risk_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if current_user.get("role") != "admin" and int(current_user.get("sub", 0)) != report.student_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only view your own report.",
        )
    return RiskReportOut.from_orm_safe(report)


@router.get("/{report_id}/download")
def download_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Serves the PDF file for download. Generates the PDF on-the-fly if needed."""
    report = get_risk_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if current_user.get("role") != "admin" and int(current_user.get("sub", 0)) != report.student_id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You can only download your own report.",
        )

    student_name = report.student.full_name if report.student else f"Student #{report.student_id}"
    student_code = (report.student.roll_number or report.student.student_code) if report.student else f"STU-{report.student_id}"

    # Generate latest styled PDF with student photo and local timing
    try:
        from backend.report_pdf import generate_pdf_report
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        reports_dir = os.path.join(base_dir, "reports", "generated_reports")
        os.makedirs(reports_dir, exist_ok=True)

        contributions = {}
        if report.student and report.student.malpractice_events:
            for ev in report.student.malpractice_events:
                if ev.id == report.malpractice_event_id and isinstance(ev.evidence, dict):
                    contributions = ev.evidence.get("score_contributions", {})

        photo_path = None
        if report.student:
            photo_path = report.student.passport_image_path or report.student.profile_image_path or report.student.id_card_image_path
            if photo_path and not os.path.isabs(photo_path):
                photo_path = os.path.join(base_dir, photo_path)

        exam_img_path = None
        if report.malpractice_event_id:
            from database.models import MalpracticeEvent
            ev_obj = db.query(MalpracticeEvent).filter_by(id=report.malpractice_event_id).first()
            if ev_obj and ev_obj.image_path:
                exam_img_path = ev_obj.image_path
                if not os.path.isabs(exam_img_path):
                    exam_img_path = os.path.join(base_dir, exam_img_path)

        if not exam_img_path and report.student and report.student.malpractice_events:
            for ev_item in report.student.malpractice_events:
                if ev_item.image_path and os.path.exists(ev_item.image_path):
                    exam_img_path = ev_item.image_path
                    if not os.path.isabs(exam_img_path):
                        exam_img_path = os.path.join(base_dir, exam_img_path)
                    break

        pdf_path = generate_pdf_report(
            report_dir=reports_dir,
            student_name=student_name,
            student_code=student_code,
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            contributions=contributions,
            summary=report.summary or "Proctoring examination risk report.",
            student_photo_path=photo_path,
            exam_image_path=exam_img_path,
            logo_path=os.path.join(base_dir, "frontend", "assets", "logo.png"),
        )

        if pdf_path and os.path.exists(pdf_path):
            rel_pdf_path = os.path.relpath(pdf_path, base_dir).replace("\\", "/")
            report.pdf_path = rel_pdf_path
            db.add(report)
            db.commit()
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=os.path.basename(pdf_path),
            )
    except Exception as e:
        pass

    # 2. Check if an existing PDF path is recorded and exists on disk
    if report.pdf_path:
        candidate_pdf = report.pdf_path if os.path.isabs(report.pdf_path) else os.path.join(base_dir, report.pdf_path)
        if os.path.exists(candidate_pdf):
            return FileResponse(
                candidate_pdf,
                media_type="application/pdf",
                filename=os.path.basename(candidate_pdf),
            )

    # 3. Fall back to plain-text report if PDF creation failed
    if report.report_path:
        candidate_txt = report.report_path if os.path.isabs(report.report_path) else os.path.join(base_dir, report.report_path)
        if os.path.exists(candidate_txt):
            return FileResponse(
                candidate_txt,
                media_type="text/plain",
                filename=os.path.basename(candidate_txt),
            )

    raise HTTPException(status_code=404, detail="Report file could not be generated.")

