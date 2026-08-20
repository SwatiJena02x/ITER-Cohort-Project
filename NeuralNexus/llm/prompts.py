"""
llm/prompts.py
-----------------
Prompt templates used to turn structured risk-scoring evidence into a
plain-language report, plus an offline fallback so the app still produces
a usable report if no LLM backend is reachable.
"""
from langchain_core.prompts import ChatPromptTemplate

REPORT_SYSTEM_PROMPT = """\
You are an academic-integrity reporting assistant. You are given structured,
already-computed evidence about a single exam-proctoring image: which
malpractice indicators were detected, a deterministic risk score (0-100,
already calculated by rule-based logic - you must NOT change or re-derive
it), and identity-match information.

Write a concise, neutral, factual summary (4-8 sentences) for an instructor
reviewing the case. Rules:
- State the risk score and level exactly as given; do not recompute it.
- Describe only what the evidence supports - do not speculate beyond it.
- Use a professional, non-accusatory tone (this is a flag for human review,
  not a final verdict).
- If evidence is weak/ambiguous, say so explicitly and recommend manual review.
- End with one recommended next step (e.g. "recommend manual review of the
  session recording").
"""

REPORT_USER_TEMPLATE = """\
Student: {student_name} ({student_code})
Risk score: {risk_score}/100
Risk level: {risk_level}

Detected indicators and contribution to score:
{contributions_block}

Face match distance to registered profile: {face_match_distance}
Faces detected in frame: {face_count}

Write the report now.
"""

report_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", REPORT_SYSTEM_PROMPT),
        ("user", REPORT_USER_TEMPLATE),
    ]
)


def render_fallback_summary(
    *,
    student_name: str,
    student_code: str,
    risk_score: float,
    risk_level: str,
    contributions: dict[str, float],
    face_match_distance: float | None,
    face_count: int,
) -> str:
    """
    Deterministic, template-based summary used when no LLM backend is
    available. Keeps the app fully functional offline.
    """
    if contributions:
        indicator_lines = "\n".join(
            f"- {label.replace('_', ' ')}: +{points} pts" for label, points in contributions.items()
        )
    else:
        indicator_lines = "- No malpractice indicators were detected."

    match_line = (
        f"Face match distance to registered profile was {face_match_distance:.2f} "
        "(higher indicates a poorer match)."
        if face_match_distance is not None
        else "No registered profile embedding was available for identity comparison."
    )

    return (
        f"Risk report for {student_name} ({student_code}): risk score "
        f"{risk_score}/100, classified as {risk_level}.\n\n"
        f"Contributing indicators:\n{indicator_lines}\n\n"
        f"{match_line} {face_count} face(s) detected in the submitted frame.\n\n"
        "This report was generated automatically from image-based evidence and "
        "reflects a preliminary risk flag, not a final determination. "
        "Recommend manual review before any disciplinary action is taken."
    )
