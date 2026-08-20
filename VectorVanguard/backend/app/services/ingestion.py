import base64
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import cv2
import pytesseract
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.evidence_store import store_evidence


# ==============================================================================
# Tesseract OCR configuration
# ==============================================================================
# Prefer an explicitly configured TESSERACT_PATH.
# Otherwise, automatically find Tesseract from the system PATH.
TESSERACT_PATH = os.getenv(
    "TESSERACT_PATH"
) or shutil.which("tesseract")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = (
        TESSERACT_PATH
    )


# ==============================================================================
# Vision model
# ==============================================================================
vision_llm = ChatOllama(
    model=settings.OLLAMA_VISION_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0,
)


# ==============================================================================
# Image preprocessing
# ==============================================================================
def preprocess_image(image_path: str) -> object:
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    _, thresholded = cv2.threshold(
        grayscale,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    return thresholded


# ==============================================================================
# OCR extraction
# ==============================================================================
def extract_ocr(image_path: str) -> str:
    processed_image = preprocess_image(
        image_path
    )

    text = pytesseract.image_to_string(
        processed_image
    )

    return text.strip()


# ==============================================================================
# Vision analysis
# ==============================================================================
def analyze_image(
    image_path: str,
) -> tuple[str, dict]:
    image_path = Path(image_path)

    suffix = image_path.suffix.lower()

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(
        suffix,
        "image/jpeg",
    )

    with image_path.open("rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    prompt = """
Analyze this exam evidence image for academic
integrity investigation.

Return ONLY valid JSON.
Do not use markdown code fences.
Do not add explanations outside the JSON.

Use exactly this structure:

{
  "student": "",
  "seat_number": "",
  "objects": [
    {
      "name": "",
      "visible": true,
      "location": "",
      "notes": ""
    }
  ],
  "electronic_devices": [
    {
      "name": "",
      "visible": true,
      "location": "",
      "notes": ""
    }
  ],
  "environment": ""
}

Rules:

1. Report only objects that are actually visible.

2. Pay special attention to objects on or near
   the primary student's desk.

3. Carefully check for:
   mobile phones, smartphones, tablets, laptops,
   smartwatches, earphones, calculators, books,
   notebooks, notes, papers, pens, pencils,
   water bottles and other electronic devices.

4. For every visible object, describe its
   approximate location.

5. If an object is uncertain or partially obscured,
   clearly mention that uncertainty in "notes".

6. Do not invent objects.

7. Do not claim an object is absent simply because
   it is small or partially obscured.

8. Identify the student's seat number if it is visible.

9. Distinguish the primary student's desk from
   objects belonging to other students whenever
   possible.

10. Focus on what can actually be observed in
    the image rather than making assumptions.
"""

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": (
                    f"data:{mime_type};base64,{image_data}"
                ),
            },
        ],
    )

    response = vision_llm.invoke(
        [message]
    )

    raw_output = str(
        response.content
    ).strip()

    # Remove markdown fences if the model
    # accidentally returns them.
    if raw_output.startswith("```"):
        raw_output = (
            raw_output
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        structured_data = json.loads(
            raw_output
        )

    except json.JSONDecodeError:
        structured_data = {
            "student": "",
            "seat_number": "",
            "objects": [],
            "electronic_devices": [],
            "environment": "",
            "raw_output": raw_output,
        }

    return (
        raw_output,
        structured_data,
    )


# ==============================================================================
# Evidence ingestion
# ==============================================================================
def ingest_evidence(
    db: Session,
    session_id: int,
    image_path: str,
    evidence_id: str,
):
    ocr_text = extract_ocr(
        image_path
    )

    (
        vision_description,
        structured_observations,
    ) = analyze_image(
        image_path
    )

    try:
        evidence = store_evidence(
            db=db,
            evidence_id=evidence_id,
            session_id=session_id,
            image_path=image_path,
            ocr_text=ocr_text,
            vision_description=vision_description,
            structured_observations=(
                structured_observations
            ),
            timestamp=datetime.now(
                timezone.utc
            ),
        )

        return evidence

    except Exception:
        db.rollback()
        raise