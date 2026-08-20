"""
detection/object_detection.py
--------------------------------
Detects malpractice-relevant objects (phones, books, notes, second person,
earphones, smartwatches, etc.) in an uploaded proctoring image using YOLO
(via the `ultralytics` package).

The COCO-pretrained model already recognises a useful subset out of the box
(cell phone, book, laptop, person). For domain-specific classes (e.g. cheat
sheets, smartwatches) fine-tune a custom YOLO model and point
YOLO_WEIGHTS_PATH in .env at it.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Classes (from COCO) that are relevant signals of exam malpractice.
SUSPICIOUS_CLASSES = {
    "cell phone": "phone_usage",
    "remote": "phone_usage",
    "mouse": "unauthorized_device",
    "toothbrush": "phone_usage",  # commonly misclassified thin devices/phones held to ear
    "cup": "unauthorized_device",
    "bottle": "unauthorized_device",
    "book": "unauthorized_material",
    "laptop": "unauthorized_device",
    "person": "multiple_people",  # >1 person box triggers this
    "tv": "unauthorized_device",
}

_model = None  # lazy-loaded singleton


@dataclass
class Detection:
    label: str
    malpractice_type: str
    confidence: float
    box: tuple[float, float, float, float]  # x1, y1, x2, y2


@dataclass
class ObjectDetectionResult:
    detections: list[Detection] = field(default_factory=list)
    person_count: int = 0


def _load_model():
    global _model
    if _model is not None:
        return _model

    try:
        from ultralytics import YOLO
    except ImportError:  # pragma: no cover - optional dependency
        logger.warning(
            "`ultralytics` not installed - object detection will return no detections. "
            "Install with `pip install ultralytics`."
        )
        return None

    weights_path = os.getenv("YOLO_WEIGHTS_PATH", "yolov8s.pt")
    if not os.path.isabs(weights_path) and not os.path.exists(weights_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(base_dir, weights_path)
        if os.path.exists(candidate):
            weights_path = candidate
        else:
            # Check detection/weights directory fallback
            weights_dir_candidate = os.path.join(base_dir, "detection", "weights", weights_path)
            if os.path.exists(weights_dir_candidate):
                weights_path = weights_dir_candidate

    logger.info("Loading YOLO weights from %s", weights_path)
    _model = YOLO(weights_path)
    return _model


def detect_objects(image_path: str, confidence_threshold: float = 0.20) -> ObjectDetectionResult:
    """
    Run YOLO inference on the image and return malpractice-relevant detections
    (filtered by SUSPICIOUS_CLASSES and appropriate confidence thresholds).
    """
    env_conf = os.getenv("YOLO_CONF_THRESHOLD")
    if env_conf:
        try:
            confidence_threshold = float(env_conf)
        except ValueError:
            pass

    model = _load_model()
    if model is None:
        return ObjectDetectionResult()

    results = model.predict(source=image_path, conf=confidence_threshold, verbose=False)
    detections: list[Detection] = []
    person_detections: list[tuple[float, tuple[float, float, float, float]]] = []

    for result in results:
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = names.get(cls_id, str(cls_id))
            conf = float(box.conf.item())
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]

            # Only count actual persons with high confidence (>= 0.45)
            # to avoid false positives on background objects/hanging clothes
            if label == "person":
                if conf >= 0.45:
                    person_detections.append((conf, (x1, y1, x2, y2)))
                continue

            if label in SUSPICIOUS_CLASSES:
                mal_type = SUSPICIOUS_CLASSES[label]
                detections.append(
                    Detection(
                        label=label,
                        malpractice_type=mal_type,
                        confidence=conf,
                        box=(x1, y1, x2, y2),
                    )
                )

    person_count = len(person_detections)

    # Only flag multiple_people if more than 1 genuine person is detected
    if person_count > 1:
        for conf, (x1, y1, x2, y2) in person_detections[1:]:
            detections.append(
                Detection(
                    label="person",
                    malpractice_type="multiple_people",
                    confidence=conf,
                    box=(x1, y1, x2, y2),
                )
            )

    return ObjectDetectionResult(detections=detections, person_count=max(1, person_count))
