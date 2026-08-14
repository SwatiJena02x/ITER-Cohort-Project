"""POST /execute endpoint.

Sends user code + test cases to Piston for sandboxed execution.
Returns pass/fail per test case.
"""
from fastapi import APIRouter, HTTPException
from app.models import ExecuteRequest, ExecuteResponse, TestResult
from app.services.piston_client import execute_code, extract_function_name

router = APIRouter()


def _get_problems_store():
    from app.main import problems_store
    return problems_store


@router.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest):
    """Execute user code against the problem's test cases."""
    problems_store = _get_problems_store()

    problem = problems_store.get(req.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem '{req.problem_id}' not found")

    function_name = extract_function_name(problem["starter_code"])

    results = await execute_code(
        code=req.code,
        test_cases=problem["test_cases"],
        function_name=function_name,
    )

    all_passed = all(r["passed"] for r in results)

    return ExecuteResponse(
        passed=all_passed,
        results=[
            TestResult(
                input=r["input"],
                expected=r["expected"],
                actual=r["actual"],
                passed=r["passed"],
            )
            for r in results
        ],
    )
