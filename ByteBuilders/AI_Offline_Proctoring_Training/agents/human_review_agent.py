"""Human review node: prepares a concise recommendation for the human reviewer.

Belongs in the `agents` package (agents/human_review_agent.py). Now built
from video_activity/audio_activity/behavior_activity (produced upstream by
agents.activity_agent) instead of raw per-timestamp evidence, and is
itself a traced LangSmith span.
"""

import logging
from typing import Any, Dict, List

from langsmith import traceable

from agents.activity_agent import (
    format_audio_activity,
    format_behavior_activity,
    format_video_activity,
)
from llm.ollama_client import call_llm

logger = logging.getLogger(__name__)

LLM_MODEL = "llama3.2"
LLM_OPTIONS = {"temperature": 0.2}


def _format_rules(rules: List[Dict[str, Any]]) -> str:
    if not rules:
        return "No rules retrieved."
    return "\n".join(r.get("text", "") for r in rules)


def _fallback_review(state: Dict[str, Any], error: Exception) -> str:
    risk_level = state.get("risk_level", "UNKNOWN")
    return f"""\
REVIEW PRIORITY:
{risk_level if risk_level in ("LOW", "MEDIUM", "HIGH") else "HIGH"}

KEY EVIDENCE:
AI summary unavailable ({error}). Please inspect video_activity, \
audio_activity, and behavior_activity directly for this session.

RELEVANT RULES:
See retrieved_rules in session state.

RECOMMENDATION:
Manual review required; automated summarization failed.

FINAL AUTHORITY:
Human reviewer.
"""


@traceable(name="human_review_agent", run_type="chain")
def human_review_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a concise, activity-grounded recommendation for the reviewer."""
    print("[human_review] preparing reviewer recommendation...")

    rules = state.get("retrieved_rules", [])
    rule_text = _format_rules(rules)

    risk_score = state.get("risk_score", "UNKNOWN")
    risk_level = state.get("risk_level", "UNKNOWN")

    video_text = format_video_activity(state.get("video_activity", []))
    audio_text = format_audio_activity(state.get("audio_activity", []))
    behavior_text = format_behavior_activity(state.get("behavior_activity", []))

    prompt = f"""\
You are an examination human-review assistant.

You are NOT the final decision maker. The final authority is always a
human reviewer.

Risk score:
{risk_score}

Risk level:
{risk_level}

Video activity:
{video_text}

Audio activity:
{audio_text}

Behavior activity:
{behavior_text}

Retrieved rules:
{rule_text}

Risk analysis:
{state.get("risk_reason", "")}

Prepare a concise recommendation for the human reviewer.

Do not claim cheating is conclusively proven.

Be concise: under 100 words total. State each fact once -- do not repeat
the risk level or any piece of evidence across sections.

Return:

REVIEW PRIORITY:
LOW / MEDIUM / HIGH

KEY EVIDENCE:
Important activity, one line per item.

RELEVANT RULES:
Relevant rules, by number only.

RECOMMENDATION:
1 sentence on what the human reviewer should inspect.

FINAL AUTHORITY:
Human reviewer.
"""

    try:
        review = call_llm(prompt, model=LLM_MODEL, options=LLM_OPTIONS)
    except Exception as exc:
        logger.error("Human review generation failed: %s", exc, exc_info=True)
        review = _fallback_review(state, exc)

    # Printed once in main.py's FINAL OUTPUT section -- no need to duplicate
    # it here.
    logger.debug(review)

    return {
        "human_review": review,
        "step_history": state.get("step_history", []) + ["human_review"],
    }
