"""POST /hint endpoint.

Returns the hint for the requested tier (0, 1, or 2), rephrased in the persona's voice.
Uses RAG to enrich the hint with relevant DSA knowledge.
Only returns the current tier's text — never exposes the full hints list.
"""
from fastapi import APIRouter, HTTPException
from app.models import HintRequest, HintResponse
from app.services.llm_client import generate_hint_in_character
from app.services.rag_service import hybrid_search

router = APIRouter()


def _get_stores():
    from app.main import problems_store, personas_store
    return problems_store, personas_store


@router.post("/hint", response_model=HintResponse)
async def get_hint(req: HintRequest):
    """Return a single hint tier, rephrased in the persona's voice."""
    problems_store, personas_store = _get_stores()

    problem = problems_store.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{req.problem_id}' not found")

    persona = personas_store.get(req.persona)
    if not persona:
        raise HTTPException(status_code=400, detail=f"Persona '{req.persona}' not found")

    hints = problem.get("hints", [])
    if req.tier < 0 or req.tier >= len(hints):
        raise HTTPException(status_code=400, detail=f"Invalid hint tier {req.tier}. Available: 0-{len(hints)-1}")

    raw_hint = hints[req.tier]

    # RAG retrieval — use the hint text as search query for enrichment
    rag_context = hybrid_search(raw_hint, top_k=2)

    # Rephrase in persona's voice via LLM with RAG context
    hint_text = generate_hint_in_character(
        persona_voice=persona["voice"],
        hint_text=raw_hint,
        rag_context=rag_context,
    )

    return HintResponse(hint_text=hint_text)
