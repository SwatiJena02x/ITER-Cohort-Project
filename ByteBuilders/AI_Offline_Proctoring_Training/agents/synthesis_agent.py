"""Risk synthesis node: retrieves relevant rules and explains the risk score via LLM.

Belongs in the `agents` package (agents/synthesis_agent.py). This is the
ONLY synthesis_agent.py that should exist in the codebase.

Two additions on top of the previous version:

1. HYBRID RETRIEVAL (rag/bm25_retriever.py + rag/hybrid.py): rule
   retrieval now combines dense (FAISS/embedding) search with sparse
   (BM25 keyword) search, merged via Reciprocal Rank Fusion. Dense search
   alone can under-rank a rule that shares an exact, distinctive keyword
   with the query in favor of a more generally-similar-but-less-precise
   rule; BM25 catches that. See rag/hybrid.py's docstring for why RRF
   specifically (no score normalization needed between the two very
   different scales FAISS and BM25 produce).

2. RETRY LOOP: if the LLM's synthesis response is missing one or more
   required section headers (a malformed response), this node is wired
   in graph/workflow.py with a conditional self-loop -- it re-runs with
   a corrective prompt, up to MAX_SYNTHESIS_ATTEMPTS times, before
   falling through to report_agent regardless. A genuine LLM-call
   failure (e.g. Ollama unreachable) does NOT trigger a retry loop --
   that's a different failure mode (see the except block below), and
   retrying a connection failure repeatedly would be pointless; it falls
   back to the deterministic risk_reason immediately instead.
"""

import logging
from typing import Any, Dict, List, Tuple

from langsmith import traceable

from agents.activity_agent import (
    format_audio_activity,
    format_behavior_activity,
    format_video_activity,
)
from llm.ollama_client import call_llm
from rag.bm25_retriever import build_bm25_index
from rag.embeddings import create_embeddings
from rag.exam_rules import split_into_rule_chunks
from rag.hybrid import reciprocal_rank_fusion
from rag.retriever import create_index, retrieve_rules

logger = logging.getLogger(__name__)

LLM_MODEL = "llama3.2"
LLM_OPTIONS = {"temperature": 0.2}

MAX_SYNTHESIS_ATTEMPTS = 2

# A valid synthesis response must contain all four required section
# headers -- this is what the retry loop checks for.
REQUIRED_SECTIONS = ("RISK LEVEL:", "ACTIVITY:", "RULES:", "EXPLANATION:")

# Built once per process from the embedded EXAM_RULES_TEXT constant.
_cached_index = None
_cached_chunks: List[str] = None
_cached_bm25_index = None


@traceable(name="build_rule_indexes", run_type="tool")
def _build_rule_indexes() -> Tuple[Any, List[str], Any]:
    """Build BOTH the FAISS (dense) and BM25 (sparse) indexes over the
    same rule_chunks, so retrieval can query both and fuse the results.
    """
    rule_chunks = split_into_rule_chunks()
    rule_embeddings = create_embeddings(rule_chunks)
    faiss_index = create_index(rule_embeddings)
    bm25_index = build_bm25_index(rule_chunks)
    return faiss_index, rule_chunks, bm25_index


def _get_rule_indexes() -> Tuple[Any, List[str], Any]:
    global _cached_index, _cached_chunks, _cached_bm25_index
    if _cached_index is None:
        logger.info("Building FAISS + BM25 rule indexes from embedded EXAM_RULES_TEXT")
        _cached_index, _cached_chunks, _cached_bm25_index = _build_rule_indexes()
    return _cached_index, _cached_chunks, _cached_bm25_index


def _format_context(rules: List[Dict[str, Any]]) -> str:
    return "\n\n".join(r.get("text", "") for r in rules)


@traceable(name="retrieve_relevant_rules_hybrid", run_type="retriever")
def _retrieve_relevant_rules_hybrid(
    faiss_index,
    rule_chunks: List[str],
    bm25_index,
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Query both retrieval methods, fuse via Reciprocal Rank Fusion."""
    query_embedding = create_embeddings([query])
    dense_results = retrieve_rules(faiss_index, rule_chunks, query_embedding, top_k=top_k)
    sparse_results = bm25_index.search(query, top_k=top_k)
    return reciprocal_rank_fusion([dense_results, sparse_results], top_k=top_k)


def _is_valid_synthesis(text: str) -> bool:
    """A well-formed synthesis response contains every required section
    header. Used by the retry loop to decide whether to accept this
    attempt or loop back for another try.
    """
    return bool(text) and all(section in text for section in REQUIRED_SECTIONS)


def _build_prompt(risk_level: str, risk_score: Any, activity_text: str, context: str, is_retry: bool) -> str:
    retry_note = ""
    if is_retry:
        retry_note = """

IMPORTANT: your previous response was missing one or more required
section headers. You MUST include all four headers exactly as written,
each on its own line: RISK LEVEL:, ACTIVITY:, RULES:, EXPLANATION:
"""

    return f"""\
You are a risk synthesis agent for an offline examination proctoring system.

You must NOT change the deterministic risk level.

Risk score:
{risk_score}

Risk level:
{risk_level}

Detected activity:
{activity_text}

Retrieved examination rules:
{context}

Explain why this session was classified as {risk_level} risk.

Do not claim that cheating is conclusively proven.

Be concise: 4-6 sentences total across all sections combined. State each
fact once -- do not repeat the risk level, the score, or any piece of
evidence more than once.
{retry_note}
Return:

RISK LEVEL:
{risk_level}

ACTIVITY:
Important suspicious activity, one line per item.

RULES:
Relevant examination rules, by number only (e.g. "RULE 1, RULE 3").

EXPLANATION:
1-2 sentences connecting the activity to the rules. Do not restate the
activity or rules list here.
"""


@traceable(name="synthesis_agent", run_type="chain")
def synthesis_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve rules relevant to the detected activity and explain the risk score.

    Retrieval (hybrid FAISS + BM25) is deterministic and always runs.
    The LLM explanation step is wrapped for two distinct failure modes:
    a genuine call failure falls back to the deterministic risk_reason
    immediately (synthesis_valid=True, no retry -- see module docstring);
    a malformed-but-successful response is retried, up to
    MAX_SYNTHESIS_ATTEMPTS, via graph/workflow.py's conditional self-loop.
    """
    attempts = state.get("synthesis_attempts", 0) + 1
    is_retry = attempts > 1

    print(f"[synthesis] retrieving rules and generating explanation... (attempt {attempts})")

    faiss_index, rule_chunks, bm25_index = _get_rule_indexes()

    video_text = format_video_activity(state.get("video_activity", []))
    audio_text = format_audio_activity(state.get("audio_activity", []))
    behavior_text = format_behavior_activity(state.get("behavior_activity", []))
    risk_level = state.get("risk_level", "UNKNOWN")
    risk_score = state.get("risk_score", 0)

    activity_text = (
        f"VIDEO ACTIVITY:\n{video_text}\n\n"
        f"AUDIO ACTIVITY:\n{audio_text}\n\n"
        f"BEHAVIOR ACTIVITY:\n{behavior_text}"
    )

    query = f"""\
Examination proctoring analysis.

Risk level:
{risk_level}

Risk score:
{risk_score}

Detected activity:

{activity_text}

Find the examination rules relevant to this activity.

Focus on:

mobile phones,
books,
electronic devices,
multiple people,
unauthorized materials,
and suspicious behavior.
"""

    rules = _retrieve_relevant_rules_hybrid(faiss_index, rule_chunks, bm25_index, query, top_k=5)

    for rule in rules:
        logger.debug("[%.4f] %s", rule["score"], rule["text"])
    print(f"[synthesis] {len(rules)} relevant rule(s) retrieved (hybrid)")

    context = _format_context(rules)
    prompt = _build_prompt(risk_level, risk_score, activity_text, context, is_retry)

    try:
        synthesis = call_llm(prompt, model=LLM_MODEL, options=LLM_OPTIONS)
        valid = _is_valid_synthesis(synthesis)
        if not valid:
            logger.warning(
                "Synthesis attempt %d/%d produced malformed output (missing required "
                "sections); %s",
                attempts, MAX_SYNTHESIS_ATTEMPTS,
                "retrying" if attempts < MAX_SYNTHESIS_ATTEMPTS else "accepting anyway",
            )
    except Exception as exc:
        logger.error("Synthesis LLM call failed: %s", exc, exc_info=True)
        synthesis = (
            state.get("risk_reason", "")
            + "\n\n[AI synthesis unavailable -- showing raw risk triggers only.]"
        )
        # A connection/model failure is not something retrying will fix --
        # treat it as "resolved" immediately so the loop exits instead of
        # retrying a network failure pointlessly.
        valid = True

    logger.debug("Risk synthesis: %s", synthesis)

    return {
        "retrieved_rules": rules,
        "risk_reason": synthesis,
        "synthesis_attempts": attempts,
        "synthesis_valid": valid or attempts >= MAX_SYNTHESIS_ATTEMPTS,
        "step_history": state.get("step_history", []) + ["synthesis"],
    }
