"""Risk scoring node: turns activity-level evidence into a numeric risk score and level.

Belongs in the `agents` package (agents/risk_agent.py).

CHANGED: scores off video_activity/audio_activity/behavior_activity (the
merged segments agents.activity_agent produces, and the exact same data
synthesis_agent/report_agent/human_review_agent display to a human
reader) instead of raw per-frame video_evidence / per-segment
audio_evidence / per-event behavior_evidence.

Why: scoring off raw evidence could silently disagree with what the
report actually showed. Two concrete ways that happened before this
change:
  1. A single continuous sighting spanning many seconds is one segment
     in the display, but was many separate raw per-frame hits when
     scored -- so a long sighting scored far higher than its single
     displayed segment would suggest.
  2. Several seconds of continuous speech could get merged into ONE
     audio_activity block for display, but scored as however many raw
     Whisper segments happened to make it up (sometimes just one) --
     so speech clearly visible in the report could contribute far less
     to the score than a reader would expect from seeing it there.
Either direction, a reviewer looking at the report had no way to
reconstruct the score from what they were actually looking at. Now:
one video segment = one scored item (weighted by its peak confidence),
one audio block = one scored item, one behavior event = one scored
item -- the score is always explainable by counting exactly what the
report shows.

This also removes the SUSPICIOUS_OBJECTS / LOW_CONFIDENCE_THRESHOLD
duplication that used to exist between this file and activity_agent.py:
video_activity segments are already filtered to suspicious objects at or
above LOW_CONFIDENCE_THRESHOLD by activity_agent itself (nothing below
that bar ever becomes a segment), so risk_agent no longer needs its own
copy of that filtering logic -- it only needs the extra HIGH/LOW split
below, for weighting *how many* points an already-qualifying segment is
worth.

Now a traced LangSmith span (run_type="chain"). As soon as risk_level is
known, this node tags its own run with the risk_level and a
"HIGH-RISK-ALERT" marker when applicable (via llm.langsmith_utils), so a
HIGH session is filterable/alertable on directly from the risk_agent span
-- not only after the whole graph finishes, which is when main.py tags
the root run.
"""

import logging
from typing import Any, Dict, List

from langsmith import traceable

from llm.langsmith_utils import log_current_run_metadata, tag_current_run

logger = logging.getLogger(__name__)

# video_activity segments are already confidence- and object-filtered by
# activity_agent (see module docstring) -- this is only the extra split
# used to weight an already-qualifying segment's point value.
HIGH_CONFIDENCE_THRESHOLD = 0.80
HIGH_CONFIDENCE_POINTS = 4
LOW_CONFIDENCE_POINTS = 2

POINTS_PER_AUDIO_EVENT = 2
POINTS_PER_BEHAVIOR_EVENT = 3

RISK_LEVEL_HIGH_THRESHOLD = 10
RISK_LEVEL_MEDIUM_THRESHOLD = 5


def _score_video_activity(video_activity: List[Dict[str, Any]], reasons: List[str]) -> int:
    score = 0
    for seg in video_activity:
        confidence = seg.get("max_confidence", 0.0)
        label = seg.get("label", "unknown")
        start = seg.get("start", 0.0)
        end = seg.get("end", 0.0)

        points = HIGH_CONFIDENCE_POINTS if confidence >= HIGH_CONFIDENCE_THRESHOLD else LOW_CONFIDENCE_POINTS
        score += points

        reasons.append(
            f"{label} visible {start:.2f}s-{end:.2f}s "
            f"(peak confidence {confidence:.2f}, {points} pts)"
        )
    return score


def _score_audio_activity(audio_activity: List[Dict[str, Any]], reasons: List[str]) -> int:
    score = 0
    for block in audio_activity:
        score += POINTS_PER_AUDIO_EVENT
        reasons.append(
            f"Speech {block.get('start', 0.0):.2f}s-{block.get('end', 0.0):.2f}s "
            f"({POINTS_PER_AUDIO_EVENT} pts)"
        )
    return score


def _score_behavior_activity(behavior_activity: List[Dict[str, Any]], reasons: List[str]) -> int:
    score = 0
    for item in behavior_activity:
        score += POINTS_PER_BEHAVIOR_EVENT
        description = item.get("description") or item.get("type", "behavior event")
        reasons.append(f"{description} ({POINTS_PER_BEHAVIOR_EVENT} pts)")
    return score


@traceable(name="risk_agent", run_type="chain")
def risk_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a numeric risk score and LOW/MEDIUM/HIGH level from activity.

    Runs after activity_agent in the graph (video -> audio -> behavior ->
    activity -> risk -> ...), specifically so this node always has
    video_activity/audio_activity/behavior_activity available to score
    against.
    """
    print("[risk] scoring evidence...")

    reasons: List[str] = []

    video_activity = state.get("video_activity", [])
    audio_activity = state.get("audio_activity", [])
    behavior_activity = state.get("behavior_activity", [])

    score = _score_video_activity(video_activity, reasons)
    score += _score_audio_activity(audio_activity, reasons)
    score += _score_behavior_activity(behavior_activity, reasons)

    if score >= RISK_LEVEL_HIGH_THRESHOLD:
        risk_level = "HIGH"
    elif score >= RISK_LEVEL_MEDIUM_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    reason = "\n".join(reasons)

    # Tag/annotate this node's LangSmith span immediately, so HIGH-risk
    # sessions are filterable/alertable on from the risk_agent span itself,
    # not only after the graph finishes (see main.py's root-run tagging).
    tag_current_run(f"risk-{risk_level}")
    if risk_level == "HIGH":
        tag_current_run("HIGH-RISK-ALERT")
    log_current_run_metadata(risk_score=score, risk_level=risk_level)

    logger.debug("Reason: %s", reason)
    print(f"[risk] score={score} level={risk_level}")

    return {
        "risk_score": float(score),
        "risk_level": risk_level,
        "risk_reason": reason,
        "step_history": state.get("step_history", []) + ["risk"],
    }
