"""Helpers for enriching LangSmith traces from within graph nodes.

Belongs in the `llm` package (llm/langsmith_utils.py).

llm.ollama_client.call_llm, rag.embeddings.create_embeddings, and
rag.retriever-adjacent retrieval calls already get their own traced spans.
This module adds the piece those didn't cover: tagging the *node-level*
run (e.g. risk_agent's own span) with something filterable -- like the
computed risk_level -- the moment it's known, from inside the node that
computed it, rather than only after the whole graph finishes.

main.py additionally tags the *root* run with the final risk_level once
`app.invoke()` returns, via `Client().update_run(...)`. That covers the
top-level run. This module covers node-level runs, so a HIGH-risk session
is filterable in the LangSmith UI/alerts at both the "give me all HIGH
sessions" (root run tag) and "give me the risk_agent span for a specific
HIGH session" (node run tag) granularity.
"""

import logging

logger = logging.getLogger(__name__)


def tag_current_run(*tags: str) -> None:
    """Best-effort: add tags to the currently-executing LangSmith run tree.

    Safe to call whether or not tracing is enabled. If LangSmith isn't
    configured, or there's no active run tree (e.g. this node is being
    unit-tested in isolation, outside a traced call), this silently
    no-ops rather than raising -- tagging is an observability nicety and
    must never affect pipeline correctness or availability.
    """
    if not tags:
        return
    try:
        from langsmith.run_helpers import get_current_run_tree

        run_tree = get_current_run_tree()
        if run_tree is None:
            return
        existing = set(run_tree.tags or [])
        run_tree.tags = sorted(existing | set(tags))
    except Exception:
        logger.debug("Skipping LangSmith run tagging", exc_info=True)


def log_current_run_metadata(**metadata) -> None:
    """Best-effort: attach extra metadata (e.g. risk_score) to the current run.

    Same non-fatal contract as tag_current_run -- never raises.
    """
    if not metadata:
        return
    try:
        from langsmith.run_helpers import get_current_run_tree

        run_tree = get_current_run_tree()
        if run_tree is None:
            return
        run_tree.extra = {**(run_tree.extra or {}), **{"metadata": metadata}}
    except Exception:
        logger.debug("Skipping LangSmith run metadata logging", exc_info=True)
