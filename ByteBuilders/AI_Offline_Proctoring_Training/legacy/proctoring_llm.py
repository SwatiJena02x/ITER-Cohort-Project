"""LLM-backed report generation for the proctoring pipeline.

NOTE: superseded. graph/workflow.py wires in agents/report_agent.py's
report_agent (deterministic report + best-effort LLM narrative, traced
via llm/ollama_client.call_llm) instead of this module's generate_report.
This produced a narrative-only report with no deterministic section and
bypassed LangSmith tracing. Kept for reference; safe to delete.
"""

import logging
from typing import Any, Dict

from llm.ollama_client import call_llm

logger = logging.getLogger(__name__)

LLM_MODEL = "llama3.2"


def _format_list(items):
    return "\n".join(str(item) for item in items) if items else "None detected."


def _format_rules(rules):
    if not rules:
        return "No rules retrieved."
    return "\n".join(f"RULE CHUNK {r['chunk_id']}: {r['text']}" for r in rules)


def generate_report(state: Dict[str, Any]) -> str:
    """Generate the LLM-narrated proctoring report from graph state.

    Falls back to a clear placeholder message rather than raising if the
    Ollama call fails, so a temporarily unreachable/unavailable local LLM
    doesn't take down the whole pipeline run.
    """
    decision = state.get("risk_level", "UNKNOWN")
    risk_score = state.get("risk_score", 0)
    risk_reason = state.get("risk_reason", "")

    video_text = _format_list(state.get("video_evidence", []))
    audio_text = _format_list(state.get("audio_evidence", []))
    behavior_text = _format_list(state.get("behavior_evidence", []))
    rule_text = _format_rules(state.get("retrieved_rules", []))

    prompt = f"""\
You are an AI examination proctoring report assistant.

You are part of a LangGraph-based multi-agent examination proctoring system.

The system has already calculated the preliminary risk level.

You MUST NOT change the risk level.

PRELIMINARY RISK LEVEL:
{decision}

RISK SCORE:
{risk_score}

VIDEO EVIDENCE:
{video_text}

AUDIO EVIDENCE:
{audio_text}

BEHAVIOR EVIDENCE:
{behavior_text}

RISK ANALYSIS:
{risk_reason}

RETRIEVED EXAMINATION RULES:
{rule_text}

TASK:
Explain the preliminary risk assessment using ONLY the detected evidence and
retrieved examination rules.

Do not claim that cheating has been conclusively proven.

A suspicious event means that human review may be required.

The final disciplinary decision must always be made by a human reviewer.

Return exactly:

RISK LEVEL:
{decision}

RISK SCORE:
{risk_score}

EVIDENCE:
List the important detected evidence with timestamps.

RULES:
List the relevant examination rules.

REASON:
Explain why the evidence is relevant to the examination rules.

RECOMMENDATION:
State whether human review is required.

FINAL AUTHORITY:
Human reviewer.
"""

    try:
        return call_llm(prompt, model=LLM_MODEL)
    except Exception as exc:
        logger.error("Report generation failed: %s", exc, exc_info=True)
        return (
            f"RISK LEVEL:\n{decision}\n\nRISK SCORE:\n{risk_score}\n\n"
            "[AI report narrative unavailable -- please review the raw "
            "evidence and risk_reason fields in session state manually.]"
        )
