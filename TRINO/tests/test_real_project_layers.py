from proctoring_assistant.storage import EvidenceRepository
from proctoring_assistant.retrieval_agent import analyze_query, route_query
from proctoring_assistant.documents import build_evidence_documents, split_evidence_documents
from proctoring_assistant.embeddings import embedding_dimension
from proctoring_assistant.vector_store import VectorEvidenceStore
from proctoring_assistant.database import EvidenceDatabase
from proctoring_assistant.service import EvidenceService
from fastapi.testclient import TestClient
from utils.ingestion import demo_evidence_records


def test_route_query_detects_semantic_context():
    route = route_query("show anything involving a phone during the exam")
    assert route == "semantic"


def test_route_query_detects_sql_context():
    route = route_query("find all evidence for STU102 in SESSION004")
    assert route == "sql"


def test_route_query_detects_hybrid_context_and_filters():
    analysis = analyze_query("find phone-related suspicious evidence for STU102 in SESSION004")

    assert analysis["query_type"] == "HYBRID"
    assert analysis["filters"] == {
        "student_id": "STU102",
        "session_id": "SESSION004",
        "suspicious": True,
    }


def test_query_analysis_extracts_time_window():
    analysis = analyze_query("Show suspicious events between 10:00 and 11:00")

    assert analysis["filters"]["start_time"] == "10:00"
    assert analysis["filters"]["end_time"] == "11:00"


def test_incident_query_does_not_force_suspicious_filter():
    analysis = analyze_query("Show all incidents for STU001")

    assert analysis["query_type"] == "SQL"
    assert analysis["filters"] == {"student_id": "STU001"}


def test_repository_can_persist_and_fetch_records(tmp_path):
    repo = EvidenceRepository(db_path=str(tmp_path / "evidence.db"))
    repo.insert_record({
        "evidence_id": "E-001",
        "student_id": "STU102",
        "session_id": "SESSION004",
        "timestamp": "2026-08-18T10:15:00Z",
        "camera": "webcam",
        "resolution": "1920x1080",
        "category": "incident",
        "source_path": "/tmp/phone.png",
        "ocr_text": "phone visible",
        "vision_description": "phone on desk",
        "metadata": {"source": "demo"},
        "suspicious": 1,
        "risk_score": 0.9,
    })

    results = repo.fetch_by_student_session("STU102", "SESSION004")
    assert len(results) == 1
    assert results[0]["evidence_id"] == "E-001"


def test_evidence_documents_preserve_traceability_and_chunk_metadata():
    records = demo_evidence_records()

    documents = build_evidence_documents(records)
    chunks = split_evidence_documents(documents, chunk_size=80, chunk_overlap=10)

    assert documents
    assert chunks
    assert all(document.metadata["evidence_id"] for document in documents)
    assert all(chunk.metadata["evidence_id"] for chunk in chunks)
    assert all(chunk.metadata["chunk_index"] >= 0 for chunk in chunks)


def test_local_embeddings_and_chroma_retrieve_evidence(tmp_path):
    records = demo_evidence_records()
    documents = split_evidence_documents(build_evidence_documents(records), chunk_size=160, chunk_overlap=20)
    store = VectorEvidenceStore(
        persist_directory=str(tmp_path / "chroma"),
        collection_name="test_exam_evidence",
    )

    store.add_documents(documents)
    results = store.similarity_search("phone evidence", k=2)

    assert embedding_dimension() == 384
    assert results
    assert results[0]["metadata"]["evidence_id"]
    assert 0.0 < results[0]["similarity"] <= 1.0


def test_sqlalchemy_database_supports_structured_filters(tmp_path):
    database = EvidenceDatabase(f"sqlite:///{tmp_path / 'structured.db'}")
    records = demo_evidence_records()
    database.upsert_records(records)

    filtered = database.query_records(student_id="STU102", session_id="SESSION004", suspicious=True)
    incidents = database.query_records(category="incident")

    assert len(filtered) == 2
    assert len(incidents) == 1
    assert filtered[0].evidence_id


def test_sqlalchemy_database_supports_time_window_filters(tmp_path):
    database = EvidenceDatabase(f"sqlite:///{tmp_path / 'time.db'}")
    database.upsert_records(demo_evidence_records())

    results = database.query_records(start_time="10:20", end_time="10:30")

    assert results
    assert all("T10:2" in record.timestamp for record in results)


def test_langgraph_agent_runs_hybrid_retrieval_and_fallback_rag(tmp_path):
    service = EvidenceService(
        database_url=f"sqlite:///{tmp_path / 'agent.db'}",
        vector_path=str(tmp_path / "vectors"),
        collection_name="test_agent_evidence",
        top_k=3,
    )

    result = service.investigate("Find phone-related suspicious evidence for STU102")

    assert result["query_type"] == "HYBRID"
    assert result["retrieved_documents"]
    assert result["reranked_documents"]
    assert result["evidence_references"]
    assert "Human review required" in result["final_answer"]


def test_api_investigate_exposes_route_and_grounded_answer(tmp_path):
    import proctoring_assistant.api as api_module

    api_module._service = EvidenceService(
        database_url=f"sqlite:///{tmp_path / 'api.db'}",
        vector_path=str(tmp_path / "api_vectors"),
        collection_name="test_api_evidence",
    )
    response = TestClient(api_module.app).post(
        "/investigate",
        json={"query": "Find phone-related incidents for STU102", "top_k": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["route"] == "HYBRID"
    assert payload["evidence_references"]
    assert "Human review required" in payload["final_answer"]
