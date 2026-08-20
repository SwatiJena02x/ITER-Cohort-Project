"""Report generation node: combines a deterministic decision with an
optional LLM narrative.

Belongs in the `agents` package (agents/report_agent.py).

The deterministic report (decision, counts, reason) is always produced --
it has no external dependency and cannot fail. An LLM-generated narrative
is appended on a best-effort basis to add explanatory detail; if the LLM
call fails for any reason, the deterministic report is unaffected and a
placeholder note takes the narrative's place.

The narrative is built from video_activity/audio_activity/behavior_activity
(produced upstream by agents.activity_agent) rather than raw
video_evidence/audio_evidence/behavior_evidence, so the report reads as a
handful of meaningful activity segments instead of a per-second timestamp
dump. The deterministic section's EVIDENCE COUNT fields still report
total detection counts from the raw evidence, since a count is a single
number, not a timestamp dump, and is useful context on its own.

The LLM call goes through llm.ollama_client.call_llm (rather than calling
ollama.chat() directly) so it gets its own LangSmith span -- prompt,
response, model, latency -- instead of only the enclosing LangGraph node
being visible in traces. report_agent itself is also a traced span.
"""

import logging
from typing import Any, Dict, List

from langsmith import traceable

from agents.activity_agent import (
    count_suspicious_video_frames,
    format_audio_activity,
    format_behavior_activity,
    format_video_activity,
)
from llm.ollama_client import call_llm

logger = logging.getLogger(__name__)

LLM_MODEL = "llama3.2"
LLM_OPTIONS = {"temperature": 0.2}


def _format_rules(rules: List[Dict[str, Any]]) -> str:
    # Each retrieved chunk already carries its own real "RULE N:" label
    # (rag.exam_rules.split_into_rule_chunks splits on those markers) --
    # don't re-prefix with chunk_id, which is just the chunk's FAISS index
    # position and not a real rule number (see synthesis_agent._format_context
    # for the bug this previously caused: a fabricated "RULE 0" label).
    if not rules:
        return "No rules retrieved."
    return "\n\n".join(r.get("text", "") for r in rules)


def _build_deterministic_report(state: Dict[str, Any]) -> Dict[str, str]:
    """Compute the always-available decision report. Cannot fail."""
    risk_level = state.get("risk_level", "UNKNOWN")
    risk_score = state.get("risk_score", 0)

    # count_suspicious_video_frames only counts frames containing an
    # actual suspicious object (phone, book, etc.) -- NOT the total number
    # of frames processed. A clean video with 17 frames and zero
    # suspicious objects now correctly reports 0 here, not 17.
    video_count = count_suspicious_video_frames(state.get("video_evidence", []))
    audio_count = len(state.get("audio_evidence", []))
    behavior_count = len(state.get("behavior_evidence", []))

    if risk_level == "LOW":
        decision = "CLEARED"
        reason = "No significant suspicious evidence was detected."
    elif risk_level in ("MEDIUM", "HIGH"):
        decision = "REQUIRES HUMAN REVIEW"
        reason = "Suspicious evidence was detected and requires human inspection."
    else:
        # Missing/unrecognized risk_level: fail safe rather than silently CLEARED.
        decision = "REQUIRES HUMAN REVIEW"
        reason = f"Risk level could not be determined (got {risk_level!r}); flagged for manual review."

    report = f"""\
EXAMINATION PROCTORING REPORT

DECISION:
{decision}

RISK LEVEL:
{risk_level}

RISK SCORE:
{risk_score}

VIDEO EVIDENCE COUNT (frames with a suspicious object):
{video_count}

AUDIO EVIDENCE COUNT:
{audio_count}

BEHAVIOR EVIDENCE COUNT:
{behavior_count}

REASON:
{reason}

FINAL AUTHORITY:
Human reviewer.
"""
    return {"report": report, "decision": decision}


def _build_narrative_prompt(state: Dict[str, Any], decision: str) -> str:
    risk_level = state.get("risk_level", "UNKNOWN")
    risk_score = state.get("risk_score", 0)
    risk_reason = state.get("risk_reason", "")

    video_text = format_video_activity(state.get("video_activity", []))
    audio_text = format_audio_activity(state.get("audio_activity", []))
    behavior_text = format_behavior_activity(state.get("behavior_activity", []))
    rule_text = _format_rules(state.get("retrieved_rules", []))

    return f"""\
You are an AI examination proctoring report assistant.

You are part of a LangGraph-based multi-agent examination proctoring system.

The system has already calculated the preliminary risk level and decision.
You MUST NOT change either of them.

DECISION:
{decision}

PRELIMINARY RISK LEVEL:
{risk_level}

RISK SCORE:
{risk_score}

VIDEO ACTIVITY:
{video_text}

AUDIO ACTIVITY:
{audio_text}

BEHAVIOR ACTIVITY:
{behavior_text}

RISK ANALYSIS:
{risk_reason}

RETRIEVED EXAMINATION RULES:
{rule_text}

TASK:
Explain the preliminary risk assessment using ONLY the detected activity
and retrieved examination rules. Do not claim that cheating has been
conclusively proven. The final disciplinary decision must always be made
by a human reviewer.

Be concise: under 120 words total. State each fact once -- do not repeat
the decision, risk level, or any activity item more than once across
sections.

Return exactly:

ACTIVITY:
Important detected activity with time ranges, one line per item.

RULES:
Relevant examination rules, by number only.

REASON:
1-2 sentences connecting activity to rules. Do not restate the activity
or rules list here.
"""


def _generate_narrative(state: Dict[str, Any], decision: str) -> str:
    """Best-effort LLM narrative. Never raises."""
    try:
        prompt = _build_narrative_prompt(state, decision)
        return call_llm(prompt, model=LLM_MODEL, options=LLM_OPTIONS)
    except Exception as exc:
        logger.error("Report narrative generation failed: %s", exc, exc_info=True)
        return (
            "[AI narrative unavailable -- the deterministic decision above is "
            "still valid. Please review the raw evidence sections manually.]"
        )


@traceable(name="report_agent", run_type="chain")
def report_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: builds the combined report and updates graph state."""
    print("[report] building final report...")

    deterministic = _build_deterministic_report(state)
    narrative = _generate_narrative(state, deterministic["decision"])

    full_report = f"{deterministic['report']}\nAI NARRATIVE:\n{narrative}\n"

    # This is the actual deliverable, not debug noise -- but main.py already
    # prints it once in the FINAL OUTPUT section at the end of the run, so
    # printing it again here would just be a duplicate.
    logger.debug(full_report)

    return {
        "final_report": full_report,
        "step_history": state.get("step_history", []) + ["report"],
    }
