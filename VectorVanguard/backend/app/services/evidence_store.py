from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection


def store_evidence(
    db: Session,
    evidence_id: str,
    session_id: int,
    image_path: str,
    ocr_text: str,
    vision_description: str | None = None,
    structured_observations: dict | None = None,
    timestamp: datetime | None = None,
):
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    evidence = EvidenceRecord(
        evidence_id=evidence_id,
        session_id=session_id,
        image_path=image_path,
        ocr_text=ocr_text,
        vision_description=vision_description,
        structured_observations=structured_observations,
        timestamp=timestamp,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # Build searchable text for ChromaDB.
    structured_text = ""

    if structured_observations:
        structured_text = (
            "\n\nSTRUCTURED OBSERVATIONS:\n"
            f"{structured_observations}"
        )

    vector_text = (
        f"OCR:\n{ocr_text}\n\n"
        f"VISION:\n{vision_description or ''}"
        f"{structured_text}"
    )

    collection.add(
        ids=[evidence_id],
        documents=[vector_text],
        metadatas=[
            {
                "evidence_id": evidence_id,
                "session_id": str(session_id),
            }
        ],
    )

    return evidence