from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .schema import EvidenceRecord, RetrievalHit


def build_evidence_index(records: Sequence[EvidenceRecord]):
    corpus = [
        " ".join(
            filter(
                None,
                [
                    record.ocr_text,
                    record.vision_description,
                    record.category,
                    record.camera,
                    record.student_id,
                    record.session_id,
                ],
            )
        )
        for record in records
    ]
    if not corpus:
        corpus = ["empty evidence corpus"]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    return {"records": list(records), "vectorizer": vectorizer, "matrix": matrix}


def retrieve_records(index: dict, query: str, top_k: int = 5) -> list[Tuple[EvidenceRecord, float]]:
    records = index["records"]
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    if not records:
        return []
    query_vector = vectorizer.transform([query or "suspicious examination evidence"])
    scores = cosine_similarity(query_vector, matrix).ravel()
    ranked_indices = np.argsort(scores)[::-1][:top_k]
    return [(records[int(index)], float(scores[int(index)])) for index in ranked_indices]


def rerank_records(query: str, retrieved: Sequence[Tuple[EvidenceRecord, float]], top_n: int = 5) -> list[RetrievalHit]:
    query_lower = query.lower()
    hits: list[RetrievalHit] = []
    for record, similarity in retrieved:
        keyword_bonus = 0.0
        reasons = []
        if "phone" in query_lower and ("phone" in (record.ocr_text or "").lower() or "phone" in (record.vision_description or "").lower()):
            keyword_bonus += 0.2
            reasons.append("Query term 'phone' matched device evidence.")
        if "multiple" in query_lower and "multiple" in (record.ocr_text or "").lower():
            keyword_bonus += 0.15
            reasons.append("Query term 'multiple' matched multi-person evidence.")
        if "absent" in query_lower and "absence" in record.category.lower():
            keyword_bonus += 0.2
            reasons.append("Query term 'absent' matched absence evidence.")
        if not reasons:
            reasons.append("Semantic similarity matched the evidence text and context.")

        rerank_score = min(1.0, 0.7 * similarity + 0.2 * record.risk_score + keyword_bonus)
        hits.append(
            RetrievalHit(
                evidence_id=record.evidence_id,
                student_id=record.student_id,
                session_id=record.session_id,
                timestamp=record.timestamp,
                camera=record.camera,
                category=record.category,
                source_path=record.source_path,
                similarity=float(similarity),
                rerank_score=float(rerank_score),
                match_reason=" ".join(reasons),
            )
        )
    hits.sort(key=lambda hit: hit.rerank_score, reverse=True)
    return hits[:top_n]
