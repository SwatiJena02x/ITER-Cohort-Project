"""Utility for extracting mono 16kHz audio from a video file via ffmpeg."""

import logging
import os
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1

# Resolved once per process instead of relying on subprocess to fail.
_FFMPEG_PATH: Optional[str] = None
_FFPROBE_PATH: Optional[str] = None


def _ffmpeg_path() -> str:
    """Return the cached path to the ffmpeg executable, resolving it once."""
    global _FFMPEG_PATH
    if _FFMPEG_PATH is None:
        path = shutil.which("ffmpeg")
        if path is None:
            raise FileNotFoundError(
                "ffmpeg executable not found. Install ffmpeg and ensure it's on PATH."
            )
        _FFMPEG_PATH = path
    return _FFMPEG_PATH


def _ffprobe_path() -> Optional[str]:
    """Return the cached path to ffprobe, or None if it isn't installed.

    Unlike ffmpeg, ffprobe is treated as optional: it's only used for the
    has_audio_stream() pre-check, and its absence shouldn't block the
    pipeline -- callers fall back to just attempting extraction.
    """
    global _FFPROBE_PATH
    if _FFPROBE_PATH is None:
        _FFPROBE_PATH = shutil.which("ffprobe") or ""
    return _FFPROBE_PATH or None


def has_audio_stream(video_path: str, timeout: int = 30) -> Optional[bool]:
    """Check whether a video file contains at least one audio stream.

    This exists so audio_agent can tell "there's no audio track to
    transcribe" (expected -- not a failure) apart from "extraction or
    transcription actually broke" (a real problem worth an ERROR log). Both
    previously looked identical from the outside: audio_evidence == [].

    Returns:
        True if at least one audio stream was found.
        False if the file was probed successfully and has no audio stream.
        None if this couldn't be determined (ffprobe missing, probe failed,
            or timed out) -- callers should fall back to just attempting
            extraction and letting extract_audio's own error handling decide.
    """
    if not os.path.isfile(video_path):
        return None

    ffprobe = _ffprobe_path()
    if ffprobe is None:
        logger.debug("ffprobe not found on PATH; skipping audio-stream pre-check")
        return None

    try:
        result = subprocess.run(
            [
                ffprobe,
                "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=index",
                "-of", "csv=p=0",
                video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.debug("ffprobe audio-stream check failed for %s: %s", video_path, exc)
        return None

    if result.returncode != 0:
        logger.debug(
            "ffprobe exited %d checking %s: %s", result.returncode, video_path, result.stderr.strip()
        )
        return None

    return bool(result.stdout.strip())


def extract_audio(
    video_path: str,
    output_path: str,
    timeout: Optional[int] = DEFAULT_TIMEOUT_SECONDS,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    channels: int = DEFAULT_CHANNELS,
    audio_stream: Optional[int] = None,
    overwrite: bool = True,
) -> str:
    """Extract PCM audio from a video file using ffmpeg.

    Args:
        video_path: Path to the source video.
        output_path: Path to write the extracted .wav audio to. Parent
            directories are created if the path includes any.
        timeout: Max seconds to allow ffmpeg to run before aborting.
        sample_rate: Output sample rate in Hz (default 16000).
        channels: Number of output audio channels (default 1 / mono).
        audio_stream: Optional explicit audio stream index (e.g. 0) to pick
            when the source has multiple audio tracks. If None, ffmpeg's
            default stream-selection behavior is used.
        overwrite: If True (default), overwrite an existing output file.
            If False, ffmpeg will fail rather than clobber it.

    Returns:
        output_path, for convenience chaining.

    Raises:
        FileNotFoundError: If video_path doesn't exist, or if the ffmpeg
            executable isn't installed / on PATH.
        RuntimeError: If ffmpeg exits with a non-zero status (message
            includes ffmpeg's stderr) or times out.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    ffmpeg = _ffmpeg_path()

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    command = [ffmpeg, "-y" if overwrite else "-n", "-i", video_path]
    if audio_stream is not None:
        command += ["-map", f"0:a:{audio_stream}"]
    command += [
        "-vn",
        "-sn",  # drop subtitles too; avoids stray stream-mapping failures
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-acodec", "pcm_s16le",
        output_path,
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,  # ffmpeg writes progress to stderr, not stdout
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if result.stderr:
            logger.debug("ffmpeg output for %s: %s", video_path, result.stderr)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else "no stderr output"
        raise RuntimeError(
            f"ffmpeg failed to extract audio from {video_path} "
            f"(exit code {exc.returncode}): {stderr}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"ffmpeg timed out after {timeout}s extracting audio from {video_path}"
        ) from exc

    return output_path
