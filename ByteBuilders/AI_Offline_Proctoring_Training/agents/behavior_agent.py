"""Behavior evidence node: merges external event logs with video-derived signals.

Belongs in the `agents` package (agents/behavior_agent.py). Now a traced
LangSmith span (run_type="chain").
"""

import json
import logging
import os
from typing import Any, Dict, List

from langsmith import traceable

logger = logging.getLogger(__name__)

EVENT_FILE = "data/events/events.json"

# A single isolated frame with 2+ "person" boxes is more likely to be a
# brief false detection (motion blur splitting one person into two boxes,
# someone passing behind a window for an instant) than an actual second
# person in the room. Requiring the detection to persist across at least
# this many consecutive sampled frames filters those one-frame blips out
# before they ever become a scored behavior event.
MIN_CONSECUTIVE_FRAMES = 2


def _load_external_events() -> List[Dict[str, Any]]:
    if not os.path.exists(EVENT_FILE):
        return []

    try:
        with open(EVENT_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except Exception as error:
        logger.warning("Could not read behavior events from %s: %s", EVENT_FILE, error)
        return []

    if not isinstance(events, list):
        logger.warning("Expected a list in %s, got %s; ignoring", EVENT_FILE, type(events))
        return []

    valid_events = [e for e in events if isinstance(e, dict)]
    if len(valid_events) != len(events):
        logger.warning(
            "Dropped %d malformed (non-dict) entries from %s",
            len(events) - len(valid_events),
            EVENT_FILE,
        )
    return valid_events


def _detect_multiple_people(video_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flag frames with 2+ people, but only for runs of at least
    MIN_CONSECUTIVE_FRAMES consecutive sampled frames.

    video_evidence is already in chronological frame order (video_agent
    appends one entry per extracted frame, in extraction order), so
    "consecutive" here means adjacent entries in this list -- not a raw
    timestamp gap check, since frames are already evenly sampled.
    """
    flags: List[Dict[str, Any]] = []
    run: List[Dict[str, Any]] = []

    def flush_run() -> None:
        if len(run) >= MIN_CONSECUTIVE_FRAMES:
            for evidence in run:
                flags.append(
                    {
                        "type": "multiple_people",
                        "timestamp": evidence.get("timestamp", 0.0),
                        "description": "More than one person detected.",
                    }
                )
        run.clear()

    for evidence in video_evidence:
        objects = evidence.get("objects", [])
        people = [obj for obj in objects if obj.get("label", "").lower() == "person"]

        if len(people) > 1:
            run.append(evidence)
        else:
            flush_run()

    flush_run()  # handle a run that extends to the very last frame

    return flags


@traceable(name="behavior_agent", run_type="chain")
def behavior_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Combine externally-logged events with multi-person detection from video."""
    print("[behavior] merging event logs with video-derived signals...")

    behavior_evidence = _load_external_events()
    behavior_evidence.extend(_detect_multiple_people(state.get("video_evidence", [])))

    # Full event-by-event detail is debug-only; the count is what's useful
    # at a glance, the detail is what agents.activity_agent condenses next.
    for item in behavior_evidence:
        logger.debug(item)
    print(f"[behavior] {len(behavior_evidence)} behavior events")

    return {
        "behavior_evidence": behavior_evidence,
        "step_history": state.get("step_history", []) + ["behavior"],
    }
