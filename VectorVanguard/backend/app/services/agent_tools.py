from langchain.tools import tool

from app.core.database import SessionLocal
from app.services.retrieval import HybridRetriever


@tool
def retrieve_evidence(query: str) -> str:
    """
    Search exam evidence using both keyword and semantic retrieval.

    Use this tool when you need evidence relevant to an investigation
    question. The search combines PostgreSQL Full-Text Search and
    ChromaDB semantic search using Reciprocal Rank Fusion.
    """

    db = SessionLocal()

    try:
        retriever = HybridRetriever(db)

        results = retriever.search(
            query=query,
            top_k=5,
        )

        hydrated_results = retriever.hydrate_results(
            results
        )

        if not hydrated_results:
            return "No relevant evidence was found."

        formatted = []

        for result in hydrated_results:
            formatted.append(
                (
                    f"Evidence ID: {result['evidence_id']}\n"
                    f"Session ID: {result['session_id']}\n"
                    f"Image Path: {result['image_path']}\n"
                    f"OCR Text: {result['ocr_text']}\n"
                    f"Timestamp: {result['timestamp']}\n"
                    f"RRF Score: {result['rrf_score']:.6f}"
                )
            )

        return "\n\n".join(formatted)

    finally:
        db.close()