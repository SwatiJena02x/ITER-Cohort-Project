"""
detection/ocr_detection.py
---------------------------
Extracts text from student ID cards using RapidOCR (ONNX Runtime)
and computes matching confidence against student's registered name and roll number.
"""
from __future__ import annotations

import logging
import os
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

_ocr_engine = None


def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is not None:
        return _ocr_engine
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
        return _ocr_engine
    except Exception as e:
        logger.warning("[ocr_detection] Could not initialize RapidOCR: %s", e)
        return None


def _clean_text(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()


def compute_id_card_ocr_match(
    id_card_path: str,
    expected_name: str,
    expected_roll: str | None = None,
) -> tuple[float | None, str]:
    """
    Runs OCR on the ID card image and checks if expected student name and roll number are present.
    Returns (score_percentage, status_text).
    e.g. (96.5, "Matched") or (None, "Not available").
    """
    if not id_card_path or not os.path.exists(id_card_path):
        return None, "Not available"

    ocr = _get_ocr_engine()
    if ocr is None:
        return None, "Not available"

    try:
        result, _ = ocr(id_card_path)
        if not result:
            return None, "No text detected"

        extracted_lines = [line[1] for line in result if len(line) >= 2]
        full_extracted = " ".join(extracted_lines)
        clean_extracted = _clean_text(full_extracted)

        clean_name = _clean_text(expected_name)
        clean_roll = _clean_text(expected_roll) if expected_roll else ""

        name_match = 0.0
        roll_match = 0.0

        # Check exact or partial substring match for name
        if clean_name in clean_extracted:
            name_match = 1.0
        else:
            # Check individual name tokens
            name_parts = expected_name.lower().split()
            found_parts = sum(1 for part in name_parts if _clean_text(part) in clean_extracted)
            if name_parts:
                token_ratio = found_parts / len(name_parts)
                seq_ratio = SequenceMatcher(None, clean_name, clean_extracted).ratio()
                name_match = max(token_ratio, seq_ratio)

        # Check roll number
        if clean_roll:
            if clean_roll in clean_extracted:
                roll_match = 1.0
            else:
                roll_match = SequenceMatcher(None, clean_roll, clean_extracted).ratio()
        else:
            roll_match = 1.0

        # Weighted score: 60% Name + 40% Roll
        combined_ratio = (name_match * 0.6) + (roll_match * 0.4)
        score_pct = round(min(100.0, max(0.0, combined_ratio * 100.0)), 1)

        if score_pct >= 60.0:
            status = "Matched"
        elif score_pct >= 40.0:
            status = "Partial Match"
        else:
            status = "Mismatch"

        logger.info(
            "[ocr_detection] %s: OCR match score=%.1f%% status=%s",
            expected_name, score_pct, status
        )
        return score_pct, status

    except Exception as e:
        logger.warning("[ocr_detection] OCR processing failed on %s: %s", id_card_path, e)
        return None, "Error"
