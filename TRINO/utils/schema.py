from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class EvidenceRecord:
    evidence_id: str
    student_id: str
    session_id: str
    timestamp: str
    camera: str
    resolution: str
    category: str
    source_path: str
    ocr_text: str = ""
    vision_description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    suspicious: bool = False
    risk_score: float = 0.0
    incident_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "student_id": self.student_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "camera": self.camera,
            "resolution": self.resolution,
            "category": self.category,
            "source_path": self.source_path,
            "ocr_text": self.ocr_text,
            "vision_description": self.vision_description,
            "metadata": self.metadata,
            "suspicious": self.suspicious,
            "risk_score": self.risk_score,
            "incident_type": self.incident_type,
        }


@dataclass(slots=True)
class EvidenceChunk:
    chunk_id: int
    start_time: float
    end_time: float
    frame_count: int
    sample_count: int
    face_peak: int
    no_face_ratio: float
    motion_score: float
    attention_score: float
    risk_score: float
    risk_label: str
    events: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    description: str = ""
    keyframe_note: str = ""


@dataclass(slots=True)
class AnalysisReport:
    video_name: str
    source: str
    duration_seconds: float
    fps: float
    chunk_seconds: int
    sample_rate: float
    chunks: List[EvidenceChunk] = field(default_factory=list)
    summary: str = ""


@dataclass(slots=True)
class VectorStore:
    chunks: List[EvidenceChunk]
    vectorizer: Any
    matrix: Any


@dataclass(slots=True)
class RetrievalHit:
    chunk: Optional[Any] = None
    similarity: float = 0.0
    rerank_score: float = 0.0
    match_reason: str = ""
    evidence_id: str = ""
    student_id: str = ""
    session_id: str = ""
    timestamp: str = ""
    camera: str = ""
    category: str = ""
    source_path: str = ""


@dataclass(slots=True)
class ProcessFlag:
    app_name: str
    category: str
    severity: str
    reason: str


@dataclass(slots=True)
class QueryResult:
    query: str
    results: List[RetrievalHit] = field(default_factory=list)
    rationale: str = ""
