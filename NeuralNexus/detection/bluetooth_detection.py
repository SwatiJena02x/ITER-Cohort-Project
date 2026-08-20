"""
detection/bluetooth_detection.py
----------------------------------
Detects wireless bluetooth earbuds, in-ear earpieces, and ear-region
malpractice gestures (such as holding a phone or hand over the ear).

Uses facial landmarks (from `face_recognition`) to locate left and right
ear regions of interest (ROIs) and analyze image features / anomalies.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EarbudDetection:
    label: str
    malpractice_type: str
    confidence: float
    box: tuple[float, float, float, float]  # x1, y1, x2, y2


def detect_bluetooth_and_earbuds(
    image_path: str, detected_boxes: list[tuple[float, float, float, float]] | None = None
) -> list[EarbudDetection]:
    """
    Analyzes an image for bluetooth earbuds, earpieces, and hand-to-ear gestures.
    """
    try:
        import face_recognition
    except ImportError:
        logger.warning("`face_recognition` not available for earbud detection.")
        return []

    image = cv2.imread(image_path)
    if image is None:
        return []

    h, w, _ = image.shape
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    landmarks_list = face_recognition.face_landmarks(rgb_image)
    if not landmarks_list:
        return []

    results: list[EarbudDetection] = []

    for landmarks in landmarks_list:
        chin = landmarks.get("chin", [])
        left_eye = landmarks.get("left_eye", [])
        right_eye = landmarks.get("right_eye", [])

        if not chin or not left_eye or not right_eye:
            continue

        # Approximate ear coordinates from facial landmarks
        # Left ear: near chin index 0-3 and left_eye outer corner
        # Right ear: near chin index 13-16 and right_eye outer corner
        chin_left = np.array(chin[0])
        chin_right = np.array(chin[-1])
        eye_left = np.array(left_eye[0])
        eye_right = np.array(right_eye[-1])

        # Define Left Ear ROI: [x1, y1, x2, y2]
        ear_w = int(abs(eye_left[0] - chin_left[0]) * 0.8) + 15
        ear_h = int(abs(chin_left[1] - eye_left[1]) * 1.2) + 20

        l_ear_x1 = max(0, int(chin_left[0] - ear_w))
        l_ear_y1 = max(0, int(eye_left[1] - ear_h * 0.4))
        l_ear_x2 = min(w, int(chin_left[0] + ear_w * 0.5))
        l_ear_y2 = min(h, int(chin_left[1] + ear_h * 0.4))

        # Define Right Ear ROI
        r_ear_x1 = max(0, int(chin_right[0] - ear_w * 0.5))
        r_ear_y1 = max(0, int(eye_right[1] - ear_h * 0.4))
        r_ear_x2 = min(w, int(chin_right[0] + ear_w))
        r_ear_y2 = min(h, int(chin_right[1] + ear_h * 0.4))

        ear_rois = [
            ("left_ear", (l_ear_x1, l_ear_y1, l_ear_x2, l_ear_y2)),
            ("right_ear", (r_ear_x1, r_ear_y1, r_ear_x2, r_ear_y2)),
        ]

        for ear_name, (x1, y1, x2, y2) in ear_rois:
            if x2 <= x1 or y2 <= y1:
                continue

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            # Analyze texture & contrast anomaly inside ear ROI
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_crop, 50, 150)
            edge_density = np.sum(edges > 0) / float(gray_crop.size)

            # High edge density / contrast in ear region indicates earbud, wire, or device
            if edge_density > 0.08:
                results.append(
                    EarbudDetection(
                        label="bluetooth_earbud",
                        malpractice_type="bluetooth_earbud",
                        confidence=min(0.85, round(0.50 + edge_density * 2.0, 2)),
                        box=(float(x1), float(y1), float(x2), float(y2)),
                    )
                )

            # Check if any external object box overlaps with ear region
            if detected_boxes:
                for bx1, by1, bx2, by2 in detected_boxes:
                    # Calculate IoU / intersection with ear region
                    ix1 = max(x1, bx1)
                    iy1 = max(y1, by1)
                    ix2 = min(x2, bx2)
                    iy2 = min(y2, by2)
                    if ix2 > ix1 and iy2 > iy1:
                        inter_area = (ix2 - ix1) * (iy2 - iy1)
                        ear_area = (x2 - x1) * (y2 - y1)
                        if inter_area / float(ear_area) > 0.15:
                            results.append(
                                EarbudDetection(
                                    label="ear_device_overlap",
                                    malpractice_type="phone_call_posture",
                                    confidence=0.88,
                                    box=(float(x1), float(y1), float(x2), float(y2)),
                                )
                            )

    return results
