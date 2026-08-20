from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Sequence

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.schema import EvidenceRecord


def _document_metadata(record: EvidenceRecord) -> Dict[str, Any]:
    metadata = dict(record.metadata)
    metadata.update(
        {
            "evidence_id": record.evidence_id,
            "student_id": record.student_id,
            "session_id": record.session_id,
            "timestamp": record.timestamp,
            "source": record.source_path,
            "camera": record.camera,
            "resolution": record.resolution,
            "category": record.category,
            "suspicious": bool(record.suspicious),
            "risk_score": float(record.risk_score),
        }
    )
    return {
        key: json.dumps(value, default=str) if isinstance(value, (list, dict)) else value
        for key, value in metadata.items()
    }


def evidence_to_document(record: EvidenceRecord) -> Document:
    observations = record.metadata.get("observations", [])
    if isinstance(observations, str):
        observations = [observations]
    observation_text = "\n".join(str(item) for item in observations)
    page_content = "\n".join(
        part
        for part in (
            record.ocr_text,
            record.vision_description,
            observation_text,
            f"category: {record.category}",
            f"camera: {record.camera}",
        )
        if part
    )
    return Document(page_content=page_content or "No textual evidence description available.", metadata=_document_metadata(record))


def build_evidence_documents(records: Iterable[EvidenceRecord]) -> List[Document]:
    return [evidence_to_document(record) for record in records]


def split_evidence_documents(
    documents: Sequence[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> List[Document]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    chunks = splitter.split_documents(list(documents))
    evidence_chunk_counts: Dict[str, int] = {}
    for chunk in chunks:
        evidence_id = str(chunk.metadata.get("evidence_id", ""))
        chunk_index = evidence_chunk_counts.get(evidence_id, 0)
        chunk.metadata["chunk_index"] = chunk_index
        chunk.metadata["chunk_id"] = f"{evidence_id}:{chunk_index}"
        evidence_chunk_counts[evidence_id] = chunk_index + 1
    return chunks
