import logging
import os
from functools import lru_cache
from typing import List, Dict

import torch
from PIL import Image
from transformers import pipeline

logger = logging.getLogger(__name__)

OBJECT_MODEL = "facebook/detr-resnet-50"
CONFIDENCE_THRESHOLD = 0.50


@lru_cache(maxsize=1)
def _get_detector():
    """Lazily load and cache the detection pipeline on first use.

    Deferring this until the first call (instead of at import time) avoids
    paying model-load cost just for importing the module, and avoids
    reloading it if this module is imported multiple times / reloaded.
    """
    device = 0 if torch.cuda.is_available() else -1
    logger.info(
        "Loading object detection model '%s' on %s...",
        OBJECT_MODEL, "GPU" if device == 0 else "CPU",
    )
    return pipeline("object-detection", model=OBJECT_MODEL, device=device)


def detect_objects(image_path: str) -> List[Dict]:
    """Run object detection on a single image.

    Args:
        image_path: Path to the image file.

    Returns:
        List of {"label": str, "score": float} dicts for detections
        at or above CONFIDENCE_THRESHOLD.

    Raises:
        FileNotFoundError: If image_path doesn't exist.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    detector = _get_detector()

    with Image.open(image_path) as img:
        image = img.convert("RGB")
        detections = detector(image)

    return [
        {"label": d["label"], "score": float(d["score"])}
        for d in detections
        if d["score"] >= CONFIDENCE_THRESHOLD
    ]


def detect_objects_batch(image_paths: List[str]) -> Dict[str, List[Dict]]:
    """Run object detection on multiple images using a single batched pass.

    Batching through the pipeline avoids per-call model dispatch overhead
    and lets the underlying model process images together on GPU.

    Args:
        image_paths: Paths to image files.

    Returns:
        Dict mapping each input path to its list of detections
        (same shape as detect_objects's return value).

    Raises:
        FileNotFoundError: If any image_path doesn't exist.
    """
    for path in image_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image file not found: {path}")

    detector = _get_detector()

    images = []
    for path in image_paths:
        with Image.open(path) as img:
            images.append(img.convert("RGB"))

    all_detections = detector(images)

    results = {}
    for path, detections in zip(image_paths, all_detections):
        results[path] = [
            {"label": d["label"], "score": float(d["score"])}
            for d in detections
            if d["score"] >= CONFIDENCE_THRESHOLD
        ]
    return results
