"""BM25 keyword-based retrieval, used alongside FAISS dense retrieval for
hybrid search.

Belongs in `rag/bm25_retriever.py`.

Dense retrieval (FAISS + sentence-transformers, rag/retriever.py) matches
on *meaning* -- it can find a rule about "secondary computing devices"
when the query says "unauthorized laptop", even though the words don't
overlap at all. What it can under-rank is an exact, distinctive keyword
match: if a query mentions "keyboard" specifically, a semantically
similar-but-not-identical rule can sometimes outrank the one rule that
actually says "keyboard" verbatim, because embedding similarity is about
overall meaning, not exact terms.

BM25 is a decades-old, well-established keyword-ranking algorithm (the
same family historically used by classic search engines) that scores
purely on literal term overlap, weighted by how rare/distinctive each
term is across the whole document set. It has no notion of meaning at
all -- but it's very good at surfacing an exact keyword match dense
retrieval alone might rank lower.

Combining both (see rag/hybrid.py) gets the strengths of each: semantic
recall from FAISS, exact-term precision from BM25.
"""

import re
from typing import Any, Dict, List

from rank_bm25 import BM25Okapi

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    """Lowercase, alphanumeric-only tokenization.

    No stemming/lemmatization -- BM25Okapi doesn't require it, and the
    rule set here is short, plain-English text where this simple
    approach is sufficient. A larger, more varied rules corpus might
    benefit from a proper tokenizer/stemmer; not needed at this scale.
    """
    return _TOKEN_PATTERN.findall(text.lower())


class BM25Index:
    """Wraps rank_bm25.BM25Okapi, returning results in the same
    {"chunk_id", "text", "score"} shape rag/retriever.py's FAISS wrapper
    uses, so rag/hybrid.py can merge both without caring which is which.
    """

    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self._bm25 = BM25Okapi([_tokenize(c) for c in chunks])

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_tokens = _tokenize(query)
        scores = self._bm25.get_scores(query_tokens)

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        return [
            {"chunk_id": idx, "text": self.chunks[idx], "score": float(scores[idx])}
            for idx in ranked_indices
            if scores[idx] > 0  # a zero score means literally no keyword overlap
        ]


def build_bm25_index(chunks: List[str]) -> BM25Index:
    return BM25Index(chunks)
