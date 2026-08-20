"""
tests/test_detection.py
---------------------------
Unit tests for the detection layer. Model-dependent calls (YOLO,
face_recognition) are mocked so tests run fast and without GPU/weights.
"""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from detection.object_detection import Detection, ObjectDetectionResult, detect_objects


@pytest.fixture()
def fake_image(tmp_path):
    """Writes a tiny valid JPEG to disk for tests that need a real file path."""
    import cv2

    path = tmp_path / "sample.jpg"
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)


def test_detect_objects_returns_empty_when_ultralytics_missing(fake_image):
    with patch("detection.object_detection._load_model", return_value=None):
        result = detect_objects(fake_image)
    assert isinstance(result, ObjectDetectionResult)
    assert result.detections == []
    assert result.person_count == 0


def test_detect_objects_filters_to_suspicious_classes(fake_image):
    """Simulates a YOLO result containing both a suspicious and a benign class."""
    fake_box_phone = MagicMock()
    fake_box_phone.cls.item.return_value = 0
    fake_box_phone.conf.item.return_value = 0.87
    fake_box_phone.xyxy = [MagicMock(tolist=lambda: [1.0, 2.0, 3.0, 4.0])]

    fake_box_chair = MagicMock()  # "chair" is not in SUSPICIOUS_CLASSES
    fake_box_chair.cls.item.return_value = 1
    fake_box_chair.conf.item.return_value = 0.7
    fake_box_chair.xyxy = [MagicMock(tolist=lambda: [5.0, 6.0, 7.0, 8.0])]

    fake_result = MagicMock()
    fake_result.names = {0: "cell phone", 1: "chair"}
    fake_result.boxes = [fake_box_phone, fake_box_chair]

    fake_model = MagicMock()
    fake_model.predict.return_value = [fake_result]

    with patch("detection.object_detection._load_model", return_value=fake_model):
        result = detect_objects(fake_image)

    assert len(result.detections) == 1
    assert result.detections[0].malpractice_type == "phone_usage"
    assert result.detections[0].label == "cell phone"


def test_face_detection_fallback_no_library(fake_image):
    """When face_recognition isn't installed, Haar cascade fallback should not crash."""
    from detection import face_detection

    with patch.object(face_detection, "HAS_FACE_RECOGNITION", False):
        faces = face_detection.detect_faces(fake_image)
    # A blank black image should yield zero faces, but must not error.
    assert isinstance(faces, list)


def test_count_faces_matches_detect_faces_length(fake_image):
    from detection import face_detection

    with patch.object(face_detection, "detect_faces", return_value=[MagicMock(), MagicMock()]):
        assert face_detection.count_faces(fake_image) == 2
