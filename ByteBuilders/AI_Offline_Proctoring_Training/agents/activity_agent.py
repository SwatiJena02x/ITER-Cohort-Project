"""Activity summarization node.

Belongs in the `agents` package (agents/activity_agent.py).

video_agent/audio_agent/behavior_agent produce raw, granular evidence:
one entry per extracted frame, one per Whisper segment, one per
externally-logged event. That's the right shape for risk_agent to score
against, but it's a bad shape to show a human or hand to an LLM -- a
30-minute exam sampled once a second is 1800 video_evidence entries, and
a report built from that is an unreadable timestamp dump.

This node runs after behavior_agent and before risk_agent and turns that
raw evidence into a handful of *activity segments*: consecutive
detections of the same suspicious object collapsed into one
start/end/peak-confidence entry, nearby speech segments merged into
continuous speech blocks, and "multiple people" flags merged into ranges.
Only suspicious/meaningful activity survives -- routine "no relevant
object detected" frames are dropped entirely.

risk_agent still scores off the raw *_evidence fields produced upstream;
this summarization is display-only (used by synthesis_agent, report_agent,
human_review_agent) and never changes the risk score.
"""

import logging
from typing import Any, Dict, List, Optional

from langsmith import traceable

logger = logging.getLogger(__name__)

SUSPICIOUS_OBJECTS = {
    "cell phone",
    "phone",
    "laptop",
    "tablet",
    "book",
    "remote",
    "keyboard",
    "mouse",
}

LOW_CONFIDENCE_THRESHOLD = 0.50

# Detections/segments this close together in time are treated as one
# continuous activity rather than two separate ones.
MAX_GAP_SECONDS = 2.0


def _summarize_video_activity(video_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collapse consecutive same-object detections into activity segments.

    Only objects in SUSPICIOUS_OBJECTS at or above LOW_CONFIDENCE_THRESHOLD
    are considered "activity" -- everything else is routine and dropped.
    """
    hits = []
    for frame in video_evidence:
        timestamp = frame.get("timestamp", 0.0)
        for obj in frame.get("objects", []):
            label = str(obj.get("label", "")).lower()
            try:
                score = float(obj.get("score", 0.0))
            except (TypeError, ValueError):
                continue
            if label in SUSPICIOUS_OBJECTS and score >= LOW_CONFIDENCE_THRESHOLD:
                hits.append((label, timestamp, score))

    hits.sort(key=lambda h: (h[0], h[1]))

    segments: List[Dict[str, Any]] = []
    open_segment: Optional[Dict[str, Any]] = None

    for label, timestamp, score in hits:
        if (
            open_segment is not None
            and open_segment["label"] == label
            and timestamp - open_segment["end"] <= MAX_GAP_SECONDS
        ):
            open_segment["end"] = timestamp
            open_segment["max_confidence"] = max(open_segment["max_confidence"], score)
            open_segment["detections"] += 1
        else:
            if open_segment is not None:
                segments.append(open_segment)
            open_segment = {
                "type": "object",
                "label": label,
                "start": timestamp,
                "end": timestamp,
                "max_confidence": score,
                "detections": 1,
            }

    if open_segment is not None:
        segments.append(open_segment)

    segments.sort(key=lambda s: s["start"])
    return segments


def _summarize_audio_activity(audio_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge nearby transcribed segments into continuous speech blocks."""
    sorted_evidence = sorted(audio_evidence, key=lambda e: e.get("start", 0.0))

    blocks: List[Dict[str, Any]] = []
    open_block: Optional[Dict[str, Any]] = None

    for seg in sorted_evidence:
        start = seg.get("start", 0.0)
        end = seg.get("end", start)
        text = (seg.get("text") or "").strip()
        if not text:
            continue

        if open_block is not None and start - open_block["end"] <= MAX_GAP_SECONDS:
            open_block["end"] = max(open_block["end"], end)
            open_block["text"] = f"{open_block['text']} {text}".strip()
        else:
            if open_block is not None:
                blocks.append(open_block)
            open_block = {"type": "speech", "start": start, "end": end, "text": text}

    if open_block is not None:
        blocks.append(open_block)

    return blocks


def _summarize_behavior_activity(behavior_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge consecutive 'multiple_people' flags into ranges; pass other events through."""
    people_hits = [e for e in behavior_evidence if e.get("type") == "multiple_people"]
    other_events = [e for e in behavior_evidence if e.get("type") != "multiple_people"]

    people_hits.sort(key=lambda e: e.get("timestamp", 0.0))

    segments: List[Dict[str, Any]] = []
    open_segment: Optional[Dict[str, Any]] = None

    for hit in people_hits:
        timestamp = hit.get("timestamp", 0.0)
        if open_segment is not None and timestamp - open_segment["end"] <= MAX_GAP_SECONDS:
            open_segment["end"] = timestamp
        else:
            if open_segment is not None:
                segments.append(open_segment)
            open_segment = {
                "type": "multiple_people",
                "start": timestamp,
                "end": timestamp,
                "description": "More than one person detected.",
            }

    if open_segment is not None:
        segments.append(open_segment)

    return other_events + segments


def format_video_activity(segments: List[Dict[str, Any]]) -> str:
    if not segments:
        return "No suspicious objects detected."
    lines = []
    for seg in segments:
        lines.append(
            f"- {seg['label']} visible {seg['start']:.1f}s-{seg['end']:.1f}s "
            f"(peak confidence {seg['max_confidence']:.2f}, {seg['detections']} detection(s))"
        )
    return "\n".join(lines)


def format_audio_activity(blocks: List[Dict[str, Any]]) -> str:
    if not blocks:
        return "No speech detected."
    lines = []
    for block in blocks:
        lines.append(f"- Speech {block['start']:.1f}s-{block['end']:.1f}s: \"{block['text']}\"")
    return "\n".join(lines)


def format_behavior_activity(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "No behavior events detected."
    lines = []
    for item in items:
        if item.get("type") == "multiple_people":
            lines.append(
                f"- Multiple people visible {item['start']:.1f}s-{item['end']:.1f}s"
            )
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def count_suspicious_video_frames(video_evidence: List[Dict[str, Any]]) -> int:
    """Count frames containing at least one suspicious object at or above
    LOW_CONFIDENCE_THRESHOLD.

    This exists so report_agent's "VIDEO EVIDENCE COUNT" can mean what it
    says -- previously it was len(video_evidence), which is just the total
    number of frames the video was sampled into, regardless of whether any
    of them contained anything suspicious. A frame with only a "person"
    detected in it (routine -- the candidate is supposed to be there)
    counted the exact same as a frame with a phone in it, which made a
    perfectly clean 17-second video's report read as "17 pieces of
    evidence".
    """
    count = 0
    for frame in video_evidence:
        for obj in frame.get("objects", []):
            label = str(obj.get("label", "")).lower()
            try:
                score = float(obj.get("score", 0.0))
            except (TypeError, ValueError):
                continue
            if label in SUSPICIOUS_OBJECTS and score >= LOW_CONFIDENCE_THRESHOLD:
                count += 1
                break  # one match is enough to count this frame once
    return count


@traceable(name="activity_agent", run_type="chain")
def activity_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Produce activity summaries from raw evidence for downstream display.

    risk_agent (which runs after this node) continues to score off the raw
    video_evidence/audio_evidence/behavior_evidence fields -- this node
    only adds new *_activity fields, it never removes or mutates the raw
    ones, so scoring is unaffected.
    """
    print("[activity] summarizing raw evidence into activity segments...")

    video_activity = _summarize_video_activity(state.get("video_evidence", []))
    audio_activity = _summarize_audio_activity(state.get("audio_evidence", []))
    behavior_activity = _summarize_behavior_activity(state.get("behavior_evidence", []))

    # Full formatted segments are debug-only -- they're what gets fed to the
    # LLM prompts downstream, not something that needs echoing to console
    # on every run. A count is enough signal here.
    logger.debug(format_video_activity(video_activity))
    logger.debug(format_audio_activity(audio_activity))
    logger.debug(format_behavior_activity(behavior_activity))
    print(
        f"[activity] {len(video_activity)} video segment(s), "
        f"{len(audio_activity)} audio block(s), {len(behavior_activity)} behavior event(s)"
    )

    return {
        "video_activity": video_activity,
        "audio_activity": audio_activity,
        "behavior_activity": behavior_activity,
        "step_history": state.get("step_history", []) + ["activity"],
    }
