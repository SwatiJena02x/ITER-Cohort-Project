"""Problem endpoints — GET /problems and GET /problems/{id}.

Only returns public fields: id, title, difficulty, description, starter_code, test_cases.
Never exposes optimal, anti_patterns, or hints.
"""
from fastapi import APIRouter, HTTPException
from app.models import ProblemSummary, ProblemDetail

router = APIRouter()


def _get_problems_store():
    """Import here to avoid circular imports."""
    from app.main import problems_store
    return problems_store


@router.get("/problems", response_model=list[ProblemSummary])
async def list_problems():
    """Return summary list of all available problems."""
    store = _get_problems_store()
    return [
        ProblemSummary(id=p["id"], title=p["title"], difficulty=p["difficulty"])
        for p in store.values()
    ]


@router.get("/problems/{problem_id}", response_model=ProblemDetail)
async def get_problem(problem_id: str):
    """Return public details for a single problem. Never leaks solution data."""
    store = _get_problems_store()
    problem = store.get(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")

    return ProblemDetail(
        id=problem["id"],
        title=problem["title"],
        difficulty=problem["difficulty"],
        description=problem["description"],
        starter_code=problem["starter_code"],
        test_cases=problem["test_cases"],
    )
