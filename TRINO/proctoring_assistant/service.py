from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import requests

from utils.schema import AnalysisReport, EvidenceRecord

from .database import EvidenceDatabase
from .documents import build_evidence_documents, split_evidence_documents
from .retrieval_agent import analyze_query
from .vector_store import VectorEvidenceStore


class EvidenceService:
    """Coordinates ingestion, persistence, vector retrieval, ranking, and RAG."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        vector_path: str = "data/vector_store",
        collection_name: str = "exam_evidence",
        chunk_size: int = 500,
        chunk_overlap: int = 80,
        top_k: int = 10,
    ) -> None:
        self.database = EvidenceDatabase(database_url)
        self.vector_store = VectorEvidenceStore(vector_path, collection_name=collection_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self._graph = None

    def ingest_records(self, records: Sequence[EvidenceRecord]) -> int:
        values = list(records)
        if not values:
            return 0
        self.database.upsert_records(values)
        documents = build_evidence_documents(values)
        chunks = split_evidence_documents(documents, self.chunk_size, self.chunk_overlap)
        self.vector_store.add_documents(chunks)
        return len(values)

    def ingest_video_report(self, report: AnalysisReport) -> int:
        records = []
        for chunk in report.chunks:
            evidence_id = f"{report.video_name}:{chunk.chunk_id}"
            records.append(
                EvidenceRecord(
                    evidence_id=evidence_id,
                    student_id="UNKNOWN_STUDENT",
                    session_id="UNKNOWN_SESSION",
                    timestamp=f"{chunk.start_time:.2f}",
                    camera="recorded_video",
                    resolution="",
                    category=chunk.events[0] if chunk.events else "video_chunk",
                    source_path=report.source,
                    ocr_text="",
                    vision_description=chunk.description,
                    metadata={
                        "source": report.video_name,
                        "observations": chunk.observations,
                        "events": chunk.events,
                        "start_time": chunk.start_time,
                        "end_time": chunk.end_time,
                    },
                    suspicious=chunk.risk_label != "low",
                    risk_score=chunk.risk_score,
                    incident_type=chunk.events[0] if chunk.events else "",
                )
            )
        return self.ingest_records(records)

    def ensure_demo_data(self) -> int:
        from utils.ingestion import demo_evidence_records

        records = demo_evidence_records()
        existing_ids = {record.evidence_id for record in self.database.query_records()}
        missing_records = [record for record in records if record.evidence_id not in existing_ids]
        if missing_records:
            self.ingest_records(missing_records)
        return len(self.database.query_records())

    def sql_retrieval(self, filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        allowed_filters = {
            key: value
            for key, value in filters.items()
            if key in {
                "student_id",
                "session_id",
                "category",
                "incident_type",
                "suspicious",
                "start_timestamp",
                "end_timestamp",
                "start_time",
                "end_time",
                "text_query",
            }
        }
        records = self.database.query_records(**allowed_filters)
        return [self._record_result(record, similarity=0.0) for record in records[:top_k]]

    def semantic_retrieval(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        return self.vector_store.similarity_search(query, k=top_k)

    def hybrid_retrieval(self, query: str, filters: Dict[str, Any], top_k: int) -> List[Dict[str, Any]]:
        structured = self.sql_retrieval(filters, top_k=max(top_k, 20))
        allowed_ids = {item["metadata"]["evidence_id"] for item in structured}
        semantic = self.semantic_retrieval(query, top_k=max(top_k, 20))
        combined: Dict[str, Dict[str, Any]] = {}
        for item in semantic:
            evidence_id = item["metadata"].get("evidence_id")
            if evidence_id in allowed_ids:
                combined[evidence_id] = item
        for item in structured:
            evidence_id = item["metadata"].get("evidence_id")
            if evidence_id not in combined:
                combined[evidence_id] = item
        return list(combined.values())[:top_k]

    def rerank(self, query: str, candidates: Sequence[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        query_terms = {term for term in query.lower().split() if len(term) > 2}
        ranked: List[Dict[str, Any]] = []
        for candidate in candidates:
            metadata = candidate.get("metadata", {})
            content = candidate.get("page_content", "").lower()
            lexical_bonus = min(0.25, 0.05 * sum(term in content for term in query_terms))
            similarity = float(candidate.get("similarity", 0.0))
            risk_score = float(metadata.get("risk_score", 0.0))
            score = min(1.0, (0.65 * similarity) + (0.2 * risk_score) + lexical_bonus)
            ranked.append(
                {
                    **candidate,
                    "rerank_score": score,
                    "match_reason": "Semantic similarity, structured metadata, and risk signals were combined.",
                }
            )
        ranked.sort(key=lambda item: item["rerank_score"], reverse=True)
        return ranked[:top_k]

    def generate_rag_answer(
        self,
        query: str,
        documents: Sequence[Dict[str, Any]],
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.1",
        use_ollama: bool = False,
    ) -> str:
        prompt = self._build_rag_prompt(query, documents)
        if use_ollama:
            answer = self._call_ollama(prompt, ollama_url, ollama_model)
            if answer:
                return answer
        if not documents:
            return "Insufficient evidence was retrieved for this question. Human review is required."
        lines = ["Potentially relevant evidence:"]
        for item in documents:
            metadata = item.get("metadata", {})
            lines.extend(
                [
                    f"Evidence ID: {metadata.get('evidence_id', 'unknown')}",
                    f"Student/session: {metadata.get('student_id', 'unknown')} / {metadata.get('session_id', 'unknown')}",
                    f"Timestamp: {metadata.get('timestamp', 'unknown')}",
                    f"Observation: {item.get('page_content', '').strip()}",
                    f"Risk score: {float(metadata.get('risk_score', 0.0)):.2f}",
                ]
            )
        lines.append("Recommendation: Human review required; these signals do not establish misconduct.")
        return "\n".join(lines)

    def investigate(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_ollama: bool = False,
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.1",
    ) -> Dict[str, Any]:
        self.ensure_demo_data()
        if self._graph is None:
            from .agent import build_agent_graph

            self._graph = build_agent_graph(self)
        return self._graph.invoke(
            {
                "user_query": query,
                "top_k": top_k or self.top_k,
                "use_ollama": use_ollama,
                "ollama_url": ollama_url,
                "ollama_model": ollama_model,
            }
        )

    @staticmethod
    def _record_result(record: EvidenceRecord, similarity: float) -> Dict[str, Any]:
        document = build_evidence_documents([record])[0]
        return {
            "page_content": document.page_content,
            "metadata": document.metadata,
            "similarity": similarity,
        }

    @staticmethod
    def _build_rag_prompt(query: str, documents: Sequence[Dict[str, Any]]) -> str:
        evidence = json.dumps(list(documents), indent=2, default=str)
        return (
            "You are an evidence reviewer. Answer only from the supplied evidence. "
            "Distinguish observations from inferences, say when evidence is insufficient, "
            "never declare a student guilty, and recommend human review.\n\n"
            f"Question: {query}\nEvidence:\n{evidence}"
        )

    @staticmethod
    def _call_ollama(prompt: str, endpoint: str, model: str) -> Optional[str]:
        try:
            response = requests.post(
                endpoint.rstrip("/") + "/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=45,
            )
            response.raise_for_status()
            value = str(response.json().get("response", "")).strip()
            return value or None
        except Exception:
            return None
