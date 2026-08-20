"""
detection/eye_movement.py
---------------------------
Detects eye gaze direction (looking away from screen) using facial landmarks.

Strategy (with graceful fallbacks):
  1. Try MediaPipe Face Mesh (best accuracy, optional dependency)
  2. Fall back to OpenCV + dlib facial landmarks if MediaPipe unavailable
  3. Final fallback: return a "cannot determine" result so the pipeline
     never hard-fails on a missing dependency

Returns a dict: { "looking_away": bool, "direction": str, "confidence": float }
"""
from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _estimate_gaze_ratio(
    eye_region: np.ndarray, threshold: float = 0.3
) -> tuple[float, str]:
    """
    Simple iris position estimator based on pixel intensity within the eye region.
    White sclera pixels are lighter than the iris/pupil.
    Returns (gaze_ratio, direction_hint).
    """
    gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY) if len(eye_region.shape) == 3 else eye_region
    _, threshold_eye = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    h, w = threshold_eye.shape
    if w == 0 or h == 0:
        return 0.5, "center"
    left_side  = threshold_eye[:, : w // 2]
    right_side = threshold_eye[:, w // 2 :]
    left_white  = cv2.countNonZero(left_side)
    right_white = cv2.countNonZero(right_side)
    total = left_white + right_white
    if total == 0:
        return 0.5, "center"
    ratio = left_white / total  # high ratio → pupil is on the right side → looking left
    if ratio < 0.3:
        return 1.0 - ratio, "right"
    elif ratio > 0.7:
        return ratio, "left"
    else:
        return 0.1, "center"


def detect_gaze_opencv(image_path: str) -> dict:
    """
    OpenCV Haar-cascade based gaze detection (fallback).
    Detects faces + eye regions, estimates if student is looking away.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"looking_away": False, "direction": "unknown", "confidence": 0.0}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
    if len(faces) == 0:
        return {"looking_away": False, "direction": "unknown", "confidence": 0.0}

    # Process the largest face
    x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
    face_gray = gray[y: y + h, x: x + w]
    face_img  = img[y: y + h, x: x + w]
    eyes = eye_cascade.detectMultiScale(face_gray, 1.1, 10, minSize=(20, 20))

    gaze_ratios = []
    direction = "center"
    for (ex, ey, ew, eh) in eyes[:2]:
        eye_img = face_img[ey: ey + eh, ex: ex + ew]
        ratio, dir_hint = _estimate_gaze_ratio(eye_img)
        gaze_ratios.append(ratio)
        direction = dir_hint

    if not gaze_ratios:
        return {"looking_away": False, "direction": "center", "confidence": 0.1}

    avg_ratio = float(np.mean(gaze_ratios))
    looking_away = avg_ratio > 0.65
    confidence = min(1.0, avg_ratio)

    return {
        "looking_away": looking_away,
        "direction": direction,
        "confidence": round(confidence, 3),
    }


def detect_gaze_mediapipe(image_path: str) -> dict:
    """
    MediaPipe Face Mesh based gaze detection (preferred).
    Uses 3D iris landmarks for accurate gaze estimation.
    """
    import mediapipe as mp

    mp_face = mp.solutions.face_mesh
    img = cv2.imread(image_path)
    if img is None:
        return {"looking_away": False, "direction": "unknown", "confidence": 0.0}

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    with mp_face.FaceMesh(static_image_mode=True, max_num_faces=1,
                          refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return {"looking_away": False, "direction": "unknown", "confidence": 0.0}

    lm = results.multi_face_landmarks[0].landmark

    # Iris centres (MediaPipe landmark indices)
    LEFT_IRIS_CENTER  = 468
    RIGHT_IRIS_CENTER = 473
    # Eye corners
    LEFT_EYE_LEFT   = 33;   LEFT_EYE_RIGHT  = 133
    RIGHT_EYE_LEFT  = 362;  RIGHT_EYE_RIGHT = 263

    def lm_xy(idx):
        return np.array([lm[idx].x * w, lm[idx].y * h])

    l_iris = lm_xy(LEFT_IRIS_CENTER)
    l_corner_l = lm_xy(LEFT_EYE_LEFT);   l_corner_r = lm_xy(LEFT_EYE_RIGHT)
    r_iris = lm_xy(RIGHT_IRIS_CENTER)
    r_corner_l = lm_xy(RIGHT_EYE_LEFT);  r_corner_r = lm_xy(RIGHT_EYE_RIGHT)

    def gaze_ratio_1d(iris_x, corner_l_x, corner_r_x):
        eye_width = abs(corner_r_x - corner_l_x)
        if eye_width < 1:
            return 0.5
        return (iris_x - min(corner_l_x, corner_r_x)) / eye_width

    l_ratio = gaze_ratio_1d(l_iris[0], l_corner_l[0], l_corner_r[0])
    r_ratio = gaze_ratio_1d(r_iris[0], r_corner_l[0], r_corner_r[0])
    avg = (l_ratio + r_ratio) / 2.0

    if avg < 0.35:
        direction = "left"
        confidence = 1.0 - avg
        looking_away = True
    elif avg > 0.65:
        direction = "right"
        confidence = avg
        looking_away = True
    else:
        direction = "center"
        confidence = 0.1
        looking_away = False

    return {
        "looking_away": looking_away,
        "direction": direction,
        "confidence": round(float(confidence), 3),
    }


def detect_gaze(image_path: str) -> dict:
    """
    Main entry point. Tries MediaPipe first, falls back to OpenCV.
    Returns: { "looking_away": bool, "direction": str, "confidence": float }
    """
    try:
        return detect_gaze_mediapipe(image_path)
    except (ImportError, AttributeError):
        logger.info("[eye_movement] mediapipe unavailable; using OpenCV fallback")
        return detect_gaze_opencv(image_path)
    except Exception as exc:
        logger.warning("[eye_movement] gaze detection failed: %s", exc)
        return {"looking_away": False, "direction": "unknown", "confidence": 0.0}
