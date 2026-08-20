from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import DATABASE_URL, OLLAMA_MODEL, OLLAMA_URL, VECTOR_DB_PATH
from .service import EvidenceService
from utils.ingestion import demo_evidence_records, load_image_evidence

app = FastAPI(title="AI Exam Proctoring Assistant API", version="0.1.0")
_service: Optional[EvidenceService] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=50)


class InvestigationRequest(SearchRequest):
    use_ollama: bool = False
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None


def get_service() -> EvidenceService:
    global _service
    if _service is None:
        _service = EvidenceService(
            database_url=DATABASE_URL,
            vector_path=VECTOR_DB_PATH,
        )
    return _service


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-exam-proctoring-assistant"}


@app.get("/evidence")
def list_evidence() -> dict:
    service = get_service()
    service.ensure_demo_data()
    records = service.database.query_records()
    return {"count": len(records), "records": [record.to_dict() for record in records]}


@app.post("/search")
def search_evidence(payload: SearchRequest) -> dict:
    result = get_service().investigate(payload.query, top_k=payload.top_k)
    reranked = result.get("reranked_documents", [])
    return {
        "query": payload.query,
        "count": len(reranked),
        "route": result.get("query_type", "HYBRID"),
        "results": [
            {
                "evidence_id": hit["metadata"].get("evidence_id", ""),
                "student_id": hit["metadata"].get("student_id", ""),
                "session_id": hit["metadata"].get("session_id", ""),
                "timestamp": hit["metadata"].get("timestamp", ""),
                "category": hit["metadata"].get("category", ""),
                "camera": hit["metadata"].get("camera", ""),
                "similarity": hit.get("similarity", 0.0),
                "rerank_score": hit.get("rerank_score", 0.0),
                "match_reason": hit.get("match_reason", ""),
            }
            for hit in reranked
        ],
    }


@app.post("/upload")
def upload_images(directory: str = "sample_evidence") -> dict:
    records = load_image_evidence(directory)
    if not records:
        raise HTTPException(status_code=404, detail="No evidence images were found in the provided directory.")
    get_service().ingest_records(records)
    return {"count": len(records), "records": [record.to_dict() for record in records]}


@app.post("/investigate")
def investigate(payload: InvestigationRequest) -> Dict[str, Any]:
    result = get_service().investigate(
        payload.query,
        top_k=payload.top_k,
        use_ollama=payload.use_ollama,
        ollama_url=payload.ollama_url or OLLAMA_URL,
        ollama_model=payload.ollama_model or OLLAMA_MODEL,
    )
    return {
        "query": payload.query,
        "route": result.get("query_type", "HYBRID"),
        "filters": result.get("filters", {}),
        "retrieved_evidence": result.get("retrieved_documents", []),
        "reranked_evidence": result.get("reranked_documents", []),
        "final_answer": result.get("final_answer", ""),
        "evidence_references": result.get("evidence_references", []),
    }


def main() -> None:
    import uvicorn

    uvicorn.run("proctoring_assistant.api:app", host="0.0.0.0", port=8000, reload=False)
