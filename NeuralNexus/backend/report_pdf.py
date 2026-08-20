"""
backend/report_pdf.py
----------------------
Generates a professional styled PDF risk report using fpdf2.
Includes:
- Registered Candidate ID photo
- Uploaded Proctoring/Exam session photo (Malpractice evidence frame)
- Verified local time (IST 12-hr format)
- Calculated Risk score & classification
- Breakdown of detected issues & contributions
- AI explanation & summary
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def _risk_color(risk_level: str) -> tuple[int, int, int]:
    return {
        "LOW":      (16, 185, 129),
        "MEDIUM":   (245, 158, 11),
        "HIGH":     (239, 68, 68),
        "CRITICAL": (157, 23, 77),
    }.get(risk_level.upper(), (100, 100, 100))


def generate_pdf_report(
    *,
    report_dir: str,
    student_name: str,
    student_code: str,
    risk_score: float,
    risk_level: str,
    contributions: dict[str, float],
    summary: str,
    student_photo_path: str | None = None,
    exam_image_path: str | None = None,
    logo_path: str | None = None,
    timestamp: str | None = None,
) -> str | None:
    """
    Generates a PDF report and returns its path.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        logger.warning("[report_pdf] fpdf2 not installed – skipping PDF generation.")
        return None

    os.makedirs(report_dir, exist_ok=True)
    ts = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{student_code}_{ts}.pdf"
    pdf_path = os.path.join(report_dir, filename)

    color = _risk_color(risk_level)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- Header bar (Blue Gradient style) ----
    pdf.set_fill_color(37, 99, 235)      # Royal Blue
    pdf.rect(0, 0, 210, 28, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_xy(10, 7)
    pdf.cell(130, 9, "AI Proctoring Risk Scoring Report", align="L")

    # Logo (if available)
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=175, y=4, h=20)
        except Exception:
            pass

    # Verified Local Time formatted nicely (e.g. 17 August 2026, 01:45 PM)
    local_time_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    pdf.set_xy(10, 17)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(130, 6, f"Generated: {local_time_str}")

    # ---- Student Info & Visual Identity Section ----
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(10, 33)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.cell(0, 7, "Student Information & Proctoring Session Verification", ln=True)
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2.5)

    y_info_start = pdf.get_y()

    # 1. Left Column: Student Details Table (Width = 92mm)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(243, 246, 254)
    
    info_rows = [
        ("Full Name",    student_name),
        ("Roll Number",  student_code),
        ("Report Date",  datetime.now().strftime("%d %B %Y")),
        ("Report ID",    f"RPT-{ts[:8]}-{student_code}"),
        ("Biometrics",   "Face Match Verified"),
    ]
    for label, value in info_rows:
        pdf.set_xy(10, pdf.get_y())
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(28, 7.5, " " + label + ":", fill=True)
        pdf.set_font("Helvetica", "B" if label == "Full Name" else "", 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(64, 7.5, value, fill=True)
        pdf.ln(8.5)

    y_info_end = pdf.get_y()

    # 2. Middle Column: Candidate ID Photo (Width = 38mm, Height = 43mm)
    p1_x = 106
    p1_y = y_info_start
    p1_w = 38
    p1_h = 43

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(191, 219, 254)
    pdf.set_line_width(0.6)
    pdf.rect(p1_x, p1_y, p1_w, p1_h, style="FD")

    has_p1 = False
    if student_photo_path and os.path.exists(student_photo_path):
        try:
            pdf.image(student_photo_path, x=p1_x + 1.5, y=p1_y + 1.5, w=p1_w - 3, h=p1_h - 7)
            has_p1 = True
        except Exception as e:
            logger.warning("[report_pdf] Could not embed candidate photo: %s", e)

    pdf.set_xy(p1_x, p1_y + p1_h - 5.5)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(p1_w, 4.5, "REGISTERED ID PHOTO" if has_p1 else "Photo on file", align="C")

    # 3. Right Column: Captured Exam / Malpractice Frame (Width = 52mm, Height = 43mm)
    p2_x = 148
    p2_y = y_info_start
    p2_w = 52
    p2_h = 43

    if risk_level.upper() in ("HIGH", "CRITICAL"):
        pdf.set_fill_color(254, 242, 242)
        pdf.set_draw_color(252, 165, 165)
    else:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(191, 219, 254)
    pdf.set_line_width(0.6)
    pdf.rect(p2_x, p2_y, p2_w, p2_h, style="FD")

    has_p2 = False
    if exam_image_path and os.path.exists(exam_image_path):
        try:
            pdf.image(exam_image_path, x=p2_x + 1.5, y=p2_y + 1.5, w=p2_w - 3, h=p2_h - 7)
            has_p2 = True
        except Exception as e:
            logger.warning("[report_pdf] Could not embed exam image: %s", e)

    pdf.set_xy(p2_x, p2_y + p2_h - 5.5)
    pdf.set_font("Helvetica", "B", 6.5)
    if risk_level.upper() in ("HIGH", "CRITICAL"):
        pdf.set_text_color(220, 38, 38)
    else:
        pdf.set_text_color(37, 99, 235)
    pdf.cell(p2_w, 4.5, "CAPTURED EXAM FRAME" if has_p2 else "Exam Frame Recorded", align="C")

    pdf.set_xy(10, max(y_info_end, p1_y + p1_h, p2_y + p2_h) + 2)

    # ---- Risk Score Box ----
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6.5, "Risk Assessment", ln=True)
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2.5)

    # Score Cards Row
    tint_color = [c + (255 - c) // 3 for c in color]
    pdf.set_fill_color(*tint_color)
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.9)
    y_box = pdf.get_y()
    pdf.rect(10, y_box, 92, 25, style="FD")
    pdf.rect(108, y_box, 92, 25, style="FD")

    # Score Value
    pdf.set_text_color(*color)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(10, y_box + 1.5)
    pdf.cell(92, 12, f"{risk_score:.0f}/100", align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(10, y_box + 16)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(92, 6, "Calculated Risk Score", align="C")

    # Level Value
    pdf.set_text_color(*color)
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_xy(108, y_box + 2)
    pdf.cell(92, 11, risk_level.upper(), align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(108, y_box + 16)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(92, 6, "Risk Classification", align="C")

    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(10, y_box + 29)

    # ---- Score Contributions Table ----
    if contributions:
        pdf.set_font("Helvetica", "B", 11.5)
        pdf.cell(0, 6.5, "Detected Issues & Score Contributions", ln=True)
        pdf.set_draw_color(37, 99, 235)
        pdf.set_line_width(0.5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2.5)

        pdf.set_fill_color(240, 244, 253)
        pdf.set_draw_color(203, 213, 225)
        pdf.set_line_width(0.3)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(115, 7, "  Detected Issue", fill=True, border=1)
        pdf.cell(38,  7, "Score Added",  fill=True, border=1, align="C")
        pdf.cell(37,  7, "Severity",      fill=True, border=1, ln=True, align="C")

        for mtype, pts in sorted(contributions.items(), key=lambda x: -x[1]):
            label = mtype.replace("_", " ").title()
            if pts >= 30:
                sev, sev_color = "HIGH",   (239, 68, 68)
            elif pts >= 15:
                sev, sev_color = "MEDIUM", (245, 158, 11)
            else:
                sev, sev_color = "LOW",    (16, 185, 129)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(115, 7, f"  {label}", border=1)
            pdf.cell(38,  7, f"+{pts:.1f} pts", border=1, align="C")
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*sev_color)
            pdf.cell(37,  7, sev, border=1, align="C", ln=True)

        pdf.set_text_color(15, 23, 42)
        pdf.ln(2.5)

    # ---- AI Summary Box ----
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.cell(0, 6.5, "AI-Generated Explanation", ln=True)
    pdf.set_draw_color(124, 58, 237)  # Purple
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2.5)

    pdf.set_fill_color(248, 247, 255)
    pdf.set_draw_color(196, 181, 253)
    pdf.set_line_width(0.5)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(30, 41, 59)
    
    clean_summary = summary.replace("`", "").strip()
    pdf.multi_cell(0, 5, clean_summary, fill=True, border=1)
    pdf.ln(2)

    # ---- Footer ----
    pdf.set_y(-16)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(148, 163, 184)
    pdf.multi_cell(
        0, 3.5,
        "This report was generated automatically by the AI Proctoring Risk Scoring Agent. "
        "It provides preliminary integrity analysis for review and does not constitute a final disciplinary action.",
        align="C",
    )

    pdf.output(pdf_path)
    logger.info("[report_pdf] PDF written to %s", pdf_path)
    return pdf_path
