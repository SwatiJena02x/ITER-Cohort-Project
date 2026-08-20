"""
agent/nodes/report_generator.py
-----------------------------------
Final agent node: uses LangChain + an LLM (with an offline deterministic
fallback) to turn the computed risk score and evidence into a
plain-language report, then saves it to disk under reports/generated_reports/.

Also generates a styled PDF report via backend/report_pdf.py.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

from agent.state import RiskScoringState
from llm.langchain_config import get_llm
from llm.prompts import render_fallback_summary, report_prompt

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join("reports", "generated_reports")


def _contributions_block(contributions: dict[str, float]) -> str:
    if not contributions:
        return "- none"
    return "\n".join(f"- {label.replace('_', ' ')}: +{pts} pts" for label, pts in contributions.items())


def run(state: RiskScoringState) -> RiskScoringState:
    student_name       = state.get("matched_student_name") or "Unknown student"
    student_code       = state.get("matched_student_code") or "UNKNOWN"
    risk_score         = state.get("risk_score", 0.0)
    risk_level         = state.get("risk_level", "LOW")
    contributions      = state.get("score_contributions", {})
    face_match_distance= state.get("face_match_distance")
    face_count         = state.get("face_count", 0)

    llm = get_llm()
    summary: str

    if llm is not None:
        try:
            chain = report_prompt | llm
            response = chain.invoke(
                {
                    "student_name": student_name,
                    "student_code": student_code,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "contributions_block": _contributions_block(contributions),
                    "face_match_distance": (
                        f"{face_match_distance:.3f}" if face_match_distance is not None else "N/A"
                    ),
                    "face_count": face_count,
                }
            )
            summary = response.content if hasattr(response, "content") else str(response)
        except Exception as exc:  # noqa: BLE001
            logger.warning("[report_generator] LLM call failed (%s); using offline fallback.", exc)
            summary = render_fallback_summary(
                student_name=student_name,
                student_code=student_code,
                risk_score=risk_score,
                risk_level=risk_level,
                contributions=contributions,
                face_match_distance=face_match_distance,
                face_count=face_count,
            )
    else:
        summary = render_fallback_summary(
            student_name=student_name,
            student_code=student_code,
            risk_score=risk_score,
            risk_level=risk_level,
            contributions=contributions,
            face_match_distance=face_match_distance,
            face_count=face_count,
        )

    state["report_summary"] = summary

    # --- Save plain-text report ---
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reports_abs_dir = os.path.join(base_dir, "reports", "generated_reports")
    os.makedirs(reports_abs_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    txt_filename = f"report_{student_code}_{timestamp}.txt"
    txt_path = os.path.join(reports_abs_dir, txt_filename)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(summary)
    state["report_path"] = os.path.relpath(txt_path, base_dir).replace("\\", "/")
    logger.info("[report_generator] text report written to %s", txt_path)

    # --- Generate PDF report ---
    try:
        from backend.report_pdf import generate_pdf_report
        logo_path = os.path.join(base_dir, "frontend", "assets", "logo.png")
        # Retrieve candidate photo if available in state or database
        student_photo = state.get("student_photo_path") or state.get("matched_student_profile_image")
        if not student_photo and student_code != "UNKNOWN":
            try:
                from database.connection import SessionLocal
                from database.models import Student
                db = SessionLocal()
                s = db.query(Student).filter(
                    (Student.student_code == student_code) | (Student.roll_number == student_code)
                ).first()
                if s:
                    student_photo = s.passport_image_path or s.profile_image_path or s.id_card_image_path
                    if student_photo and not os.path.isabs(student_photo):
                        student_photo = os.path.join(base_dir, student_photo)
                db.close()
            except Exception:
                pass

        pdf_path = generate_pdf_report(
            report_dir=reports_abs_dir,
            student_name=student_name,
            student_code=student_code,
            risk_score=risk_score,
            risk_level=risk_level,
            contributions=contributions,
            summary=summary,
            student_photo_path=student_photo,
            exam_image_path=state.get("image_path"),
            logo_path=logo_path if os.path.exists(logo_path) else None,
            timestamp=timestamp,
        )
        if pdf_path:
            state["pdf_path"] = os.path.relpath(pdf_path, base_dir).replace("\\", "/")
            logger.info("[report_generator] PDF written to %s", pdf_path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[report_generator] PDF generation failed: %s", exc)

    return state
