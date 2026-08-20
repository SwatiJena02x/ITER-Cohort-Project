# ============================================================
# api/hint.py
#
# AI DSA Hint API
#
# Endpoint:
# POST /hint
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ai_service import get_ai_feedback


# ============================================================
# ⭐ CHANGE 1:
# Create API router
# ============================================================

router = APIRouter()


# ============================================================
# Request Schema
# ============================================================

class HintRequest(BaseModel):

    problem: str

    language: str = "Python"

    code: str = ""

    approach: str = ""

    hint_level: int = 1


# ============================================================
# Response Schema
# ============================================================

class HintResponse(BaseModel):

    hint: str

    hint_level: int


# ============================================================
# ⭐ CHANGE 2:
# POST /hint
#
# This is the endpoint your frontend is calling:
#
# axios.post("/hint", ...)
# ============================================================

@router.post("/hint", response_model=HintResponse)
def generate_hint(request: HintRequest):

    # --------------------------------------------------------
    # Validate problem
    # --------------------------------------------------------

    if not request.problem.strip():

        raise HTTPException(
            status_code=400,
            detail="Problem statement is required."
        )


    # --------------------------------------------------------
    # Validate hint level
    # --------------------------------------------------------

    if request.hint_level not in [1, 2, 3]:

        raise HTTPException(
            status_code=400,
            detail="Hint level must be 1, 2, or 3."
        )


    # ========================================================
    # ⭐ CHANGE 3:
    # Different instructions for each hint level
    # ========================================================

    if request.hint_level == 1:

        guidance = """
Give a gentle conceptual hint.

Help the student understand:

- the important observation
- the likely DSA pattern
- the possible data structure

Do NOT give the complete algorithm.
Do NOT provide code.
Do NOT reveal the final answer.
"""


    elif request.hint_level == 2:

        guidance = """
Give a stronger algorithmic hint.

Explain:

- which algorithm may be useful
- which data structure may help
- how the student should think about the solution
- an important condition or observation

Do NOT provide complete code.
Do NOT reveal the complete solution.
"""


    else:

        guidance = """
Give a detailed final hint.

Explain the important algorithmic steps
and reasoning needed to solve the problem.

The student should be able to implement
the solution after reading this hint.

Do NOT provide complete executable code.
Do NOT provide the final solution directly.
"""


    # ========================================================
    # ⭐ CHANGE 4:
    # Build AI prompt
    #
    # Using normal string concatenation instead of a huge
    # triple-quoted f-string avoids the previous:
    #
    # SyntaxError: unterminated triple-quoted string
    # ========================================================

    prompt = (
        "You are an expert DSA interview coach.\n\n"

        "Your job is to help a student solve a DSA problem "
        "without directly giving the complete solution.\n\n"

        + guidance +

        "\n\n"
        "PROBLEM:\n"
        + request.problem +

        "\n\n"
        "LANGUAGE:\n"
        + request.language +

        "\n\n"
        "STUDENT CODE:\n"
        + request.code +

        "\n\n"
        "STUDENT APPROACH:\n"
        + request.approach +

        "\n\n"
        "HINT LEVEL:\n"
        + str(request.hint_level) +

        "\n\n"
        "Return ONLY the hint text.\n\n"

        "Do not include:\n"
        "- complete solution code\n"
        "- code blocks\n"
        "- final answer\n"
        "- unnecessary introduction"
    )


    # ========================================================
    # ⭐ CHANGE 5:
    # Call Groq AI
    # ========================================================

    try:

        hint = get_ai_feedback(prompt)


        # ----------------------------------------------------
        # Check AI response
        # ----------------------------------------------------

        if not hint or not hint.strip():

            raise HTTPException(
                status_code=500,
                detail="The AI did not return a hint."
            )


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return HintResponse(

            hint=hint.strip(),

            hint_level=request.hint_level

        )


    except HTTPException:

        raise


    except Exception as e:

        print("========================================")
        print("HINT API ERROR")
        print("========================================")
        print(repr(e))
        print("========================================")


        raise HTTPException(

            status_code=500,

            detail=f"Failed to generate hint: {str(e)}"

        )