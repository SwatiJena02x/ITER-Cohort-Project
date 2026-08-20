"""Utility package for the AI exam proctoring assistant."""

from .cache import LocalEvidenceCache
from .ingestion import demo_evidence_records, load_image_evidence, validate_required_fields
from .process_monitor import detect_unauthorized_processes, detect_vm, get_running_processes
from .rag import build_evidence_index, retrieve_records, rerank_records
from .schema import AnalysisReport, EvidenceChunk, EvidenceRecord, ProcessFlag, RetrievalHit
