"""Video evidence collection node: extracts frames and detects objects.

Belongs in the `agents` package (agents/video_agent.py). Now a traced
LangSmith span (run_type="chain") so it shows up as its own node in the
trace tree alongside the already-traced embedding/retrieval/LLM spans
deeper in the pipeline.
"""

import logging
import os
import uuid
from typing import Any, Dict, List

from langsmith import traceable

from video_processing.frame_extractor import extract_frames
from vision.object_detector import detect_objects

logger = logging.getLogger(__name__)

FRAME_FOLDER_ROOT = "data/frames"


def _make_run_frame_folder(video_path: str) -> str:
    """Build a per-invocation frame folder so concurrent/repeat runs on
    different videos don't overwrite each other's frames."""
    base = os.path.splitext(os.path.basename(video_path))[0]
    run_id = f"{base}_{uuid.uuid4().hex[:8]}"
    return os.path.join(FRAME_FOLDER_ROOT, run_id)


def _detect_objects_safe(frame_path: str) -> List[Dict[str, Any]]:
    """Run detection on a single frame; a bad frame shouldn't kill the run."""
    try:
        return detect_objects(frame_path) or []
    except Exception as exc:
        logger.warning("Object detection failed for frame %s: %s", frame_path, exc)
        return []


@traceable(name="video_agent", run_type="chain")
def video_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract frames from the exam video and detect suspicious objects.

    Per-frame detection failures are logged and skipped rather than
    aborting the whole run. A total failure to extract frames at all is
    NOT swallowed here -- without any video, there's nothing to score, so
    that error is allowed to propagate and halt the pipeline rather than
    silently producing a false "no evidence" result.
    """
    print("[video] extracting frames and detecting objects...")

    video_path = state["video_path"]
    frame_folder = _make_run_frame_folder(video_path)

    frames = extract_frames(video_path, frame_folder, interval_seconds=1)

    evidence = []

    for frame in frames:
        frame_path = frame.get("path")
        timestamp = frame.get("timestamp", 0.0)

        objects = _detect_objects_safe(frame_path)

        object_list = []
        for obj in objects:
            try:
                object_list.append(
                    {
                        "label": obj.get("label", "unknown"),
                        "score": float(obj.get("score", 0.0)),
                    }
                )
            except (TypeError, ValueError) as exc:
                logger.warning("Skipping malformed detection %r: %s", obj, exc)

        evidence.append(
            {
                "timestamp": timestamp,
                "frame": frame_path,
                "objects": object_list,
            }
        )

        # Per-frame detail is only useful when actively debugging a specific
        # run, and at 1 frame/sec a 30-minute video is 1800 log lines at
        # INFO -- that's noise, not signal. Full detail is one flag away.
        logger.debug("Timestamp: %.2fs Objects: %s", timestamp, object_list)

    hits = sum(1 for e in evidence if e["objects"])
    print(f"[video] {len(frames)} frames processed, {hits} with detected objects")

    return {
        "frames": frames,
        "video_evidence": evidence,
        "step_history": state.get("step_history", []) + ["video"],
    }
