# ============================================================
# feedback.py
#
# DSA Coach API
#
# Endpoints:
#
# POST /feedback/analyze
# POST /hint
# GET  /feedback/health
#
# This file communicates with ai_service.py
# and returns structured feedback to the React frontend.
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import re

from services.ai_service import get_ai_feedback


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/feedback",
    tags=["DSA Feedback"]
)


# ============================================================
# Request Models
# ============================================================

class FeedbackRequest(BaseModel):
    problem: str
    language: str
    code: str
    approach: str


class HintRequest(BaseModel):
    problem: str
    language: str = "Python"
    code: str = ""
    approach: str = ""
    hint_level: int = 1


# ============================================================
# Helper Functions
# ============================================================

def extract_json(text: str):
    """
    Extract JSON from an AI response.

    Handles:
    1. Pure JSON
    2. JSON inside ```json ... ```
    3. JSON surrounded by additional text
    """

    if not text:
        return None

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    text = text.strip()

    # --------------------------------------------------------
    # Try direct JSON parsing
    # --------------------------------------------------------

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Find JSON object inside response
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    return None


def ensure_list(value):
    """
    Make sure a field is returned as a list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value]

    return [str(value)]


# ============================================================
# FEEDBACK PROMPT
# ============================================================

def build_feedback_prompt(
    problem: str,
    language: str,
    code: str,
    approach: str
):

    prompt = f"""
You are an expert DSA interview coach.

Evaluate the candidate's DSA solution.

You must analyze:

1. Correctness
2. Time complexity
3. Space complexity
4. Strengths
5. Weaknesses
6. Suggestions
7. Learning plan
8. Interview readiness

IMPORTANT:

- Do not invent information.
- Judge the submitted code.
- Consider edge cases.
- Consider the candidate's stated approach.
- Keep the feedback useful for a coding interview.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not wrap the JSON in ```json.

============================================================
PROBLEM
============================================================

{problem}

============================================================
LANGUAGE
============================================================

{language}

============================================================
CANDIDATE APPROACH
============================================================

{approach}

============================================================
SUBMITTED CODE
============================================================

{code}

============================================================
REQUIRED JSON FORMAT
============================================================

{{
    "overall_score": 0,
    "correctness": "",
    "time_complexity": "",
    "space_complexity": "",
    "interview_result": "",
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "learning_plan": []
}}

============================================================

Scoring rules:

90-100 = Strong
75-89  = Good
60-74  = Developing
40-59  = Needs Improvement
0-39   = Weak

Return only the JSON object.
"""

    return prompt


# ============================================================
# HINT PROMPT
# ============================================================

def build_hint_prompt(
    problem: str,
    language: str,
    code: str,
    approach: str,
    hint_level: int
):

    if hint_level == 1:
        hint_style = """
Give a conceptual hint.

Do NOT reveal the algorithm directly.
Point the candidate toward the right concept or data structure.
"""

    elif hint_level == 2:
        hint_style = """
Give a stronger algorithmic hint.

You may mention the appropriate data structure,
algorithmic pattern, or direction to investigate.

Do NOT provide complete solution code.
"""

    else:
        hint_style = """
Give a detailed final hint.

Explain the important steps the candidate should follow,
but DO NOT provide the complete executable solution.
"""

    prompt = f"""
You are an expert DSA interview coach.

Your task is to provide a progressive hint to a candidate.

{hint_style}

IMPORTANT:

- Do NOT provide the complete solution.
- Do NOT provide complete executable code.
- Do NOT reveal the final answer directly.
- Keep the hint concise and useful.
- Base the hint on the candidate's submitted code and approach.

============================================================
PROBLEM
============================================================

{problem}

============================================================
LANGUAGE
============================================================

{language}

============================================================
CANDIDATE APPROACH
============================================================

{approach}

============================================================
SUBMITTED CODE
============================================================

{code}

============================================================
HINT LEVEL
============================================================

{hint_level}

Return ONLY the hint text.
"""

    return prompt


# ============================================================
# ANALYZE SOLUTION
# ============================================================

@router.post("/analyze")
async def analyze_solution(request: FeedbackRequest):

    try:

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not request.problem.strip():
            raise HTTPException(
                status_code=400,
                detail="Problem statement is required."
            )

        if not request.code.strip():
            raise HTTPException(
                status_code=400,
                detail="Code is required."
            )

        if not request.approach.strip():
            raise HTTPException(
                status_code=400,
                detail="Approach is required."
            )

        # ----------------------------------------------------
        # Build prompt
        # ----------------------------------------------------

        prompt = build_feedback_prompt(
            problem=request.problem,
            language=request.language,
            code=request.code,
            approach=request.approach
        )

        # ----------------------------------------------------
        # Call AI
        # ----------------------------------------------------

        ai_response = get_ai_feedback(prompt)

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        feedback = extract_json(ai_response)

        # ----------------------------------------------------
        # If AI returned invalid JSON
        # ----------------------------------------------------

        if feedback is None:

            return {
                "feedback": {
                    "overall_score": 60,
                    "correctness": (
                        "The AI generated feedback, but the response "
                        "could not be parsed into structured feedback."
                    ),
                    "time_complexity": "Unable to determine",
                    "space_complexity": "Unable to determine",
                    "interview_result": (
                        "Review the submitted solution and try again."
                    ),
                    "strengths": [
                        "The solution was submitted successfully."
                    ],
                    "weaknesses": [
                        "AI response formatting could not be parsed."
                    ],
                    "suggestions": [
                        "Try submitting the solution again."
                    ],
                    "learning_plan": [
                        "Continue practicing DSA problems."
                    ]
                }
            }

        # ----------------------------------------------------
        # Normalize response
        # ----------------------------------------------------

        feedback["overall_score"] = int(
            feedback.get("overall_score", 60)
        )

        feedback["correctness"] = feedback.get(
            "correctness",
            "No correctness analysis was provided."
        )

        feedback["time_complexity"] = feedback.get(
            "time_complexity",
            "Not determined"
        )

        feedback["space_complexity"] = feedback.get(
            "space_complexity",
            "Not determined"
        )

        feedback["interview_result"] = feedback.get(
            "interview_result",
            "Keep practicing and improving your explanation."
        )

        feedback["strengths"] = ensure_list(
            feedback.get("strengths")
        )

        feedback["weaknesses"] = ensure_list(
            feedback.get("weaknesses")
        )

        feedback["suggestions"] = ensure_list(
            feedback.get("suggestions")
        )

        feedback["learning_plan"] = ensure_list(
            feedback.get("learning_plan")
        )

        # ----------------------------------------------------
        # Clamp score
        # ----------------------------------------------------

        feedback["overall_score"] = max(
            0,
            min(
                100,
                feedback["overall_score"]
            )
        )

        return {
            "feedback": feedback
        }

    except HTTPException:
        raise

    except Exception as e:

        print("Feedback analysis error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Feedback generation failed: {str(e)}"
        )


# ============================================================
# AI HINT
# ============================================================

@router.post("/hint")
async def generate_hint(request: HintRequest):

    try:

        # ----------------------------------------------------
        # Validate hint level
        # ----------------------------------------------------

        if request.hint_level < 1:
            request.hint_level = 1

        if request.hint_level > 3:
            request.hint_level = 3

        # ----------------------------------------------------
        # Validate problem
        # ----------------------------------------------------

        if not request.problem.strip():

            raise HTTPException(
                status_code=400,
                detail="Problem statement is required."
            )

        # ----------------------------------------------------
        # Build hint prompt
        # ----------------------------------------------------

        prompt = build_hint_prompt(
            problem=request.problem,
            language=request.language,
            code=request.code,
            approach=request.approach,
            hint_level=request.hint_level
        )

        # ----------------------------------------------------
        # Call AI
        # ----------------------------------------------------

        ai_response = get_ai_feedback(prompt)

        if not ai_response:

            raise HTTPException(
                status_code=500,
                detail="The AI did not return a hint."
            )

        return {
            "hint": ai_response.strip(),
            "hint_level": request.hint_level
        }

    except HTTPException:
        raise

    except Exception as e:

        print("Hint generation error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Hint generation failed: {str(e)}"
        )


# ============================================================
# ROUTER HEALTH
# ============================================================

@router.get("/health")
async def feedback_health():

    return {
        "status": "ok",
        "service": "DSA Coach Feedback API"
    }