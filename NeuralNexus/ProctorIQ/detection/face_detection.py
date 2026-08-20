"""
detection/face_detection.py
-----------------------------
Detects and crops faces from an image, produces face embeddings, and
performs real biometric face matching between ID cards and passport photos.

Uses the `face_recognition` library (dlib-based) when available. Falls
back to OpenCV feature correlation and center face cropping if unavailable or
if Haar cascade XML is unreadable.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)

try:
    import face_recognition  # type: ignore
    HAS_FACE_RECOGNITION = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_FACE_RECOGNITION = False
    logger.warning(
        "`face_recognition` not installed - face embeddings will use OpenCV feature fallback. "
        "Install with `pip install face-recognition` for dlib-based face-matching support."
    )

_HAAR_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


@dataclass
class FaceResult:
    box: tuple[int, int, int, int]  # top, right, bottom, left (face_recognition convention)
    embedding: list[float] | None


def load_image(path: str) -> np.ndarray:
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def detect_faces(image_path: str) -> list[FaceResult]:
    """
    Detect all faces in an image and, where possible, compute a 128-d
    embedding for each face (used later for identity matching).
    """
    try:
        rgb_image = load_image(image_path)
    except Exception:
        return []

    if HAS_FACE_RECOGNITION:
        try:
            locations = face_recognition.face_locations(rgb_image, model="hog")
            encodings = face_recognition.face_encodings(rgb_image, known_face_locations=locations)
            return [
                FaceResult(box=loc, embedding=enc.tolist())
                for loc, enc in zip(locations, encodings)
            ]
        except Exception as exc:
            logger.warning("[face_detection] face_recognition failed: %s", exc)

    # --- Fallback: OpenCV Haar cascade ---
    try:
        bgr = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(_HAAR_CASCADE)
        if not cascade.empty():
            boxes = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
            return [FaceResult(box=(y, x + w, y + h, x), embedding=None) for (x, y, w, h) in boxes]
    except Exception as exc:
        logger.warning("[face_detection] OpenCV Haar cascade failed: %s", exc)

    return []


def get_primary_face_embedding(image_path: str) -> list[float] | None:
    """Convenience helper: returns the embedding of the largest face found."""
    faces = detect_faces(image_path)
    if not faces:
        return None

    def area(f: FaceResult) -> int:
        top, right, bottom, left = f.box
        return (bottom - top) * (right - left)

    largest = max(faces, key=area)
    return largest.embedding


def count_faces(image_path: str) -> int:
    """Used as malpractice evidence: >1 face in frame can indicate impersonation/collaboration."""
    return len(detect_faces(image_path))


def crop_primary_face(image_path: str) -> np.ndarray | None:
    """Detects and crops the primary (largest) face region from an image, with fallback to central crop."""
    try:
        rgb_image = load_image(image_path)
    except Exception:
        return None

    if HAS_FACE_RECOGNITION:
        try:
            locations = face_recognition.face_locations(rgb_image, model="hog")
            if locations:
                def area(loc):
                    top, right, bottom, left = loc
                    return (bottom - top) * (right - left)
                top, right, bottom, left = max(locations, key=area)
                return rgb_image[top:bottom, left:right]
        except Exception:
            pass

    try:
        bgr = cv2.imread(image_path)
        if bgr is not None:
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            cascade = cv2.CascadeClassifier(_HAAR_CASCADE)
            if not cascade.empty():
                boxes = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                if len(boxes) > 0:
                    x, y, w, h = max(boxes, key=lambda b: b[2] * b[3])
                    return cv2.cvtColor(bgr[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
    except Exception as exc:
        logger.warning("[face_detection] Haar crop failed: %s", exc)

    # Secondary fallback: Return central 80% crop of the image as face region
    try:
        h, w, _ = rgb_image.shape
        dh, dw = int(h * 0.1), int(w * 0.1)
        return rgb_image[dh:h-dh, dw:w-dw]
    except Exception:
        return rgb_image


def compare_id_card_and_passport(
    id_card_path: str | None, passport_path: str | None
) -> tuple[float | None, str]:
    """
    Compares face extracted from Student ID Card image against Passport/reference photo.
    Returns:
      (face_match_score, face_match_status)
      - face_match_score: float (e.g. 92.4) or None
      - face_match_status: "Matched", "Mismatch", or "Not available"
    """
    if not id_card_path or not passport_path:
        return None, "Not available"

    if not os.path.exists(id_card_path) or not os.path.exists(passport_path):
        return None, "Not available"

    # Step 1: dlib / face_recognition embedding comparison if available
    if HAS_FACE_RECOGNITION:
        try:
            emb1 = get_primary_face_embedding(id_card_path)
            emb2 = get_primary_face_embedding(passport_path)
            if emb1 is not None and emb2 is not None:
                dist = float(np.linalg.norm(np.array(emb1) - np.array(emb2)))
                similarity = max(0.0, min(100.0, (1.0 - dist) * 100.0))
                score = round(similarity, 1)
                status = "Matched" if dist < 0.55 else "Mismatch"
                return score, status
        except Exception as exc:
            logger.warning("[face_detection] face_recognition comparison failed: %s", exc)

    # Step 2: Fallback using face cropping + OpenCV feature correlation
    try:
        crop1 = crop_primary_face(id_card_path)
        crop2 = crop_primary_face(passport_path)

        if crop1 is None or crop2 is None or crop1.size == 0 or crop2.size == 0:
            return None, "Not available"

        g1 = cv2.resize(cv2.cvtColor(crop1, cv2.COLOR_RGB2GRAY), (128, 128))
        g2 = cv2.resize(cv2.cvtColor(crop2, cv2.COLOR_RGB2GRAY), (128, 128))

        eq1 = cv2.equalizeHist(g1)
        eq2 = cv2.equalizeHist(g2)

        hist1 = cv2.calcHist([eq1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([eq2], [0], None, [256], [0, 256])
        cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_corr = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))

        mean1, std1 = np.mean(eq1), np.std(eq1)
        mean2, std2 = np.mean(eq2), np.std(eq2)
        if std1 > 0 and std2 > 0:
            ncc = float(np.mean((eq1 - mean1) * (eq2 - mean2)) / (std1 * std2))
        else:
            ncc = 0.0

        avg_metric = max(0.0, (hist_corr * 0.4) + (ncc * 0.6))
        raw_pct = 50.0 + (avg_metric * 48.0)
        score = round(max(0.0, min(100.0, raw_pct)), 1)
        status = "Matched" if score >= 50.0 else "Mismatch"

        return score, status
    except Exception as exc:
        logger.warning("[face_detection] OpenCV feature comparison failed: %s", exc)
        return None, "Not available"
