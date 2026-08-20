from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.evidence import EvidenceRecord
from app.core.vector_store import collection


class KeywordRetriever:
    """
    Handles lexical keyword retrieval using
    PostgreSQL Native Full-Text Search.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        ts_query = func.plainto_tsquery("english", query)

        ts_vector = func.to_tsvector(
            "english",
            func.coalesce(EvidenceRecord.ocr_text, "")
        )

        rank = func.ts_rank(
            ts_vector,
            ts_query
        ).label("rank")

        stmt = (
            select(EvidenceRecord, rank)
            .where(ts_vector.bool_op("@@")(ts_query))
            .order_by(rank.desc())
            .limit(top_k)
        )

        results = self.db.execute(stmt).all()

        return [
            {
                "evidence_id": record.evidence_id,
                "ocr_text": record.ocr_text,
                "score": float(score),
            }
            for record, score in results
        ]


class SemanticRetriever:
    """
    Handles semantic retrieval using ChromaDB
    and Nomic embeddings.
    """

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        formatted_results = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for evidence_id, document, distance in zip(
            ids,
            documents,
            distances,
        ):
            formatted_results.append(
                {
                    "evidence_id": evidence_id,
                    "ocr_text": document,
                    "score": float(distance),
                }
            )

        return formatted_results


class HybridRetriever:
    """
    Combines keyword and semantic retrieval using
    Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, db_session: Session):
        self.db = db_session

        self.keyword_retriever = KeywordRetriever(
            db_session
        )

        self.semantic_retriever = SemanticRetriever()

    def search(
        self,
        query: str,
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[dict]:

        keyword_results = self.keyword_retriever.search(
            query=query,
            top_k=top_k,
        )

        semantic_results = self.semantic_retriever.search(
            query=query,
            top_k=top_k,
        )

        fused = {}

        # Keyword results
        for rank, result in enumerate(
            keyword_results,
            start=1,
        ):
            evidence_id = result["evidence_id"]

            if evidence_id not in fused:
                fused[evidence_id] = {
                    "evidence_id": evidence_id,
                    "ocr_text": result["ocr_text"],
                    "rrf_score": 0.0,
                    "keyword_rank": None,
                    "semantic_rank": None,
                }

            fused[evidence_id]["keyword_rank"] = rank

            fused[evidence_id]["rrf_score"] += (
                1 / (rrf_k + rank)
            )

        # Semantic results
        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            evidence_id = result["evidence_id"]

            if evidence_id not in fused:
                fused[evidence_id] = {
                    "evidence_id": evidence_id,
                    "ocr_text": result["ocr_text"],
                    "rrf_score": 0.0,
                    "keyword_rank": None,
                    "semantic_rank": None,
                }

            fused[evidence_id]["semantic_rank"] = rank

            fused[evidence_id]["rrf_score"] += (
                1 / (rrf_k + rank)
            )

        results = sorted(
            fused.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        return results[:top_k]

    def hydrate_results(
        self,
        results: list[dict],
    ) -> list[dict]:
        """
        Fetch authoritative evidence metadata
        from PostgreSQL using evidence_id.
        """

        if not results:
            return []

        evidence_ids = [
            result["evidence_id"]
            for result in results
        ]

        stmt = select(EvidenceRecord).where(
            EvidenceRecord.evidence_id.in_(evidence_ids)
        )

        records = self.db.execute(stmt).scalars().all()

        records_by_id = {
            record.evidence_id: record
            for record in records
        }

        hydrated = []

        for result in results:
            record = records_by_id.get(
                result["evidence_id"]
            )

            if record is None:
                continue

            hydrated.append(
                {
                    "evidence_id": record.evidence_id,
                    "session_id": record.session_id,
                    "image_path": record.image_path,
                    "ocr_text": record.ocr_text,
                    "timestamp": record.timestamp,
                    "rrf_score": result["rrf_score"],
                    "keyword_rank": result["keyword_rank"],
                    "semantic_rank": result["semantic_rank"],
                }
            )

        return hydrated