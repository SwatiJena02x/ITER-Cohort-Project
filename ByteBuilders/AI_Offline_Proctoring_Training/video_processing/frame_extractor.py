import logging
import os

import cv2

logger = logging.getLogger(__name__)

DEFAULT_JPEG_QUALITY = 90


def extract_frames(
    video_path,
    output_folder,
    interval_seconds=1,
    jpeg_quality=DEFAULT_JPEG_QUALITY,
):
    """Extract frames from a video at a fixed time interval.

    Args:
        video_path: Path to the source video.
        output_folder: Directory to write extracted JPEG frames to.
        interval_seconds: Approximate seconds between extracted frames.
        jpeg_quality: JPEG encode quality (0-100, higher = larger/better).

    Returns:
        List of dicts: [{"path": ..., "timestamp": ...}, ...]

    Raises:
        FileNotFoundError: If video_path doesn't exist.
        RuntimeError: If the video can't be opened.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    saved_frames = []

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(
            "Video info: fps=%.2f, total_frames=%d, duration=%.2fs",
            fps, total_frames, duration,
        )

        frame_interval = max(1, int(fps * interval_seconds)) if fps > 0 else 1
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]

        frame_number = 0
        while True:
            # Skip undecoded frames with grab() (cheap) instead of read()
            # (grab + decode) when we don't need them -- decoding is the
            # expensive part, so this avoids wasted work on skipped frames.
            if frame_number % frame_interval != 0:
                if not cap.grab():
                    break
                frame_number += 1
                continue

            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_number / fps if fps > 0 else 0
            filename = f"frame_{len(saved_frames):06d}.jpg"
            path = os.path.join(output_folder, filename)

            cv2.imwrite(path, frame, encode_params)

            saved_frames.append({"path": path, "timestamp": timestamp})
            frame_number += 1
    finally:
        cap.release()

    logger.info("Frames extracted: %d", len(saved_frames))

    return saved_frames
