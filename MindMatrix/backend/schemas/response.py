# ============================================================
# response.py
#
# Purpose:
# Defines API response format returned to the frontend.
#
# Shape below matches the JSON structure produced by
# supervisor_agent.py's LLM prompt (see supervisor_prompt).
# ============================================================

from pydantic import BaseModel, Field
from typing import List, Optional


class FinalFeedback(BaseModel):
    """Final combined feedback produced by the supervisor agent."""

    overall_score: int = Field(
        0, ge=0, le=100, description="Overall performance score out of 100."
    )
    correctness: str = Field(
        "", description="Evaluation of whether the solution is correct."
    )
    time_complexity: str = Field(
        "", description="Time complexity of the submitted solution, e.g. 'O(n)'."
    )
    space_complexity: str = Field(
        "", description="Space complexity of the submitted solution, e.g. 'O(1)'."
    )
    strengths: List[str] = Field(
        default_factory=list, description="What the candidate did well."
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Weak points in the solution or explanation."
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Concrete suggestions for improvement."
    )
    interview_result: str = Field(
        "", description="Overall interview-readiness verdict."
    )
    learning_plan: List[str] = Field(
        default_factory=list, description="Recommended topics/resources to study next."
    )

    # Only present if JSON parsing failed in parse_json_response()
    error: Optional[str] = Field(
        None, description="Present only if the AI response could not be parsed as JSON."
    )


class FeedbackResponse(BaseModel):
    """API response envelope returned to the frontend."""

    feedback: FinalFeedback

    class Config:
        json_schema_extra = {
            "example": {
                "feedback": {
                    "overall_score": 88,
                    "correctness": "Solution correctly solves the problem for all test cases.",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(n)",
                    "strengths": [
                        "Efficient single-pass hashmap approach",
                        "Clear variable naming",
                    ],
                    "weaknesses": ["No handling for empty input array"],
                    "suggestions": [
                        "Add an early return for empty input",
                        "Add a docstring explaining the approach",
                    ],
                    "interview_result": "Strong, interview-ready with minor polish needed.",
                    "learning_plan": [
                        "Practice more hashmap-based two-pointer variants",
                    ],
                    "error": None,
                }
            }
        }