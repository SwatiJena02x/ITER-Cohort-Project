"""Reciprocal Rank Fusion (RRF): merges multiple ranked retrieval result
lists into one combined ranking.

Belongs in `rag/hybrid.py`.

FAISS's cosine-similarity scores and BM25's term-frequency scores live on
completely different, incomparable scales -- there's no principled way
to add "0.87 cosine similarity" to "4.2 BM25 score" directly. RRF sidesteps
that problem entirely: it only looks at each item's *rank position*
within each list (1st, 2nd, 3rd...), not its raw score, so no score
normalization is needed at all.
"""

from typing import Any, Dict, List

# The standard constant from the original RRF paper (Cormack et al.,
# 2009). It de-emphasizes small rank differences (being ranked 1st vs.
# 2nd matters less than you'd think with this constant) without needing
# any per-query tuning -- this default is used essentially unchanged
# across most production hybrid-search systems.
RRF_K = 60


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Merge several ranked lists (each ordered best-first, each item a
    dict with a "chunk_id" key) into one fused ranking.

    Each item's fused score is the sum, across every list it appears in,
    of 1 / (RRF_K + rank_within_that_list + 1). An item ranked well in
    BOTH the dense and sparse results ends up highest overall; an item
    only one method found still gets partial credit, just less of it --
    so hybrid search never does *worse* than the better of the two
    individual methods for a well-matched item, and can surface an item
    only one method found on its own.
    """
    fused_scores: Dict[int, float] = {}
    chunk_lookup: Dict[int, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list):
            chunk_id = item["chunk_id"]
            fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
            chunk_lookup.setdefault(chunk_id, item)

    ranked_chunk_ids = sorted(fused_scores, key=lambda cid: fused_scores[cid], reverse=True)

    results = []
    for chunk_id in ranked_chunk_ids[:top_k]:
        item = dict(chunk_lookup[chunk_id])
        item["score"] = fused_scores[chunk_id]  # replace with the fused RRF score
        results.append(item)
    return results
