"""
detection/talking_detection.py
--------------------------------
Detects whether the student is talking (mouth open) during examination.

Strategy:
  1. MediaPipe Face Mesh: compute Mouth Aspect Ratio (MAR) from 3D landmarks
  2. OpenCV Haar cascade fallback: detect mouth region, estimate openness

MAR = vertical_mouth_opening / horizontal_mouth_width
 - MAR > threshold (~0.3) → mouth is open → possible talking
"""
from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)

MAR_THRESHOLD = 0.30  # Above this → mouth considered open / talking


def _mar_mediapipe(image_path: str) -> dict:
    """MediaPipe Face Mesh based Mouth Aspect Ratio detection."""
    import mediapipe as mp

    mp_face = mp.solutions.face_mesh
    img = cv2.imread(image_path)
    if img is None:
        return {"talking": False, "confidence": 0.0, "mar": 0.0}

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    with mp_face.FaceMesh(
        static_image_mode=True, max_num_faces=1,
        refine_landmarks=False, min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return {"talking": False, "confidence": 0.0, "mar": 0.0}

    lm = results.multi_face_landmarks[0].landmark

    def pt(idx):
        return np.array([lm[idx].x * w, lm[idx].y * h])

    # MediaPipe mouth landmarks (outer lip)
    # Horizontal: corners  13 (left) and 14 (right) — these are inner lip
    # Vertical top/bottom: 0 (upper lip centre) and 17 (lower lip centre)
    # Using standard LIPS landmarks
    upper = pt(13)   # upper inner lip centre
    lower = pt(14)   # lower inner lip centre
    left  = pt(61)   # left mouth corner
    right = pt(291)  # right mouth corner

    vertical   = float(np.linalg.norm(upper - lower))
    horizontal = float(np.linalg.norm(left - right))

    mar = vertical / horizontal if horizontal > 0 else 0.0
    talking = mar > MAR_THRESHOLD
    confidence = min(1.0, mar / MAR_THRESHOLD) if mar > 0 else 0.0

    return {
        "talking": talking,
        "confidence": round(float(confidence), 3),
        "mar": round(mar, 4),
    }


def _mar_opencv(image_path: str) -> dict:
    """OpenCV Haar cascade fallback for talking detection."""
    img = cv2.imread(image_path)
    if img is None:
        return {"talking": False, "confidence": 0.0, "mar": 0.0}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    mouth_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_smile.xml"
    )

    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
    if len(faces) == 0:
        return {"talking": False, "confidence": 0.0, "mar": 0.0}

    x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
    # Look for open mouth in the lower half of the face
    lower_face = gray[y + h // 2: y + h, x: x + w]
    mouths = mouth_cascade.detectMultiScale(
        lower_face, 1.5, 11, minSize=(25, 15), maxSize=(200, 100)
    )

    if len(mouths) > 0:
        # Smile/open-mouth detected → likely talking
        mx, my, mw, mh = mouths[0]
        mar = mh / mw if mw > 0 else 0.0
        confidence = min(1.0, max(0.4, mar / 0.5))
        return {"talking": True, "confidence": round(float(confidence), 3), "mar": round(mar, 4)}

    return {"talking": False, "confidence": 0.05, "mar": 0.0}


def detect_talking(image_path: str) -> dict:
    """
    Main entry point. Tries MediaPipe first, falls back to OpenCV.
    Returns: { "talking": bool, "confidence": float, "mar": float }
    """
    try:
        return _mar_mediapipe(image_path)
    except (ImportError, AttributeError):
        logger.info("[talking_detection] mediapipe unavailable; using OpenCV fallback")
        return _mar_opencv(image_path)
    except Exception as exc:
        logger.warning("[talking_detection] detection failed: %s", exc)
        return {"talking": False, "confidence": 0.0, "mar": 0.0}
