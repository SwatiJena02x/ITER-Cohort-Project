"""POST /analyze endpoint.

Flow:
1. Run AST analyzer against the code for this problem's anti_patterns
2. Retrieve relevant DSA knowledge via hybrid RAG search
3. If a rule matches → call Groq with persona voice + anti-pattern + RAG context
4. Return structured {comment, tone, hint_available}
"""
from fastapi import APIRouter, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.ast_analyzer import analyze_code
from app.services.llm_client import generate_analyze_comment

router = APIRouter()


def _get_stores():
    from app.main import problems_store, personas_store
    return problems_store, personas_store


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """Analyze user code for anti-patterns, generate in-character comment if triggered."""
    problems_store, personas_store = _get_stores()

    problem = problems_store.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{req.problem_id}' not found")

    persona = personas_store.get(req.persona)
    if not persona:
        raise HTTPException(status_code=400, detail=f"Persona '{req.persona}' not found")

    # Step 1: Deterministic AST check
    matched_pattern = analyze_code(req.code, problem.get("anti_patterns", []))

    # Step 2: LLM call to generate in-character comment
    result = generate_analyze_comment(
        persona_voice=persona["voice"],
        anti_pattern=matched_pattern,
        code=req.code,
        optimal_solutions=problem.get("optimal_solutions", []),
        previous_comments=req.previous_comments,
    )

    return AnalyzeResponse(
        triggered=True,
        comment=result.get("comment"),
        tone=result.get("tone", "playful_warning"),
        hint_available=result.get("hint_available", True),
    )
