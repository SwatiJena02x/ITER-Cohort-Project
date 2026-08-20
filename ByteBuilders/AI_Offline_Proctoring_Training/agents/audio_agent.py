"""Audio evidence collection node: transcribes exam audio via Whisper.

Belongs in the `agents` package (agents/audio_agent.py). Now a traced
LangSmith span (run_type="chain").
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import whisper
from langsmith import traceable

from audio.audio_extractor import extract_audio, has_audio_stream

logger = logging.getLogger(__name__)

MODEL = "base"
AUDIO_FOLDER_ROOT = "data/audio"

# Lazily-loaded, process-wide singleton -- avoids paying model-load cost at
# import time and lets us pick a real device instead of hardcoding "cuda"
# (which crashes outright on any machine without an NVIDIA GPU).
_model = None


def _select_device() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def get_model():
    global _model
    if _model is None:
        device = _select_device()
        logger.info("Loading Whisper model '%s' on %s", MODEL, device)
        _model = whisper.load_model(MODEL, device=device)
    return _model


def _make_run_audio_path(video_path: str) -> str:
    base = os.path.splitext(os.path.basename(video_path))[0]
    run_id = f"{base}_{uuid.uuid4().hex[:8]}"
    return os.path.join(AUDIO_FOLDER_ROOT, f"{run_id}.wav")


@traceable(name="audio_agent", run_type="chain")
def audio_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and transcribe audio, returning timestamped evidence.

    Audio issues (extraction failure, no audio track, transcription
    failure) are treated as non-fatal: they're logged and the agent
    returns empty audio_evidence rather than aborting the whole pipeline,
    since video evidence is the primary signal and a session shouldn't be
    lost just because its audio track is unusable.

    audio_evidence == [] can mean three different things, which previously
    all looked identical from the outside. This now distinguishes them
    with a specific console line + log reason each time the result is
    empty, instead of a silent "0 speech segments":
      1. The source video has no audio track at all (checked up front via
         has_audio_stream) -- expected, not a problem.
      2. Extraction or transcription raised an exception -- a real
         failure, logged at ERROR with the traceback.
      3. There IS audio and transcription succeeded, but Whisper found no
         speech (silence/noise-only) -- expected, not a problem, but
         distinct from case 1 so you know the audio track was read.
    """
    print("[audio] extracting and transcribing audio...")

    video_path = state["video_path"]
    audio_path = _make_run_audio_path(video_path)

    audio_evidence: List[Dict[str, Any]] = []

    # Case 1: no audio track present. Skip extraction/transcription
    # entirely rather than let ffmpeg fail and log it as an error.
    audio_present = has_audio_stream(video_path)
    if audio_present is False:
        logger.info("No audio stream detected in %s -- skipping transcription", video_path)
        print("[audio] 0 speech segments transcribed (source video has no audio track)")
        return {
            "audio_evidence": audio_evidence,
            "step_history": state.get("step_history", []) + ["audio"],
        }
    # audio_present is None -> ffprobe unavailable/inconclusive; fall
    # through and let extraction itself determine what's actually there.

    # Case 2: extraction or transcription genuinely failed.
    try:
        extract_audio(video_path, audio_path)
        model = get_model()
        result = model.transcribe(audio_path, fp16=False)
    except Exception as exc:
        logger.error("Audio extraction/transcription failed: %s", exc, exc_info=True)
        print("[audio] 0 speech segments transcribed (extraction/transcription failed -- see log)")
        return {
            "audio_evidence": audio_evidence,
            "step_history": state.get("step_history", []) + ["audio"],
        }

    segments = result.get("segments", [])

    for segment in segments:
        text = (segment.get("text") or "").strip()
        if not text:
            continue

        start = segment.get("start", 0.0)
        end = segment.get("end", 0.0)

        audio_evidence.append({"start": start, "end": end, "text": text})
        # Per-segment detail is debug-only -- see video_agent for the same
        # reasoning; a long exam can have dozens of transcribed segments.
        logger.debug("%.2fs - %.2fs: %s", start, end, text)

    # Case 3: audio was read and transcribed fine, Whisper just found no speech.
    if not audio_evidence:
        logger.info(
            "Audio track present and transcribed (%d raw segment(s)) but no "
            "speech detected in %s",
            len(segments),
            video_path,
        )
        print("[audio] 0 speech segments transcribed (audio present, but silent/no speech detected)")
    else:
        print(f"[audio] {len(audio_evidence)} speech segments transcribed")

    return {
        "audio_evidence": audio_evidence,
        "step_history": state.get("step_history", []) + ["audio"],
    }
